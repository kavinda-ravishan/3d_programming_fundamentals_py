from typing import Union, Final, cast
from copy import deepcopy
from math import pi
from Utils import Vec2, Vec3, Mat3, Scene, PC3Transformer, Cube, Color, WrapAngle, Surface, TextureVertex

class TextureCubeScene(Scene):
    def __init__(self):
        super().__init__()
        self.cube: Final[Cube] = Cube(1.0)
        self.texture: Final[Surface] = Surface.FromFile( "./images/sauron.png" )
        self.d_thete: Final[float] = pi
        self.offset_z: float = 2.0
        self.theta_x: float = 0.0
        self.theta_y: float = 0.0
        self.theta_z: float = 0.0

        self.colors: Final[list[Color]] = [
            Color.White,
            Color.Blue,
            Color.Cyan,
            Color.Gray,
            Color.Green,
            Color.Magenta,
            Color.LightGray,
            Color.Red,
            Color.Yellow,
            Color.White,
            Color.Blue,
            Color.Cyan
        ]

    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")
        self.pc3: PC3Transformer = PC3Transformer(self.gfx.surface.GetWidth(), self.gfx.surface.GetHeight())

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
        if not hasattr(self, 'pc3'): return

        triangles = deepcopy(self.cube.GetTrianglesTex())

        rotation_matrix: Final[Mat3] = Mat3.RotationX(self.theta_x) * Mat3.RotationY(self.theta_y) * Mat3.RotationZ(self.theta_z)

        # =============================== CUBE ===============================
        # transform from model space -> world (/view) space
        vertices: list[TextureVertex] = cast(list[TextureVertex], triangles.vertices)

        for i, _ in enumerate(vertices):
            vertices[i].pos = vertices[i].pos * rotation_matrix
            vertices[i].pos = vertices[i].pos + Vec3(0.0, 0.0, self.offset_z)

        # backface culling test
        for i, triangle in enumerate(triangles.indices):
            v0 = vertices[triangle[0]].pos
            v1 = vertices[triangle[1]].pos
            v2 = vertices[triangle[2]].pos
            triangles.cull_flag[i] = (v1 - v0).Cross(v2 - v0).Dot(v0) >= 0.0
        
        # transform from world (/view) space -> screen space
        for i, _ in enumerate(vertices):
            self.pc3.Transform(vertices[i].pos)

        for i, triangle in enumerate(triangles.indices):

            if not triangles.cull_flag[i]:
                v0 = vertices[triangle[0]]
                v1 = vertices[triangle[1]]
                v2 = vertices[triangle[2]]
                self.gfx.DrawTriangleTex(v0, v1, v2, self.texture)
