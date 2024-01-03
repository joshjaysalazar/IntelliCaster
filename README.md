# IntelliCaster

IntelliCaster is an AI-powered tool for generating voice commentary on iRacing race replays. Leveraging OpenAI for text generation and ElevenLabs for voice synthesis, it adds dynamic and immersive commentary to your replays. Currently in early prerelease, IntelliCaster is under active development. Users should note that while the current version uses OpenAI and ElevenLabs, this may change as new technologies emerge and the project evolves. Early adopters should expect some instability and are encouraged to contribute feedback.

## Example

To give you a better idea of what IntelliCaster is capable of, check out this example video. It showcases the AI-generated commentary in a typical iRacing replay, demonstrating both the quality of the commentary and the integration with race footage. This also shows that IntelliCaster is very much in an early prerelease state, as the commentary is not always accurate and the video rendering is not yet optimized. As the project matures, these issues will be addressed.

[![IntelliCaster Example Video](https://img.youtube.com/vi/Gokr_ocneCw/0.jpg)](https://www.youtube.com/watch?v=Gokr_ocneCw)

## Installation

To get started with IntelliCaster in its current prerelease state, follow these steps:

1. Ensure you have Python 3.12 installed on your system.
2. Clone the IntelliCaster repository from GitHub.
3. Navigate to the cloned directory and install the required libraries using `pip install -r requirements.txt`.
4. Run `main.py` located in the src directory to start the application.

## Usage

Using IntelliCaster is straightforward:

1. Open the IntelliCaster application.
2. Go to the Settings tab and enter your OpenAI and ElevenLabs API keys. Adjust any other settings as needed. A restart of the software may be required after changing settings.
3. Launch an iRacing replay and jump to a race lap.
4. Press the 'Start Commentary' button to initiate commentary. The replay will automatically rewind to the beginning of the race session.
5. Enjoy the AI-generated commentary as the race unfolds.
6. To stop the commentary, simply press the 'Stop Commentary' button. IntelliCaster will then render a video file with the commentary.

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
