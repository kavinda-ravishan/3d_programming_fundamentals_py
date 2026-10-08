from abc import ABC, abstractmethod
from typing import Any, Union, Optional, Final, Generic, TypeVar, overload, Protocol, Self
from math import sin, cos, pi, ceil
from copy import deepcopy
import cv2
import numpy as np

VertexT = TypeVar("VertexT", bound="VertexArithmetic")

class VertexArithmetic(Protocol):
    pos: "Vec3"

    def __add__(self, other: Union[Self, int, float]) -> Self: ...
    def __sub__(self, other: Union[Self, int, float]) -> Self: ...
    def __mul__(self, other: Union[Self, int, float]) -> Self: ...
    def __truediv__(self, other: Union[Self, int, float]) -> Self: ...

    def UpdatePos(self, pos: "Vec3", src: Self) -> Self: ...

def Interpolate(src: Any, dst: Any, alpha: float) -> Any:
    return src + ((dst - src) * alpha)

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

    def Dot(self, other: "Vec2"):
        return (self.x * other.x) + (self.y * other.y)

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

    def __mul__(self, other: Union["Vec2", int, float]):
        if isinstance(other, Vec2): # vec-vec dot product
            return Vec2(self.x * other.x, self.y * other.y)
        else: # scalar-vec multiplication
            return Vec2(self.x * other, self.y * other)

    def __truediv__(self, other: Union["Vec2", int, float]):
        if isinstance(other, Vec2):
            return Vec2(self.x / other.x, self.y / other.y)
        else:
            return Vec2(self.x / other, self.y / other)

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

    def Dot(self, other: "Vec3"):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def Cross(self, other: "Vec3"):
        return Vec3(
			(self.y * other.z) - (self.z * other.y),
			(self.z * other.x) - (self.x * other.z),
			(self.x * other.y) - (self.y * other.x) 
        )

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

    def __sub__(self, other: Union["Vec3", int, float]):
        if isinstance(other, Vec3):
            return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return Vec3(self.x - other, self.y - other, self.z - other)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

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

    @classmethod
    def FromVec3(cls, vec: Vec3):
        return Color(int(vec.x), int(vec.y), int(vec.z))

    def __repr__(self):
        return f"Color(R: {self.r}, G: {self.g}, B: {self.b})"

    def __setattr__(self, name: str, value: int):
        if name in {"r", "g", "b"}:
            super().__setattr__(name, int(value))
        else:
            super().__setattr__(name, value)

class ZBuffer:
    def __init__(self, width: int, height: int):
        """
        Initialize the Z-buffer with given dimensions.
        Depth values are initialized to +inf (far away).
        """
        self.width: Final[int] = width
        self.height: Final[int] = height
        self.buffer = np.full((height, width), np.inf, dtype=np.float32)

    def Clear(self):
        """
        Reset the Z-buffer
        """
        self.buffer.fill(np.inf)

    def TestAndSet(self, x: int, y: int, depth: float):
        if self.buffer[y][x] > depth:
            self.buffer[y][x] = depth
            return True
        else:
            return False

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

class Triangle(Generic[VertexT]):
    def __init__(self, v0: VertexT, v1: VertexT, v2: VertexT):
        self.v0 = deepcopy(v0)
        self.v1 = deepcopy(v1)
        self.v2 = deepcopy(v2)

# PC3 : Pre-cliped 3D space
class PC3Transformer(Generic[VertexT]):
    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.x_factor: Final[float] = screen_width / 2
        self.y_factor: Final[float] = screen_height / 2

    def GetTransform(self, vertex: VertexT):
        z_inv: Final[float] = 1.0 / vertex.pos.z

        transformed = vertex * z_inv

        transformed.pos.x = (transformed.pos.x + 1.0) * self.x_factor
        transformed.pos.y = (-transformed.pos.y + 1.0) * self.y_factor
        transformed.pos.z = z_inv

        return transformed

class IndexedTriangleList:
    def __init__(self, vertices: list[Any], indices: list[tuple[int, int, int]]) -> None:
        self.vertices: Final[list[Any]] = list(vertices)
        self.indices: Final[list[tuple[int, int, int]]] = indices

class Cube:
    def __init__(self, ) -> None: ...

    @staticmethod
    def GetPlainIndependentFaces(size: float = 1.0, color: bool = True) -> IndexedTriangleList:
        side: Final[float] = size / 2.0
        vertices: list[Vec3] = [
            Vec3( -side,-side,-side ), # 0 near side
            Vec3( side,-side,-side ), # 1
            Vec3( -side,side,-side ), # 2
            Vec3( side,side,-side ), # 3
            Vec3( -side,-side,side ), # 4 far side
            Vec3( side,-side,side ), # 5
            Vec3( -side,side,side ), # 6
            Vec3( side,side,side ), # 7
            Vec3( -side,-side,-side ), # 8 left side
            Vec3( -side,side,-side ), # 9
            Vec3( -side,-side,side ), # 10
            Vec3( -side,side,side ), # 11
            Vec3( side,-side,-side ), # 12 right side
            Vec3( side,side,-side ), # 13
            Vec3( side,-side,side ), # 14
            Vec3( side,side,side ), # 15
            Vec3( -side,-side,-side ), # 16 bottom side
            Vec3( side,-side,-side ), # 17
            Vec3( -side,-side,side ), # 18
            Vec3( side,-side,side ), # 19
            Vec3( -side,side,-side ), # 20 top side
            Vec3( side,side,-side ), # 21
            Vec3( -side,side,side ), # 22
            Vec3( side,side,side ) # 23
        ]

        tverts: list[Any] = []

        if color:
            colors: list[Color] = [
                Color.Red,
                Color.Green,
                Color.Blue,
                Color.Yellow,
                Color.Cyan,
                Color.Magenta
            ]

            tverts = [
                SolidEffect.Vertex(position, colors[int(i/4)])
                for i, position in enumerate(vertices)
            ]
        else:
            tverts = [
                VertexPositionColorEffect.Vertex(position)
                for _, position in enumerate(vertices)
            ]

        return IndexedTriangleList(
            tverts, [
				(0,2, 1),  ( 2,3,1),
				(4,5, 7),  ( 4,7,6),
				(8,10, 9), (10,11,9),
				(12,13,15),(12,15,14),
				(16,17,18),(18,17,19),
				(20,23,21),(20,22,23)
            ])

    @staticmethod
    def GetSkinned(size: float = 1.0) -> IndexedTriangleList:
        side: Final[float] = size / 2.0

        def convert_tex_coord(u: float, v: float) -> Vec2:
            return Vec2((u + 1.0) / 3.0, v / 4.0);

        vertices: list[Vec3] = [
            Vec3(-side, -side, -side),  # 0
            Vec3(side, -side, -side),   # 1
            Vec3(-side, side, -side),   # 2
            Vec3(side, side, -side),    # 3
            Vec3(-side, -side, side),   # 4
            Vec3(side, -side, side),    # 5
            Vec3(-side, side, side),    # 6
            Vec3(side, side, side),     # 7
            Vec3(-side, -side, -side),  # 8
            Vec3(side, -side, -side),   # 9
            Vec3(-side, -side, -side),  # 10
            Vec3(-side, -side, side),   # 11
            Vec3(side, -side, -side),   # 12
            Vec3(side, -side, side),    # 13
        ]
        texture_coordinates: list[Vec2] = [
            convert_tex_coord(1.0, 0.0),
            convert_tex_coord(0.0, 0.0),
            convert_tex_coord(1.0, 1.0),
            convert_tex_coord(0.0, 1.0),
            convert_tex_coord(1.0, 3.0),
            convert_tex_coord(0.0, 3.0),
            convert_tex_coord(1.0, 2.0),
            convert_tex_coord(0.0, 2.0),
            convert_tex_coord(1.0, 4.0),
            convert_tex_coord(0.0, 4.0),
            convert_tex_coord(2.0, 1.0),
            convert_tex_coord(2.0, 2.0),
            convert_tex_coord(-1.0, 1.0),
            convert_tex_coord(-1.0, 2.0),
        ]
        tverts = [
            TextureEffect.Vertex(position, texture_coordinates[i])
            for i, position in enumerate(vertices)
        ]

        return IndexedTriangleList(
            tverts, [
                (0, 2, 1), (2, 3, 1),
                (4, 8, 5), (5, 8, 9),
                (2, 6, 3), (3, 6, 7),
                (4, 5, 7), (4, 7, 6),
                (2, 10, 11), (2, 11, 6),
                (12, 3, 7), (12, 7, 13),
            ])

class Surface:
    def __init__(self, width: int, height: int, canvas: Optional[np.ndarray[Any, Any]] = None):
        self.width: Final[int] = width
        self.height: Final[int] = height
        if canvas is None:
            self.canvas = np.zeros((self.height, self.width, 3), dtype="uint8")
        else:
            self.canvas = canvas

    @classmethod
    def FromFile(cls, path: str):
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Could not load image from path: {path}")
        height, width = image.shape[:2]
        return cls(width, height, image)
        
    def GetCanvas(self):
        return self.canvas

    def Clear(self):
        self.canvas = np.zeros_like(self.canvas)

    def PutPixel(self, x: int, y: int, color: Color):
        if(x >=0 and y >= 0 and x < self.width and y < self.height):
            self.canvas[int(y),int(x)] = (color.b, color.g, color.r)
        else:
            raise IndexError("Pixel coordinates are out of bounds")

    def GetPixel(self, x: int, y: int):
        if(x >=0 and y >= 0 and x < self.width and y < self.height):
            pixel = self.canvas[int(y),int(x)]
            return Color(pixel[2], pixel[1], pixel[0])
        else:
            raise IndexError("Pixel coordinates are out of bounds")

    def GetWidth(self): return self.width
    def GetHeight(self): return self.height

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

class DefaultVertexShader(Generic[VertexT]):
    def __init__(self):
        self.rotation: Mat3 = Mat3().Identity()
        self.translation : Vec3 = Vec3()

    def BindRotation(self, rotation: Mat3):
        self.rotation = rotation

    def BindTranslation(self, translation: Vec3):
        self.translation = translation

    def __call__(self, input: VertexT):
            # transform vertices using matrix + vector
            return input.UpdatePos((input.pos * self.rotation) + self.translation, input)

class VertexPositionColorEffect(Generic[VertexT]):
    class Vertex(VertexArithmetic):
        def __init__(self, pos: Vec3):
            self.pos: Vec3 = pos

        def UpdatePos(self, pos: Vec3, src: "VertexPositionColorEffect.Vertex"):
            return VertexPositionColorEffect.Vertex(pos)

        def __add__(self, other: Union["VertexPositionColorEffect.Vertex", float, int]):
            if isinstance(other, VertexPositionColorEffect.Vertex):
                return VertexPositionColorEffect.Vertex(self.pos + other.pos)
            else:
                return VertexPositionColorEffect.Vertex(self.pos + other)

        def __sub__(self, other: Union["VertexPositionColorEffect.Vertex", float, int]):
            if isinstance(other, VertexPositionColorEffect.Vertex):
                return VertexPositionColorEffect.Vertex(self.pos - other.pos)
            else:
                return VertexPositionColorEffect.Vertex(self.pos - other)

        def __mul__(self, other: Union["VertexPositionColorEffect.Vertex", float, int]):
            if isinstance(other, VertexPositionColorEffect.Vertex):
                return VertexPositionColorEffect.Vertex(self.pos * other.pos)
            else:
                return VertexPositionColorEffect.Vertex(self.pos * other)

        def __truediv__(self, other:Union["VertexPositionColorEffect.Vertex", float, int]):
            if isinstance(other, VertexPositionColorEffect.Vertex):
                return VertexPositionColorEffect.Vertex(self.pos / other.pos)
            else:
                return VertexPositionColorEffect.Vertex(self.pos / other)

    class VSOut(VertexArithmetic):
        def __init__(self, pos: Vec3, color: Vec3):
            self.pos: Vec3 = pos
            self.color: Vec3 = color

        def UpdatePos(self, pos: Vec3, src: "VertexPositionColorEffect.VSOut"):
            return VertexPositionColorEffect.VSOut(pos, src.color)

        def __add__(self, other: Union["VertexPositionColorEffect.VSOut", float, int]):
            if isinstance(other, VertexPositionColorEffect.VSOut):
                return VertexPositionColorEffect.VSOut(self.pos + other.pos, self.color + other.color)
            else:
                return VertexPositionColorEffect.VSOut(self.pos + other, self.color + other)

        def __sub__(self, other: Union["VertexPositionColorEffect.VSOut", float, int]):
            if isinstance(other, VertexPositionColorEffect.VSOut):
                return VertexPositionColorEffect.VSOut(self.pos - other.pos, self.color - other.color)
            else:
                return VertexPositionColorEffect.VSOut(self.pos - other, self.color - other)

        def __mul__(self, other: Union["VertexPositionColorEffect.VSOut", float, int]):
            if isinstance(other, VertexPositionColorEffect.VSOut):
                return VertexPositionColorEffect.VSOut(self.pos * other.pos, self.color * other.color)
            else:
                return VertexPositionColorEffect.VSOut(self.pos * other, self.color * other)

        def __truediv__(self, other:Union["VertexPositionColorEffect.VSOut", float, int]):
            if isinstance(other, VertexPositionColorEffect.VSOut):
                return VertexPositionColorEffect.VSOut(self.pos / other.pos, self.color / other.color)
            else:
                return VertexPositionColorEffect.VSOut(self.pos / other, self.color / other)

    class VertexShader:
        def __init__(self):
            self.rotation: Mat3 = Mat3().Identity()
            self.translation : Vec3 = Vec3()

        def BindRotation(self, rotation: Mat3):
            self.rotation = rotation

        def BindTranslation(self, translation: Vec3):
            self.translation = translation

        def __call__(self, input: VertexPositionColorEffect.Vertex) -> VertexPositionColorEffect.VSOut:

                pos = (input.pos * self.rotation) + self.translation
                color = Vec3(abs(pos.x), abs(pos.y), abs(min(1.0, 1/pos.z))) * 255.0

                input.color = color # type: ignore
                # transform vertices using matrix + vector
                return VertexPositionColorEffect.VSOut(pos, color)

    class PixelShader:
        def __init__(self): ...

        def __call__(self, input: "VertexPositionColorEffect.VSOut") -> Color:
            return Color.FromVec3(input.color)

    def __init__(self):
        self.ps: VertexPositionColorEffect.PixelShader = VertexPositionColorEffect.PixelShader()
        self.vs: VertexPositionColorEffect.VertexShader = VertexPositionColorEffect.VertexShader()

class SolidEffect(Generic[VertexT]):

    class Vertex(VertexArithmetic):
        def __init__(self, pos: Vec3, color: Color):
            self.pos: Vec3 = pos
            self.color: Color = color

        def UpdatePos(self, pos: Vec3, src: "SolidEffect.Vertex"):
            return SolidEffect.Vertex(pos, src.color)

        def __add__(self, other: Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos + other.pos, self.color)
            else:
                return SolidEffect.Vertex(self.pos + other, self.color)

        def __sub__(self, other: Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos - other.pos, self.color)
            else:
                return SolidEffect.Vertex(self.pos - other, self.color)

        def __mul__(self, other: Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos * other.pos, self.color)
            else:
                return SolidEffect.Vertex(self.pos * other, self.color)

        def __truediv__(self, other:Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos / other.pos, self.color)
            else:
                return SolidEffect.Vertex(self.pos / other, self.color)

    class PixelShader:
        def __init__(self): ...

        def __call__(self, input: "SolidEffect.Vertex") -> Color:
            return input.color

    def __init__(self):
        self.ps: SolidEffect.PixelShader = SolidEffect.PixelShader()
        self.vs: DefaultVertexShader[VertexT] = DefaultVertexShader[VertexT]()

class TextureEffect(Generic[VertexT]):

    class Vertex(VertexArithmetic):
        def __init__(self, pos: Vec3, t: Vec2):
            self.pos: Vec3 = pos
            self.t: Vec2 = t

        def UpdatePos(self, pos: Vec3, src: "TextureEffect.Vertex"):
            return TextureEffect.Vertex(pos, src.t)

        def __add__(self, other: Union["TextureEffect.Vertex", float, int]):
            if isinstance(other, TextureEffect.Vertex):
                return TextureEffect.Vertex(self.pos + other.pos, self.t + other.t)
            else:
                return TextureEffect.Vertex(self.pos + other, self.t + other)

        def __sub__(self, other: Union["TextureEffect.Vertex", float, int]):
            if isinstance(other, TextureEffect.Vertex):
                return TextureEffect.Vertex(self.pos - other.pos, self.t - other.t)
            else:
                return TextureEffect.Vertex(self.pos - other, self.t - other)

        def __mul__(self, other: Union["TextureEffect.Vertex", float, int]):
            if isinstance(other, TextureEffect.Vertex):
                return TextureEffect.Vertex(self.pos * other.pos, self.t * other.t)
            else:
                return TextureEffect.Vertex(self.pos * other, self.t * other)

        def __truediv__(self, other:Union["TextureEffect.Vertex", float, int]):
            if isinstance(other, TextureEffect.Vertex):
                return TextureEffect.Vertex(self.pos / other.pos, self.t / other.t)
            else:
                return TextureEffect.Vertex(self.pos / other, self.t / other)

    class PixelShader:
        def __init__(self):
            self.texture: Surface = Surface(0, 0)
            self.tex_width: float = 0.0
            self.tex_height: float = 0.0
            self.tex_xclamp: float = 0.0
            self.tex_yclamp: float = 0.0

        def __call__(self, input: "TextureEffect.Vertex") -> Color:
            return self.texture.GetPixel(
                int(max(0, min(input.t.x * self.tex_width + 0.5, self.tex_xclamp))),
                int(max(0, min(input.t.y * self.tex_height + 0.5, self.tex_yclamp)))
            )

        def BindTexture(self, filename: str):
            self.texture = Surface.FromFile(filename)
            self.tex_width = float(self.texture.GetWidth())
            self.tex_height = float(self.texture.GetHeight())
            self.tex_xclamp = self.tex_width - 1.0
            self.tex_yclamp = self.tex_height - 1.0

    def __init__(self):
        self.ps: TextureEffect.PixelShader = TextureEffect.PixelShader()
        self.vs: DefaultVertexShader[VertexT] = DefaultVertexShader[VertexT]()

class Pipeline(Generic[VertexT]):
    def __init__(self, graphics: Graphics, effect: Any):
        self.gfx: Final[Graphics] = graphics

        frame_width: Final[int] = self.gfx.surface.GetWidth()
        frame_height: Final[int] = self.gfx.surface.GetHeight()

        self.pc3: Final[PC3Transformer[VertexT]] = PC3Transformer(frame_width, frame_height)
        self.z_buffer: Final[ZBuffer] = ZBuffer(frame_width, frame_height)
        
        self.effect: Any = effect

    def Draw(self, triangle_list: IndexedTriangleList):
        self._ProcessVertices(triangle_list.vertices, triangle_list.indices)

    def BeginFrame(self):
        self.z_buffer.Clear()
    
    def _ProcessVertices(self, vertices: list[Any], indices: list[tuple[int, int, int]]):
        # create vertex vector for vs output
        vertices_out: list[Any] = []

        # call vertex shader on each vertex
        for v in vertices:
            vertices_out.append(self.effect.vs(v))

		# assemble triangles from stream of indices and vertices
        self._AssembleTriangles(vertices_out, indices)

    def _AssembleTriangles(self, vertices: list[VertexT], indices: list[tuple[int, int, int]]):
        for triangle_indices in indices:
            v0 = vertices[triangle_indices[0]]
            v1 = vertices[triangle_indices[1]]
            v2 = vertices[triangle_indices[2]]

            if((v1.pos - v0.pos).Cross(v2.pos - v0.pos).Dot(v0.pos) <= 0.0):
                self._ProcessTriangle(v0, v1, v2)

    def _ProcessTriangle(self, v0: VertexT, v1: VertexT, v2: VertexT):
        self._PostProcessTriangleVertices(Triangle(v0, v1, v2))

    def _PostProcessTriangleVertices(self, triangle: Triangle[VertexT]):
		# perspective divide and screen transform for all 3 vertices
        triangle.v0 = self.pc3.GetTransform( triangle.v0 )
        triangle.v1 = self.pc3.GetTransform( triangle.v1 )
        triangle.v2 = self.pc3.GetTransform( triangle.v2 )

		# draw the triangle
        self._DrawTriangle( triangle )

    def _DrawTriangle(self, triangle: Triangle[VertexT]):
        v0: VertexT = triangle.v0
        v1: VertexT = triangle.v1
        v2: VertexT = triangle.v2

        # sorting vertices by y
        # v0.pos.y < v1.pos.y < v2.pos.y
        v0, v1, v2 = sorted([v0, v1, v2], key=lambda v: v.pos.y)

        if( v0.pos.y == v1.pos.y ): # natural flat top
            # sorting top vertices by x
            if( v1.pos.x < v0.pos.x ): v0, v1 = v1, v0
            self._DrawFlatTopTriangle(v0, v1, v2)
        elif( v1.pos.y == v2.pos.y ): # natural flat bottom
            # sorting bottom vertices by x
            if( v2.pos.x < v1.pos.x ): v1, v2 = v2, v1
            self._DrawFlatBottomTriangle(v0, v1, v2)
        else: # general triangle
            # find splitting vertex
            alpha_split: float = (v1.pos.y - v0.pos.y) / (v2.pos.y - v0.pos.y)
            # alpha_split also,
            # alpha_split = (vi - v0) / (v2 - v0)
            # vi = (alpha_split * v2) + (v0 * (1 - alpha_split))
            # vi = v0 + (alpha_split * (v2 - v0))
            vi  = Interpolate(v0, v2, alpha_split)

            if( v1.pos.x < vi.pos.x ): # major right
                self._DrawFlatBottomTriangle(v0, v1, vi)
                self._DrawFlatTopTriangle(v1,vi, v2)
            else: # major left
                self._DrawFlatBottomTriangle(v0, vi, v1)
                self._DrawFlatTopTriangle(vi, v1, v2)

    def _DrawFlatTopTriangle(self, it0: VertexT, it1: VertexT, it2: VertexT):
        # calulcate dVertex / dy
        # change in interpolant for every 1 change in y
        delta_y: float = it2.pos.y - it0.pos.y
        dit0 = (it2 - it0) / delta_y
        dit1 = (it2 - it1) / delta_y

        # create right edge interpolant
        it_edge1 = it1;

        # call the flat triangle render routine
        self._DrawFlatTriangle(it0, it1, it2, dit0, dit1, it_edge1)

    def _DrawFlatBottomTriangle(self, it0: VertexT, it1: VertexT, it2: VertexT):
        # calulcate dVertex / dy
        # change in interpolant for every 1 change in y
        delta_y: float = it2.pos.y - it0.pos.y
        dit0 = (it1 - it0) / delta_y
        dit1 = (it2 - it0) / delta_y

        # create right edge interpolant
        it_edge1 = it0;

        # call the flat triangle render routine
        self._DrawFlatTriangle(it0, it1, it2, dit0, dit1, it_edge1)

    def _DrawFlatTriangle(self, 
                          it0: VertexT,
						  it1: VertexT,
						  it2: VertexT,
						  dv0: VertexT,
						  dv1: VertexT,
						  it_edge_1: VertexT):
		# create edge interpolant for left edge (always v0)
        it_edge0 = it0
        it_edge1 = it_edge_1

		# calculate start and end scanlines
        y_start: Final[int] = int(ceil(float(it0.pos.y - 0.5)))
        y_end: Final[int] = int(ceil(float(it2.pos.y - 0.5))) # the scanline AFTER the last line drawn

        # do interpolant prestep
        it_edge0 += dv0 * (float(y_start) + 0.5 - it0.pos.y)
        it_edge1 += dv1 * (float(y_start) + 0.5 - it0.pos.y)       

        for y in range(y_start, y_end):
			# calculate start and end pixels
            x_start: int = int(ceil(float(it_edge0.pos.x - 0.5)))
            x_end: int = int(ceil(float(it_edge1.pos.x - 0.5))) # the pixel AFTER the last pixel drawn

            # create scanline interpolant startpoint
            # (some waste for interpolating x,y,z, but makes life easier not having
            #  to split them off, and z will be needed in the future anyways...)
            i_line = it_edge0

            # calculate delta scanline interpolant / dx
            dx: float = it_edge1.pos.x - it_edge0.pos.x
            di_line = (it_edge1 - i_line) / dx

            # prestep scanline interpolant
            i_line += di_line * (float(x_start) + 0.5 - it_edge0.pos.x)

            for x in range(x_start, x_end):
                z = 1.0 / i_line.pos.z
                attr = i_line * z

                if self.z_buffer.TestAndSet(x, y, z):
                    # perform texture lookup, clamp, and write pixel
                    self.gfx.PutPixel(x, y, self.effect.ps(attr))

                i_line += di_line

            it_edge0 += dv0
            it_edge1 += dv1

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
