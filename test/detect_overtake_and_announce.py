import irsdk
from os import environ
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import elevenlabs
import keys


# Set the API keys
environ["OPENAI_API_KEY"] = keys.OPENAI_KEY
elevenlabs.set_api_key(keys.ELEVENLABS_KEY)

# Set up the LLMChain
template = """You will be provided with information about the state of a race, and you will provide commentary on the event.
Be sure to use previous events as context, indicating how it affects other cars not mentioned where applicable.
Prefer drivers' last names, and drop any numbers from their name if they exist.
Keep your response limited to no more than 10 words.
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

# Set up the iRacing SDK
ir = irsdk.IRSDK()
ir.startup()

# Create a list of drivers
drivers = []

while True:
    # Store the previous state of the drivers
    prev_drivers = drivers.copy()

    # Clear the drivers list
    drivers = []

    # Update the drivers list
    if ir["CarIdxPosition"] != []: # If the race hasn't started, the list will be empty
        for i, pos in enumerate(ir["CarIdxPosition"]):
            if pos == 0: # If a car has a position of 0, it either doesn't exist or is the pace car
                continue
            if not ir["DriverInfo"]["Drivers"][i]["UserName"]: # If the driver disconnected, the next block throws an error
                continue
            drivers.append({
                "name": ir["DriverInfo"]["Drivers"][i]["UserName"],
                "position": pos,
                "gap_to_leader": ir["CarIdxF2Time"][i],
                "laps_completed": ir["CarIdxLapCompleted"][i],
                "track_position": ir["CarIdxLapDistPct"][i],
                "car_number": ir["DriverInfo"]["Drivers"][i]["CarNumber"],
                "in_pits": ir["CarIdxOnPitRoad"][i]
            })
    
    # Sort the list by laps completed + track position
    # NOTE: At the very start, this is only accurate once every car has crossed the line
    drivers.sort(key=lambda x: x["laps_completed"] + x["track_position"], reverse=True)

    # Update positions based on the sorted list
    for i, driver in enumerate(drivers):
        driver["position"] = i + 1

    # # Print out the driver list in position order
    # for driver in drivers:
    #     print(driver["position"], driver["track_position"] + driver["laps_completed"], driver["name"], driver["car_number"])

    # Detect overtakes
    for i, driver in enumerate(drivers):
        # Get this driver's previous position by searching for their name in the previous driver list
        prev_driver = next((item for item in prev_drivers if item["name"] == driver["name"]), None)

        # If a driver's position has decreased, they have overtaken someone
        if prev_driver and driver["position"] < prev_driver["position"]:
            # Find the driver whose position is one higher than this driver's
            overtaken_driver = next((item for item in drivers if item["position"] == driver["position"] + 1), None)

            # If either car was in the pits, don't announce the overtake
            # NOTE: This does not account for position changes between two cars on track that happen due to a third car pitting
            if driver["in_pits"] or overtaken_driver["in_pits"]:
                print(f"{driver['name']} has overtaken {overtaken_driver['name']} for P{driver['position']} (in pit)")
                continue

            # Announce the overtake
            output = llm_chain.run(f"{driver['name']} has overtaken {overtaken_driver['name']} for P{driver['position']}")
            output = output.replace(".", "!")
            output = output.upper()
            print(output)

            # Move the camera to focus on the overtaking driver
            ir.cam_switch_num(driver["car_number"], 11)

            # Generate and play audio
            audio = elevenlabs.generate(
                text=output,
                voice="Harry",
                model="eleven_monolingual_v1",
                stream=True
            )

            elevenlabs.stream(audio)