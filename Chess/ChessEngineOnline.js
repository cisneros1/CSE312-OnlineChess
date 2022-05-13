let socket = new WebSocket('ws://' + window.location.host + '/connect_socket');

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
        let message = JSON.stringify({'messageType': 'chatMessage', 'comment': comment})
        socket.send(message);
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

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType
    console.log('Got message: ' + ws_message.data)

    switch (messageType) {
        case 'chatMessage':
            console.log('got a chat message')
            addMessage(message);
            break;

        case 'startGame':
            break;

        case 'chessMove':
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
    console.log("Websocket connection closed on connected_socket connection")
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


// -------------------------------------- START OF CHESS ENGINE -----------------------------------

class Piece {
    constructor(piece_name, grid_coord) {
        this.piece_name = piece_name;   // could be "b_pawn", w_knight", etc
        this.grid_y = grid_coord[0];   // The piece of the piece in chess_grid 2d array
        this.grid_x = grid_coord[1];
        this.captured = false; // If the piece has been captured
        this.has_moved = false; // If a piece has been moved or not
        this.clicked = false; // If a piece is being dragged by the cursor
        // Array of possible moves
        this.moves = [];
        this.attack_moves = [];

        this.color = piece_name.startsWith('w') ? "white" : "black"; // Assign "white" or "black" to a piece
        // The image attached to a piece. This will send a request for the image.
        this.image = new Image();
        this.image.src = '../frontend/image/' + piece_name + '.png';
        let new_piece_size = square_size - 10;
        this.image.height = new_piece_size;
        this.image.width = new_piece_size;

        // Dimensions of the piece
        chess_grid[this.grid_y][this.grid_x] = piece_name;  // grid[y][x] = 'b_pawn'
    }

    display_piece(context, cursor_pos = null) {
        // Only display if this piece has not been captured yet
        if (this.captured === false && cursor_pos === null) {
            let position = this.grid_to_pos();
            context.drawImage(this.image, position[1], position[0], this.image.width, this.image.height);
        }
        // if a piece was clicked then it will follow the cursor
        else if (this.captured === false && cursor_pos !== null) {
            let x_pos = cursor_pos[0];
            let y_pos = cursor_pos[1];
            let offset = -this.image.width / 2;
            context.drawImage(this.image, x_pos + offset, y_pos + offset, this.image.width, this.image.height);
        }
    }

    // Check if a move is valid
    // TODO - Untested.
    validate_move(color, y, x, grid, can_capture = true) {
        if (!within_grid(y, x)) {
            return '';
        }
        let piece = gridtoPiece(y, x, grid);    // Returns a piece if there's a piece there. Returns '' otherwise.
        // console.log(this);
        if (color === "white") {
            if (piece) {
                if (piece.color === "black" && grid[y][x].startsWith('b') && can_capture) {
                    return "capture_move";
                }
            } else {
                if (grid[y][x] === ' ') {
                    return "valid_move";
                }
            }
        } else {
            if (piece) {
                if (piece.color === "white" && grid[y][x].startsWith('w') && can_capture) {
                    return "capture_move";
                }
            } else {
                if (grid[y][x] === ' ') {
                    return "valid_move";
                }
            }
        }
        // If there's a piece of the same color in grid[y][x] or if a piece can't be taken on that square (only for pawns).
        return '';
    }

    // This method takes a grid index and converts it to an x and y on the canvas
    grid_to_pos() {
        let board_x = top_left_coord[1];
        let board_y = top_left_coord[0];
        let offset_x = 5;
        let offset_y = 2;

        let pos_x = offset_x + board_x + square_size * this.grid_x;
        let pos_y = offset_y + board_y + square_size * this.grid_y;
        return [pos_y, pos_x];
    }

    // This method will be overridden
    generateMoves(grid) {
        ;
    }

    // This method is for Queen, Rooks, and Bishops pieces.
    // Inputs: grid is obvious. offsets = [y_offset, x_offset]
    // TODO - Test this.
    generateMovesMany(grid, offsets) {
        let opposite_color = this.color === 'white' ? 'b' : 'w';
        let cur_y = this.grid_y;
        let cur_x = this.grid_x;
        let offset_y = offsets[0];
        let offset_x = offsets[1];

        cur_x += offset_x;
        cur_y += offset_y;
        while (within_grid(cur_y, cur_x) && grid[cur_y][cur_x] === ' ') {
            this.moves.push([cur_y, cur_x]);
        }
        if (within_grid(cur_y, cur_x) && grid[cur_y][cur_x].startsWith(opposite_color)) {
            this.moves.push([cur_y, cur_x]);
            this.attack_moves.push([cur_y, cur_x]);
        }
    }

    // Draw the available moves
    displayMoves(context) {
        context.save();
        context.globalAlpha = 0.65;
        for (let move of this.moves) {
            // If a move is also a capture move then make the square red.
            let in_attack_moves = this.attack_moves.find(attack_move => move[0] === attack_move[0] && move[1] === attack_move[1]);
            if (in_attack_moves) {
                context.fillStyle = "#be2a2a";
            } else {
                context.fillStyle = "#4ea8ff";
            }
            let offset_x = -1;
            context.fillRect(top_left_coord[1] + move[1] * square_size + offset_x, top_left_coord[0] + move[0] * square_size, square_size, square_size);
        }
        context.restore();
    }
}

class Pawn extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    // TODO - Update to include en passant moves. Untested.
    generateMoves(grid) {
        // Offset values. y, x, can_capture
        let flip_y = this.color === 'white' ? 1 : -1;
        let moves = [[-1 * flip_y, 0, false]];   // An offset from the current position. For black side multiply y by -1.
        let opposite_color = this.color === 'white' ? 'black' : 'white';
        // Cover capture moves
        if (!this.has_moved) {
            moves.push([-2 * flip_y, 0, false]);
        }
        // Check if this pawn can capture another piece on it's left and right
        let check_left = gridtoPiece(-1 * flip_y + this.grid_y, -1 + this.grid_x, grid);
        let check_right = gridtoPiece(-1 * flip_y + this.grid_y, 1 + this.grid_x, grid);

        if (check_left && check_left.color === opposite_color) {
            moves.push([-1 * flip_y, -1, true]);
        }
        if (check_right && check_right.color === opposite_color) {
            moves.push([-1 * flip_y, 1, true]);
        }
        for (let move of moves) {
            let offset_y = move[0] + this.grid_y;
            let offset_x = move[1] + this.grid_x;
            let is_valid = this.validate_move(this.color, offset_y, offset_x, grid, move[2]);
            if (is_valid === "capture_move") {
                this.moves.push([offset_y, offset_x]);
                this.attack_moves.push([offset_y, offset_x]);
            } else if (is_valid === "valid_move") {
                this.moves.push([offset_y, offset_x]);
            }
        }
    }
}

class Bishop extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    generateMoves(grid) {
        // Check upper-left
        this.generateMovesMany(grid, [-1, -1]);
        // Check upper-right
        this.generateMovesMany(grid, [-1, 1]);
        // Check lower-left
        this.generateMovesMany(grid, [1, -1]);
        // Check lower-right
        this.generateMovesMany(grid, [1, 1]);
    }
}

class Knight extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    // TODO - Untested.
    generateMoves(grid) {
        let moves = [[-1, 2], [-2, -1], [-2, 1], [-1, 2], [1, -2], [2, -1], [2, 1], [1, 2]] // List of offset from the current grid position.
        for (let move of moves) {
            let offset_y = this.grid_y + move[0];
            let offset_x = this.grid_x + move[1];
            let is_valid = this.validate_move(this.color, offset_y, offset_x, grid);
            if (is_valid === "capture_move") {
                this.moves.push([offset_y, offset_x]);
                this.attack_moves.push([offset_y, offset_x]);
            } else if (is_valid === "valid_move") {
                this.moves.push([offset_y, offset_x]);
            }
        }
    }
}

class Queen extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    generateMoves(grid) {
        // Check upper-left
        this.generateMovesMany(grid, [-1, -1]);
        // Check upper-right
        this.generateMovesMany(grid, [-1, 1]);
        // Check lower-left
        this.generateMovesMany(grid, [1, -1]);
        // Check lower-right
        this.generateMovesMany(grid, [1, 1]);
        // Check left
        this.generateMovesMany(grid, [0, -1]);
        // Check up
        this.generateMovesMany(grid, [-1, 0]);
        // Check right
        this.generateMovesMany(grid, [0, 1]);
        // Check down
        this.generateMovesMany(grid, [1, 0]);
    }
}

class Rook extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    generateMoves(grid) {
        // Check left
        this.generateMovesMany(grid, [0, -1]);
        // Check up
        this.generateMovesMany(grid, [-1, 0]);
        // Check right
        this.generateMovesMany(grid, [0, 1]);
        // Check down
        this.generateMovesMany(grid, [1, 0]);
    }
}

// TODO - Add castling.
class King extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    generateMoves(grid) {
        let moves = [[-1, -1], [-1, 1], [1, -1], [1, 1], [0, -1], [-1, 0], [0, 1], [1, 0]];
        for (let move of moves) {
            let offset_y = this.grid_y + move[0];
            let offset_x = this.grid_x + move[1];
            let is_valid = this.validate_move(this.color, offset_y, offset_x, grid);
            if (is_valid === "capture_move") {
                this.moves.push([offset_y, offset_x]);
                this.attack_moves.push([offset_y, offset_x]);
            } else if (is_valid === "valid_move") {
                this.moves.push([offset_y, offset_x]);
            }
        }
    }
}

// Saves the state of the board
// Will be used to check for checks, check mates, and rolling back turns
class GameState {
    constructor(grid, pieces, your_turn) {
        this.grid = grid;
        console.log(copy2d(this.grid));

        this.pieces = pieces;
        this.cursor_x = 0;
        this.cursor_y = 0;
        this.canvas = document.getElementById("chess_canvas");
        this.context = this.canvas.getContext("2d");
        this.last_clicked = [0, 0];
        // Update the location of the cursor position
        let instance = this;
        window.addEventListener('mousemove', function (e) {
            instance.cursor_x = e.offsetX;
            instance.cursor_y = e.offsetY;
        });
        // TODO - This will need to be changed at some point. Websocket stuff
        this.generateAllMoves();
        this.game_started = true;
        this.your_turn = your_turn;
        this.in_check = false;
        this.player_color = ''; // Will be set to 'white' or 'black'
        this.board_state_stack = [];    // To roll back turns. To check for checks, stalemates and checkmates.

        // TODO - The event handlers below are unfinished.
        // Listen for mouse clicks
        window.addEventListener('mousedown', function (e) {
            instance.last_clicked = [e.offsetY, e.offsetX];
            let square_clicked = coordToGrid(e.offsetX, e.offsetY);
            // If a piece was clicked. The empty string is falsy.
            if (square_clicked) {
                let piece_clicked = gridtoPiece(square_clicked[0], square_clicked[1], instance.grid);
                if (piece_clicked) {
                    piece_clicked.clicked = true;
                }
            }
        });
        // Listen for mouse release. This is where we make a chess move
        window.addEventListener('mouseup', function (e) {
            // Set all pieces to the un-clicked state.
            instance.last_clicked = [0, 0];
            // TODO - This line is causing issues :(
            // let piece_clicked = this.all_pieces.find(piece => piece.clicked === true);
            // if (instance.your_turn && piece_clicked) {
            //     ;
            // }
            for (let piece of instance.pieces) {
                piece.clicked = false;
            }
        });
        console.log("Created Game State");
        // Begin main loop
        this.updateGame();
    }

    // Returns true if your king is in check
    inCheck() {
        let opposite_color = this.player_color === 'white' ? 'black' : 'white';
        let king = this.pieces.find(piece => piece instanceof King && piece.color === this.player_color);
        for (let piece of this.pieces) {
            if (piece.color === opposite_color) {
                let in_check = piece.attack_moves.find(move => move[0] === king.grid_y && move[1] === king.grid_x);
                if (in_check) {
                    return true;
                }
            }
        }
        return false;
    }


    // This will remove moves that put the player in check
    // TODO - finish this method
    filterMoves() {
        let saved_board = this.saveBoardState();
        let player_pieces = this.pieces.filter(piece => piece.color === this.player_color);
        for (let piece of player_pieces) {
            let filtered_moves = [];
            let filtered_capture_moves = [];
            for (const move of piece.moves) {
                this.MakeMove(piece, move);
                this.generateAllMoves();
                let in_check = this.in_check();
                if (!in_check) {
                    filtered_moves.push(move);
                    filtered_capture_moves.push(move);
                }
                this.loadBoardState(saved_board);
            }
            piece.moves = filtered_moves;
            piece.attack_moves = filtered_capture_moves;
        }
    }

    // This method will make a move.
    MakeMove(piece, move) {
        let move_y = move[0];
        let move_x = move[1];
        this.grid[piece.grid_y][piece.grid_x] = ' ';
        piece.grid_y = move_y;
        piece.grid_x = move_x;

        let capture_move = piece.attack_moves.find(attack_move => move[0] === attack_move[0] && move[1] === attack_move[1]);
        let captured_piece = gridtoPiece(move_y, move_x, this.grid);
        if (capture_move) {
            captured_piece.captured = true;
            this.grid[captured_piece.grid_y][captured_piece.grid_x] = piece.piece_name;
            captured_piece.grid_y = -1;
            captured_piece.grid_x = -1;

        } else {
            this.grid[move_y][move_x] = piece.piece_name;
        }
    }

    // TODO - untested.
    // Saves the state of the entire board.
    saveBoardState() {
        let board_state = {
            grid: copy2d(this.grid), in_check: this.in_check, your_turn: this.your_turn, piece_states: new Map()
        }
        for (let piece of this.pieces) {
            let piece_state = {
                grid_y: piece.grid_y,
                grid_x: piece.grid_x,
                captured: piece.captured,
                has_moved: piece.has_moved,
                moves: copy2d(piece.moves),
                attack_moves: copy2d(piece.attack_moves)
            }
            board_state.piece_states.set(piece, piece_state);   // Set a Mapping of (piece => piece_state)
        }
        return board_state;
    }

    // Changes the state of the game
    loadBoardState(board_state) {
        this.grid = board_state.grid;
        this.in_check = board_state.in_check;
        this.your_turn = board_state.your_turn;
        for (let piece of this.pieces) {
            let piece_state = board_state.piece_states.get(piece);
            piece.grid_y = piece_state.grid_y;
            piece.grid_x = piece_state.grid_x;
            piece.captured = piece_state.captured;
            piece.has_moved = piece_state.has_moved;
            piece.moves = piece_state.moves;
            piece.attack_moves = piece_state.attack_moves;
        }
    }

    // Display all of the chess pieces
    // TODO - Check if a piece is captured or not.
    displayAllPieces() {
        for (let piece of this.pieces) {
            if (piece.clicked && !piece.captured) {
                piece.display_piece(this.context, [this.cursor_x, this.cursor_y]);
            } else {
                piece.display_piece(this.context);
            }
        }
    }

    // Debug method - Generate all moves
    generateAllMoves() {
        for (let piece of this.pieces) {
            if (!piece.captured) {
                piece.generateMoves(this.grid);
            }
        }
    }

    // TODO - Update this to not include piece that have been captured and only display if the game has started and it's the player turn
    displayAllMoves() {
        for (let piece of this.pieces) {
            if (piece.clicked && !piece.captured) {
                piece.displayMoves(this.context);
            }
            // piece.displayMoves(this.context);
        }
    }

    // The main loop.
    updateGame() {
        clearAll(this.context);
        clearBoard();
        this.displayAllMoves();
        this.displayAllPieces();
        let offset = square_size / 2;
        // this.context.fillRect(this.cursor_x - offset, this.cursor_y - offset, square_size, square_size);
        // console.log("Cursor X: " + this.cursor_x + " Cursor Y: " + this.cursor_y);
        // console.log(coordToGrid(this.cursor_x, this.cursor_y));
        requestAnimationFrame(this.updateGame.bind(this));  // Repeatedly call this method.
    }
}

// Some constants
const chess_pieces = ['b_bishop', 'b_king', 'b_knight', 'b_pawn', 'b_queen', 'b_rook', 'w_bishop', 'w_king', 'w_knight', 'w_pawn', 'w_queen', 'w_rook'];
// 8*8 grid.
const chess_grid = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']];
const board_coord = [100, 100];   // y, x
const board_size = document.getElementById('chess_image').width;    // This should be 800. Board is an 800*800 canvas
const piece_dim = [65, 65];     // width and height of each piece
const square_size = 74;
const top_left_coord = [154, 154];  // y, x coordinate of where the chess board squares starts at the upper-left
console.log("Board Width: " + board_size);
let all_pieces = [];    // Do not change this.


// Display a chess on the board
function displayImage(piece_name, x, y, height, width) {
    let canvas = document.getElementById("chess_canvas");
    let context = canvas.getContext("2d");
    const image = new Image();
    image.src = '../frontend/image/' + piece_name + '.png';
    image.height = height;
    image.width = width;
    image.onload = () => {
        context.drawImage(image, x, y);
    };
    return image;
}

// Make a copy of a 2d array.
function copy2d(array_2d) {
    if (array_2d.length === 0) {
        return [];
    }
    let array_copy = [];
    for (let row of array_2d) {
        array_copy.push([...row]);
    }
    return array_copy;
}

// Given an x and y grid index return the corresponding chess on that square. Returns '' if no piece was clicked.
function gridtoPiece(y, x, grid) {
    let piece = '';
    if (!within_grid(y, x)) {
        return piece;
    }
    for (let piece of all_pieces) {
        if (piece.grid_y === y && piece.grid_x === x && grid[y][x] === piece.piece_name) {
            return piece;
        }
    }
    return piece;
}

// Within bounds.
function within_grid(y, x) {
    return x >= 0 && x < chess_grid.length && y >= 0 && y < chess_grid.length;
}

function within_range(value, min, max) {
    return value > min && value <= max;
}

function coordToGrid(x_pos, y_pos) {
    for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 8; j++) {
            if (within_range(x_pos, top_left_coord[1] + j * square_size, top_left_coord[1] + j * square_size + square_size)) {
                if (within_range(y_pos, top_left_coord[0] + i * square_size, top_left_coord[0] + i * square_size + square_size)) {
                    return [i, j];
                }
            }
        }
    }
    return [];
}

// Draw the chess onto the canvas
function clearBoard() {
    const canvas = document.getElementById("chess_canvas");
    const context = canvas.getContext("2d");
    let chess_image = document.getElementById("chess_image");
    context.drawImage(chess_image, board_coord[0], board_coord[1]); // Draw the board
}

// Draw clear the canvas
function clearAll(context) {
    let canvas = document.getElementById("chess_canvas");
    let canvas_width = canvas.width;
    let canvas_height = canvas.height;
    context.clearRect(0, 0, canvas_width, canvas_height);
}


// function startGame() {
//     console.log("Started a game.")
//     socket = new WebSocket('ws://' + window.location.host + '/connect_socket');
//     game_started = true;
// }
window.onload = function () {
    console.log('loaded chess online')
    setup();
}

function setup() {
    console.log("Called setup()");
    clearBoard();    // Display the board
    // Begin initializing the chess pieces
    for (let i = 0; i < 8; i++) {
        let white_pawn = new Pawn('w_pawn', [6, i]);
        let black_pawn = new Pawn('b_pawn', [1, i]);
        all_pieces = all_pieces.concat([white_pawn, black_pawn]);
        if (i === 0) {
            let white_rook = new Rook('w_rook', [7, 0]);
            let black_rook = new Rook('b_rook', [0, 0]);

            let white_knight = new Knight('w_knight', [7, 1]);
            let black_knight = new Knight('b_knight', [0, 1]);

            let white_bishop = new Bishop('w_bishop', [7, 2]);
            let black_bishop = new Bishop('b_bishop', [0, 2]);

            let white_king = new King('w_king', [7, 3]);
            let black_king = new King('b_king', [0, 3]);

            let white_queen = new Queen('w_queen', [7, 4]);
            let black_queen = new Queen('b_queen', [0, 4]);
            all_pieces = all_pieces.concat([white_rook, black_rook, white_knight, black_knight, white_bishop, black_bishop, white_king, black_king, white_queen, black_queen]);
        }
        if (i === 1) {
            let white_bishop = new Bishop('w_bishop', [7, 5]);
            let black_bishop = new Bishop('b_bishop', [0, 5]);

            let white_knight = new Knight('w_knight', [7, 6]);
            let black_knight = new Knight('b_knight', [0, 6]);

            let white_rook = new Rook('w_rook', [7, 7]);
            let black_rook = new Rook('b_rook', [0, 7]);
            all_pieces = all_pieces.concat([white_bishop, black_bishop, white_knight, black_knight, white_rook, black_rook]);
        }
    }
    let game_state = new GameState(chess_grid, all_pieces);
}