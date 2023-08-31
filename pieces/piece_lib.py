from kivy.app import App
root = App.get_running_app().root
grid = root.get_screen("game_screen").grid if root.current != 'game_screen_edit' else\
    root.get_screen("game_screen_edit").grid


# movement_types:
# [directions: list of two ints, steps: int]
vertical = [[0, 1], [0, -1]]
horizontal = [[1, 0], [-1, 0]]
diagonally = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
rook = vertical + horizontal
queen = rook + diagonally
