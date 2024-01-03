# IntelliCaster

IntelliCaster is an AI-powered tool for generating voice commentary on iRacing race replays. Leveraging OpenAI for text generation and ElevenLabs for voice synthesis, it adds dynamic and immersive commentary to your replays. Currently in early prerelease, IntelliCaster is under active development. Users should note that while the current version uses OpenAI and ElevenLabs, this may change as new technologies emerge and the project evolves. Early adopters should expect some instability and are encouraged to contribute feedback.

## Example Video

To give you a better idea of what IntelliCaster is capable of, check out this example video. It showcases the AI-generated commentary in a typical iRacing replay, demonstrating both the quality of the commentary and the integration with race footage. This also shows that IntelliCaster is very much in an early prerelease state, as the commentary is not always accurate and the video rendering is not yet optimized. As the project matures, these issues will be addressed.

[![IntelliCaster Example Video](https://img.youtube.com/vi/Gokr_ocneCw/0.jpg)](https://www.youtube.com/watch?v=Gokr_ocneCw)

## Requirements

Before you start with IntelliCaster, ensure that you meet the following requirements:

- A clean Python 3.12+ installation
- A stable internet connection for API communication
- A valid OpenAI API key
- A valid ElevenLabs API key
- Adjust iRacing graphics settings to allow for smooth video capture

## Installation

To get started with IntelliCaster in its current prerelease state, follow these steps:

1. Ensure all requirements are met.
2. Clone the IntelliCaster repository from GitHub:
    `git clone https://github.com/joshjaysalazar/IntelliCaster.git`
3. Navigate to the cloned directory:
    `cd IntelliCaster`
4. Install the required libraries:
    `pip install -r requirements.txt`
5. Run `main.py` in the src directory to start IntelliCaster:
    `python src/main.py`

## Usage

Using IntelliCaster is straightforward:

1. Open IntelliCaster. The application interface should appear.
2. In the Settings tab, enter your OpenAI and ElevenLabs API keys.
3. Adjust any other necessary settings. Note that a restart of the software might be required after modifying settings.
4. To generate commentary, open an iRacing replay and navigate to any race lap.
5. Press the "Start Commentary" button. IntelliCaster will rewind the replay to the beginning of the session and start generating commentary.
6. Once you're done, press the "Stop Commentary" button. IntelliCaster will then render the video file with the added commentary.

## API Usage and Costs

### OpenAI and ElevenLabs API Costs

IntelliCaster integrates the OpenAI and ElevenLabs APIs for text and voice commentary generation. These services have a usage-based pricing model, meaning costs may be incurred based on the amount of commentary generated through IntelliCaster.

### Disclaimer

Neither I, as the developer, nor any contributors to the IntelliCaster project are responsible for any charges that users may incur while using these APIs. Users are solely responsible for understanding and managing their usage according to the pricing policies of OpenAI and ElevenLabs. It is advised to refer to their respective websites for detailed information on pricing and usage limits.

Users should monitor their API usage to avoid unexpected charges and consider setting usage limits if available.

## Contributing

Contributions are not only welcome but highly encouraged! Whether you're fixing bugs, proposing new features, or improving the documentation, your help is invaluable. Here's how you can contribute:

1. Fork the IntelliCaster repository.
2. Make your changes in a dedicated branch.
3. Submit a pull request with a clear description of your changes.
4. For any bugs or feature requests, please open an issue in the GitHub repository.

Your contributions will play a significant role in shaping the future of IntelliCaster.

## License

IntelliCaster is released under the GPL-3.0 license. For more details, see the [LICENSE](LICENSE) file in the repository.

## Issues

Encountered a bug? Have a feature request or a question? Feel free to open an issue in the IntelliCaster repository. Your input helps us make IntelliCaster better for everyone.
