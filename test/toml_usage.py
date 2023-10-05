import tomllib

with open("test/test.toml", "rb") as f:
    data = tomllib.load(f)

print(data)