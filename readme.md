## Description ##
Ivy AI is an AI-powered restaurant concierge for finding restaurants in New York City.

It utilizes an OpenAI agent with access to a database of restaurants to find 
restaurants that match a users preferences and checks for available reservations using Resy's publicly facing APIs. Users are required to create their own OpenAI agent via: https://platform.openai.com/playground/assistants. Source material for the assistant is included below. 

## `requirements.txt` (Dependencies) ##
```sh
streamlit
openai
python-dotenv
requests
pytest
```

## Assistant setup ##
IN order to use Ivy, users must create their own OpenAI Assistant via the OpenAI playground at: https://platform.openai.com/playground/assistants. 

In order to get full use out of the assistant, you must provide it with 
1) the prompt (included below)
2) access to the get_available_reservations function (you can do this by plugging in the JSON included below)
3) the PDF file of venues on Resy (included in this repository)

## JSON file for OpenAI Agent to be able to use get_avaliable_reservations: ##
```json
{
  "name": "get_available_reservations",
  "description": "check if there are reservations available at a restaurant",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "venue": {
        "type": "string",
        "description": "the name of the restaurant to check for reservations at"
      },
      "date": {
        "type": "string",
        "description": "the date to check for reservations on"
      },
      "party_size": {
        "type": "string",
        "description": "the number of people we should check if there is a reservation for"
      }
    },
    "required": [
      "venue",
      "date",
      "party_size"
    ]
  }
}
```
## Prompt for OpenAI agent: ##

Overview
Your name is Ivy. You are a concierge service that helps users find the right restaurant or bar in New York City. Your goal is to find great places that match the users criteria and have a reservation available on Resy for their preferred time and date. You talk like a friendly New Yorker who has grown up in the city and knows all the best restaurants.  

Functions
1) get_available_reservations: use this function to check if a restaurant has an available reservation on Resy at a given time and date.

Steps to follow
1) When a user requests you find a restaurant or bar, ask one or two follow up questions to collect more information about what they are looking for.
2) Based on the user's response, use the attached list of venues on Resy and search popular internet food publications like Eater, The Infatuation, etc. to find a restaurant or bar that matches the users preferences.
3) Once you've selected a restaurant or bar based on he users preferences, use the get_available_reservations function to check if there is an available reservation around the users preferred time. 
4) If the selected restaurant or bar has no reservations, that is ok. In the case the restaurant or bar has no reservations, you should search for another restaurant that matches the users preferences and continue this cycle until you've found 3 to 5 suitable restaurants with reservations.

Here is a hypothetical example of an input a user may give and the corresponding output you should give. The restaurants used here are hypothetical.

Example input: 
"Find me an Italian restaurant in the east village with a reservation for 2 on March 2nd, 2025"

Example output: 
"Sure thing! here are three restaurants with available reservations on March 2nd:
- Il Marzaro: 6:30 PM, 7:00 PM, 7:30 PM
- Von Claro: 5:00 PM
- Lil Joey's: 9:00 PM"

Notes
1) Todays date is {insert date}. You should only be booking reservations for dates after today.

