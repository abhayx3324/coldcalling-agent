document.addEventListener('DOMContentLoaded', () => {
    let mediaRecorder;
    let socket;
    let isTranscribing = false;
    let audioStream;
    let DEEPGRAM_API_KEY;

    fetch('/get-deepgram-key')
        .then(response => response.json())
        .then(data => {
            if (data.deepgram_api_key) {
                DEEPGRAM_API_KEY = data.deepgram_api_key; // Store the API key
                console.log('Deepgram API key loaded successfully');
            } else {
                console.error('Failed to load Deepgram API key:', data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching Deepgram API key:', error);
        });

    document.getElementById('startButton').addEventListener('click', () => {
        document.querySelector('#status').textContent = 'Connecting...';
        document.querySelector('#status').classList.remove('text-red-500');
        document.querySelector('#status').classList.add('text-yellow-500');
        const startButton = document.getElementById('startButton');
        
        if (!isTranscribing) {
            // Start transcription
            fetch('/start')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('transcript').textContent = data.message;

                    document.getElementById('transcript').textContent = data.response;
                    document.getElementById('transcript').classList.remove('text-gray-500');
                    document.getElementById('transcript').classList.add('text-gray-200');
                    speakText("Hello! My name is Pooja. May I have your first and last name, please?")
                    
                    document.querySelector('#status').textContent = 'Connected';
                    document.querySelector('#status').classList.remove('text-yellow-500');
                    document.querySelector('#status').classList.add('text-green-500');

                    navigator.mediaDevices.getUserMedia({
                        audio: {
                            deviceId: 'default',
                            echoCancellation: true,
                            noiseSuppression: true,
                        }
                    }).then((stream) => {
                        audioStream = stream;

                        if (!MediaRecorder.isTypeSupported('audio/webm'))
                            return alert('Browser not supported');

                        mediaRecorder = new MediaRecorder(stream, {
                            mimeType: 'audio/webm',
                        });

                        const accessToken = DEEPGRAM_API_KEY; // Replace with your actual Deepgram API key
                        const model = 'nova-2';
                        const punctuate = true;
                        const language = 'en-US';
                        const encoding = 'linear16';
                        const channels = 1;
                        const sampleRate = 16000;
                        const endpointing = 400;

                        const url = new URL('wss://api.deepgram.com/v1/listen');
                        url.searchParams.append('model', model);
                        url.searchParams.append('punctuate', punctuate.toString());
                        url.searchParams.append('endpointing', endpointing.toString());
                        url.searchParams.append('language', language);
                        url.searchParams.append('encoding', encoding);
                        url.searchParams.append('channels', channels.toString());

                        socket = new WebSocket(url.toString(), [
                            'token',
                            accessToken,
                        ]);

                        socket.onopen = () => {
                            mediaRecorder.addEventListener('dataavailable', (event) => {
                                if (event.data.size > 0 && socket.readyState === 1) {
                                    socket.send(event.data);
                                }
                            });
                            mediaRecorder.start(1000);
                        };

                        socket.onmessage = (message) => {
                            const received = JSON.parse(message.data);
                            const transcript = received.channel.alternatives[0].transcript;
                            console.log(transcript);
                            if (transcript && received.is_final) {
                                if (audioPlayer) {
                                    audioPlayer.pause();
                                }

                                fetch('/transcript', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({ transcript: transcript })
                                })
                                
                                .then(response => response.json())
                                .then(data => {
                                    if (data.status === 'success') {

                                        document.getElementById('transcript').textContent = `AI: ${data.response}`;

                                        console.log(data.response)
                                        
                                        speakText(data.response);
                                    }
                                })
                                .catch(error => {
                                    console.error('Error sending transcript to Flask:', error);
                                });
                            }
                        };

                        socket.onclose = () => {
                            console.log('WebSocket closed');
                        };

                        socket.onerror = (error) => {
                            console.error('WebSocket error:', error);
                        };
                    });

                    startButton.textContent = 'Stop Call';
                    startButton.classList.remove('bg-blue-500', 'hover:bg-blue-700', 'shadow-blue-700/50');
                    startButton.classList.add('bg-red-500', 'hover:bg-red-700', 'shadow-red-700/50');
                    isTranscribing = true;
                })
                .catch(error => {
                    console.error('Error starting transcription:', error);
                });
        } else {
            const audioPlayer = document.getElementById('audioPlayer');
            if (audioPlayer) {
                audioPlayer.pause();
            }

            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
            if (socket && socket.readyState === 1) {
                socket.close();
            }

            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
            }

            document.getElementById('transcript').textContent = "AI response goes here"
            document.getElementById('transcript').classList.remove('text-gray-200');
            document.getElementById('transcript').classList.add('text-gray-500');

            startButton.textContent = 'Start Call';
            startButton.classList.remove('bg-red-500', 'hover:bg-red-700', 'shadow-red-700/50');
            startButton.classList.add('bg-blue-500', 'hover:bg-blue-700', 'shadow-blue-700/50');
            document.querySelector('#status').textContent = 'Not Connected';
            document.querySelector('#status').classList.remove('text-green-500', 'text-yellow-500');
            document.querySelector('#status').classList.add('text-red-500');
            isTranscribing = false;
        }
    });

    function speakText(text) {
        const accessToken = DEEPGRAM_API_KEY;
        const ttsUrl = 'https://api.deepgram.com/v1/speak?model=aura-luna-en';

        fetch(ttsUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        })
        .then(response => response.blob())
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob);
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.src = audioUrl;

            // Play the TTS audio
            audioPlayer.play();

        })
        .catch(error => {
            console.error('Error with Deepgram TTS:', error);
        });
    }
});