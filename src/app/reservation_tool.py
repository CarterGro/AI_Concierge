import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from resy_availability import get_avaliability_venue_name
from openai import OpenAI
import time
import json
from datetime import datetime
import logging

# Configure the logging settings
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Give OpenAI API Key and Assistant ID
def get_assistant(client, assistant_id):
    return client.beta.assistants.retrieve(assistant_id)

# get_avaliable_reservations takes (venue, date, party_size) and returns either a reservation report listing avaliable reservations or 
def get_avaliable_reservations(venue, date, party_size):

    # log the inputs to the function
    logging.info(f"Inputs to get_avaliable_reservation call: venue={venue}, date={date}, party_size={party_size}")

    # check if the date being asked for is in the past
    current_date = datetime.now()
    
    if datetime.strptime(date, "%Y-%m-%d") < current_date:
        return(f"the date {date} is invalid because it is the past. please enter a date sometime in the future.")
    
    # call get_avaliabilty_venue_name
    else:
        reservation_list = get_avaliability_venue_name(venue, date, party_size)
        if type(reservation_list) != list:
            if reservation_list == "a good match for this venue was not found on Resy":
                return("a good match for this venue was not found on Resy. Are you sure this restaurant exists?")
            else:
                return(f"{venue} does not have any avaliable reservations on {date}")
        else: 
            reservation_report = f"Here are the reservations available on {date} at {venue}: \n"

            for reservation in reservation_list:
                print(reservation)
                reservation_type = reservation[1]
                reservation_time = reservation[0]
                reservation_report += f"- There is a {reservation_type} reservation at {reservation_time} \n"
            print(reservation_report)   
            return reservation_report

def get_output_for_tool_call(tool_call):
    venue = json.loads(tool_call.function.arguments)['venue']
    date = json.loads(tool_call.function.arguments)['date']
    party_size = json.loads(tool_call.function.arguments)['party_size']
    
    print(venue, date, party_size)

    current_date = datetime.now()
    
    if datetime.strptime(date, "%Y-%m-%d") < current_date:
        return {
            "tool_call_id": tool_call.id,
            "output": f"The date {date} is invalid because it is in the past. Please enter a date sometime in the future."
        }
    
    avaliable_reservations = get_avaliable_reservations(venue=venue,date=date,party_size=party_size)
    logging.info(f"available reservations: {avaliable_reservations}")
        
    if avaliable_reservations == "the venue was found, but there are no reservations available":
        return {
            "tool_call_id": tool_call.id,
            "output": f"{venue} does not have any available reservations on {date}"
        }
        
    elif avaliable_reservations == "a good match for this venue was not found on Resy. Are you sure this restaurant exists?":
        return {
            "tool_call_id": tool_call.id,
            "output": "A good match for this venue was not found on Resy. Are you sure this restaurant exists?"
        }
    
    else:
        return {
            "tool_call_id": tool_call.id,
            "output": avaliable_reservations
        }
    
