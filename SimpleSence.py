from typing import Union, Final
from copy import deepcopy
from math import pi
from Utils import Vec2, Vec3, Mat3, Scene, PC3Transformer, Cube, Color, WrapAngle

class SimpleSence(Scene):
    def __init__(self):
        super().__init__()
        self.cube: Final[Cube] = Cube(1.0)
        self.cube_fix: Final[Cube] = Cube(1.0)
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
        elif 'r' == key:
            self.offset_z += (2.0 * dt)
        elif 'f' == key:
            self.offset_z -= (2.0 * dt)

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pc3'): return

        triangles = deepcopy(self.cube.GetTriangles())
        triangles_fix = deepcopy(self.cube_fix.GetTriangles())

        rotation_matrix: Final[Mat3] = Mat3.RotationX(self.theta_x) * Mat3.RotationY(self.theta_y) * Mat3.RotationZ(self.theta_z)
        rotation_matrix__fix: Final[Mat3] = Mat3.RotationX(-self.theta_x) * Mat3.RotationY(-self.theta_y) * Mat3.RotationZ(-self.theta_z)

        # =============================== Fix CUBE ===============================
        # transform from model space -> world (/view) space
        for i, _ in enumerate(triangles_fix.vertices):
            triangles_fix.vertices[i] = triangles_fix.vertices[i] * rotation_matrix__fix
            triangles_fix.vertices[i] = triangles_fix.vertices[i] + Vec3(0.0, 0.0, 2.0)

        # backface culling test
        for i, triangle in enumerate(triangles_fix.indices):
            v0 = triangles_fix.vertices[triangle[0]]
            v1 = triangles_fix.vertices[triangle[1]]
            v2 = triangles_fix.vertices[triangle[2]]
            triangles_fix.cull_flag[i] = (v1 - v0).Cross(v2 - v0).Dot(v0) >= 0.0
        
        # transform from world (/view) space -> screen space
        for i, _ in enumerate(triangles_fix.vertices):
            self.pc3.Transform(triangles_fix.vertices[i])

        for i, triangle in enumerate(triangles_fix.indices):

            if not triangles_fix.cull_flag[i]:
                v0 = triangles_fix.vertices[triangle[0]]
                v1 = triangles_fix.vertices[triangle[1]]
                v2 = triangles_fix.vertices[triangle[2]]
                self.gfx.DrawTriangle(v0, v1, v2, self.colors[i%len(self.colors)])


        # =============================== CUBE ===============================
        # transform from model space -> world (/view) space
        for i, _ in enumerate(triangles.vertices):
            triangles.vertices[i] = triangles.vertices[i] * rotation_matrix
            triangles.vertices[i] = triangles.vertices[i] + Vec3(0.0, 0.0, self.offset_z)

        # backface culling test
        for i, triangle in enumerate(triangles.indices):
            v0 = triangles.vertices[triangle[0]]
            v1 = triangles.vertices[triangle[1]]
            v2 = triangles.vertices[triangle[2]]
            triangles.cull_flag[i] = (v1 - v0).Cross(v2 - v0).Dot(v0) >= 0.0
        
        # transform from world (/view) space -> screen space
        for i, _ in enumerate(triangles.vertices):
            self.pc3.Transform(triangles.vertices[i])

        for i, triangle in enumerate(triangles.indices):

            if not triangles.cull_flag[i]:
                v0 = triangles.vertices[triangle[0]]
                v1 = triangles.vertices[triangle[1]]
                v2 = triangles.vertices[triangle[2]]
                self.gfx.DrawTriangle(v0, v1, v2, self.colors[i%len(self.colors)])
