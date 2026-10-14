from typing import Union, Final
from math import pi
from Utils import Vec2, Vec3, Mat4, WrapAngle
from Engine import Pipeline, Scene
from Models import Cube
from Effects import TextureEffect

class SceneTextureCube(Scene):
    def __init__(self):
        super().__init__()
        self.it_list = Cube.GetSkinned(
            lambda vertices, texture_coordinates: [TextureEffect.Vertex(position.ToVec4(), texture_coordinates[i]) for i, position in enumerate(vertices)]
        )

        self.proj: Final[Mat4] = Mat4.ProjectionHFOV(100.0, 1.33333, 1.0, 10.0)

        self.d_thete: Final[float] = pi

        self.cam_rot_inv: Mat4 = Mat4.Identity()
        self.cam_pos: Vec3 = Vec3(0.0, 0.0, 0.0)

        self.mod_pos: Vec3 = Vec3(0.0, 0.0, 2.2)
        
        self.theta_x: float = 0.0
        self.theta_y: float = 0.0
        self.theta_z: float = 0.0

    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")
        effect = TextureEffect[TextureEffect.Vertex]()
        effect.ps.BindTexture("./images/office_skin.jpg")
        self.pipeline: Pipeline[TextureEffect.Vertex] = Pipeline(self.gfx, effect)

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
            self.mod_pos.z += (self.d_thete * dt)
        elif 'f' == key:
            self.mod_pos.z -= (self.d_thete * dt)

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pipeline'): return

        self.pipeline.BeginFrame()

        # camera
        view: Final[Mat4] = Mat4.TranslationVec(-self.cam_pos) * self.cam_rot_inv

        rotation_matrix: Final[Mat4] = Mat4.RotationX(self.theta_x) * Mat4.RotationY(self.theta_y) * Mat4.RotationZ(self.theta_z)
        translation: Final[Mat4] = Mat4.TranslationVec(self.mod_pos)
    
    	# set pipeline transform
        self.pipeline.effect.vs.BindWorldView(rotation_matrix * translation * view)
        self.pipeline.effect.vs.BindProjection(self.proj)

        self.pipeline.Draw(self.it_list)
    