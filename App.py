from Utils import Game
from SimpleSence import SimpleSence

if '__main__' == __name__:
    frame_width = 640
    frame_height = 640
    fps = 60.0

    game = Game(frame_width, frame_height, fps, [SimpleSence()])
    game.Go()
