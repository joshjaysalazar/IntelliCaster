import openai
import elevenlabs


class TextGenerator:
    def __init__(self, settings):
        # Member variables
        self.settings = settings

        # Set the API key
        openai.api_key = self.settings["keys"]["openai_api_key"]

        # Create an empty list to hold previous responses
        self.previous_responses = []
    
    def generate_commentary(self, event, role, tone, limit, info):        
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
        # Member variables
        self.settings = settings

        # Set the API key
        elevenlabs.set_api_key(self.settings["keys"]["elevenlabs_api_key"])