from typing import Union, Final
from math import pi
from Utils import Vec2, Vec3, Mat3, WrapAngle
from Engine import Pipeline, Scene
from Models import Cube
from Effects import TextureEffect

class SceneTextureCube(Scene):
    def __init__(self):
        super().__init__()
        self.it_list = Cube.GetSkinned(
            lambda vertices, texture_coordinates: [TextureEffect.Vertex(position, texture_coordinates[i]) for i, position in enumerate(vertices)]
        )
        self.d_thete: Final[float] = pi
        self.offset_z: float = 2.0
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
            self.offset_z += (2.0 * dt)
        elif 'f' == key:
            self.offset_z -= (2.0 * dt)

    def Draw(self):
        if not hasattr(self, 'gfx'): return
        if not hasattr(self, 'pipeline'): return

        self.pipeline.BeginFrame()

        rotation_matrix: Final[Mat3] = Mat3.RotationX(self.theta_x) * Mat3.RotationY(self.theta_y) * Mat3.RotationZ(self.theta_z)
        translation: Final[Vec3] = Vec3(0.0, 0.0, self.offset_z)
    
    	# set pipeline transform
        self.pipeline.effect.vs.BindRotation(rotation_matrix)
        self.pipeline.effect.vs.BindTranslation(translation)

        self.pipeline.Draw(self.it_list)
    