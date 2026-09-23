from math import cos, sin
from copy import deepcopy
from Utils import Vec2, Color, Game, Scene

class Star:
    @staticmethod
    def Make(outer_radius: float, inner_radius: float, n_flares: int):
        star: list[Vec2] = []
        d_theta = (2.0 * 3.14159) / (n_flares * 2)

        for i in range(n_flares * 2):
            rad = outer_radius if (i % 2 == 0) else inner_radius
            star.append(
                Vec2(rad * cos(i * d_theta),  rad * sin(i * d_theta))
            )

        return star

class Entity:
    def __init__(self, model: list[Vec2], position: Vec2):
        self.model = model
        self.pos = position
        self.scale = 1.0

    def TranslateBy(self, offset: Vec2):
        self.pos += offset

    def ScaleBy(self, val: float):
        self.scale *= val

    def GetPolyLine(self) -> list[Vec2]:
        poly = deepcopy(self.model)
        for i in range(len(poly)):
            poly[i] *= self.scale
            poly[i] += self.pos

        return poly

class PolylinesScene(Scene):
    def __init__(self):
        super().__init__()

        self.entities = [
            Entity(Star.Make(100.0, 50.0, 5), Vec2(460.0, 0.0)),
            Entity(Star.Make(150.0, 50.0, 5), Vec2(150.0, 300.0)),
            Entity(Star.Make(100.0, 50.0, 5), Vec2(250.0, -200.0)),
            Entity(Star.Make(150.0, 50.0, 5), Vec2(-250.0, 200.0)),
            Entity(Star.Make(100.0, 50.0, 8), Vec2(0.0, 0.0)),
            Entity(Star.Make(200.0, 50.0, 5), Vec2(-150.0, -300.0)),
            Entity(Star.Make(100.0, 50.0, 5), Vec2(400.0, 300.0))
        ]
        
    def CompsSetupComplete(self): ...

    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float):
        m_x = mouse_stat[0][0]
        m_y = mouse_stat[0][1]
        m_lb = mouse_stat[1]
        m_rb = mouse_stat[2]

        speed = 20.0
        if 'w' == key: self.camera.MoveBy(Vec2(0.0, speed))
        elif 's' == key: self.camera.MoveBy(Vec2(0.0, -speed))
        elif 'd' == key: self.camera.MoveBy(Vec2(speed, 0.0))
        elif 'a' == key: self.camera.MoveBy(Vec2(-speed, 0.0))

        elif 'q' == key: self.camera.Zoom(0.95)
        elif 'e' == key: self.camera.Zoom(1.05)
    
    def Draw(self):
        for entity in self.entities:
            self.camera.DrawClosePolyline(entity.GetPolyLine(), Color.Yellow)

if '__main__' == __name__:


    try:
        frame_width = 800
        frame_height = 800
        fps = 30.0

        game = Game(frame_width, frame_height, fps, [PolylinesScene()])
        game.Go()
    except Exception as ex:
        print(f'Exeption : {ex}')
