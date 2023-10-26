document.addEventListener('DOMContentLoaded', function () {

    var submit_endpoint = document.getElementById('submit-endpoint').textContent;
    console.log('Submit endpoint:', submit_endpoint);
    var clientID = document.getElementById('client-id').textContent;
    document.getElementById('submitButton').addEventListener('click', function () {
        console.log('Submit Button Clicked in submit-button.js on client ID:', clientID);
        fetch(submit_endpoint, {
            method: 'POST',
        }
        ).then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error submitting operation:', error));
    });

});