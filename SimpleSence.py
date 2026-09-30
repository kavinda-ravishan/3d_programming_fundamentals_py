from typing import Union
from math import cos, sin, pi
from random import randint
from Utils import Vec2, Vec3, Mat3, Rect, Color, Scene, Entity

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

class SimpleSence(Scene):
    def __init__(self):
        super().__init__()

    def CompsSetupComplete(self): ...

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float): ...

    def Draw(self):
        camera = self.camera
        if camera is None:
            raise Exception("Camera is not initialized for this scene.")

        star = Star(50.0, 100.0, 5, Vec2(0, 0), Color.Yellow)
        
        entity: Entity = star

        t_scale = Mat3.Scale(2.0)
        t_flip = Mat3.FlipY()
        t_rot = Mat3.Rotation(pi/2)
        t_trans = Mat3.Translation(200, 200)

        #     t_cat apply from -----------------------
        #                                            |
        #                                            \/
        #     t_cat = to here <-------------------- here
        t_cat: Mat3 = t_rot * t_trans * t_scale * t_flip
        # flip -> scale -> trans -> rot

        for i, v in enumerate(entity.model):
            new_v: Vec3 = t_cat * Vec3.FromVec2(v)
            entity.model[i] = Vec2.FromVec3(new_v)

        camera.Draw(entity.GetDrawable())
