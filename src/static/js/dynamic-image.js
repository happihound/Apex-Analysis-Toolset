document.addEventListener('DOMContentLoaded', function () {
    const clientID = document.getElementById('client-id').textContent;
    const statusElement = document.getElementById('status');
    const imageElement = document.getElementById('dynamicImage');


    console.log(clientID);
    var socketUrl = window.location.protocol + '//' + document.domain + ':' + location.port + '/image';
    var socket = io('http://localhost:5000/image', {
        transports: ['websocket'],
        query: { client_id: clientID },
    });
    console.log(socket)

    socket.on('connect', function () {
        console.log('WebSocket connected!');
        statusElement.textContent = 'Connected';
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        statusElement.textContent = 'Disconnected';
    });

    socket.on('image', (data) => {
        if (data.client_id === clientID) {
            console.log('Image received');
            imageElement.src = 'data:image/jpeg;base64,' + data.image;
            imageElement.alt = data.altText;
            statusElement.textContent = 'Connected (Image Received)';
        }
    });
});