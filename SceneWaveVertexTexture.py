from typing import Union, Final
from math import pi
from Utils import Vec2, Vec3, Mat3, WrapAngle
from Engine import Pipeline, Scene
from Models import Plain
from Effects import WaveVertexTextureEffec

class SceneWaveVertexTexture(Scene):
    def __init__(self):
        super().__init__()
        self.it_list = Plain.GetPlain(
            lambda vertices, texture_coordinates: [WaveVertexTextureEffec.Vertex(position, texture_coordinates[i]) for i, position in enumerate(vertices)], 
            20
        )
        self.d_thete: Final[float] = pi
        self.offset_z: float = 1.1666666666666674
        self.theta_x: float = 1.0471975511965976
        self.theta_y: float = 0.13089969389957476
        self.theta_z: float = 0.0

        self.light_dir: Final[Vec3] = Vec3(0.2, -0.5, 1.0)
        self.phi_x: float = 5.8904862254808625
        self.phi_y: float =  0.7853981633974483
        self.phi_z: float = 0.0
        self.time: float = 0.0

    def SetupComplete(self):
        if not hasattr(self, 'gfx'): raise Exception("Graphics not found")
        effect = WaveVertexTextureEffec[WaveVertexTextureEffec.Vertex]()
        effect.ps.BindTexture("./images/sauron.png")
        self.pipeline: Pipeline[WaveVertexTextureEffec.Vertex] = Pipeline(self.gfx, effect)

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
            self.phi_x = WrapAngle(self.phi_x + (self.d_thete * dt))
        elif 'i' == key:
            self.phi_y = WrapAngle(self.phi_y + (self.d_thete * dt))
        elif 'o' == key:
            self.phi_z = WrapAngle(self.phi_z + (self.d_thete * dt))
        elif 'j' == key:
            self.phi_x = WrapAngle(self.phi_x - (self.d_thete * dt))
        elif 'k' == key:
            self.phi_y = WrapAngle(self.phi_y - (self.d_thete * dt))
        elif 'l' == key:
            self.phi_z = WrapAngle(self.phi_z - (self.d_thete * dt))

        self.time += dt

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pipeline'): return

        self.pipeline.BeginFrame()

        rotation_matrix: Final[Mat3] = Mat3.RotationX(self.theta_x) * Mat3.RotationY(self.theta_y) * Mat3.RotationZ(self.theta_z)
        rot_phi: Final[Mat3] = Mat3.RotationX(self.phi_x) * Mat3.RotationY(self.phi_y) * Mat3.RotationZ(self.phi_z)
        translation: Final[Vec3] = Vec3(0.0, 0.0, self.offset_z)
    
    	# set pipeline transform
        self.pipeline.effect.vs.BindRotation(rotation_matrix)
        self.pipeline.effect.vs.BindTranslation(translation)
        self.pipeline.effect.vs.SetTime(self.time)
        self.pipeline.effect.gs.SetLightDirection(self.light_dir * rot_phi)

        self.pipeline.Draw(self.it_list)
    