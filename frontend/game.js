let socket = new WebSocket('ws://' + window.location.host + '/connect_socket');
let username = '';

socket.onmessage = function (ws_message){
    console.log('Got a message in game.js');
};

function welcome() {
    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀";
}