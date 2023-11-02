import elevenlabs


elevenlabs.set_api_key("40a4eb61a0a0b2431ce56fdf1a06b93f")

user = elevenlabs.api.User.from_api()
print(user)