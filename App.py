from Utils import Vec2, Color, Game, Scene

class SimpleScene(Scene):
    def __init__(self):
        super().__init__()
        self.p0 = Vec2()
        self.p1 = Vec2()
        self.m_lb = False
        self.x_max = 0
        self.y_max = 0
        
    def GraphicsSetupComplete(self): ...

    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float):
        m_x = mouse_stat[0][0]
        m_y = mouse_stat[0][1]
        self.m_lb = mouse_stat[1]

        if(not self.m_lb):
            self.p0.x = m_x
            self.p0.y = m_y

        self.p1.x = m_x
        self.p1.y = m_y
    
    def Draw(self):
        if self.m_lb:
            self.gfx.DrawLineVec(self.p0, self.p1, Color(255, 255, 255))

if '__main__' == __name__:

    try:
        game = Game(1280, 720, SimpleScene())
        game.Go()
    except Exception as ex:
        print(f'Exeption : {ex}')
