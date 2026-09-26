from Utils import Game
from PolylinesScene import PolylinesScene
from PlankScene import PlankScene
from CarromboardSence import CarromboardSence

if '__main__' == __name__:
    frame_width = 800
    frame_height = 800
    fps = 60.0

    game = Game(frame_width, frame_height, fps, [CarromboardSence(), PlankScene(), PolylinesScene()])
    game.Go()
