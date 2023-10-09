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
    
    def generate_commentary(self, question, role, tone):
        # Role must be either "play-by-play" or "color commentary"
        if role not in ["play-by-play", "color commentary"]:
            raise ValueError(
                "Role must be either \"play-by-play\" or \"color commentary\""
            )
        
        # Create an empty prompt
        prompt = ""

        # Add behavioral instructions
        prompt += "You are providing commentary to a race.\n"
        prompt += "You'll use previous events as context.\n"
        prompt += "You'll use drivers' last names.\n"
        if role == "play-by-play":
            prompt += "You'll keep your response limited to 10 words.\n"
        else:
            prompt += "You'll keep your response limited to 20 words.\n"
        
        # Build the prompt
        prompt += f"Role: {role}\n"
        prompt += f"Tone: {tone}\n"
        
        # Add the previous responses (limit to 5)
        for q, a in self.previous_responses[-5:]:
            prompt += f"Human: {q}\nAI: {a}\n"

        prompt += f"Human: {question}\nAI:\n"
        
        # Call the API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=256
        )
        
        answer = response["choices"][0]["message"]["content"]
        self.previous_responses.append((question, answer))
        
        return answer

class VoiceGenerator:
    def __init__(self, settings):
        # Member variables
        self.settings = settings

        # Set the API key
        elevenlabs.set_api_key(self.settings["keys"]["elevenlabs_api_key"])