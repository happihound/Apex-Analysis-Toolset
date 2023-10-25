const clientID = document.getElementById('client-id').textContent; 

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

