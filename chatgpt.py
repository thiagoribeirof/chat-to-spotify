import os
import openai
import re
import json

openai.api_key = "YOUR OPENAI API KEY GOES HERE" #ATTENTION: must not be shared. it's better implemented as environment variable.

MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.7 #temperature defines the 'creativity' of the model


def callPrompt(prompt): #callPrompt method
    response = openai.ChatCompletion.create( #defining a variable calling the openai chat method
        model=MODEL,
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful and creative assistant. Your goal is to"
                "help creating song playlists.",
            },
            {"role": "user", "content": "Create a playlist with: "+prompt},
            {"role": "user", "content": "\nMake sure to include around 50 different songs."},
            {
                "role": "user",
                "content": "\nReturn an array of songs in a JSON object called 'songs', including artist name as 'artist' and song name as 'song' for each song"
            },
            {
                "role": "user",
                "content": "\nThe response must not include any human comment, just the JSON object." #defining the response as JSON obj in order to make it easier.
            }
        ],
        temperature=TEMPERATURE,
    )
    chatGptReply = response["choices"][0]["message"]["content"] #getting the content
    jsonObj = json.loads(chatGptReply) #transforms jsonObj to python dict

    return jsonObj #return the python dict, similar to a json obj


