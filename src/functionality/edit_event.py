import os
import csv
from datetime import datetime
from functionality.shared_functions import load_key, decrypt_file, encrypt_file, add_event_to_file
from functionality.shared_functions import read_event_file, create_event_tree, delete_event_from_file
from functionality.create_event_type import parse_user_input_to_datetime
from discord.ext import commands

async def edit_event(ctx, client):
    """
    Function:
        edit_event
    Description:
        Walks a user through the event editing process
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - An edited event in the user's calendar file
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    user_id = str(ctx.author.id)

    # Open and read user's calendar file
    create_event_tree(str(ctx.author.id))
    rows = read_event_file(str(ctx.author.id)) 
    event = {'number':0,'name': '', 'start_date': '', 'end_date': '', 'priority': '0', 'type': '', 'url':'', 'location':'','desc': '',}
    events = []

   # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows:
            # Get event details
            print(row[0])
            event['number']= row[0]
            event['name'] = row[1]
            event['start_date'] = row[2]
            event['end_date'] = row[3]
            event['priority'] = row[4]
            event['type'] = row[5]
            event['url'] = row[6]
            event['location']=row[7]
            try:
                event['desc'] = row[8]
            except IndexError:
                event['desc'] = ''
            events.append(event)
    
    print(events)
    # # Display the list of events to the user
    events_msg = "Here are your existing events:\n"
    for index, event in enumerate(events, start=1):
        print(event)
        events_msg += f"{index}. {event['number']} - {event['start_date']} to {event['end_date']}\n"
    await channel.send(events_msg)

    await channel.send("Which event do you want to edit? Enter the event number.")

    event_msg = await client.wait_for("message", check=check)  # Wait for user input
    event_number = int(event_msg.content) - 1  # Adjust for 0-based indexing

    # Check if the entered event number is valid
    while not (0 <= event_number < len(events)):
        await channel.send("Invalid event number. Please try again.")

    selected_event = events[event_number]
    await channel.send(f"Selected event: {selected_event['name']} - {selected_event['start_date']} to {selected_event['end_date']}")
        
    await channel.send("Enter the new name for the event:")
    event_msg = await client.wait_for("message", check=check)
    new_name = event_msg.content

    await channel.send("Enter the new start date and start time for the event (mm/dd/yy hh:mm am/pm):")
    event_msg = await client.wait_for("message", check=check)
    new_start_date_time = datetime.strptime(event_msg.content, "%m/%d/%y %I:%M %p")

    await channel.send("Enter the new end date and end time for the event (mm/dd/yy hh:mm am/pm):")
    event_msg = await client.wait_for("message", check=check)
    new_end_date_time = datetime.strptime(event_msg.content, "%m/%d/%y %I:%M %p")

    # Update the selected event
    print(selected_event)
    selected_event['name'] = new_name
    selected_event['start_date'] = new_start_date_time
    selected_event['end_date'] = new_end_date_time
    print(selected_event)
    try:
        create_event_tree(str(ctx.author.id))
        add_event_to_file(str(ctx.author.id), selected_event)
    except Exception as e:
        # Outputs an error message if the event could not be created
        print(e)
        TracebackType.print_exc()
        await channel.send(
            "There was an error creating your event. Make sure your formatting is correct and try creating the event again."
        )
    await channel.send("Your event was successfully edited!")    

    # Encrypt and save the updated events to file
    # encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")
