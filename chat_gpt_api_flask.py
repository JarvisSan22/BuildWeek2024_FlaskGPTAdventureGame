from openai import OpenAI
import os 
from flask import Flask, request, jsonify,render_template,session

import json
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
#os.environ["OPENAI_API_KEY"]=os.getenv('API_KEY')

from utils import random_str,append_message_to_json_file,Gen_image

section_file="test.json" #random_str()+".json"
client = OpenAI()


# Initialize the Flask application
app = Flask(__name__)

client = OpenAI()
def ChatGTP_call(messages,model="gpt-3.5-turbo"):
        response = client.chat.completions.create(
        model=model,
        messages=messages,
        )
        # Extract the text of the response
        bot_response = response.choices[0].message.content
        return bot_response

# Set your OpenAI API key here
system_data = """
You are an adventure game storybook, 
You Foreigner in Japan and are preparing for a date in Shinjiku station,
you must navigate Shinjuku station to collect  3 random items , from the item list , for your date, and complete 2 tasks from the task list then finnaly meet your date,
The game ends when you Gather all the items for your date then meet a date in Shibuya station,
The user can only speak English and must overcome Japanese people who only speak in Japanese
For each phase of the game, give the story and a description of the scene for image generation AI,
The user will be given 4 options  on  how they want to interact with the story to move to the next phase,
the game is not easy, you can fail your date and die, there is a murderer on the lose
The story start with the first start input 
Output as JSON file, with the phase number, story, description_scene, with the options as 1 2 3 4 
item list 
・Roses
・Box Chocolates
・Otaku Tshirt
・Anime merch 
・BDay Cake
・Neckless
・PhotoFrame
・Japan merch
Actions list 
・Book a room for the night Love hotel
・Put your baggage in the locker 
・Go for a shower in the Manga Cafe 
・Get Hair cut 
・Buy some new clothes 

"""
#messages=[{"role": "system","content":system_data}]
#_=append_message_to_json_file(section_file,messages)
def setup_response(data):
    story=data["story"]
    image_dec=data["description_scene"]
    
    
    
    
    button_messages = {}
    button_states = {}
    options=data["options"]
    if "/n" in options:
        options=options.split("\n")
        for i, option in enumerate(options):
            print(i,option)
            button_messages[f"{i+1}"] = option
    else:
        button_messages=options
    # Initialize the button states
    for button_name in button_messages.keys():
        button_states[button_name] = False

    # Generate an image based on the chat response text    
    _,image_url = Gen_image(image_dec)

    return story,image_url,button_messages,button_states

@app.route('/', methods=['GET','POST'])
def home():
    title="LOST-IN-SHINJIUKU"
    # Initialize the button messages and button states dictionaries
    button_messages = {}
    button_states = {}
    
    if request.method== "GET":
        if os.path.exists(section_file):
            os.remove(section_file)
        messages = append_message_to_json_file(section_file,{"role": "system","content":system_data})
        messages= append_message_to_json_file(section_file,{"role": "user", "content":"start"})
        #print(messages)
        bot_response =ChatGTP_call(messages)
        data=json.loads(bot_response)
        print(data)
        story,image_url,button_messages,button_states=setup_response(data)
        message = append_message_to_json_file(section_file,{'role':'assistant', 'content':bot_response })
       
   
     # If the request method is POST (i.e., a button has been clicked), update the chat
    message = None
    button_name = None
    if request.method == "POST":
        # Get the user message from the request
        button_name = request.form.get('button_name')
        print("button num", button_name)
         #Set the state of the button to "True"
        button_states[button_name] = True
        # Get the message associated with the clicked button
        #user_message = button_messages.get(button_name)
        messages = append_message_to_json_file(section_file,{"role": "user", "content":button_name})
        # Generate a response using OpenAI's GPT model
        print(messages)
        bot_response =ChatGTP_call(messages)
        data=json.loads(bot_response)
        story,image_url,button_messages,button_states=setup_response(data)

        message = append_message_to_json_file(section_file,{'role':'assistant', 'content':bot_response })
        #message[]
        
        
        
    return render_template('home.html', title=title, 
                           text=story, image_url=image_url, 
                           button_messages=button_messages,
                             button_states=button_states, 
                             message=message)

        #return jsonify({'response': bot_response})
    
    



if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000)
