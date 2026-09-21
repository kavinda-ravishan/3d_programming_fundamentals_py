from Utils import Game, Scene

class SimpleScene(Scene):
    def __init__(self):
        super().__init__()

    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float):
        pass
    
    def Draw(self):
        self.gfx.PutPixel(300, 300, (255, 255, 255))

if '__main__' == __name__:

    try:
        game = Game(SimpleScene())
        game.Go()
    except Exception as ex:
        print(f'Exeption : {ex}')
