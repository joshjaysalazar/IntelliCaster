from elevenlabs import generate, save, voices
from elevenlabs import set_api_key
import keys


set_api_key(keys.ELEVENLABS_KEY)

# voices = voices()
# for voice in voices:
#     print(voice)
#     print()

audio = generate(
  text="Hello! My name is Bella!",
  voice="Bella",
  model="eleven_monolingual_v1"
)

save(audio, "test.wav")

audio = generate(
  text="AND ROBERTSON MAKES A PASS ON THE INSIDE, MAKING HIS WAY UP TO THE FRONT OF THE PACK!!!",
  voice="Harry",
  model="eleven_monolingual_v1"
)

save(audio, "test2.wav")