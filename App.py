from math import cos, sin
from copy import deepcopy
from random import randint
from Utils import Vec2, Rect, Color, Drawable, Game, Scene

class Star:
    def __init__(self, inner_radius: float, outer_radius: float, n_flares: int, pos: Vec2):
        self.inner_radius = float(inner_radius)
        self.outer_radius = float(outer_radius)
        self.n_flares = int(n_flares)
        self.pos = pos

    def GetRadius(self): return self.outer_radius
    def GetPos(self): return self.pos

    def Make(self):
        star: list[Vec2] = []
        d_theta = (2.0 * 3.14159) / (self.n_flares * 2)

        for i in range(self.n_flares * 2):
            rad = self.outer_radius if (i % 2 == 0) else self.inner_radius
            star.append(
                Vec2(rad * cos(i * d_theta),  rad * sin(i * d_theta))
            )

        return star

    def GetBoundingBox(self) -> Rect:
        wh = self.outer_radius * 2
        return Rect.FromWH(self.pos, wh, wh)

    @staticmethod
    def GetRandParams() -> tuple[int, int, int]:
        inner_rad_min = 30
        inner_rad_max = 70
        outer_rad_min = 100
        outer_rad_max = 200
        n_flares_min = 2
        n_flares_max = 8

        return (randint(inner_rad_min, inner_rad_max), randint(outer_rad_min, outer_rad_max), randint(n_flares_min, n_flares_max))

    @staticmethod
    def GetRandPos() -> Vec2:
        x_min = -1000
        x_max = 1000
        y_min = -1000
        y_max = 1000

        return Vec2(randint(x_min, x_max), randint(y_min, y_max))

class Entity:
    def __init__(self, model: list[Vec2], bbox: Rect, position: Vec2, color: Color = Color.Yellow):
        self.model = model
        self.bbox = bbox
        self.pos = position
        self.scale = 1.0
        self.color = color

    def TranslateBy(self, offset: Vec2):
        self.pos += offset

    def ScaleBy(self, val: float):
        self.scale *= val

    def GetBBox(self):
        return self.bbox

    def GetDrawable(self):
        drawable = Drawable(deepcopy(self.model), self.color)
        drawable.Scale(self.scale)
        drawable.Translate(self.pos)
        return drawable

class PolylinesScene(Scene):
    def __init__(self):
        super().__init__()
        self.entities: list[Entity] = []
        stars: list[Star] = []

        n_max_stars = 100
        max_reject_count = 100
        reject_count = 0
        while n_max_stars > len(stars):
            new_star = Star(*Star.GetRandParams(), Star.GetRandPos())

            rejected = False
            for old_star in stars:
                if (old_star.GetPos() - new_star.GetPos()).Len() < (old_star.GetRadius() + new_star.GetRadius()):
                    reject_count += 1
                    rejected = True

            if not rejected:
                stars.append(new_star)
                reject_count = 0
            elif reject_count > max_reject_count:
                break

        for star in stars:
            self.entities.append(Entity(star.Make(), star.GetBoundingBox(), star.GetPos()))

    def CompsSetupComplete(self): ...

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
        draw_count = 0
        for entity in self.entities:
            if entity.GetBBox().Intersects(vp_rect):
                self.camera.Draw(entity.GetDrawable())
                draw_count += 1

        print(draw_count, '/', len(self.entities))

if '__main__' == __name__:
    frame_width = 800
    frame_height = 800
    fps = 60.0

    game = Game(frame_width, frame_height, fps, [PolylinesScene()])
    game.Go()

