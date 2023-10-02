import openai
import keys

openai.api_key = keys.OPENAI_KEY

# Set up the default message and get a rolling list of messages going
messages = [
    {
      "role": "system",
      "content": "You will be provided with information about the state of a race, and you will provide commentary on the event. Be sure to use previous events as context. Keep your response limited to 1 sentence."
    }
]

def chat(message):
    global messages

    messages.append(
        {
        "role": "user",
        "content": message
        }
    )

    response = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    output = response["choices"][0]["message"]["content"].replace(".", "!!!").upper()

    return output

print(chat("The number 14 car pass the number 2 car on the inside, making his way up to the front of the pack."))
print(chat("The number 2 car is now in the lead."))
print(chat("The number 14 car is now in the lead."))