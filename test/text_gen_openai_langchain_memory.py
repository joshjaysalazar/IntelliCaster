from os import environ
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import keys

environ["OPENAI_API_KEY"] = keys.OPENAI_KEY

template = """You will be provided with information about the state of a race, and you will provide commentary on the event.
Be sure to use previous events as context, indicating how it affects other cars not mentioned where applicable.
Keep your response limited to 1 sentence.
{chat_history}
Human: {question}
AI:
"""
prompt_template = PromptTemplate(
    input_variables=["chat_history", "question"],
    template=template
)
memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=prompt_template,
    verbose=False,
    memory=memory,
)

output = llm_chain.run("The number 14 car pass the number 2 car on the inside, making his way up to the front of the pack.")
print(output)
print()

output = llm_chain.run("The number 2 car is now in the lead.")
print(output)
print()

output = llm_chain.run("The gap between the number 2 car and the number 14 car is 3.2 seconds.")
print(output)
print()

output = llm_chain.run("The number 6 car is now 2.4 seconds behind the number 14 car.")
print(output)
print()

output = llm_chain.run("There are 3 laps remaining.")
print(output)
print()

output = llm_chain.run("The number 2 car has gone off in turn 3.")
print(output)
print()

output = llm_chain.run("There's contact between the number 14 car and the number 6 car.")
print(output)