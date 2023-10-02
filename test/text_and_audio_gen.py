import openai
import elevenlabs
import keys


openai.api_key = keys.OPENAI_KEY
elevenlabs.set_api_key(keys.ELEVENLABS_KEY)

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You will be provided with information about the state of a race, and you will provide commentary on the event. Keep your response limited to 2 sentences."
    },
    {
      "role": "user",
      "content": "The number 14 car, Robertson, passed the number 2 car, Alexi, on the inside, making his way up to the front of the pack."
    }
  ],
  temperature=0,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

output = response["choices"][0]["message"]["content"]
output = output.replace(".", "!!!")
output = output.upper()

print(output)
print()

audio = elevenlabs.generate(
  text=output,
  voice="Harry",
  model="eleven_monolingual_v1"
)

elevenlabs.save(audio, "combined_test.wav")
print("File saved as combined_test.wav")