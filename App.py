from Utils import Game
from PolylinesScene import PolylinesScene

if '__main__' == __name__:
    frame_width = 800
    frame_height = 800
    fps = 60.0

    game = Game(frame_width, frame_height, fps, [PolylinesScene()])
    game.Go()
