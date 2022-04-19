//TODO - Do import

let chess_pieces = ['b_bishop', 'b_king', 'b_knight', 'b_pawn', 'b_queen', 'b_rook', 'w_bishop', 'w_king', 'w_knight', 'w_pawn', 'w_queen', 'w_rook'];

let chess_grid = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]



// Saves the state of the board
// Will be used to check for checks, check mates, and rolling back turns
class GameState {
    constructor() {
    }
}
let piece = new Piece('pawn', [0, 0])
console.log(piece.piece_name)

function new_img(piece_name, height, width, context) {
    const image = new Image();
    image.src = '../frontend/image/' + piece_name + '.png';
    image.height = height;
    image.width = width;
    image.onload = () => {
        context.drawImage(image, 0, 0);
    };
    return image;
}

function setup() {
    console.log("Test 1");
    const canvas = document.getElementById("chess_canvas");
    const context = canvas.getContext("2d");

    let chess_image = document.getElementById("chess_image");
    board_coord = [100, 100]; // x, y
    piece_dim = [100, 100]; // width and height of each piece
    context.drawImage(chess_image, board_coord[0], board_coord[1]);
    let piece_imgs = [];    // Array of all the images
    // Set all pieces

}