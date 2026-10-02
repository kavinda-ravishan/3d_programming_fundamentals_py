from abc import ABC, abstractmethod
from typing import Any, Union, Final
from copy import deepcopy
import cv2
import numpy as np

class Vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def FromVec2(cls, vec: "Vec2"):
        cls(vec.x, vec.y)

    def __repr__(self):
        return f"Vec2({self.x:.3f}, {self.y:.3f})"

    def __setattr__(self, name: str, value: float):
        if name in {"x", "y"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

    def __add__(self, other: Union["Vec2", int, float]):
        if isinstance(other, Vec2):
            return Vec2(self.x + other.x, self.y + other.y)
        else:
            return Vec2(self.x + other, self.y + other)

    def dot(self, other: "Vec2"):
        return (self.x * other.x) + (self.y * other.y)

class Vec3(Vec2):
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        super().__init__(x, y)
        self.z = float(z)

    @classmethod
    def FromVec3(cls, vec: "Vec3"):
        return cls(vec.x, vec.y, vec.z)

    def __repr__(self):
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    def __setattr__(self, name: str, value: float):
        if name in {"x", "y", "z"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

    def __add__(self, other: Union["Vec2", "Vec3", int, float]):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, Vec2):
            raise TypeError("Vec3 addition does not support Vec2 operands; use Vec3 instead.")
        else:
            return Vec3(self.x + other, self.y + other, self.z + other)

    def dot(self, other: Union[Vec2, "Vec3"]):
        if isinstance(other, Vec3):
            return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)
        else:
            raise TypeError("Vec3.dot() requires a Vec3 instance.")

class Color:
    White: "Color"
    Black: "Color"
    Gray: "Color"
    LightGray: "Color"
    Red: "Color"
    Green: "Color"
    Blue: "Color"
    Yellow: "Color"
    Cyan: "Color"
    Magenta: "Color"

    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    def __repr__(self):
        return f"Color(R: {self.r}, G: {self.g}, B: {self.b})"

    def __setattr__(self, name: str, value: int):
        if name in {"r", "g", "b"}:
            super().__setattr__(name, int(value))
        else:
            super().__setattr__(name, value)

Color.White = Color(255, 255, 255)
Color.Black = Color(0, 0, 0)
Color.Gray = Color(0x80, 0x80, 0x80)
Color.LightGray = Color(0xD3, 0xD3, 0xD3)
Color.Red = Color(255, 0, 0)
Color.Green = Color(0, 255, 0)
Color.Blue = Color(0, 0, 255)
Color.Yellow = Color(255, 255, 0)
Color.Cyan = Color(0, 255, 255)
Color.Magenta = Color(255, 0, 255)

# PC3 : Pre-cliped 3D space
class PC3Transformer:
    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.x_factor: Final[float] = screen_width / 2
        self.y_factor: Final[float] = screen_height / 2

    def Transform(self, vec: Vec3):
        vec.x = (vec.x + 1.0) * self.x_factor
        vec.y = (-vec.y + 1.0) * self.y_factor
        return vec

    def GetTransformed(self, vec: Vec3):
        return self.Transform(Vec3.FromVec3(vec))

class IndexedLineList:
    def __init__(self, vertices: list[Vec3], indices: list[tuple[int, int]]) -> None:
        self.vertices: Final[list[Vec3]] = vertices
        self.indices: Final[list[tuple[int, int]]] = indices

class Cube:
    def __init__(self, size: float = 1.0) -> None:
        self.vertices: list[Vec3] = []

        side: Final[float] = size / 2.0
        self.vertices.append( Vec3(-side,-side,-side) )
        self.vertices.append( Vec3(side,-side,-side) )
        self.vertices.append( Vec3(-side,side,-side) )
        self.vertices.append( Vec3(side,side,-side) )
        self.vertices.append( Vec3(-side,-side,side) )
        self.vertices.append( Vec3(side,-side,side) )
        self.vertices.append( Vec3(-side,side,side) )
        self.vertices.append( Vec3(side,side,side) )

    def GetLines(self) -> IndexedLineList:
        return IndexedLineList( 
            deepcopy(self.vertices), [
                (0,1), (1,3), (3,2), (2,0),
                (0,4), (1,5), (3,7), (2,6),
                (4,5), (5,7), (7,6), (6,4)
            ]
        )

class Surface:
    def __init__(self, width: int, height: int):
        self.width: Final[int] = width
        self.height: Final[int] = height
        self.canvas = np.zeros((self.height, self.width, 3), dtype="uint8")

    def GetCanvas(self):
        return self.canvas

    def Clear(self):
        self.canvas = np.zeros_like(self.canvas)

    def PutPixel(self, x: int, y: int, color: Color):
        if(x >=0 and y >= 0 and x < self.width and y < self.height):
            self.canvas[int(y),int(x)] = (color.b, color.g, color.r)

    def GetFrameWidth(self): return self.width
    def GetFrameHeight(self): return self.height

class Mouse:
    def __init__(self):
        self.pos = Vec2(0, 0)
        self.lb_down = False
        self.rb_down = False

    def Callback(self, event: int, x: int, y: int, flags: Any , param: Any):
        if event == cv2.EVENT_MOUSEMOVE:
            self.pos = Vec2(x, y)
            
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.lb_down = True

        elif event == cv2.EVENT_LBUTTONUP:
            self.lb_down = False

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.rb_down = True

        elif event == cv2.EVENT_RBUTTONUP:
            self.rb_down = False
    
    # out: (pos, lb down, rb down)
    def GetState(self) -> tuple[Vec2, bool, bool]:
        return self.pos, self.lb_down, self.rb_down
        
class Keyboard:
    def __init__(self):
        self.key: Union[str, None] = None
        # Map special non-printable keys
        self.special_keys: Final[dict[int, str]] = {
            27: "esc",
            32: "space",
            13: "enter",
            9: "tab",
            8: "backspace"
        }

    def Callback(self, key_code: int):
        if key_code != 255:  # 255 means no key was pressed
            self.key = self.special_keys.get(key_code, chr(key_code) if 32 < key_code < 127 else f"unknown({key_code})")

    def GetKey(self):
        key = self.key
        self.key = None
        return key

class Graphics:
    def __init__(self, window_name: str, frame_width: int, frame_height: int, delay: int):

        self.delay: Final[int] = delay
        self.mouse: Final[Mouse] = Mouse()
        self.keyboard: Final[Keyboard] = Keyboard()
        self.window_name: Final[str] = window_name
        self.surface: Final[Surface] = Surface(frame_width, frame_height)

        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse.Callback)

    def __del__(self):
        cv2.destroyAllWindows()

    def BeginFrame(self):
        self.ClearFrame()

    def EndFrame(self):
        cv2.imshow(self.window_name, self.surface.GetCanvas())

    def ClearFrame(self):
        self.surface.Clear()

    def PutPixel(self, x: int, y: int, color: Color):
        self.surface.PutPixel(x, y, color)

    def Wait(self):
        status_code = cv2.waitKey(self.delay)
        key_code = status_code & 0xFF
        self.keyboard.Callback(key_code)

    def GetKey(self):
        return self.keyboard.GetKey()

    def GetMouseState(self):
        return self.mouse.GetState()

    def DrawLineVec(self, p0: Vec2, p1: Vec2, color: Color):
        self.DrawLineXY(p0.x, p0.y, p1.x, p1.y, color)

    # Bresenham's Line Algorithm
    def DrawLineXY(self, x1: float, y1: float, x2: float, y2: float, color: Color):
        dx = x2 - x1
        dy = y2 - y1

        if dy == 0.0 and dx == 0.0:
            self.PutPixel(int(x1), int(y1), color)
        elif abs(dy) > abs(dx):
            if (dy < 0.0):
                x1, x2 = x2, x1
                y1, y2 = y2, y1

            m = dx / dy
            last_int_y = 0
            y = y1
            x = x1
            while y < y2:

                last_int_y = int(y)
                self.PutPixel(int(x), last_int_y, color)

                x += m
                y += 1
                
            if int(y2) > last_int_y:
                self.PutPixel(int(x2), int(y2), color)
        else:
            if dx < 0.0:
                x1, x2 = x2, x1
                y1, y2 = y2, y1

            m = dy / dx
            last_int_x = 0
            x = x1
            y = y1
            while x < x2:

                last_int_x = int(x);
                self.PutPixel(last_int_x, int(y), color);

                y += m
                x += 1
            
            if int(x2) > last_int_x:
                self.PutPixel(int(x2), int(y2), color);

class Scene(ABC):
    def __init__(self): ...

    def Setup(self, gfx: Graphics):
        self.gfx = gfx
        self.SetupComplete()

    @abstractmethod
    def SetupComplete(self): ...

    @abstractmethod
    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float): pass

    @abstractmethod
    def Draw(self): pass

class Game:
    def __init__(self, frame_width: int, frame_height: int, fps: float, scenes : list[Scene]):
        self.main_loop_active: bool = True
        window_name: Final[str] = "Canvas"
        self.dt: Final[float] = 1.0 / fps
        time_per_frame_ms: Final[float] = self.dt * 1000
        self.gfx: Final[Graphics] = Graphics(window_name, frame_width, frame_height, int(time_per_frame_ms))

        self.c_scene_id = 0
        self.scenes = scenes
        for scene in scenes:
            scene.Setup(self.gfx)

    def UpdateModel(self):
        key = self.gfx.GetKey()
        mouse_stat = self.gfx.GetMouseState()

        self.scenes[self.c_scene_id].Update(key, mouse_stat, self.dt)
        self.ManageInputs(key)

    def ComposeFrame(self):
        self.scenes[self.c_scene_id].Draw()

    def ManageInputs(self, key: Union[str, None]):
            if key == 'esc':
                self.main_loop_active = False
            elif key == 'tab':
                self.c_scene_id = (self.c_scene_id + 1)%len(self.scenes)

    def Go(self):
        print("Game loop started")
        while self.main_loop_active:
            self.gfx.BeginFrame()

            self.ComposeFrame()

            self.gfx.EndFrame()
            self.gfx.Wait()

            self.UpdateModel()

        print("Game loop ended")
