// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');
let webRTCConnection;
let token = "";
let username = '';


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

    // const image_file = document.getElementById("form-file");
    // const file = image_file.value;

    chatBox.value = "";


    chatBox.focus();
    if (comment !== "") {
        // TODO: Handle images and text from user uploads
        console.log('Sending a Normal Message');
        console.log(comment)
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': comment}));
    }
}

// Renders a new chat message to the page
function addMessage(chatMessage) {
    console.log('The Chat Message to be added is below');
    console.log(chatMessage);
    let chat = document.getElementById('chat');
    chat.innerHTML += "<b>" + chatMessage["username"] + "</b>: " + chatMessage["comment"] + "<br/>";
}

function escape_html(message) {
    return message.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

}

// Render a single users
function addUser(user) {
    // TODO - Handle html escaping?
    console.log(`Adding ${user} to html. username = ${username}`);
    // user is the other user being templated
    if (user === username || username === '') {
        return;
    }

    let box = document.getElementById('onlineUsers');

    // const form = document.createElement("form");
    // form.method = "POST";
    // form.action = `/challenge_${username}_${user}`;


    // div for one user
    let escaped_user = escape_html(user);
    const user_div = document.createElement("div");
    user_div.id = `div_${escaped_user}`;

    // chat box for a user. format is:
    // <label for="chat-comment">Chat: </label>
    // <input id="chat-comment" type="text" name="comment">
    // <button onclick="sendMessage()">Send</button>
    const label = document.createElement("label");
    label.for = `${escaped_user}_chat`;
    label.innerText = `MESSAGE ${escaped_user}: `;
    user_div.innerHTML += label.outerHTML;

    // The input field for DMing
    const chat_box = document.createElement("input");
    chat_box.type = "text";
    chat_box.id = `${escaped_user}_chat`;
    chat_box.name = "message";
    user_div.innerHTML += chat_box.outerHTML;

    // Send DM button
    const send_button = document.createElement("button");
    send_button.innerText = "Direct Message";
    send_button.setAttribute('onclick', `sendDM('${escaped_user}')`);
    user_div.innerHTML += send_button.outerHTML;

    // Send Challenge
    const challenge_button = document.createElement("button");
    challenge_button.innerText = "Challenge";
    challenge_button.setAttribute('onclick', `sendChallenge('${escaped_user}')`);
    user_div.innerHTML += challenge_button.outerHTML;

    console.log('HTML element: ' + user_div.outerHTML);
    box.innerHTML += user_div.outerHTML;
    box.innerHTML += '</br>';
}

// Send a challenge to a user
function sendChallenge(to_challenge) {
    socket.send(JSON.stringify({
        'messageType': 'Challenge',
        'sender': username,
        'receiver': to_challenge
    }));
}

function sendDM(user) {
    console.log(`Calling sendDM on ${user}`);
    let chat_box = document.getElementById(`${user}_chat`)
    let direct_message = chat_box.value;
    chat_box.value = '';

    socket.send(JSON.stringify({
        'messageType': 'DirectMessage',
        'comment': direct_message,
        'sender': username,
        'receiver': user
    }));
}

function AcceptChallenge(challenger) {
    return confirm(`Accept a chess match from ${challenger}?`);
}

function get_online_users() {
    console.log('Getting Online Users');
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log('The below response is about to be parsed');
            console.log(this.response);
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
        case 'setUsername':
            username = message.username;
            console.log("Setting username = " + username);
            get_online_users();
            break;
        // The case where a user got challenged and then accepts or declines
        case 'Challenge':
            let sender = message.sender;
            let receiver = message.receiver;
            if (AcceptChallenge(sender)) {
                socket.send(JSON.stringify({
                    'messageType': 'ChallengeAccepted',
                    'sender': sender,
                    'receiver': receiver
                }));
                window.location.replace(`/game_${sender}_${receiver}`);
            }

            break;

        case 'ChallengeAccepted':
            let challenger = message.sender;
            let challenged = message.receiver;
            window.location.replace(`/game_${challenger}_${challenged}`);
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
    // const request = new XMLHttpRequest();
    // request.open("GET", "/close_websocket");
    // request.send();
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
    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀";
    get_chat_history();
}


function redirect() {
    let xmlHttpReq = new XMLHttpRequest();
    xmlHttpReq.open("GET", '/login', false);
    xmlHttpReq.send(null);
    return xmlHttpReq.responseText;
}

// console.log(httpGet('https://jsonplaceholder.typicode.com/posts'));