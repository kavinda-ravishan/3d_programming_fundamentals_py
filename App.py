from Utils import Game
from SolidCubeScene import SolidCubeScene
from TextureCubeScene import TextureCubeScene

if '__main__' == __name__:
    frame_width = 640
    frame_height = 640
    fps = 24.0

    game = Game(frame_width, frame_height, fps, [SolidCubeScene(), TextureCubeScene()])
    game.Go()
