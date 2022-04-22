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
}

class Pawn extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    // TODO - Update to include capture moves and en passant moves. Untested.
    generateMoves(grid) {
        // Offset values. y, x, can_capture
        let flip_y = this.color === 'white' ? 1 : -1;
        let moves = [[-1 * flip_y, 0, false], [-2, 0, false], [-1 * flip_y, -1, true], [-1 * flip_y, 1, true]]   // An offset from the current position. For black side multiply y by -1.
        if (!this.has_moved) {
            moves.push([-2 * flip_y, 0, false]);
        }
        for (let move of moves) {
            let offset_y = move[0] + this.grid_y;
            let offset_x = move[1] + this.grid_x;
            let is_valid = this.validate_move(this.color, offset_y, offset_x, grid, move[2]);
            if (is_valid === "capture_move") {
                this.moves.push([move[0], move[1]]);
                this.attack_moves.push([move[0], move[1]]);
            } else if (is_valid === "valid_move") {
                this.moves.push([move[0], move[1]]);
            }
        }
    }
}

class Bishop extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }

    generateMoves(grid) {
        ;
    }
}

class Knight extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

class Queen extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

class Rook extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

class King extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

// Saves the state of the board
// Will be used to check for checks, check mates, and rolling back turns
class GameState {
    constructor(grid, pieces) {
        this.grid = grid;
        console.log(this.grid);
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
        this.board_state_stack = [];    // To roll back turns. To check for checks, stalemates and checkmates.
        this.board_state = {
            turn: "white",
            total_turns: 0,

        }

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
            // Set all pieces to the unclicked state.
            instance.last_clicked = [0, 0];
            for (let piece of instance.pieces) {
                piece.clicked = false;
            }
        });
        console.log("Created Game State");
        // Begin main loop
        this.updateGame();
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

    // The main loop.
    updateGame() {
        clearAll(this.context);
        clearBoard();
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
const chess_grid = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']];
const board_coord = [100, 100];   // y, x
const board_size = document.getElementById('chess_image').width;            // This should be 800. Board is an 800*800 canvas
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

// Given an x and y grid index return the corresponding chess on that square. Returns '' if no piece was clicked.
function gridtoPiece(y, x, grid) {
    let piece = '';
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
            let white_bishop = new Knight('w_bishop', [7, 5]);
            let black_bishop = new Knight('b_bishop', [0, 5]);

            let white_knight = new Knight('w_knight', [7, 6]);
            let black_knight = new Knight('b_knight', [0, 6]);

            let white_rook = new Rook('w_rook', [7, 7]);
            let black_rook = new Rook('b_rook', [0, 7]);
            all_pieces = all_pieces.concat([white_bishop, black_bishop, white_knight, black_knight, white_rook, black_rook]);
        }
    }
    let game_state = new GameState(chess_grid, all_pieces);
}