import openai
import keys


openai.api_key = keys.OPENAI_KEY

prompt = "The quick brown fox"
response = openai.Completion.create(
  engine="gpt-3.5-turbo-instruct",
  prompt=prompt,
  max_tokens=50
)

generated_text = response.choices[0].text.strip()
print(generated_text)
