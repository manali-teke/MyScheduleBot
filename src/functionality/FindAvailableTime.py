from datetime import datetime
import os
import csv
import re

from Event import Event
from functionality.create_event_type import create_event_type
from functionality.export_file import load_key, encrypt_file, decrypt_file


async def find_avaialbleTime(ctx, client):
    """
    Function:
        find_avaialbleTime
    Description:
        Lets the user know about entered time range for event_type
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A new event type is added to the users event_type file
        - Provides users with the time range for the given event
    """
    channel = await ctx.author.create_dm()

    # print(ctx.author.id)

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    await channel.send("Let's find time for your event. Enter the Event Type :-")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event = event_msg.content  # Strips message to just the text the user entered

    try:

        key = load_key(str(ctx.author.id))
        decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(
            ctx.author.id) + "event_types" + ".csv")
        de_type = True
        # Open the calendar file for user
        with open(
                os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(ctx.author.id) + "event_types" + ".csv",
                "r") as event_file:
            # Read the calendar file
            csv_reader = csv.reader(event_file, delimiter=',')
            # For every row in calendar file
            flag = False
            range1 = ''
            range2 = ''
            for row in csv_reader:
                # Get event details
                if row[0] == event:
                    flag = True
                    range1 = row[1]
                    range2 = row[2]
                    await channel.send(
                        "You have a time range from " + row[1] + ' to ' + row[2] + ' for events of type ' + row[0])
                    break

        encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(
            ctx.author.id) + "event_types" + ".csv")
        de_type = False
        event_created = False
        if flag == False:
            await channel.send("Looks like you currently don't have this event type." +
                               "Would you like to specify a time range for it (y/n)\n")
            event_msg1 = await client.wait_for("message", check=check)  # Waits for user input
            event_msg1 = event_msg1.content  # Strips message to just the text the user entered
            if event_msg1 == 'y':
                event_created = await create_event_type(ctx, client, event)
            elif event_msg1 == 'n':
                await channel.send("Event type creation is canceled")

            if event_created:
                decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(
                    ctx.author.id) + "event_types" + ".csv")
                de_type = True
                with open(os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(
                        ctx.author.id) + "event_types" + ".csv", "r") as event_file:
                    # Read the calendar file
                    csv_reader = csv.reader(event_file, delimiter=',')

                    for row in csv_reader:
                        # Get event details
                        if row[0] == event:
                            range1 = row[1]
                            range2 = row[2]
                            flag = True
                            await channel.send(
                                "You have a time range from " + row[1] + ' to ' + row[2] + ' for events of type ' + row[
                                    0])

                            de_type = False
                            break
                encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(
                    ctx.author.id) + "event_types" + ".csv")

        # matchedrows = getEventsOnDate(ctx,event.start_date)

    except FileNotFoundError as err:
        await channel.send(
            "Looks like I cannot find your event types. Try adding event types using the '!typecreate' command!")
        if de_type:
            encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(
                ctx.author.id) + "event_types" + ".csv")

    # Ask for the date
    await channel.send(
        "Now give me the date for you event. "
        + "Here is the format you should follow:\n"
        + "mm/dd/yy"
    )

    event_date = False
    date = ''
    # A loop that keeps running until a user enters correct start and end dates for their event following the required format
    while not event_date:
        msg_content = ""
        if ctx.message.author != client.user:
            # Waits for user input
            date_msg = await client.wait_for("message", check=check)
            # Strips message to just the text the user entered
            msg_content = date_msg.content

        try:
            date_ms = msg_content
            date = datetime.strptime(date_ms, "%m/%d/%y")
        except Exception as e:
            await channel.send(
                "Looks like "
                + str(e)
                + ". Please re-enter your dates.\n"
                + "Here is the format you should follow:\n"
                + "mm/dd/yy"
            )
            event_date = False
            continue

        event_date = True

    if date_ms != '':
        date_str = date.strftime("%Y-%m-%d")
        events = getEventsOnDate(ctx, date_str)
        msg = ''
        inte = findIntersection(date_ms, datetime.strptime(date_ms + " " + range1, "%m/%d/%y %I:%M %p"),
                                datetime.strptime(date_ms + " " + range2, "%m/%d/%y %I:%M %p"), events)
        avai_msg = ""
        if len(inte) == 0:
            avai_msg += "There is no available time for the event."
        else:
            avai_msg += "There are some available time slots for your event: \n"
            for t in inte:
                avai_msg += t.get('start').strftime("%Y-%m-%d %H:%M:%S") + " - " + t.get('end').strftime(
                    "%Y-%m-%d %H:%M:%S") + "\n"
        for e in events:
            msg += e.name + ", from " + e.start_date + " to " + e.end_date + "\n"
        await channel.send(
            "On " + date_str + ", you have scheduled: \n"
            + msg
            + "\n"
            + avai_msg
        )


def findIntersection(date, range1, range2, events):
    """
    Function:
        findIntersection
    Description:
        Find the intersection of the preferred time of event type and the scheduled events
    Input:
        date - String of date, the date that user is looking for available time
        range1 - The start time of the preferred time of event type
        range2 - The end time of the preferred time of event type
        events - A list of events which scheduled on the date
    Output:
        - A list of available time for the date
    """
    etime = []
    event_atime = []
    available_time = []
    for e in events:
        start_date = re.split("\s", e.start_date)
        end_date = re.split("\s", e.end_date)
        start = datetime.strptime(date + " " + start_date[1], "%m/%d/%y %H:%M:%S")
        end = ''
        if datetime.strptime(end_date[0], "%Y-%m-%d") > datetime.strptime(date, "%m/%d/%y"):
            end = datetime.strptime(date + " 24:00:00", "%m/%d/%y %H:%M:%S")
        else:
            end = datetime.strptime(date + " " + end_date[1], "%m/%d/%y %H:%M:%S")
        etime.append({'start': start, 'end': end})
    print(etime)
    # Find available time
    a_time = []
    if len(etime) == 0:
        pass
    else:
        for t in etime:
            aetime = []
            # If no intersection between event and favored time
            if range1 >= t.get('end'):
                free_start = range1
                free_end = range2
                aetime.append({'start': free_start, 'end': free_end})
            if range2 <= t.get('start'):
                free_start = range1
                free_end = range2
                aetime.append({'start': free_start, 'end': free_end})

            # If favored time in between the event
            if t.get('start') <= range1 < range2 <= t.get('end'):
                # do nothing
                pass

            # If favored time overlap the event
            if t.get('start') < range1 < t.get('end') < range2:
                free_start = t.get('end')
                free_end = range2
                aetime.append({'start': free_start, 'end': free_end})
            if range1 < t.get('start') < range2 < t.get('end'):
                free_start = range1
                free_end = t.get('start')
                aetime.append({'start': free_start, 'end': free_end})

            # If event in between the favored time
            if range1 <= t.get('start') < t.get('end') <= range2:
                free_start = range1
                free_end = t.get('start')
                aetime.append({'start': free_start, 'end': free_end})
                free_start = t.get('end')
                free_end = range2
                aetime.append({'start': free_start, 'end': free_end})

            event_atime.append(aetime)
        print(event_atime)
        if len(event_atime) == 1:
            available_time = event_atime[0]
        if len(event_atime) > 1:
            # Find intersection, if no intersection, then no available time
            next_event = event_atime[1]
            available_time = findInter(next_event, event_atime, 0, len(event_atime) - 1)

    return available_time


def findInter(next_event, event_atime, idx, end):
    """
    Function:
        findInter
    Description:
        The helper iterator function to find the intersection
    Input:
        next_event - available time based on the next event
        event_atime - a list of available time based on events on date
        idx - index of the current available time in the list
        end - lenght of the list
    Output:
        - A list of available time for the date
    """
    if idx == end:
        return next_event
    available_time = []
    for at in event_atime[idx]:
        for nt in next_event:
            # If no intersection between event and favored time
            if at.get('start') >= nt.get('end'):
                pass
            if at.get('end') <= nt.get('start'):
                pass

            # If in between
            if nt.get('start') <= at.get('start') < at.get('end') <= nt.get('end'):
                free_start = at.get('start')
                free_end = at.get('end')
                f_time = {'start': free_start, 'end': free_end}
                if f_time not in available_time:
                    available_time.append({'start': free_start, 'end': free_end})

            if at.get('start') < nt.get('start') < nt.get('end') < at.get('end'):
                free_start = nt.get('start')
                free_end = nt.get('end')
                f_time = {'start': free_start, 'end': free_end}
                if f_time not in available_time:
                    available_time.append({'start': free_start, 'end': free_end})

            # If overlap
            if nt.get('start') <= at.get('start') < nt.get('end') <= at.get('end'):
                free_start = at.get('start')
                free_end = nt.get('end')
                f_time = {'start': free_start, 'end': free_end}
                if f_time not in available_time:
                    available_time.append({'start': free_start, 'end': free_end})
            if at.get('start') <= nt.get('start') < at.get('end') <= nt.get('end'):
                free_start = nt.get('start')
                free_end = at.get('end')
                f_time = {'start': free_start, 'end': free_end}
                if f_time not in available_time:
                    available_time.append({'start': free_start, 'end': free_end})
    return findInter(available_time, event_atime, idx + 1, end)


def getEventsOnDate(ctx, stdate):
    """
    Function:
        getEventsOnDate
    Description:
        Fetches the events on a particular day
    Input:
        ctx - Discord context window
        yourdate - Date for which events to be pulled
    Output:
        - Provides a list of events associated with that day
    """
    key = load_key(str(ctx.author.id))
    decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv")
    with open(os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv",
              "r") as calendar_lines:
        calendar_lines = csv.reader(calendar_lines, delimiter=",")
        fields = next(calendar_lines)  # The column headers will always be the first line of the csv file
        rows = []
        line = []
        line_number = 0
        for line in calendar_lines:
            if len(line) > 0:
                temp = re.split("\s", line[2])
                if str(temp[0]).__contains__(str(stdate)):
                    rows.append(line)

        Events = []
        for line in rows:
            eve = Event(line[1], line[2], line[3], line[4], line[5], line[6], line[7])
            Events.append(eve)
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv")
    return Events
