from configparser import ConfigParser
import json
import os


def create_context_file(file_name):
    """
    Creates a context JSON file with default values if it doesn't exist.
    
    Args:
        file_name (str): The name of the JSON file to create.
    """
    if not os.path.exists(file_name):
        # Create the context dictionary
        context = {
            "league": {
                "name": "My Awesome League",
                "short_name": "MAL"
            }
        }

        # Write to file
        with open(file_name, "w") as context_file:
            json.dump(context, context_file, indent=4)

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

        # Set up iRacing section
        config.add_section("iracing")
        config.set(
            "iracing", "iracing_path", "path/to/your/iRacing/folder"
        )
        config.set("iracing", "video_format", "mp4")
        config.set("iracing", "video_framerate", "60")
        config.set("iracing", "video_resolution", "1920x1080")

        # Set up director section
        config.add_section("director")
        config.set("director", "update_frequency", "1")

        # Set up commentary section
        config.add_section("commentary")
        config.set("commentary", "pbp_voice", "Harry")
        config.set("commentary", "color_voice", "Elli")
        config.set("commentary", "color_chance", "0.5")
        config.set("commentary", "memory_limit", "10")

        # Set up system section
        config.add_section("system")
        config.set("system", "context_file", "context.json")

        # Write to file
        with open(file_name, "w") as config_file:
            config.write(config_file)
