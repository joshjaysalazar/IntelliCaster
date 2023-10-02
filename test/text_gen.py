import time
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Time the initialization
start_time = time.time()
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
elapsed_time = time.time() - start_time
print(f"Initialization Time: {elapsed_time:.4f} seconds")

# Time encoding the input text
start_time = time.time()
text = "Please say hello to me."
encoded_input = tokenizer(text, return_tensors='pt')
input_ids = encoded_input['input_ids']
elapsed_time = time.time() - start_time
print(f"Encoding Time: {elapsed_time:.4f} seconds")

# Time generating the text
start_time = time.time()
with torch.no_grad():
    output = model.generate(input_ids, max_length=50)
elapsed_time = time.time() - start_time
print(f"Text Generation Time: {elapsed_time:.4f} seconds")

# Time decoding the text
start_time = time.time()
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
elapsed_time = time.time() - start_time
print(f"Decoding Time: {elapsed_time:.4f} seconds")

# Output the generated text
print(generated_text)
