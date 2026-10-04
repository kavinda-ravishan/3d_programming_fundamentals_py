from abc import ABC, abstractmethod
from typing import Any, Union, Final, overload
from copy import copy, deepcopy
from math import sin, cos, pi, ceil
import cv2
import numpy as np

def WrapAngle(theta: float) -> float:
    """
    Wraps an angle in radians to the range [0, 2π).
    
    Parameters:
        theta (float): Angle in radians.
    
    Returns:
        float: Wrapped angle in radians.
    """
    return theta % (2 * pi)

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

    def __sub__(self, other: Union["Vec2", int, float]):
        if isinstance(other, Vec2):
            return Vec2(self.x - other.x, self.y - other.y)
        else:
            return Vec2(self.x - other, self.y - other)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __mul__(self, other: Union["Vec2", int, float]) -> Union["Vec2", int, float]:
        if isinstance(other, Vec2): # vec-vec dot product
            return (self.x * other.x) + (self.y * other.y)
        else: # scalar-vec multiplication
            return Vec2(self.x * other, self.y * other)

    def __truediv__(self, other: Union["Vec2", int, float]):
        if isinstance(other, Vec2):
            return Vec2(self.x / other.x, self.y / other.y)
        else:
            return Vec2(self.x / other, self.y / other)

    def dot(self, other: "Vec2"):
        return (self.x * other.x) + (self.y * other.y)

class Vec3:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def FromVec3(cls, vec: "Vec3"):
        return cls(vec.x, vec.y, vec.z)

    def MatMul(self, mat: "Mat3"):
        new_vec = Vec3()
            
        new_vec.x = (mat[0][0] * self.x) + (mat[1][0] * self.y) + (mat[2][0] * self.z)
        new_vec.y = (mat[0][1] * self.x) + (mat[1][1] * self.y) + (mat[2][1] * self.z)
        new_vec.z = (mat[0][2] * self.x) + (mat[1][2] * self.y) + (mat[2][2] * self.z)

        return new_vec

    def VecMul(self, vec: "Vec3"):
        new_vec = Vec3()

        new_vec.x = self.x * vec.x
        new_vec.y = self.y * vec.y
        new_vec.z = self.z * vec.z

        return new_vec

    def ScalerMul(self, scaler: Union[int, float]):
        new_vec = Vec3()

        new_vec.x = self.x * scaler
        new_vec.y = self.y * scaler
        new_vec.z = self.z * scaler

        return new_vec

    def dot(self, other: "Vec3"):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def ToVec2(self):
        return Vec2(self.x, self.y)

    def __repr__(self):
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    def __setattr__(self, name: str, value: float):
        if name in {"x", "y", "z"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

    def __add__(self, other: Union["Vec3", int, float]):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Vec3(self.x + other, self.y + other, self.z + other)

    def __mul__(self, other: Union["Mat3", "Vec3", int, float]) -> "Vec3":
        if isinstance(other, Mat3): # Mat-Mat multiplication
            return self.MatMul(other)
        elif isinstance(other, Vec3): # Mat-vec multiplication
            return self.VecMul(other)
        else: # scalar-Mat multiplication
            return self.ScalerMul(other)

    def __truediv__(self, other: Union["Vec3", int, float]):
        if isinstance(other, Vec3):
            return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            return Vec3(self.x / other, self.y / other, self.z / other)

class Mat3:
    def __init__(self, mat: \
                 tuple[\
                     tuple[Union[int, float], Union[int, float], Union[int, float]], \
                     tuple[Union[int, float], Union[int, float], Union[int, float]], \
                     tuple[Union[int, float], Union[int, float], Union[int, float]], \
                    ] = \
                    ((0, 0, 0), (0, 0, 0), (0, 0, 0))):
        # [row][col]
        self.mat: list[list[Union[int, float]]] = [list(row) for row in mat]

    def __repr__(self) -> str:
        return f"Mat3([\n  {self.mat[0]},\n  {self.mat[1]}\n  {self.mat[2]}\n])"

    def __getitem__(self, idx: int) -> list[Union[int, float]]:
        """Allow access like mat[row][col]."""
        return self.mat[idx]

    def __setitem__(self, idx: int, value: list[Union[int, float]]) -> None:
        """Allow assignment like mat[row] = [..]."""
        if len(value) != 3:
            raise ValueError("Each row must have exactly 3 elements")
        self.mat[idx] = value

    def ScalerMul(self, scaler: Union[int, float]):
        new_mat = Mat3()
        for r, row in enumerate(self.mat):
            for c, val in enumerate(row):
                new_mat.mat[r][c] = scaler * val

        return new_mat

    def MatMul(self, mat: "Mat3"):
        new_mat = Mat3()

        for row_left in range(3):
            for col_rigth in range(3):
                for i in range(3):
                    new_mat.mat[row_left][col_rigth] += self.mat[row_left][i] * mat.mat[i][col_rigth]

        return new_mat

    @overload
    def __mul__(self, other: "Mat3") -> "Mat3": ...

    @overload
    def __mul__(self, other: Vec3) -> Vec3: ...

    @overload
    def __mul__(self, other: Union[int, float]) -> Vec3: ...

    def __mul__(self, other: Union["Mat3", Vec3, int, float]) -> Union[Vec3, "Mat3"]:
        if isinstance(other, Mat3): # Mat-Mat multiplication
            return self.MatMul(other)
        elif isinstance(other, Vec3): # Mat-vec multiplication
            raise TypeError("Mat3 * Vec3 is not supported; Direct3D uses row vectors, so use Vec3 * Mat3 instead.")
        else: # scalar-Mat multiplication
            return self.ScalerMul(other)

    @staticmethod
    def Scale(factor: Union[int, float]):
        return Mat3(
            (
                (factor, 0, 0), 
                (0, factor, 0), 
                (0, 0, factor)
            )
        )

    @staticmethod
    def Identity():
        return Mat3.Scale(1)

    @staticmethod
    def RotationZ(theta: float):
        cos_theta: Final[float] = cos(theta)
        sin_theta: Final[float] = sin(theta)
        return Mat3(
            (
                (cos_theta, -sin_theta, 0.0), 
                (sin_theta, cos_theta,  0.0), 
                (0.0,       0.0,        1.0)
            )
        )

    @staticmethod
    def RotationY(theta: float):
        cos_theta: Final[float] = cos(theta)
        sin_theta: Final[float] = sin(theta)
        return Mat3(
            (
                (cos_theta, 0.0, -sin_theta),
                (0.0,       1.0, 0.0),
                (sin_theta, 0.0, cos_theta)
            )
        )

    @staticmethod
    def RotationX(theta: float):
        cos_theta: Final[float] = cos(theta)
        sin_theta: Final[float] = sin(theta)
        return Mat3(
            (
                (1.0, 0.0,       0.0),
                (0.0, cos_theta, sin_theta),
                (0.0, -sin_theta, cos_theta)
            )
        )

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
        z_inv: Final[float] = 1.0 / vec.z
        vec.x = ((vec.x * z_inv) + 1.0) * self.x_factor
        vec.y = ((-vec.y * z_inv) + 1.0) * self.y_factor
        return vec

    def GetTransformed(self, vec: Vec3):
        return self.Transform(Vec3.FromVec3(vec))

class IndexedTriangleList:
    def __init__(self, vertices: list[Vec3], indices: list[tuple[int, int, int]]) -> None:
        self.vertices: Final[list[Vec3]] = vertices
        self.indices: Final[list[tuple[int, int, int]]] = indices

class IndexedLineList:
    def __init__(self, vertices: list[Vec3], indices: list[tuple[int, int]]) -> None:
        self.vertices: Final[list[Vec3]] = vertices
        self.indices: Final[list[tuple[int, int]]] = indices

class Cube:
    def __init__(self, size: float) -> None:
        self.vertices: list[Vec3] = []

        side: Final[float] = size / 2.0
        self.vertices.append( Vec3(-side,-side,-side) )
        self.vertices.append( Vec3( side,-side,-side) )
        self.vertices.append( Vec3(-side, side,-side) )
        self.vertices.append( Vec3( side, side,-side) )
        self.vertices.append( Vec3(-side,-side, side) )
        self.vertices.append( Vec3( side,-side, side) )
        self.vertices.append( Vec3(-side, side, side) )
        self.vertices.append( Vec3( side, side, side) )

    def GetLines(self) -> IndexedLineList:
        return IndexedLineList( 
            deepcopy(self.vertices), [
                (0,1), (1,3), (3,2), (2,0),
                (0,4), (1,5), (3,7), (2,6),
                (4,5), (5,7), (7,6), (6,4)
            ])

    def GetTriangles(self) -> IndexedTriangleList:
        return IndexedTriangleList(
            deepcopy(self.vertices), [
                (0,2,1), (2,3,1),
                (1,3,5), (3,7,5),
                (2,6,3), (3,6,7),
                (4,5,7), (4,7,6),
                (0,4,2), (2,4,6),
                (0,1,4), (1,5,4) 
            ])

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

    def DrawTriangle(self, v0: Union[Vec2, Vec3], v1: Union[Vec2, Vec3], v2: Union[Vec2, Vec3], color: Color ):
        def _ToVec2(v: Union[Vec2, Vec3]) -> Vec2:
            if isinstance(v, Vec3):
                return Vec2(v.x, v.y)
            return copy(v)  # already Vec2
        
        # using pointers so we can swap (for sorting purposes)
        pv0: Vec2 = _ToVec2(v0)
        pv1: Vec2 = _ToVec2(v1)
        pv2: Vec2 = _ToVec2(v2)

        # sorting vertices by y
        if( pv1.y < pv0.y ): pv0, pv1 = pv1, pv0
        if( pv2.y < pv1.y ): pv1, pv2 = pv2, pv1
        if( pv1.y < pv0.y ): pv0, pv1 = pv1, pv0

        if( pv0.y == pv1.y ): # natural flat top
            # sorting top vertices by x
            if( pv1.x < pv0.x ): pv0, pv1 = pv1, pv0
            self._DrawFlatTopTriangle(pv0, pv1, pv2, color)
        elif( pv1.y == pv2.y ): # natural flat bottom
            # sorting bottom vertices by x
            if( pv2.x < pv1.x ): pv1, pv2 = pv2, pv1
            self._DrawFlatBottomTriangle(pv0, pv1, pv2, color)
        else: # general triangle
            # find splitting vertex
            alpha_split: float = (pv1.y - pv0.y) / (pv2.y - pv0.y)
            # alpha_split also,
            # alpha_split = (vi - pv0) / (pv2 - pv0)
            # vi = (alpha_split * pv2) + (pv0 * (1 - alpha_split))
            # vi = pv0 + (alpha_split * (pv2 - pv0))
            vi: Vec2  = pv0 + ((pv2 - pv0) * alpha_split)

            if( pv1.x < vi.x ): # major right
                self._DrawFlatBottomTriangle(pv0, pv1, vi, color)
                self._DrawFlatTopTriangle(pv1,vi, pv2, color)
            else: # major left
                self._DrawFlatBottomTriangle(pv0, vi, pv1, color)
                self._DrawFlatTopTriangle(vi, pv1, pv2, color)

    def _DrawFlatTopTriangle(self, v0: Vec2, v1: Vec2, v2: Vec2, color: Color):
        # calulcate slopes in screen space
        m0: float = (v2.x - v0.x) / (v2.y - v0.y)
        m1: float = (v2.x - v1.x) / (v2.y - v1.y)

        # calculate start and end scanlines
        y_start: int = int(ceil( v0.y - 0.5 ))
        y_end: int = int(ceil( v2.y - 0.5 )) # the scanline AFTER the last line drawn

        for y in range(y_start, y_end):
            # caluclate start and end points (x-coords)
            # add 0.5 to y value because we're calculating based on pixel CENTERS
            px0: float = m0 * (float( y ) + 0.5 - v0.y) + v0.x
            px1: float = m1 * (float( y ) + 0.5 - v1.y) + v1.x

            # calculate start and end pixels
            x_start: int = int(ceil( px0 - 0.5 ))
            x_end: int = int(ceil( px1 - 0.5 )) # the pixel AFTER the last pixel drawn

            for x in range(x_start, x_end):
                self.PutPixel( x,y,color )

    def _DrawFlatBottomTriangle(self, v0: Vec2, v1: Vec2, v2: Vec2, color: Color ):
        # calulcate slopes in screen space
        m0: float = (v1.x - v0.x) / (v1.y - v0.y)
        m1: float = (v2.x - v0.x) / (v2.y - v0.y)

        # calculate start and end scanlines
        y_start: int = int(ceil( v0.y - 0.5 ))
        y_end: int = int(ceil( v2.y - 0.5 )) # the scanline AFTER the last line drawn

        for y in range(y_start, y_end):
            # caluclate start and end points
            # add 0.5 to y value because we're calculating based on pixel CENTERS
            px0: float = m0 * (float( y ) + 0.5 - v0.y) + v0.x
            px1: float = m1 * (float( y ) + 0.5 - v0.y) + v0.x

            # calculate start and end pixels
            x_start: int = int(ceil( px0 - 0.5 ))
            x_end: int = int(ceil( px1 - 0.5 )) # the pixel AFTER the last pixel drawn

            for x in range(x_start, x_end):
                self.PutPixel( x,y,color )

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
