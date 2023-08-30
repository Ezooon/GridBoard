from pieces.piece_lib import *

self = grid.current_piece
grid.show_movement = None
grid.change_turn_on = "die_roll"

c, r = self.cell
die = grid.dies_sum
if die == 6:
    grid.previous_turn()

blue_home = 0 <= c <= 5 and 0 <= r <= 5
red_home = 0 <= c <= 5 and 9 <= r <= 14
green_home = 9 <= c <= 14 and 9 <= r <= 14
yellow_home = 9 <= c <= 14 and 0 <= r <= 5

b_g = [0, 0]
r_g = [0, 0]
g_g = [0, 0]
y_g = [0, 0]
for x, y in [[1, 1], [4, 1], [1, 4], [4, 4]]:
    if not grid.cells_pieces[x][y]:
        b_g = [x, y]

for x, y in [[1, 10], [4, 10], [1, 13], [4, 13]]:
    if not grid.cells_pieces[x][y]:
        r_g = [x, y]

for x, y in [[10, 10], [13, 10], [10, 13], [13, 13]]:
    if not grid.cells_pieces[x][y]:
        g_g = [x, y]

for x, y in [[10, 1], [13, 1], [10, 4], [13, 4]]:
    if not grid.cells_pieces[x][y]:
        y_g = [x, y]


if self.name == "blue_piece_trans.png":
    road = [[6, r] for r in range(1, 6)] + list(reversed([[c, 6] for c in range(6)])) + [[0, 7]] + \
           [[c, 8] for c in range(6)] + [[6, r] for r in range(9, 15)] + [[7, 14]] + \
           list(reversed([[8, r] for r in range(9, 15)])) + [[c, 8] for c in range(9, 15)] + [[14, 7]] + \
           list(reversed([[c, 6] for c in range(9, 15)])) + list(reversed([[8, r] for r in range(6)])) + \
           [[7, r] for r in range(7)]

elif self.name == "red_piece_trans.png":
    road = [[c, 8] for c in range(1, 6)] + [[6, r] for r in range(9, 15)] + [[7, 14]] + \
           list(reversed([[8, r] for r in range(9, 15)])) + [[c, 8] for c in range(9, 15)] + [[14, 7]] + \
           list(reversed([[c, 6] for c in range(9, 15)])) + list(reversed([[8, r] for r in range(6)])) + [[7, 0]] +\
           [[6, r] for r in range(6)] + list(reversed([[c, 6] for c in range(6)])) + \
           [[c, 7] for c in range(7)]

elif self.name == "green_piece_trans.png":
    road = list(reversed([[8, r] for r in range(9, 14)])) + [[c, 8] for c in range(9, 15)] + [[14, 7]] + \
           list(reversed([[c, 6] for c in range(9, 15)])) + list(reversed([[8, r] for r in range(6)])) + [[7, 0]] + \
           [[6, r] for r in range(6)] + list(reversed([[c, 6] for c in range(6)])) + [[0, 7]] + \
           [[c, 8] for c in range(6)] + [[6, r] for r in range(9, 15)] + \
           list(reversed([[7, r] for r in range(8, 15)]))
else:
    road = list(reversed([[c, 6] for c in range(9, 14)])) + list(reversed([[8, r] for r in range(6)])) + [[7, 0]] +\
           [[6, r] for r in range(6)] + list(reversed([[c, 6] for c in range(6)])) + [[0, 7]] + \
           [[c, 8] for c in range(6)] + [[6, r] for r in range(9, 15)] + [[7, 14]] + \
           list(reversed([[8, r] for r in range(9, 15)])) + [[c, 8] for c in range(9, 15)] + \
           list(reversed([[c, 7] for c in range(8, 15)]))

save_zone = [[6, 1], [2, 6], [1, 8], [6, 12], [8, 13], [12, 8], [13, 6]]

n_cell = None
if self.cell in road:
    i = road.index(self.cell)
    if i + die < len(road):
        n_cell = road[i+die]

elif die == 6:
    i = [blue_home, red_home, green_home, yellow_home].index(True)
    n_cell = [[6, 1], [1, 8], [8, 13], [13, 6]][i]


def stop_piece(piece):
    piece.movable = False


on_press = []
if n_cell:
    c, r = n_cell
    kills = grid.cells_pieces[c][r]
    if kills and n_cell not in save_zone:
        if kills[0].player != self.player:
            on_press.append(grid.kill([n_cell]))
            on_press.append([grid.previous_turn, []])
    on_press.append(grid.move(self.cell, n_cell))
    if n_cell in [[7, 6], [7, 8], [6, 7], [8, 7]]:
        on_press.append([grid.previous_turn, []])
    on_press.append([stop_piece, [self]])

logic = {
    "blue_piece_trans.png": {
        "on_press": on_press,
        "on_killed": [
            grid.move(n_cell, b_g, True)
        ]
    },

    "green_piece_trans.png": {
        "on_press": on_press,
        "on_killed": [
            grid.move(n_cell, g_g, True)
        ]
    },

    "red_piece_trans.png": {
        "on_press": on_press,
        "on_killed": [
            grid.move(n_cell, r_g, True)
        ]
    },

    "yellow_piece_trans.png": {
        "on_press": on_press,
        "on_killed": [
            grid.move(n_cell, y_g, True)
        ]
    },

}
# def movement(rm_save_zone=False):
#     if rm_save_zone and n_cell in save_zone:
#         return grid.to_cell(n_cell)
#     return []
#
# logic = {
#     "blue_piece_trans.png": {
#         "movements": [
#             (blue_home and die == 6, (grid.to_cell([6, 1]), 1)),
#             (not blue_home, (movement(), 1, True, True)),
#         ],
#         "kills": [
#             (not blue_home, (movement(True), 1, True, True)),
#         ],
#         "on_press": on_press,
#         "on_killed": [
#             grid.move(self.new_cell, b_g, True)
#         ]
#     },
#
#     "green_piece_trans.png": {
#         "movements": [
#             (green_home and die == 6, (grid.to_cell([8, 13]), 1)),
#             (not green_home, (movement(), 1, True, True)),
#         ],
#         "kills": [
#             (not green_home, (movement(True), 1, True, True)),
#         ],
#         "on_killed": [
#             grid.move(self.new_cell, g_g, True)
#         ]
#     },
#
#     "red_piece_trans.png": {
#         "movements": [
#             (red_home and die == 6, (grid.to_cell([1, 8]), 1)),
#             (not red_home, (movement(), 1, True, True)),
#         ],
#         "kills": [
#             (not red_home, (movement(True), 1, True, True)),
#         ],
#         "on_killed": [
#             grid.move(self.new_cell, r_g, True)
#         ]
#     },
#
#     "yellow_piece_trans.png": {
#         "movements": [
#             (yellow_home and die == 6, (grid.to_cell([13, 6]), 1)),
#             (not yellow_home, (movement(), 1, True, True)),
#         ],
#         "kills": [
#             (not yellow_home, (movement(True), 1, True, True)),
#         ],
#         "on_killed": [
#             grid.move(n_cell, y_g, True)
#         ]
#     },
#
# }
