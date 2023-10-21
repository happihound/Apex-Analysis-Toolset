document.addEventListener('DOMContentLoaded', function() {
    console.log('Document is loaded');

    var socketUrl = window.location.protocol + '//' + document.domain + ':' + location.port;
    console.log('Connecting to WebSocket at:', socketUrl);
    var socket = io.connect(socketUrl);

    socket.on('connect', function() {
        console.log('WebSocket connected!');
    });

    socket.on('console_output', function(message) {
        console.log('Console Output received:', message.data);
        var consoleElement = document.getElementById('console-output');
        consoleElement.textContent = message.data.join('\n');
    });

    
    var coll = document.getElementsByClassName("collapsible-console");
    console.log('Number of collapsible-console elements:', coll.length);
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            console.log('Collapsible button clicked (console.js)');
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
});