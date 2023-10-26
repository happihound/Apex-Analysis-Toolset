function createCollapsibleConsole() {
    // Create button element
    var button = document.createElement('button');
    button.classList.add('collapsible', 'collapsible-console');

    var icon = document.createElement('i');
    icon.classList.add('fas', 'fa-chevron-down', 'chevron-icon');
    button.appendChild(icon);

    // Create span element for text
    var span = document.createElement('span');
    span.textContent = 'Console Output';
    button.appendChild(span);

    // Create Font Awesome icon element

    // Create content div
    var contentDiv = document.createElement('div');
    contentDiv.classList.add('content');

    // Create pre element for console output
    var consoleOutput = document.createElement('pre');
    consoleOutput.id = 'console-output';

    // Append console output to content div
    contentDiv.appendChild(consoleOutput);

    // Append button and content div to body (or another parent element)
    var parentElement = document.getElementById('insert_console');
    parentElement.appendChild(button);
    parentElement.appendChild(contentDiv);
}
document.addEventListener('DOMContentLoaded', function () {
    console.log('Document is loaded');
    var client_id1 = document.getElementById('client-id').textContent;
    console.log('Client ID:', client_id1);
    var socketUrl = window.location.protocol + '//' + document.domain + ':' + location.port;
    console.log('Connecting to WebSocket at:', socketUrl);

    var socket = io('http://localhost:5000', {
        transports: ['websocket'],
        query: { client_id: client_id1 },
    });
    console.log(socket)
    socket.on('connect', function () {
        console.log('WebSocket connected!');
    });

    socket.on('console_output', function (message) {
        console.log('Console Output received:', message.data);
        var consoleElement = document.getElementById('console-output');
        consoleElement.textContent += message.data + '\n';
        //Cut the text if it goes over 12 lines
        var lines = consoleElement.textContent.split('\n');
        if (lines.length > 12) {
            consoleElement.textContent = lines.slice(lines.length - 12).join('\n');
        }
    });

    // Call function to create and inject the collapsible console HTML
    createCollapsibleConsole();

    // Collapsible button event listener setup
    var coll = document.getElementsByClassName("collapsible-console");
    console.log('Number of collapsible-console elements:', coll.length);
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
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
