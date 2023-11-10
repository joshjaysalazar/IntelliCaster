import base64
import os
import time

import elevenlabs
import openai
from PIL import Image
import pyautogui
import pygetwindow as gw


class TextGenerator:
    """
    Handles text generation for race commentary.

    Uses OpenAI's GPT to generate text commentary based on events, roles,
    tones, and additional information. Maintains a list of previous responses
    to use as context for future commentary.
    """

    def __init__(self, settings):
        """Initialize the TextGenerator class.
    
        Initializes the OpenAI API key and sets up an empty list to hold
        previous responses generated for commentary.

        Args:
            settings (ConfigParser): The settings containing API keys and
            other configurations.

        Attributes:
            settings (ConfigParser): The settings containing API keys and
            other configurations.
            previous_responses (list): A list of previous responses generated
            for commentary.
        """
        # Member variables
        self.settings = settings

        # Create the OpenAI client
        self.client = openai.OpenAI(
            api_key=self.settings["keys"]["openai_api_key"]
        )

        # Pick the appropriate model based on settings
        model_setting = self.settings["commentary"]["gpt_model"]
        if model_setting == "GPT-3.5 Turbo":
            self.model = "gpt-3.5-turbo"
        elif model_setting == "GPT-4 Turbo":
            self.model = "gpt-4-1106-preview"
        elif model_setting == "GPT-4 Turbo with Vision":
            self.model = "gpt-4-vision-preview"
        else:
            raise ValueError("Invalid GPT model setting.")

        # Create an empty list to hold previous responses
        self.previous_responses = []
    
    def generate(self, event, role, tone, ir, other_info=""):
        """Generate text commentary for the given event.
        
        Generates text commentary for the given event based on the provided
        instructions. Uses the provided iRacing information to provide context
        for the commentary. Adds the generated commentary to the list of
        previous responses.
        
        Args:
            event (str): The event that occurred.
            role (str): The role of the commentator.
            tone (str): The tone of the commentary.
            ir_info (dict): The information from iRacing.
            other_info (str): Additional information to be included in the
                system message.
        
        Returns:
            str: The generated commentary.
        """
        # Create an empty list to hold the messages
        messages = []

        # Start building the system message
        new_msg = ""

        # Get the names of the commentators
        pbp_name = self.settings["commentary"]["pbp_voice"]
        color_name = self.settings["commentary"]["color_voice"]

        # Add messages based on role
        if role == "play-by-play":
            # Add the name to the system message
            new_msg += "You are a motorsport play-by-play commentator named "
            new_msg += f"{pbp_name}. "
            new_msg += f"Your co-commentator is {color_name}. "

            # Add play-by-play instructions
            new_msg += "You will respond with a single short sentence. "
            new_msg += "Do not provide too much detail. Focus on the action. "
            new_msg += "Almost always refer to drivers by only their surname. "
            new_msg += f"Use a {tone} tone. "

        elif role == "color":
            # Add the name to the system message
            new_msg += "You are a motorsport color commentator named "
            new_msg += f"{color_name}. "
            new_msg += f"Your co-commentator is {pbp_name}. "

            # Add color instructions
            new_msg += "You will respond with one to two short sentences. "
            new_msg += "Stick to providing insight or context that enhances "
            new_msg += "the viewer's understanding. "
            new_msg += "Usually refer to drivers by only their surname. "
            new_msg += f"Use a {tone} tone. "

        # Add additional info to the end of the system message
        new_msg += other_info

        # Add the initial system message
        sys_init = {
            "role": "system",
            "name": "instructions",
            "content": new_msg
        }
        messages.append(sys_init)

        # Start building the event info system message
        new_msg = ""

        # Gather the information from iRacing
        track = ir["WeekendInfo"]["TrackDisplayName"]
        city = ir["WeekendInfo"]["TrackCity"]
        country = ir["WeekendInfo"]["TrackCountry"]
        air_temp = ir["WeekendInfo"]["TrackAirTemp"]
        track_temp = ir["WeekendInfo"]["TrackSurfaceTemp"]
        skies = ir["WeekendInfo"]["TrackSkies"]

        # Compile that information into a message
        new_msg += f"The race is at {track} in {city}, {country}. "
        new_msg += f"The air temperature is {air_temp}., and "
        new_msg += f"the track temperature is {track_temp}. "
        new_msg += f"The skies are {skies.lower()}. "

        # Add the event info system message
        sys_event = {
            "role": "system",
            "name": "event_info",
            "content": new_msg
        }
        messages.append(sys_event)

        # Add all previous messages to the list
        for msg in self.previous_responses:
            messages.append(msg)

        # Add the event message
        event_msg = {
            "role": "user",
            "content": event
        }
        messages.append(event_msg)

        # Add the event message to previous messages
        self.previous_responses.append(event_msg)

        # If the vision model is being used, add the image to the messages
        model_setting = self.settings["commentary"]["gpt_model"]
        if model_setting == "GPT-4 Turbo with Vision":
            # Set the screenshot path
            path = os.path.join(
                self.settings["general"]["iracing_path"],
                "videos"
            )

            # Get the iRacing window
            window = gw.getWindowsWithTitle("iRacing.com Simulator")[0]

            # Get the coordinates of the window
            x = window.left
            y = window.top
            width = window.width
            height = window.height

            # Take a screenshot of the window
            screenshot = pyautogui.screenshot(region=(x, y, width, height))

            # Save the screenshot
            screenshot_path = os.path.join(path, "screenshot.png")
            screenshot.save(screenshot_path)

            # Process the image and save it
            with Image.open(screenshot_path) as image:
                # Get the image's current dimensions
                width, height = image.size

                # Crop the left and right sides on center
                left = width // 4
                right = width - left
                top = 0
                bottom = height
                image = image.crop((left, top, right, bottom))

                # Resize the image
                image = image.resize((512, 512))

                # Save the image
                image.save(screenshot_path)

            # Encode that image in base64
            with open(screenshot_path, "rb") as file:
                encoded_image = base64.b64encode(file.read()).decode("utf-8")

            # Create the image message
            image_msg = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Use this image in addition to the other " \
                            "information to help you commentate."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                            "detail": "high"
                        }
                    }
                ]
            }

            # Add the image message to the list of messages
            messages.append(image_msg)

        # Call the API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=300
        )

        # Extract the response
        answer = response.choices[0].message.content

        # Add the response to the list of previous responses
        formatted_answer = {
            "role": "assistant",
            "name": pbp_name if role == "play-by-play" else color_name,
            "content": answer
        }
        self.previous_responses.append(formatted_answer)

        # If the list is too long, remove the two oldest responses
        length = int(self.settings["commentary"]["memory_limit"]) * 2
        if len(self.previous_responses) > length:
            self.previous_responses.pop(0)
            self.previous_responses.pop(0)

        # Return the answer
        return answer
    
class VoiceGenerator:
    """
    Handles text-to-speech functionality for race commentary.

    Utilizes the ElevenLabs API to convert text into audio. Handles the
    generation and saving of audio files.
    """

    def __init__(self, settings):
        """Initialize the VoiceGenerator class with the given settings.

        Sets up the API key for the ElevenLabs service, enabling text-to-speech
        capabilities for the application.

        Args:
            settings (ConfigParser): Settings parsed from an INI file.

        Attributes:
            settings (ConfigParser): Settings parsed from an INI file.
            tier (str): The user's subscription tier.
            sample_rate (int): The sample rate to use for audio.
        """
        # Member variables
        self.settings = settings

        # Set the API key
        elevenlabs.set_api_key(self.settings["keys"]["elevenlabs_api_key"])

        # Get the user's subscription tier
        user = elevenlabs.api.User.from_api()
        self.tier = user.subscription.tier

        # Set sample rate based on tier (used for time calculations)
        if self.tier == "free":
            self.sample_rate = 16000
        elif self.tier == "starter":
            self.sample_rate = 22050
        elif self.tier == "creator":
            self.sample_rate = 24000
        else:
            self.sample_rate = 44100

    def generate(self, text, timestamp, yelling=False, voice="Harry"):
        """Generate and save audio for the provided text.

        Calls the ElevenLabs API to create audio from the text using the
        specified voice, then saves the audio.

        Args:
            text (str): The text to convert to audio.
            timestamp (str): The timestamp of the event.
            yelling (bool): Whether or not to convert the text to yelling.
            voice (str): The voice to use for the audio.
        """
        # Convert to yelling for voice commentary if requested
        if yelling:
            text = text.upper()
            if text[-1] == ".":
                text = text[:-1] + "!!!"

        # Replace "P" with "P-" to avoid issues with the API
        for i in range(len(text)):
            if text[i] == "P" and text[i + 1].isdigit():
                # Replace the P with "P-"
                text = text[:i] + "P-" + text[i + 1:]

        # Generate and play audio
        audio = elevenlabs.generate(
            text=text,
            voice=voice,
            model="eleven_monolingual_v1"
        )

        # Get the iRacing videos folder
        path = os.path.join(self.settings["general"]["iracing_path"], "videos")

        # Create the file name
        file_name = f"commentary_{timestamp}.wav"

        # Save the audio to a file
        elevenlabs.save(audio, os.path.join(path, file_name))

        # Get the length of the audio file
        length = len(audio) / self.sample_rate

        # Wait for the length of the audio
        time.sleep(length)