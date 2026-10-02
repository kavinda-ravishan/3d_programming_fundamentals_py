from typing import Union
from Utils import Vec2, Scene

class SimpleSence(Scene):
    def __init__(self):
        super().__init__()

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float): ...

    def Draw(self): ...
