from Engine import Game
# from SceneVertexPositionColorCube import SceneVertexPositionColorCube
# from SceneSolidCubes import SceneSolidCubes
# from SceneTextureCube import SceneTextureCube
# from SceneFlatIndependentCube import SceneFlatIndependentCube
# from SceneWaveVertexTexture import SceneWaveVertexTexture
# from SceneGouraud import SceneGouraud
# from ScenePoint import ScenePoint
from SceneSpecularPhongPoint import SceneSpecularPhongPoint

if '__main__' == __name__:
    frame_width = 320
    frame_height = 320
    fps = 24.0

    game = Game(
        frame_width, 
        frame_height, 
        fps, 
        [
            SceneSpecularPhongPoint(), 
            # ScenePoint(), 
            # SceneGouraud(), 
            # SceneWaveVertexTexture(), 
            # SceneFlatIndependentCube(), 
            # SceneVertexPositionColorCube(), 
            # SceneSolidCubes(), 
            # SceneTextureCube()
        ]
    )
    
    game.Go()
