import asyncio
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
import signal
import sys

# Replace this with your actual Deepgram API key
DEEPGRAM_API_KEY = "3267961fc4555bd0e1e9b7536d3e333c8aade93d"

class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()

async def get_transcript():
    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY, config)

        # Change from asynclive to asyncwebsocket
        dg_connection = deepgram.listen.asyncwebsocket.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            print(result)
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                print(f"speaker: {full_sentence}")
                transcript_collector.reset()

        async def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=400
        )

        await dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # Start microphone
        microphone.start()

        # Create a function to handle graceful shutdown on interrupt
        def signal_handler(sig, frame):
            print("\nStopping transcription...")
            microphone.finish()
            asyncio.create_task(dg_connection.finish())  # Use asyncio.create_task to await in the signal handler
            sys.exit(0)

        # Set up the signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)

        while True:
            if not microphone.is_active():
                break
            await asyncio.sleep(1)

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

if __name__ == "__main__":
    asyncio.run(get_transcript())
