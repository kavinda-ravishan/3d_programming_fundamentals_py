from typing import Union, Final
from math import pi
from Utils import Vec2, Vec3, Mat4, WrapAngle
from Engine import Pipeline, Scene
from Models import Sphere
from Models import Cube
from Effects import SceneSpecularPhongPointEffect, SolidEffect

class SceneSpecularPhongPoint(Scene):
    def __init__(self):
        super().__init__()
        self.it_list = Cube.GetPlainIndependentFaces(
            lambda vertices, normals: [SceneSpecularPhongPointEffect.Vertex(position.ToVec4(), normals[i].ToVec4()) for i, position in enumerate(vertices)]
        )
        self.light_indicator = Sphere.GetPlain(
            lambda vertices, _: [SolidEffect.Vertex(position.ToVec4()) for position in vertices], 0.05
        )
        
        self.d_thete: Final[float] = pi
        self.offset_z: float = 2.0
        self.theta_x: float = 0.0
        self.theta_y: float = 0.0
        self.theta_z: float = 0.0

        self.lpos_x: float = 0.0
        self.lpos_y: float = 0.0
        self.lpos_z: float = 0.6

    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")
        effect = SceneSpecularPhongPointEffect[SceneSpecularPhongPointEffect.Vertex]()
        self.pipeline = Pipeline[SceneSpecularPhongPointEffect.Vertex](self.gfx, effect)
        
        effect = SolidEffect[SolidEffect.Vertex]()
        self.li_pipeline = Pipeline[SolidEffect.Vertex](self.gfx, effect, self.pipeline.GetZBuffer())

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
        
        elif 'u' == key:
            self.lpos_x += (2.0 * dt)
        elif 'i' == key:
            self.lpos_x -= (2.0 * dt)
        elif 'o' == key:
            self.lpos_y += (2.0 * dt)
        elif 'j' == key:
            self.lpos_y -= (2.0 * dt)
        elif 'k' == key:
            self.lpos_z += (2.0 * dt)
        elif 'l' == key:
            self.lpos_z -= (2.0 * dt)

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pipeline'): return

        self.pipeline.BeginFrame()

        # draw mobile cube
        rotation_matrix: Final[Mat4] = Mat4.RotationX(self.theta_x) * Mat4.RotationY(self.theta_y) * Mat4.RotationZ(self.theta_z)
        translation: Final[Mat4] = Mat4.Translation(0.0, 0.0, self.offset_z)
        transformation_matrix: Final[Mat4] = rotation_matrix * translation
        
        light_position: Final[Vec3] = Vec3(self.lpos_x, self.lpos_y, self.lpos_z)
        transformation_matrix_light_position: Final[Mat4] = Mat4.TranslationVec(light_position)
    
    	# set pipeline transform
        self.pipeline.effect.vs.BindTransformation(transformation_matrix)
        self.pipeline.effect.ps.SetLightPosition(light_position)

        self.pipeline.Draw(self.it_list)

        # draw light indicator with different pipeline
        # don't call beginframe on this pipeline b/c wanna keep zbuffer contents
        # (don't like this assymetry but we'll live with it for now)
        self.li_pipeline.effect.vs.BindTransformation(transformation_matrix_light_position)
        self.li_pipeline.Draw(self.light_indicator)
