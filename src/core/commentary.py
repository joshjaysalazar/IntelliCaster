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
    
    def generate_commentary(self, event, role, tone, limit):        
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
        
        # Add the previous responses (limit to 5) if there are any
        if len(self.previous_responses) > 5:
            for e, a in self.previous_responses[-5:]:
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