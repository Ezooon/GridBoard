from pieces.piece_lib import *
self = grid.current_piece

logic = {

    "bishop_black.png": {
        "movements": [
            (True, (diagonally,))
        ],
        "kills": [
            (True, (diagonally,))
        ],
    },

    "bishop_white.png": {
        "movements": [
            (True, (diagonally,))
        ],
        "kills": [
            (True, (diagonally,))
        ],
    },

    "king_black.png": {
        "movements": [
            (True, (queen, 1)),
            (
                self.cell == [4, 7] and grid.piece_in_cell('rook_black.png', [7, 7]),
                ([[1, 0]], 2),
                [grid.move([7, 7], [5, 7])]
            )
        ],
        "kills": [
            # (True, (queen, 1))
        ],
    },

    "king_white.png": {
        "movements": [
            (True, (queen, 1)),
            (
                self.cell == [4, 0] and grid.piece_in_cell('rook_white.png', [7, 0]),
                ([[1, 0]], 2),
                [grid.move([7, 0], [5, 0])]
            )
        ],
        "kills": [
            (True, (queen, 1))
        ],
    },

    "knight_black.png": {
        "movements": [
            (True, ([[1, 2], [2, 1], [-1, -2], [-2, -1], [-1, 2], [-2, 1], [1, -2], [2, -1]], 1, True))
        ],
        "kills": [
            (True, ([[1, 2], [2, 1], [-1, -2], [-2, -1], [-1, 2], [-2, 1], [1, -2], [2, -1]], 1, True))
        ],
    },

    "knight_white.png": {
        "movements": [
            (True, ([[1, 2], [2, 1], [-1, -2], [-2, -1], [-1, 2], [-2, 1], [1, -2], [2, -1]], 1, True))
        ],
        "kills": [
            (True, ([[1, 2], [2, 1], [-1, -2], [-2, -1], [-1, 2], [-2, 1], [1, -2], [2, -1]], 1, True))
        ],
    },

    "pawn_black.png": {
        "movements": [
            (True, ([[0, -1]], 1, False)),
            (self.cell[1] == 6, ([[0, -2]], 1, False))
        ],
        "kills": [
            (True, ([[-1, -1], [1, -1]], 1))
        ],
    },

    "pawn_white.png": {
        "movements": [
            (True, ([[0, 1]], 1, False)),
            (self.cell[1] == 1, ([[0, 2]], 1, False))
],
        "kills": [
            (True, ([[1, 1], [-1, 1]], 1))
        ],
    },

    "queen_black.png": {
        "movements": [
            (True, (queen,))
        ],
        "kills": [
            (True, (queen,))
        ],
    },

    "queen_white.png": {
        "movements": [
            (True, (queen,))
        ],
        "kills": [
            (True, (queen,))
        ],
    },

    "rook_black.png": {
        "movements": [
            (True, (rook,))
        ],
        "kills": [
            (True, (rook,))
        ],
    },

    "rook_white.png": {
        "movements": [
            (True, (rook,))
        ],
        "kills": [
            (True, (rook,))
        ],
    },

}