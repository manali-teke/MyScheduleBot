import os
import csv
from datetime import datetime
from functionality.shared_functions import load_key, decrypt_file, encrypt_file
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

    # Checks if the calendar csv file exists, and creates it if it does not
    if not os.path.exists(os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv"):
        await channel.send("No events found to edit.")
        return

    key = load_key(user_id)
    decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")

    # Read existing events
    with open(os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv", "r") as events_file:
        events_reader = csv.reader(events_file)
        events_data = list(events_reader)

    # Display the list of events to the user
    events_msg = "Here are your existing events:\n"
    for index, event in enumerate(events_data, start=1):
        events_msg += f"{index}. {event[0]} - {event[1]} to {event[2]}\n"
    await channel.send(events_msg)

    await channel.send("Which event do you want to edit? Enter the event number.")

    event_msg = await client.wait_for("message", check=check)  # Wait for user input
    event_number = int(event_msg.content) - 1  # Adjust for 0-based indexing

    # Check if the entered event number is valid
    if 0 <= event_number < len(events_data):
        selected_event = events_data[event_number]

        # Call the edit_event_type function to modify the event
        await edit_event_type(ctx, client, selected_event)

        await channel.send("Your event was successfully edited!")

    else:
        await channel.send("Invalid event number. Please try again.")

    # Encrypt and save the updated events to file
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")

async def edit_event_type(ctx, client, selected_event):
    """
    Function:
        edit_event_type
    Description:
        Walks a user through the event type editing process
    Input:
        ctx - Discord context window
        client - Discord bot user
        selected_event - The event to be edited
    Output:
        - An edited event type in the user's calendar file
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    # Display the selected event to the user
    await channel.send(f"Selected event: {selected_event[0]} - {selected_event[1]} to {selected_event[2]}")

    await channel.send("Enter the new name for the event:")
    event_msg = await client.wait_for("message", check=check)
    new_name = event_msg.content

    await channel.send("Enter the new start time for the event (hh:mm am/pm):")
    event_msg = await client.wait_for("message", check=check)
    new_start_time = parse_user_input_to_datetime(event_msg.content)

    await channel.send("Enter the new end time for the event (hh:mm am/pm):")
    event_msg = await client.wait_for("message", check=check)
    new_end_time = parse_user_input_to_datetime(event_msg.content)

    # Update the selected event
    selected_event[0] = new_name
    selected_event[1] = new_start_time.strftime("%I:%M %p")
    selected_event[2] = new_end_time.strftime("%I:%M %p")

    # Inform the user that the event type has been successfully updated
    await channel.send(f"Event type '{new_name}' has been successfully updated from {new_start_time} to {new_end_time}")

# Call this function to edit events
#await edit_event(ctx, client)
