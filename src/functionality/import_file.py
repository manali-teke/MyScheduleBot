import os
import csv
import discord
import pandas as pd
import tempfile
from discord import Attachment
from functionality.shared_functions import create_event_tree, create_type_tree, add_event_to_file, turn_types_to_string
from Event import Event
from parse.match import parse_period
from icalendar import Calendar

import fnmatch


def verify_csv(data):
    """
    Function:
        verify_csv
    Description:
        Verifies that CSV data retrieved through pandas matches the expected format
    Input:
        data - A Pandas Dataframe of data pulled from a CSV
    Output:
        - True if the data matches the expectation, false otherwise
    """

    if data.columns[0] != "ID":
        return False
    if data.columns[1] != "Name":
        return False
    if data.columns[2] != "Start Date":
        return False
    if data.columns[3] != "End Date":
        return False
    if data.columns[4] != "Priority":
        return False
    if data.columns[5] != "Type":
        return False
    if data.columns[6] != "Url":
        return False
    if data.columns[7] != "Location":
        return False
    if data.columns[8] != "Notes":
        return False

    return True


def convert_time(old_str):
    """
    Function:
        convert_time
    Description:
        Converts a time string from the YYYY-MM-DD HH:MM:SS format to the mm/dd/yy hh:mm am/pm format
    Input:
        old_str - The string to be converted
    Output:
        - the converted string
    """

    new_str = old_str[5:7] + '/' + old_str[8:10] + '/' + old_str[2:4] + ' '

    if(len(old_str)==10): #Doesn't include hours/minutes
        return new_str + "12:00 am"

    hour_int = int(old_str[11:13])
    if hour_int >= 12:
        am_or_pm = "pm"
        if hour_int != 12:
            hour_int = hour_int - 12
    else:
        am_or_pm = "am"

    hour = str(hour_int)
    if len(hour) == 1:
        hour = '0' + hour

    new_str = new_str + hour + ':' + old_str[14:16] + " " + am_or_pm

    return new_str


def get_ics_data(calendar):
    """
    Function:
        get_ics_data
    Description:
        Fethces relevant data from an ICS calendar
    Input:
        calendar - The string to be converted
    Output:
        - A pandas table containing the calendar data.
    """

    columns = ['ID',
               'Name',
               'Start Date',
               'End Date',
               'Priority',
               'Type',
               'Url',
               'Location',
               'Notes']

    data = pd.DataFrame(columns=columns)

    for component in calendar.walk():
        if component.name == "VEVENT":
            print("Adding Event....")
            data = data.append({'ID': '',
                         'Name': component.get('summary'),
                         'Start Date': str(component.get('dtstart').dt),
                         'End Date': str(component.get('dtend').dt),
                         'Priority': '3',
                         'Type': '',
                         'Url': component.get('url'),
                         'Location': component.get('location'),
                         'Notes': component.get('description')}, ignore_index=True)

    return data


async def import_file(ctx, client):
    """
    Function:
        importfile
    Description:
        Reads a CSV file containing events submitted by the user, and adds those events
    Input:
        ctx - Discord context window
        client - The Discord chat bot
    Output:
        - Events are added to a users profile.
    """
    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    user_id = str(ctx.author.id)

    # Checks if the calendar csv file exists, and creates it if it does not
    await channel.send("Please upload your file below.")

    # Loops until we receive a file.
    while True:

        event_msg = await client.wait_for("message", check=check)

        if len(event_msg.attachments) != 1:
            await channel.send("No file detected. Please upload your file below.\nYou can do this by dropping "
                               "the file directly into Discord. Do not write out the file contents in a message.")
        else:
            break

    temp_file = open("import_temp_file", "w")
    temp_path = str(os.path.abspath(temp_file.name))
    temp_file.close()
    try:
        await event_msg.attachments[0].save(temp_path, seek_begin=True, use_cached=False)

        if event_msg.attachments[0].filename.endswith(".csv"):
            data = pd.read_csv(temp_path)
        elif event_msg.attachments[0].filename.endswith(".ics"):
            temp_file = open("import_temp_file", "r")
            gcal = Calendar.from_ical(temp_file.read())
            temp_file.close()

            data = get_ics_data(gcal)

        else:
            await channel.send("File is not a CSV or ICS file. Import has failed.")
            return

        if not verify_csv(data):
            await channel.send("Unexpected CSV Format. Import has failed.")
            return

    except pd.errors.EmptyDataError:
        await channel.send("File is empty. Import has Failed.")
        return
    except pd.errors.ParserError:
        await channel.send("File is not a CSV. Import has Failed.")
        return
    finally:
        temp_file.close()
        os.remove(temp_path)

    if not verify_csv(data):
        await channel.send("Unexpected CSV Format. Import has failed.")
        return

    # creates an event tree if one doesn't exist yet.
    create_event_tree(str(ctx.author.id))

    for index, row in data.iterrows():
        print(convert_time(row['Start Date']) + ' ' + convert_time(row['End Date']))
        time_period = parse_period(convert_time(row['Start Date']) + ' ' + convert_time(row['End Date']))
        current = Event(row['Name'], time_period[0], time_period[1], row['Priority'], row['Type'], row["Url"], row['Location'], row['Notes'])
        add_event_to_file(str(ctx.author.id), current)

    await channel.send("Your events were successfully added!")
