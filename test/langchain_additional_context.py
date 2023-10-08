from os import environ
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import keys

"""
I need to figure out how to incorporate memory back in, so the commentators
appear to be having a conversation and not forgetting what they've said.
"""

environ["OPENAI_API_KEY"] = keys.OPENAI_KEY

# Define your prompt template with the new variables
template = """Role: {commentator_type}
Tone: {guided_tone}
Race Context: {race_season_stats}
Time: Lap {current_lap}/{total_laps}
Human: {question}
AI:
"""

# Update your PromptTemplate to include these new input variables
prompt_template = PromptTemplate(
    input_variables=["commentator_type", "guided_tone", "race_season_stats", "current_lap", "total_laps", "question"],
    template=template
)

# Initialize your LLMChain as before
llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=prompt_template,
    verbose=False,
)

# Now, when you run the chain, include those new variables as arguments
output = llm_chain.run(
    commentator_type="Play-by-Play",
    guided_tone="Factual and straightforward",
    race_season_stats="Roberston leads the championship by 10 points.",
    current_lap=25,
    total_laps=50,
    question="Roberston has overtaken Johnson for P6"
)

print(output)
