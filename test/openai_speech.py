import openai
import keys
import os


os.environ["OPENAI_API_KEY"] = keys.OPENAI_KEY

client = openai.OpenAI()

path = "test.mp3"

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="alloy",
    input="SMITH PASSES JOHNSON FOR P4!!!"
)

response.stream_to_file(path)