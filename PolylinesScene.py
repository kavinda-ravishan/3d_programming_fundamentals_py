from typing import Union, Final
from math import cos, sin, pi
from random import randint
from Utils import Vec2, Rect, Color, Scene, Entity

class Star(Entity):
    def __init__(self, inner_radius: float, outer_radius: float, n_flares: int, position: Vec2, color: Color):
        super().__init__(
            Star.Make(inner_radius, outer_radius, n_flares), 
            Star.BoundingBox(inner_radius, outer_radius, position), 
            position, 
            color
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
        self.selected_ids: list[int] = []

    def CompsSetupComplete(self): ...

    @staticmethod
    def GenerateEntities():
        entities: list[Entity] = []
        stars: list[Star] = []
        n_max_stars = 100
        max_reject_count = 100
        reject_count = 0
        while n_max_stars > len(stars):
            new_star = Star(*Star.GetRandParams(), Star.GetRandPos(), Color.Yellow)

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

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float):
        m_c: Final[Vec2] = mouse_stat[0]
        m_lb: Final[bool] = mouse_stat[1]
        m_rb: Final[bool] = mouse_stat[2]

        move_speed: Final[float] = 10.0
        rotational_speed: Final[float] = pi/100
        zoom_out_factor: Final[float] = 0.95
        zoom_in_factor: Final[float] = 1.05

        camera = self.camera
        if camera is None:
            raise Exception("Camera is not initialized for this scene.")

        if m_lb:
            m_c_w = camera.ScreenToWorldCoordinate(m_c)
            for i in range(len(self.entities)):
                bbox = self.entities[i].GetBoundingBox()
                if bbox is not None and bbox.PointContain(m_c_w):
                    if i not in self.selected_ids:
                        self.entities[i].SetColor(Color.Red)
                        self.selected_ids.append(i)
        elif m_rb:
            for i in self.selected_ids:
                self.entities[i].SetColor(Color.Yellow)
            self.selected_ids.clear()

        if not self.selected_ids:
            if 'w' == key: camera.MoveBy(Vec2(0.0, move_speed).Rotate(camera.GetAngle()))
            elif 's' == key: camera.MoveBy(Vec2(0.0, -move_speed).Rotate(camera.GetAngle()))
            elif 'd' == key: camera.MoveBy(Vec2(move_speed, 0.0).Rotate(camera.GetAngle()))
            elif 'a' == key: camera.MoveBy(Vec2(-move_speed, 0.0).Rotate(camera.GetAngle()))
            elif 'q' == key: camera.Zoom(zoom_out_factor)
            elif 'e' == key: camera.Zoom(zoom_in_factor)
            elif 'z' == key: camera.RotateBy(rotational_speed)
            elif 'x' == key: camera.RotateBy(-rotational_speed)
        else:
            if 'w' == key:
                for i in self.selected_ids:
                    self.entities[i].TranslateBy(Vec2(0.0, move_speed).Rotate(camera.GetAngle()))
            elif 's' == key:
                for i in self.selected_ids:
                    self.entities[i].TranslateBy(Vec2(0.0, -move_speed).Rotate(camera.GetAngle()))
            elif 'd' == key:
                for i in self.selected_ids:
                    self.entities[i].TranslateBy(Vec2(move_speed, 0.0).Rotate(camera.GetAngle()))
            elif 'a' == key:
                for i in self.selected_ids:
                    self.entities[i].TranslateBy(Vec2(-move_speed, 0.0).Rotate(camera.GetAngle()))
            elif 'q' == key:
                for i in self.selected_ids:
                    self.entities[i].ScaleBy(zoom_out_factor)
            elif 'e' == key:
                for i in self.selected_ids:
                    self.entities[i].ScaleBy(zoom_in_factor)
            elif 'z' == key:
                for i in self.selected_ids:
                    self.entities[i].RotateBy(rotational_speed)
            elif 'x' == key:
                for i in self.selected_ids:
                    self.entities[i].RotateBy(-rotational_speed)

    def Draw(self):
        camera = self.camera
        if camera is None:
            raise Exception("Camera is not initialized for this scene.")

        vp_rect = camera.GetViewportRect()
        for entity in self.entities:
            bbox = entity.GetBoundingBox()
            if bbox is None or vp_rect.Intersects(bbox):
                camera.Draw(entity.GetDrawable())
            
