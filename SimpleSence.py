from typing import Union, Final
from copy import deepcopy
from math import pi
from Utils import Vec2, Vec3, Mat3, Scene, PC3Transformer, Cube, Color, WrapAngle

class SimpleSence(Scene):
    def __init__(self):
        super().__init__()
        self.cube: Final[Cube] = Cube()
        self.d_thete: Final[float] = pi
        self.theta_x: float = 0.0
        self.theta_y: float = 0.0
        self.theta_z: float = 0.0

    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")
        self.pc3: PC3Transformer = PC3Transformer(self.gfx.surface.GetFrameWidth(), self.gfx.surface.GetFrameHeight())

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

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pc3'): return

        lines = deepcopy(self.cube.GetLines())

        rotation_matrix: Final[Mat3] = Mat3.RotationX(self.theta_x) * Mat3.RotationY(self.theta_y) * Mat3.RotationZ(self.theta_z)

        for i, _ in enumerate(lines.vertices):
            lines.vertices[i] = lines.vertices[i] * rotation_matrix
            lines.vertices[i] = lines.vertices[i] + Vec3(0.0, 0.0, 1.0)
            self.pc3.Transform(lines.vertices[i])

        for line in lines.indices:
            v0 = lines.vertices[line[0]]
            v1 = lines.vertices[line[1]]
            self.gfx.DrawLineVec(v0, v1, Color.White)
        