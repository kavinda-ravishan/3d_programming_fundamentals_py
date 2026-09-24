from math import cos, sin
from random import randint
from Utils import Vec2, Rect, Color, Scene, Entity

class Star(Entity):
    def __init__(self, inner_radius: float, outer_radius: float, n_flares: int, position: Vec2):
        super().__init__(
            Star.Make(inner_radius, outer_radius, n_flares), 
            Star.BoundingBox(inner_radius, outer_radius, position), 
            position, 
            Color.Yellow
        )
        self.radius =  max(outer_radius, inner_radius)
        self.position = position

    def GetRadius(self): return self.radius
    
    def GetPosition(self): return self.position

    @staticmethod
    def Make(inner_radius: float, outer_radius: float, n_flares: int):
        star: list[Vec2] = []
        d_theta = (2.0 * 3.14159) / (n_flares * 2)

        for i in range(n_flares * 2):
            rad = outer_radius if (i % 2 == 0) else inner_radius
            star.append(
                Vec2(rad * cos(i * d_theta),  rad * sin(i * d_theta))
            )

        return star

    @staticmethod
    def BoundingBox(inner_radius: float, outer_radius: float, position: Vec2) -> Rect:
        wh = max(outer_radius, inner_radius) * 2
        return Rect.FromWH(position, wh, wh)

    @staticmethod
    def GetRandParams() -> tuple[int, int, int]:
        rad_min = 10
        rad_max = 100
        n_flares_min = 2
        n_flares_max = 8

        return (randint(rad_min, rad_max), randint(rad_min, rad_max), randint(n_flares_min, n_flares_max))

    @staticmethod
    def GetRandPos() -> Vec2:
        x_min = -1000
        x_max = 1000
        y_min = -1000
        y_max = 1000

        return Vec2(randint(x_min, x_max), randint(y_min, y_max))

class PolylinesScene(Scene):
    def __init__(self):
        super().__init__()
        self.entities = PolylinesScene.GenerateEntities()

    def CompsSetupComplete(self): ...

    @staticmethod
    def GenerateEntities():
        entities: list[Entity] = []
        stars: list[Star] = []
        n_max_stars = 100
        max_reject_count = 100
        reject_count = 0
        while n_max_stars > len(stars):
            new_star = Star(*Star.GetRandParams(), Star.GetRandPos())

            rejected = False
            for old_star in stars:
                if (old_star.GetPosition() - new_star.GetPosition()).Len() < (old_star.GetRadius() + new_star.GetRadius()):
                    reject_count += 1
                    rejected = True

            if not rejected:
                stars.append(new_star)
                reject_count = 0
            elif reject_count > max_reject_count:
                break

        for star in stars:
            entities.append(star)

        return entities

    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float):
        m_x = mouse_stat[0][0]
        m_y = mouse_stat[0][1]
        m_lb = mouse_stat[1]
        m_rb = mouse_stat[2]

        speed = 10.0

        if 'w' == key: self.camera.MoveBy(Vec2(0.0, speed))
        elif 's' == key: self.camera.MoveBy(Vec2(0.0, -speed))
        elif 'd' == key: self.camera.MoveBy(Vec2(speed, 0.0))
        elif 'a' == key: self.camera.MoveBy(Vec2(-speed, 0.0))

        elif 'q' == key: self.camera.Zoom(0.95)
        elif 'e' == key: self.camera.Zoom(1.05)
    
    def Draw(self):
        vp_rect = self.camera.GetViewportRect()
        for entity in self.entities:
            if vp_rect.Intersects(entity.GetBoundingBox()):
                self.camera.Draw(entity.GetDrawable())
