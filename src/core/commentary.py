import openai
import elevenlabs
import os


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
    
    def generate(self, event, role, tone, limit, ir_info, other_info):
        """Generate race commentary text based on the given event and role.

        Constructs a prompt that includes behavioral instructions, role,
        tone, and any additional information. Sends the prompt to the OpenAI
        API to generate a response. Adds this response to a list of 
        previous responses for context in future calls.

        Args:
            event (str): The event to generate commentary for.
            role (str): The role of the commentary, e.g., "play-by-play".
            tone (str): The tone to use, e.g., "excited".
            limit (int): The word limit for the generated text.
            ir_info (dict): Information from iRacing.
            other_info (str): Any additional information to be included.

        Returns:
            str: The generated commentary text.
        """
        # Create an empty prompt
        prompt = ""

        # Add behavioral instructions
        prompt += "You are providing commentary to a race.\n"
        prompt += "Use previous events as context, but don't be repetitive.\n"
        prompt += "Do not, under any circumstances, invent details. Only " \
            "comment on the information you have.\n"
        prompt += "Use drivers' last names.\n"
        prompt += f"Your responses MUST NOT exceed {limit} words.\n"

        # Set role
        if role == "play-by-play":
            prompt += "You are the play-by-play commentator.\n"
            prompt += "Do not provide too much detail. Focus on the action.\n"
            prompt += "Limit your response to a single sentence."
            prompt += "Do not provide color commentary.\n"
            prompt += "DO NOT use unnecessary exclamations or filler " \
                "phrases. Your job is only to report the action.\n"
            prompt += "Do not call out turn numbers if you don't have them.\n"
            prompt += "Do not add subjective descriptors like 'impressive' " \
                "or 'amazing' unless specifically mentioned in the input. " \
                "Stick to factual reporting of events.\n"
        elif role == "color":
            prompt += "You are the color commentator.\n"
            prompt += "Stick to providing insight or context that enhances " \
                "the viewer's understanding.\n"
            prompt += "Do not provide play-by-play commentary.\n"
            prompt += "Do not invent details.\n"
        
        # Build the prompt
        prompt += f"Tone: {tone}\n"
        prompt += f"Track: {ir_info['WeekendInfo']['TrackDisplayName']}\n"
        prompt += f"City: {ir_info['WeekendInfo']['TrackCity']}\n"
        prompt += f"Country: {ir_info['WeekendInfo']['TrackCountry']}\n"
        prompt += f"Additional Info: {other_info}\n"
        
        # Add the previous responses if there are any
        if len(self.previous_responses) > 0:
            prompt += "Previous Commentary (oldest to latest):\n"
            limit = int(self.settings["commentary"]["memory_limit"])
            for message in self.previous_responses:
                prompt += f"- {message}\n"

        prompt += f"Event: {event}\nAI:\n"
        
        # Call the API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=1024,
            temperature=0.6
        )
        
        # Extract the response
        answer = response.choices[0].text.strip()

        # Remove quotes the AI sometimes likes to add
        if answer[0] == "\"" and answer[-1] == "\"":
            answer = answer[1:-1]

        # Add the response to the list of previous responses
        self.previous_responses.append(answer)

        # If the list is too long, remove the oldest response
        if len(self.previous_responses) > limit:
            self.previous_responses.pop(0)
        
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

    def generate(self, text, timestamp, yelling=False, voice="Arnold"):
        """Generate and play audio for the provided text.

        Calls the ElevenLabs API to create audio from the text using the
        specified voice, then streams the audio.

        Args:
            text (str): The text to be converted to audio.
            voice (str, optional): The voice to use for text-to-speech. Defaults
                to "Harry".
        """
        # Convert to yelling for voice commentary if requested
        if yelling:
            text = text.upper()
            if text[-1] == ".":
                text = text[:-1] + "!!!"

        # Generate and play audio
        audio = elevenlabs.generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )

        # Get the iRacing videos folder
        path = os.path.join(self.settings["general"]["iracing_path"], "videos")

        # Create the file name
        file_name = f"commentary_{timestamp}.wav"

        # Save the audio to a file
        elevenlabs.save(audio, os.path.join(path, file_name))