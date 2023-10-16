import os
from configparser import ConfigParser


def create_settings_file(file_name):
    """
    Create a settings INI file with specified sections and keys if it doesn't
    exist.

    Args:
        file_name (str): The name of the INI file to create.
    """
    if not os.path.exists(file_name):
        # Initialize ConfigParser
        config = ConfigParser()

        # Set up keys section
        config.add_section("keys")
        config.set("keys", "openai_api_key", "YOUR_API_KEY")
        config.set("keys", "elevenlabs_api_key", "YOUR_API_KEY")

        # Set up director section
        config.add_section("director")
        config.set("director", "update_frequency", "1")

        # Set up commentary section
        config.add_section("commentary")
        config.set("commentary", "memory_limit", "5")

        # Write to file
        with open(file_name, "w") as config_file:
            config.write(config_file)
