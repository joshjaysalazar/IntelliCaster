import openai
import elevenlabs
import os
import time


class TextGenerator:
    """
    Handles text generation for race commentary.

    Uses OpenAI's GPT-3 to generate text commentary based on events, roles,
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
        """
        # Member variables
        self.settings = settings

        # Set the API key
        openai.api_key = self.settings["keys"]["openai_api_key"]

        # Create an empty list to hold previous responses
        self.previous_responses = []
    
    def generate(self, event, role, tone, ir_info, other_info=""):
        """Generate text commentary for the given event.
        
        Generates text commentary for the given event based on the provided
        role and tone. Uses the provided iRacing information to provide context
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
            new_msg += "Limit your response to a single short sentence. "
            new_msg += "Do not provide too much detail. Focus on the action. "
            new_msg += "Almost always refer to drivers by only their surname. "
            new_msg += f"Use a {tone} tone. "

        elif role == "color":
            # Add the name to the system message
            new_msg += "You are a motorsport color commentator named "
            new_msg += f"{color_name}. "
            new_msg += f"Your co-commentator is {pbp_name}. "

            # Add color instructions
            new_msg += "Limit your response to two short sentences. "
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
        track = ir_info["WeekendInfo"]["TrackDisplayName"]
        city = ir_info["WeekendInfo"]["TrackCity"]
        country = ir_info["WeekendInfo"]["TrackCountry"]
        air_temp = ir_info["WeekendInfo"]["TrackAirTemp"]
        track_temp = ir_info["WeekendInfo"]["TrackSurfaceTemp"]
        skies = ir_info["WeekendInfo"]["TrackSkies"]

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

        # Call the API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Extract the response
        answer = response["choices"][0]["message"]["content"]   

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

    Utilizes the ElevenLabs API to convert text into audio. Streams the
    generated audio to provide real-time commentary.
    """

    def __init__(self, settings):
        """Initialize the VoiceGenerator class with the given settings.

        Sets up the API key for the ElevenLabs service, enabling text-to-speech
        capabilities for the application.

        Args:
            settings (ConfigParser): Settings parsed from an INI file.
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
        """Generate and play audio for the provided text.

        Calls the ElevenLabs API to create audio from the text using the
        specified voice, then streams the audio.

        Args:
            text (str): The text to be converted to audio.
            voice (str, optional): The voice to use for text-to-speech. Defaults
                to "Arnold".
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