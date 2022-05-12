// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');
let webRTCConnection;
let token = "";


// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendMessage();
    }
});

// Read the comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
function sendMessage() {
    const chatBox = document.getElementById("chat-comment");
    const comment = chatBox.value;

    const image_file = document.getElementById("form-file");
    const file = image_file.value;

    chatBox.value = "";


    chatBox.focus();
    if (comment !== "" && !file.includes(".jpg")) {
        // TODO: Handle images and text from user uploads
        console.log('Sending a Normal Message');
        console.log(comment)
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': comment}));
    } else if (comment === "" && file.includes(".jpg")) {
        console.log('Sending Image only');
        console.log(file);
        socket.send(JSON.stringify({ 'messageType': 'imageMessage', 'comment': comment }));
    } else {
        console.log('Sending text and image in message');
        console.log(comment)
        console.log(file);
        socket.send(JSON.stringify({ 'messageType': 'chatImageMessage', 'comment': comment }));
    }
}

// Renders a new chat message to the page
function addMessage(chatMessage) {
    console.log('The Chat Message to be added is below');
    console.log(chatMessage);
    let chat = document.getElementById('chat');
    chat.innerHTML += "<b>" + chatMessage["username"] + "</b>: " + chatMessage["comment"] + "<br/>";
}

// Render online users in html
function addUser(user) {
    console.log('Adding a new user to html');
    console.log(user);
    let box = document.getElementById('onlineUsers');

    box.innerHTML += "<b>" + user + "</b>: </br>";
}

function get_online_users() {
    console.log('Getting Online Users');
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log('The below response is about to be parsed')
            console.log(this.response)
            const users = JSON.parse(this.response);
            for (const user of users) {
                console.log(user);
                addUser(user);
            }
        }
    };
    request.open("GET", "/online-users");
    request.send();
}


// called when the page loads to get the chat_history
function get_chat_history() {
    console.log('Getting Chat history');
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log('The below USER response is about to be parsed')
            console.log(this.response)
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                console.log(message); // -> So I can see the message that will be added
                addMessage(message);
            }
        }
    };
    request.open("GET", "/chat-history");
    request.send();
}

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType
    console.log('Got message: ' + message)

    switch (messageType) {
        case 'chatMessage':
            addMessage(message);
            break;
        case 'webRTC-offer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
            webRTCConnection.createAnswer().then(answer => {
                webRTCConnection.setLocalDescription(answer);
                socket.send(JSON.stringify({"messageType": "webRTC-answer", "answer": answer}));
            });
            break;
        case 'webRTC-answer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
            break;
        case 'webRTC-candidate':
            webRTCConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            break;
        default:
            console.log("received an invalid WS messageType");
    }
}

socket.onclose = function (event) {
    console.log("Websocket connection closed")
    const request = new XMLHttpRequest();
    request.open("GET", "/close_websocket");
    request.send();
};

function startVideo() {
    const constraints = {video: true, audio: true};
    navigator.mediaDevices.getUserMedia(constraints).then((myStream) => {
        const elem = document.getElementById("myVideo");
        elem.srcObject = myStream;

        // Use Google's public STUN server
        const iceConfig = {
            'iceServers': [{'url': 'stun:stun2.1.google.com:19302'}]
        };

        // create a WebRTC connection object
        webRTCConnection = new RTCPeerConnection(iceConfig);

        // add your local stream to the connection
        webRTCConnection.addStream(myStream);

        // when a remote stream is added, display it on the page
        webRTCConnection.onaddstream = function (data) {
            const remoteVideo = document.getElementById('otherVideo');
            remoteVideo.srcObject = data.stream;
        };

        // called when an ice candidate needs to be sent to the peer
        webRTCConnection.onicecandidate = function (data) {
            console.log(data);
            console.log('Sending ice candidate')
            socket.send(JSON.stringify({'messageType': 'webRTC-candidate', 'candidate': data.candidate}));
        };
    })
}


function connectWebRTC() {
    // create and send an offer
    webRTCConnection.createOffer().then(webRTCOffer => {
        console.log('Creating Candidate Offer to Send')
        socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer}));
        webRTCConnection.setLocalDescription(webRTCOffer);
    });

}


function welcome() {
    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀"
    get_chat_history();
    get_online_users();
    // const tokenLoad = document.getElementById("xsrf_token");
    // token = tokenLoad.value;
    // console.log(token);
}


function redirect() {
    let xmlHttpReq = new XMLHttpRequest();
    xmlHttpReq.open("GET", '/login', false);
    xmlHttpReq.send(null);
    return xmlHttpReq.responseText;
}

// console.log(httpGet('https://jsonplaceholder.typicode.com/posts'));