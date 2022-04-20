class Piece {
    constructor(piece_name, grid_coord, context) {
        this.piece_name = piece_name;
        this.grid_y = grid_coord[0];   // eg [1, 1]
        this.grid_x = grid_coord[1];
        this.captured = false; // If the piece has been captured
        this.has_moved = false; // If a piece has been moved or not
        this.clicked = false; // If a piece is being dragged by the cursor
        this.context = context;

        // Dimensions of the piece
        this.width = piece_dim[0];
        this.height = piece_dim[1];
        chess_grid[this.grid_y][this.grid_x] = piece_name;  // grid[x][y] = 'b_pawn'
    }

    display_piece() {
        // TODO - change x and y values
        if (this.captured === false) {
            // Only display if this piece has not been captured yet
            let position = this.grid_to_pos();
            displayImage(this.piece_name, position[1], position[0], this.height, this.width, this.context)
        }
    }

    // This method takes a grid index and converts it to an x and y on the canvas
    grid_to_pos() {
        let board_x = board_coord[0];
        let board_y = board_coord[1];
        let offset = Math.floor(piece_dim[0] / 2);
        let square_size = Math.floor(board_size / 8);

        let pos_x = board_x + square_size * this.grid_x;
        let pos_y = board_y + square_size * this.grid_y;
        return [pos_y, pos_x];
    }
}

class Pawn extends Piece {
    constructor(piece_name, grid_coord, context) {
        super(piece_name, grid_coord, context);
    }
}

class Bishop extends Piece {
    constructor(piece_name, grid_coord, context) {
        super(piece_name, grid_coord, context);
    }
}

class Knight extends Piece {
    constructor(piece_name, grid_coord, context) {
        super(piece_name, grid_coord, context);
    }
}

class Queen extends Piece {
    constructor(piece_name, grid_coord, context) {
        super(piece_name, grid_coord, context);
    }
}

class Rook extends Piece {
    constructor(piece_name, grid_coord, context) {
        super(piece_name, grid_coord, context);
    }
}

class King extends Piece {
    constructor(piece_name, grid_coord, context) {
        super(piece_name, grid_coord, context);
    }
}

// Saves the state of the board
// Will be used to check for checks, check mates, and rolling back turns
class GameState {
    constructor(grid, pieces, context) {
        this.grid = grid;
        this.pieces = pieces;
        this.context = context;
        this.cursor_x = 0;
        this.cursor_y = 0;
        window.addEventListener('mousemove', function (e) {
            this.cursor_x = e.pageX;
            this.cursor_y = e.pageY;
        });
        console.log("Created Game State");
    }
    updateGame() {
        // clearBoard(this.context);
        // console.log("cursor_x: " + this.cursor_x + " cursor_y: " + this.cursor_y);
    }
}

// Some constants
const chess_pieces = ['b_bishop', 'b_king', 'b_knight', 'b_pawn', 'b_queen', 'b_rook', 'w_bishop', 'w_king', 'w_knight', 'w_pawn', 'w_queen', 'w_rook'];
// 8*8 grid.
const chess_grid = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]
const board_coord = [100, 100];   // x, y
const board_size = 800            // Board is a 800*800 canvas
const piece_dim = [100, 100];     // width and height of each piece


// Display a chess on the board
function displayImage(piece_name, x, y, height, width, context) {
    const image = new Image();
    image.src = '../frontend/image/' + piece_name + '.png';
    image.height = height;
    image.width = width;
    image.onload = () => {
        context.drawImage(image, x, y);
    };
    return image;
}

function clearBoard(context) {
    let chess_image = document.getElementById("chess_image");
    context.drawImage(chess_image, board_coord[0], board_coord[1]); // Draw the board
}

// function updateGame(context, pieces, cursor_x, cursor_y) {
//     // clearBoard(context);
//     console.log("cursor_x: " + cursor_x + " cursor_y: " + cursor_y);
//     // for (let piece of pieces){
//     //     piece.display_piece();
//     // }
// }

function setup() {
    console.log("Test 1");
    const canvas = document.getElementById("chess_canvas");
    const context = canvas.getContext("2d");
    let cursor_x = 0;
    let cursor_y = 0;
    clearBoard(context);    // Display the board
    // Begin initializing the chess pieces
    let all_pieces = [];
    for (let i = 0; i < 8; i++) {
        let white_pawn = new Pawn('w_pawn', [6, i], context);
        let black_pawn = new Pawn('b_pawn', [1, i], context);
        all_pieces = all_pieces.concat([white_pawn, black_pawn]);
        if (i === 0) {
            let white_rook = new Rook('w_rook', [7, 0], context);
            let black_rook = new Rook('b_rook', [0, 0], context);

            let white_knight = new Knight('w_knight', [7, 1], context);
            let black_knight = new Knight('b_knight', [0, 1], context);

            let white_bishop = new Bishop('w_bishop', [7, 2], context);
            let black_bishop = new Bishop('b_bishop', [0, 2], context);

            let white_king = new King('w_king', [7, 3], context);
            let black_king = new King('b_king', [0, 3], context);

            let white_queen = new Queen('w_queen', [7, 4], context);
            let black_queen = new Queen('b_queen', [0, 4], context);
            all_pieces = all_pieces.concat([white_rook, black_rook, white_knight, black_knight, white_bishop, black_bishop, white_king, black_king, white_queen, black_queen]);
        }
        if (i === 1) {
            let white_bishop = new Knight('w_bishop', [7, 5], context);
            let black_bishop = new Knight('b_bishop', [0, 5], context);

            let white_knight = new Knight('w_knight', [7, 6], context);
            let black_knight = new Knight('b_knight', [0, 6], context);

            let white_rook = new Rook('w_rook', [7, 7], context);
            let black_rook = new Rook('b_rook', [0, 7], context);
            all_pieces = all_pieces.concat([white_bishop, black_bishop, white_knight, black_knight, white_rook, black_rook]);
        }
    }
    let game_state = new GameState(chess_grid, all_pieces, context);
    let interval = setInterval(game_state.updateGame, 50);
}