document.addEventListener('DOMContentLoaded', function() {
  const clientID = 'kill-tracker' // Set this to match the client ID used in your Python server code
  const statusElement = document.getElementById('status');
  const imageElement = document.getElementById('kill-image');

  console.log(clientID);
    var socketUrl = window.location.protocol + '//' + document.domain + ':' + location.port+'/image';
    var socket = io('http://localhost:5000/image', {
    transports: ['websocket'],
    query: { client_id: clientID },
  });
    console.log(socket)


    // var socket = io.connect(socketUrl);
    console.log('Connecting to WebSocket at:', socketUrl);

    socket.on('connect', function() {
        console.log('WebSocket connected!');
    });

  socket.on('image', (data) => {
      console.log('Image received');
      imageElement.src = 'data:image/jpeg;base64,' + data.image;
      statusElement.textContent = 'Connected (Image Received)';
    
  });

// document.addEventListener('DOMContentLoaded', () => {
//   const clientID = 'kill-tracker'; // Set this to match the client ID used in your Python server code
//   const statusElement = document.getElementById('status');
//   const imageElement = document.getElementById('kill-Image');

//   const socket = io('http://localhost:5000/image', {
//     transports: ['websocket'],
//     query: { client_id: clientID },
//   });

//   socket.on('connect', () => {
//     console.log('Connected to server');
//     statusElement.textContent = 'Connected';
//   });

//   socket.on('disconnect', () => {
//     console.log('Disconnected from server');
//     statusElement.textContent = 'Disconnected';
//   });

//   socket.on('image', (data) => {
//     if (data.client_id === clientID) {
//       console.log('Image received');
//       imageElement.src = 'data:image/jpeg;base64,' + data.image;
//       statusElement.textContent = 'Connected (Image Received)';
//     }
//   });

});
document.getElementById('cancelButton').addEventListener('click', function() {
    fetch('/cancel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error cancelling operation:', error));
});

document.getElementById('submitButton').addEventListener('click', function() {
    fetch('/kill-tracker', {
        method: 'POST',
    })
});
