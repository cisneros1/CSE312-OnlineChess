export class Piece {
    constructor(piece_name, grid_coord) {
        this.piece_name = piece_name;
        this.grid_coord = grid_coord;
    }

}

export class Pawn extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

export class Bishop extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

export class Queen extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

export class Rook extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}

export class King extends Piece {
    constructor(piece_name, grid_coord) {
        super(piece_name, grid_coord);
    }
}