class Piece {
    constructor(piece_name, grid_coord) {
        this.piece_name = piece_name;
        this.grid_y = grid_coord[0];   // eg [1, 1]
        this.grid_x = grid_coord[1];
        this.captured = false; // If the piece has been captured
        this.has_moved = false; // If a piece has been moved or not
        this.clicked = false; // If a piece is being dragged by the cursor
        // The image attached to a piece
        this.image = new Image();
        this.image.src = '../frontend/image/' + piece_name + '.png';
        this.image.height = piece_dim[0];
        this.image.width = piece_dim[1];

        // Dimensions of the piece
        this.width = piece_dim[0];
        this.height = piece_dim[1];
        chess_grid[this.grid_y][this.grid_x] = piece_name;  // grid[x][y] = 'b_pawn'
    }

    display_piece(context) {
        // TODO - change x and y values
        if (this.captured === false) {
            // Only display if this piece has not been captured yet
            let position = this.grid_to_pos();
            context.drawImage(this.image, position[1], position[0], this.image.width, this.image.height);
        }
    }

    // This method takes a grid index and converts it to an x and y on the canvas
    grid_to_pos() {
        let board_x = top_left_coord[1];
        let board_y = top_left_coord[0];
        let offset = Math.floor(piece_dim[0] / 2);
        let square_size = Math.floor(80);

        let pos_x = board_x + square_size * this.grid_x;
        let pos_y = board_y + square_size * this.grid_y;
        return [pos_y, pos_x];
    }
}

class Pawn extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

class Bishop extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
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
        // Call updateGame every t milliseconds
        let instance = this;
        let t = 20;
        let interval = setInterval(function () {
            instance.updateGame();
        }, t)

        window.addEventListener('mousemove', function (e) {
            instance.cursor_x = e.pageX;
            instance.cursor_y = e.pageY;
        });
        console.log("Created Game State");
    }

    updateGame() {
        clearAll(this.context);
        clearBoard();
        for (let piece of this.pieces) {
            piece.display_piece(this.context);
        }
        this.context.save();
        // Draw high opacity square to find the right coordinates
        this.context.fillStyle = "#FF0000";
        this.context.fillRect(100, 100, 80, 80);
        this.context.restore();
        console.log("Cursor X: " + this.cursor_x + " Cursor Y: " + this.cursor_y);
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
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]
const board_coord = [100, 100];   // x, y
const board_size = 800            // Board is a 800*800 canvas
const piece_dim = [70, 70];     // width and height of each piece
const top_left_coord = [1216, 148]  // coordinate of where the chess board squares starts at the upper-left


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

function clearBoard() {
    const canvas = document.getElementById("chess_canvas");
    const context = canvas.getContext("2d");
    let chess_image = document.getElementById("chess_image");
    context.drawImage(chess_image, board_coord[0], board_coord[1]); // Draw the board
}

function clearAll(context) {
    let canvas = document.getElementById("chess_canvas");
    let canvas_width = 1000;
    let canvas_height = 1000;
    context.clearRect(0, 0, canvas_width, canvas_height);
}

function setup() {
    console.log("Test 1");
    clearBoard();    // Display the board
    // Begin initializing the chess pieces
    let all_pieces = [];
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