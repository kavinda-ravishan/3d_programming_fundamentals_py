from typing import Union
from Utils import Vec2, Vec3, Scene, PC3Transformer, Cube, Color

class SimpleSence(Scene):
    def __init__(self):
        super().__init__()

    def SetupComplete(self):
        if not hasattr(self, 'gfx'):
            raise Exception("Graphics not found")

        self.pc3: PC3Transformer = PC3Transformer(self.gfx.surface.GetFrameWidth(), self.gfx.surface.GetFrameHeight())
        self.cube: Cube = Cube()

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float): ...

    def Draw(self):
        if not hasattr(self, 'gfx'):
            return

        if not hasattr(self, 'pc3'):
            return

        if not hasattr(self, 'cube'):
            return

        lines = self.cube.GetLines()
        for i, v in enumerate(lines.vertices):
            lines.vertices[i] = v + Vec3(0.0, 0.0, 1.0)
            self.pc3.Transform(lines.vertices[i])

        for line in lines.indices:
            v0 = lines.vertices[line[0]]
            v1 = lines.vertices[line[1]]
            self.gfx.DrawLineVec(v0, v1, Color.White)
        