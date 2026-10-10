from typing import Union, Final
from math import pi
from Utils import Vec2, Mat4, Color, WrapAngle
from Engine import Pipeline, Scene
from Models import Cube
from Effects import SolidEffect

class SceneSolidCubes(Scene):
    def __init__(self):
        super().__init__()
        self.it_list = Cube.GetPlain(lambda vertices: [SolidEffect.Vertex(position.ToVec4()) for _, position in enumerate(vertices)])
        self.d_thete: Final[float] = pi
        self.offset_z: float = 2.0
        self.theta_x: float = 0.0
        self.theta_y: float = 0.0
        self.theta_z: float = 0.0


    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")

        colors: Final[list[Color]] = [
            Color.Red,
            Color.Green,
            Color.Blue,
            Color.Yellow,
            Color.Cyan,
            Color.Magenta
        ]

        effect = SolidEffect[SolidEffect.Vertex]()
        effect.gs.BindColors(colors)

        self.pipeline = Pipeline[SolidEffect.Vertex](self.gfx, effect)

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float):
        # m_c = mouse_stat[0]
        # m_lb = mouse_stat[1]
        # m_rb = mouse_stat[2]

        if 'q' == key:
            self.theta_x = WrapAngle(self.theta_x + (self.d_thete * dt))
        elif 'w' == key:
            self.theta_y = WrapAngle(self.theta_y + (self.d_thete * dt))
        elif 'e' == key:
            self.theta_z = WrapAngle(self.theta_z + (self.d_thete * dt))
        elif 'a' == key:
            self.theta_x = WrapAngle(self.theta_x - (self.d_thete * dt))
        elif 's' == key:
            self.theta_y = WrapAngle(self.theta_y - (self.d_thete * dt))
        elif 'd' == key:
            self.theta_z = WrapAngle(self.theta_z - (self.d_thete * dt))
        elif 'r' == key:
            self.offset_z += (2.0 * dt)
        elif 'f' == key:
            self.offset_z -= (2.0 * dt)

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pipeline'): return

        self.pipeline.BeginFrame()

        # draw fixed cube
        rotation_matrix__fix: Final[Mat4] = Mat4.RotationX(-self.theta_x) * Mat4.RotationY(-self.theta_y) * Mat4.RotationZ(-self.theta_z)
        translation_fix: Final[Mat4] = Mat4.Translation(0.0, 0.0, 2.0)
        
        # set pipeline transform
        self.pipeline.effect.vs.BindTransformation(rotation_matrix__fix * translation_fix)

        self.pipeline.Draw(self.it_list)


        # draw mobile cube
        rotation_matrix: Final[Mat4] = Mat4.RotationX(self.theta_x) * Mat4.RotationY(self.theta_y) * Mat4.RotationZ(self.theta_z)
        translation: Final[Mat4] = Mat4.Translation(0.0, 0.0, self.offset_z)
    
    	# set pipeline transform
        self.pipeline.effect.vs.BindTransformation(rotation_matrix * translation)

        self.pipeline.Draw(self.it_list)
