import openai
import elevenlabs


class TextGenerator:
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
    
    def generate(self, event, role, tone, limit, info):
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
            info (str): Any additional information to be included.

        Returns:
            str: The generated commentary text.
        """
        # Create an empty prompt
        prompt = ""

        # Add behavioral instructions
        prompt += "You are providing commentary to a race.\n"
        prompt += "Use previous events as context.\n"
        prompt += "Prefer to use drivers' last names, rarely use full names.\n"
        prompt += f"Your responses MUST NOT exceed {limit} words.\n"
        
        # Build the prompt
        prompt += f"Role: {role}\n"
        prompt += f"Tone: {tone}\n"
        prompt += f"Additional Info: {info}\n"
        
        # Add the previous responses (limited by settings) if there are any
        limit = int(self.settings["commentary"]["memory_limit"])
        if len(self.previous_responses) > limit:
            for e, a in self.previous_responses[-limit:]:
                prompt += f"Human: {e}\nAI: {a}\n"
        elif len(self.previous_responses) > 0:
            for e, a in self.previous_responses:
                prompt += f"Human: {e}\nAI: {a}\n"

        prompt += f"Human: {event}\nAI:\n"
        
        # Call the API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=256
        )
        
        answer = response.choices[0].text.strip()
        self.previous_responses.append((event, answer))
        
        return answer

class VoiceGenerator:
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

    def generate(self, text, voice="Harry"):
        """Generate and play audio for the provided text.

        Calls the Eleven Labs API to create audio from the text using the
        specified voice, then streams the audio.

        Args:
            text (str): The text to be converted to audio.
            voice (str, optional): The voice to use for text-to-speech.
                Defaults to "Harry".
        """
        # Generate and play audio
        audio = elevenlabs.generate(
            text=text,
            voice=voice,
            model="eleven_monolingual_v1",
            stream=True
        )

        elevenlabs.stream(audio)