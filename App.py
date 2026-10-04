from Utils import Game
from SimpleSence import SimpleSence

if '__main__' == __name__:
    frame_width = 300
    frame_height = 300
    fps = 24.0

    game = Game(frame_width, frame_height, fps, [SimpleSence()])
    game.Go()
