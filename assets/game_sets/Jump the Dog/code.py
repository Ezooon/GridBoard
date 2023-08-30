from pieces.piece_lib import *
self = grid.current_piece
grid.change_turn_on = "custom"
c, r = self.cell

logic = {
    "black.png": {
        "movements": [
            (True, (rook, 1, False), ),
        ],
        "kills": [
            (grid.in_direction('white.png', [[1, 0]], 1), ([[2, 0]], 1, True, False), [grid.kill([[c+1, r]])]),
            (grid.in_direction('white.png', [[0, 1]], 1), ([[0, 2]], 1, True, False), [grid.kill([[c, r+1]])]),
            (grid.in_direction('white.png', [[-1, 0]], 1), ([[-2, 0]], 1, True, False), [grid.kill([[c-1, r]])]),
            (grid.in_direction('white.png', [[0, -1]], 1), ([[0, -2]], 1, True, False), [grid.kill([[c, r-1]])]),
        ],
    },
    "white.png": {
        "movements": [
            (True, (rook, 1, False), ),
        ],
        "kills": [
            (grid.in_direction('black.png', [[1, 0]], 1), ([[2, 0]], 1, True, False), [grid.kill([[c+1, r]])]),
            (grid.in_direction('black.png', [[0, 1]], 1), ([[0, 2]], 1, True, False), [grid.kill([[c, r+1]])]),
            (grid.in_direction('black.png', [[-1, 0]], 1), ([[-2, 0]], 1, True, False), [grid.kill([[c-1, r]])]),
            (grid.in_direction('black.png', [[0, -1]], 1), ([[0, -2]], 1, True, False), [grid.kill([[c, r-1]])]),
        ],
    },
}
