
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import requests
import json
from datetime import datetime, timedelta
import logging

# Configure the logging settings
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

headers = {
    'authority': 'api.resy.com',
    'method': 'POST',
    'path': '/3/venuesearch/search',
    'scheme': 'https',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'Authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json',
    'Origin': 'https://resy.com',
    'Referer': 'https://resy.com/',
    'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'X-Origin': 'https://resy.com',
}


# ========== algorithm to help decide if search successfuly chose the right restaurant ==========

def word_match_score(word1, word2):
    word1_lower = word1.lower()
    word2_lower = word2.lower()

    # Check if any letter from word1 appears in word2
    matching_letters = sum(1 for char1 in word1_lower if char1 in word2_lower)

    # Calculate the percentage of matching letters
    total_letters = min(len(word1_lower), len(word2_lower))
    match_percentage = (matching_letters / total_letters) * 100

    return match_percentage

# ========== Given a venue name, date, and party size from Ivy, return the venue ID ==========

# venue = string, party_size = int, date = string in format "YYYY-MM-DD"
def search_venue_id(venue, date, party_size):
    
    logging.info(f"Inputs to search_venue_id: venue={venue}, date={date}, party_size={party_size}")

    # setup search API call
    search_endpoint = "https://api.resy.com/3/venuesearch/search"

    original_payload = {
    "geo": {
        "latitude": 40.8241,
        "longitude": -73.8977
    },
    "highlight": {
        "pre_tag": "<b>",
        "post_tag": "</b>"
    },
    "per_page": 5,
    "query": venue,
    "slot_filter": {
        "day": date,
        "party_size": party_size
    },
    "types": ["venue", "cuisine"]
}

    # Convert to JSON
    json_payload = json.dumps(original_payload)

    #make post request to search API
    response = requests.post(search_endpoint, data=json_payload, headers=headers)

    # convert string response to JSON
    if response.status_code == 200:
        string_response = json.dumps(response.json(), indent=2)
        json_response = json.loads(string_response)

        # extract venue ID and name of result
        try:
            venue_id = json_response['search']['hits'][0]['id']['resy']
        except IndexError:
            logging.info("search_venue_id: no match on resy")
            return("a good match for this venue was not found on Resy")
        
        venue_name = json_response['search']['hits'][0]['name']

        # set matching % required and check if entered venue name is similar to resy venue name
        threshold_percent = 80

        # if yes, return venue ID
        if word_match_score(venue, venue_name) > threshold_percent:
            logging.info(f"search_venue_id: match was made, venue ID={venue_id}")
            return(venue_id)
        else:
            logging.info("search_venue_id: a match was found on Resy, but it doesnt match the input well")
            return("a good match for this venue was not found on Resy")
            
    else:
        return("there was an error with the Resy API")
    
    # if venue ID is returned, make call to check avaliability given time, date, and party size and venue ID

# ========== Given venue_id, date, and party size, get the avaliability on a given day ==========

def get_avaliability_venue_id(venue_id, date, party_size):
     
    # Make the API request
    avaliability_endpoint = "https://api.resy.com/4/find"

    headers = {
    'authority': 'api.resy.com',
    'method': 'GET',
    'path': '/4/find',
    'scheme': 'https',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'Authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json',
    'Origin': 'https://resy.com',
    'Referer': 'https://resy.com/',
    'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'X-Origin': 'https://resy.com',
}
    
    params = {
        "lat": "40.728843",
        "long": "-73.9802",
        "day": date,
        "party_size": party_size,
        "venue_id": venue_id
        }

    response = requests.get(avaliability_endpoint, headers=headers, params=params)
  
    response_json = response.json()
    

    # pull avaliable slots for the given date and party size
    avaliable_slots_json = response_json['results']['venues'][0]['slots']
    
    # this is a cool way to iteratively append items to a list, cleaner than a while statement
    avaliable_slots = [[slot['date']['start'].split(' ')[1],slot['config']['type'] ] for slot in avaliable_slots_json]

    for slot in avaliable_slots:
        slot[0] = datetime.strptime(slot[0], "%H:%M:%S")
        slot[0] = slot[0].strftime("%I:%M:%S %p")

    return(avaliable_slots)

# ========== Given venue name, date, and party size, return avaliability ==========

def get_avaliability_venue_name(venue, date, party_size):
    
    logging.info(f"Inputs to get_avaliable_venue_name call: venue={venue}, date={date}, party_size={party_size}")

    current_date = datetime.now()

    venue_id_search_response = search_venue_id(venue, date, party_size)
    # logging.info(f"venue_id_search_response is {venue_id_search_response}")

    if isinstance(venue_id_search_response, int):
        valid_venue_id = venue_id_search_response
        
        avaliable_reservations = get_avaliability_venue_id(valid_venue_id, date, party_size)

        if not avaliable_reservations:
            return("the venue was found, but there are no reservations avaliable")
        
        else:
            return(avaliable_reservations)

    else:
        if venue_id_search_response == "a good match for this venue was not found on Resy":
            return("a good match for this venue was not found on Resy")
        else:
            return("a valid venue ID was not found")