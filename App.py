from Utils import Game
from SolidCubesScene import SolidCubesScene
from TextureCubeScene import TextureCubeScene

if '__main__' == __name__:
    frame_width = 320
    frame_height = 320
    fps = 24.0

    game = Game(frame_width, frame_height, fps, [SolidCubesScene(), TextureCubeScene()])
    game.Go()
