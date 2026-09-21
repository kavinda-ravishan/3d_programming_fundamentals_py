from Utils import Vec2, Color, Game, Scene

class SimpleScene(Scene):
    def __init__(self):
        super().__init__()
        self.p0 = Vec2()
        self.p1 = Vec2()
        self.m_lb = False
        self.x_max = 0
        self.y_max = 0
        
    def GraphicsSetupComplete(self):
        self.x_max = self.gfx.GetFrameWidth() - 1
        self.y_max = self.gfx.GetFrameHeight() - 1

    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float):
        # print(f'{mouse_stat[0][0]}, {mouse_stat[0][1]}')
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
            self.DrawLine(self.p0, self.p1, Color(255, 255, 255))

    def DrawLine(self, p0: Vec2, p1: Vec2, c: Color):
        if(p0.x == p1.x): return

        p1.x = self.x_max if p1.x > self.x_max else p1.x
        p1.x = 0 if p1.x < 0 else p1.x

        p1.y = self.y_max if p1.y > self.y_max else p1.y
        p1.y = 0 if p1.y < 0 else p1.y

        if(p0.x > p1.x):
            p1, p0 = p0, p1

        m = (p1.y - p0.y) / (p1.x - p0.x)
        b = p0.y - m * p0.x

        for x in range(int(p0.x), int(p1.x)):
            y = (m * x) + b
            self.gfx.PutPixel(x, y, c)


if '__main__' == __name__:

    try:
        game = Game(1280, 720, SimpleScene())
        game.Go()
    except Exception as ex:
        print(f'Exeption : {ex}')
