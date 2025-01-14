# CALL-E: AI Voice Agent

CALL-E is an advanced AI voice agent designed to facilitate interactive, conversational, and persuasive product sales. It integrates state-of-the-art technologies for speech-to-text (STT), text-to-speech (TTS), and natural language processing (NLP) to provide a seamless conversational experience.

---

## Features

1. **Dynamic Web Scraping:**

   - Accepts product name, company name, and a brief product description from the user.
   - Performs web scraping using OpenAI GPT Turbo 3.5 to gather relevant information about the product online.

2. **Conversational Selling:**

   - Engages users in a conversation on a web platform.
   - Uses a carefully crafted prompt and web-scraped data to simulate a real-time sales experience.

3. **High-Quality Speech Processing:**

   - Converts spoken user input into text using Deepgram’s STT capabilities.
   - Generates natural, expressive responses with OpenAI GPT Turbo 3.5.
   - Delivers responses via Deepgram’s TTS system for an engaging auditory experience.

4. **Adaptive Interrupt Handling:**

   - Can handle interruptions during the conversation and adapt accordingly to ensure a smooth and natural user experience.

---

## Try It Out
Visit the live website to test CALL-E in action:
[Live Demo](google.com)

## How It Works

1. **User Input:**

   - The user provides the product name, company name, and a brief description of the product.

2. **Web Scraping:**

   - CALL-E uses OpenAI GPT Turbo 3.5 to search the web and collect relevant product information.

3. **Conversation:**

   - The user initiates a conversation on the website.
   - CALL-E, powered by the collected web data and a refined conversational prompt, engages in a real-time discussion aimed at persuading the user to purchase the product.

4. **Voice Interaction:**

   - User speech is converted to text with Deepgram STT.
   - Responses are crafted by OpenAI GPT Turbo 3.5 and delivered through Deepgram TTS for a smooth conversational flow.

---

## Tech Stack

- **STT:** [Deepgram](https://deepgram.com) for speech-to-text processing.
- **LLM:** [OpenAI GPT Turbo 3.5](https://openai.com) for natural language understanding and response generation.
- **TTS:** [Deepgram](https://deepgram.com) for text-to-speech synthesis.
- **Web Framework:** Flask for backend services.
- **Frontend:** Tailwind CSS for responsive and elegant user interfaces.
- **Programming Language:** Python 3.12.7 for backend logic and integration.

---

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/symelbak/coldcalling-agent
   cd coldcalling-agent
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys:

   - Add your Deepgram API key and OpenAI API key to the `.env` file:
     ```
     DEEPGRAM_API_KEY=your_deepgram_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

4. Run the Flask server:

   ```bash
   python app.py
   ```

5. Access the web interface:

   - Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Future Enhancements

- Multi-language support for global accessibility.
- Improved scraping algorithms for more accurate and reliable product information.
- Integration with e-commerce platforms for direct product purchases.
- Reduce latency for faster and more responsive interactions.
- AI-driven sentiment analysis to tailor responses based on user mood.

---