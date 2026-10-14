from typing import Union, Final
from math import pi
from Utils import Vec2, Vec3, Vec4, Mat4, WrapAngle
from Engine import Pipeline, Scene
from Models import Sphere
from Models import Cube
from Effects import SceneSpecularPhongPointEffect, SolidEffect

class SceneSpecularPhongPoint(Scene):
    def __init__(self):
        super().__init__()
        self.it_list = Cube.GetPlainIndependentFaces(
            lambda vertices, normals: [SceneSpecularPhongPointEffect.Vertex(position.ToVec4(), normals[i]) for i, position in enumerate(vertices)]
        )
        self.light_indicator = Sphere.GetPlain(
            lambda vertices, _: [SolidEffect.Vertex(position.ToVec4()) for position in vertices], 0.05
        )

        # self.proj: Final[Mat4] = Mat4.Projection(2.6666666, 2.0, 1.0, 10.0)
        self.proj = Mat4.ProjectionHFOV(100.0, 1.33333, 1.0, 10.0)
        
        self.d_thete: Final[float] = pi
        self.d_speed: Final[float] = 2.0

        self.cam_rot_inv: Mat4 = Mat4.Identity()
        self.cam_pos: Vec3 = Vec3(0.0, 0.0, 0.0)

        self.mod_pos: Vec3 = Vec3(0.0, 0.0, 2.2)

        self.theta_x: float = 0.0
        self.theta_y: float = 0.0
        self.theta_z: float = 0.0

        self.lpos: Vec3 = Vec3(0.0, 0.0, 1.1)

    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")
        effect = SceneSpecularPhongPointEffect[SceneSpecularPhongPointEffect.Vertex]()
        self.pipeline = Pipeline[SceneSpecularPhongPointEffect.Vertex](self.gfx, effect)
        
        effect = SolidEffect[SolidEffect.Vertex]()
        self.li_pipeline = Pipeline[SolidEffect.Vertex](self.gfx, effect, self.pipeline.GetZBuffer())

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float):
        # m_c = mouse_stat[0]
        m_lb = mouse_stat[1]
        # m_rb = mouse_stat[2]

        if not m_lb:
            if 'w' == key:
                self.cam_pos += (Vec4(0, 1, 0, 0) * self.cam_rot_inv.Inv()).ToVec3() * self.d_thete * dt
            elif 's' == key:
                self.cam_pos += (Vec4(0, -1, 0, 0) * self.cam_rot_inv.Inv()).ToVec3() * self.d_thete * dt
            elif 'a' == key:
                self.cam_pos += (Vec4(-1, 0, 0, 0) * self.cam_rot_inv.Inv()).ToVec3() * self.d_thete * dt
            elif 'd' == key:
                self.cam_pos += (Vec4(1, 0, 0, 0) * self.cam_rot_inv.Inv()).ToVec3() * self.d_thete * dt
            elif 'q' == key:
                self.cam_pos += (Vec4(0, 0, -1, 0) * self.cam_rot_inv.Inv()).ToVec3() * self.d_thete * dt
            elif 'e' == key:
                self.cam_pos += (Vec4(0, 0, 1, 0) * self.cam_rot_inv.Inv()).ToVec3() * self.d_thete * dt

            elif 'i' == key:
                self.cam_rot_inv = self.cam_rot_inv * Mat4.RotationX((self.d_thete * dt))
            elif 'k' == key:
                self.cam_rot_inv = self.cam_rot_inv * Mat4.RotationX(-(self.d_thete * dt))
            elif 'j' == key:
                self.cam_rot_inv = self.cam_rot_inv * Mat4.RotationY((self.d_thete * dt))
            elif 'l' == key:
                self.cam_rot_inv = self.cam_rot_inv * Mat4.RotationY(-(self.d_thete * dt))
            elif 'u' == key:
                self.cam_rot_inv = self.cam_rot_inv * Mat4.RotationZ((self.d_thete * dt))
            elif 'o' == key:
                self.cam_rot_inv = self.cam_rot_inv * Mat4.RotationZ(-(self.d_thete * dt))
        else:
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
            
            elif 'u' == key:
                self.lpos.x += (self.d_thete * dt)
            elif 'i' == key:
                self.lpos.x -= (self.d_thete * dt)
            elif 'o' == key:
                self.lpos.y += (self.d_thete * dt)
            elif 'j' == key:
                self.lpos.y -= (self.d_thete * dt)
            elif 'k' == key:
                self.lpos.z += (self.d_thete * dt)
            elif 'l' == key:
                self.lpos.z -= (self.d_thete * dt)

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pipeline'): return

        self.pipeline.BeginFrame()

        # camera
        view: Final[Mat4] = Mat4.TranslationVec(-self.cam_pos) * self.cam_rot_inv

        # draw mobile cube
        rotation_matrix: Final[Mat4] = Mat4.RotationX(self.theta_x) * Mat4.RotationY(self.theta_y) * Mat4.RotationZ(self.theta_z)
        translation: Final[Mat4] = Mat4.TranslationVec(self.mod_pos)
        transformation_matrix: Final[Mat4] = rotation_matrix * translation

        # light indicator
        transformation_matrix_light_position: Final[Mat4] = Mat4.TranslationVec(self.lpos)
    
    	# set pipeline transform
        self.pipeline.effect.vs.BindWorldView(transformation_matrix * view)
        self.pipeline.effect.vs.BindProjection(self.proj)
        self.pipeline.effect.ps.SetLightPosition((self.lpos.ToVec4(1.0) * view).ToVec3())

        self.pipeline.Draw(self.it_list)

        # draw light indicator with different pipeline
        # don't call beginframe on this pipeline b/c wanna keep zbuffer contents
        # (don't like this assymetry but we'll live with it for now)
        self.li_pipeline.effect.vs.BindWorldView(transformation_matrix_light_position * view)
        self.li_pipeline.effect.vs.BindProjection(self.proj)
        self.li_pipeline.Draw(self.light_indicator)
