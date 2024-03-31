import secrets
import string
import json
from datetime import date,datetime
import os,io
from PIL import Image
import requests
import replicate 

def random_str(n=8):
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits
    # Generate the unreplicable string of length 8
    unreplicable_string = ''.join(secrets.choice(characters) for _ in range(n))
    return unreplicable_string


def append_message_to_json_file(file_path, message):
    """
    Appends a message to a list in a JSON file.

    :param file_path: The path to the JSON file.
    :param message: The message to append.
    """
    try:
        # Read the current content of the file
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file does not exist, start with an empty list
        data = []
    except json.JSONDecodeError:
        # If the file is empty or contains invalid JSON, start with an empty list
        data = []

    # Append the message to the data (assuming it's a list)
    data.append(message.copy())

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    return data


def Gen_image(prompt,lr=0.8,
              model="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
              save_loc="/home/jarvissan21/lost-in-shinjuku/chat_gpt_flask/templates/static/images/",type="background"):
  if type=="background":
    w=1280
    h=720
  elif type=="character":
    w=720
    h=1280
  #Gen image
  output = replicate.run(
      model,
      input={
          "width": w,
          "height": h,
          "prompt": prompt+", in a anime style",
          "refine": "no_refiner",
          "scheduler": "K_EULER",
          "lora_scale": lr,
          "num_outputs": 1,
          "guidance_scale": 7.5,
          "apply_watermark": True,
          "high_noise_frac": 0.8,
          "seed":2024331,
          "negative_prompt": "",
          "prompt_strength": 0.8,
          "num_inference_steps": 50
      }
  )
 

  #Get image
  img_url=output[0]
  r=requests.get(img_url)
  image = Image.open(io.BytesIO(r.content))
  #Img edig
  if type=="character":
    print("Cut background")

  #Save image
  file_saveloc=os.path.join(save_loc,f"GenImage_{type}_{date.today().strftime('%Y-%m-%d')}_{random_str()}.png")
  image.save(file_saveloc)
  return image,img_url #file_saveloc
