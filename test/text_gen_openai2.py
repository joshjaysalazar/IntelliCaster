import openai
import keys


openai.api_key = keys.OPENAI_KEY

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You will be provided with information about the state of a race, and you will provide commentary on the event."
    },
    {
      "role": "user",
      "content": "The number 14 car pass the number 2 car on the inside, making his way up to the front of the pack."
    }
  ],
  temperature=0,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

output = response["choices"][0]["message"]["content"].replace(".", "!!!").upper()

print(output)
# generated_text = response.choices[0].text.strip()
# print(generated_text)