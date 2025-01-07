navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    console.log({ stream })
    if (!MediaRecorder.isTypeSupported('audio/webm'))
        return alert('Browser not supported')
    const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
    })
    const socket = new WebSocket('wss://api.deepgram.com/v1/listen', [
        'token',
        '3267961fc4555bd0e1e9b7536d3e333c8aade93d',
    ])
    socket.onopen = () => {
        document.querySelector('#status').textContent = 'Connected'
        console.log({ event: 'onopen' })
        mediaRecorder.addEventListener('dataavailable', async (event) => {
            if (event.data.size > 0 && socket.readyState == 1) {
                socket.send(event.data)
            }
        })
        mediaRecorder.start(1000)
    }

    socket.onmessage = (message) => {
        const received = JSON.parse(message.data)
        const transcript = received.channel.alternatives[0].transcript
        if (transcript && received.is_final) {
            console.log(transcript)
            document.querySelector('#transcript').textContent +=
            transcript + ' '

            // Send transcript data to Flask backend
            fetch('http://localhost:5000/transcript', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transcript: transcript })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Data sent to Flask:', data)
            })
            .catch(error => {
                console.error('Error sending data to Flask:', error)
            })
        }
    }

    socket.onclose = () => {
      console.log({ event: 'onclose' })
    }

    socket.onerror = (error) => {
      console.log({ event: 'onerror', error })
    }
})
