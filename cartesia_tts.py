from cartesia import Cartesia
import pyaudio

# Set up Cartesia TTS API
client = Cartesia(api_key="sk_car_R7nWUD5h9uFZz3dJkc7C6")
voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091"
voice = client.voices.get(id=voice_id)

# Audio format settings
output_format = {
    "container": "raw",
    "encoding": "pcm_f32le",
    "sample_rate": 22050,
}
rate = 22050
p = pyaudio.PyAudio()

def get_default_output_device():
    """
    Get the default output device or fallback to system's default.
    """
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxOutputChannels"] > 0 and "Default" in device_info["name"]:
            return i
    # Fallback to first output device
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxOutputChannels"] > 0:
            return i
    raise RuntimeError("No output device found.")

# Automatically select the default output device
output_device_index = get_default_output_device()

def speak(transcript):
    """
    Generate speech for the given transcript and play it.
    """
    stream = None
    ws = client.tts.websocket()
    try:
        for output in ws.send(
                model_id="sonic-english",
                transcript=transcript,
                voice_embedding=voice["embedding"],
                stream=True,
                output_format=output_format,
        ):
            buffer = output["audio"]

            if not stream:
                stream = p.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=rate,
                    output=True,
                    output_device_index=output_device_index
                )

            stream.write(buffer)
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        ws.close()