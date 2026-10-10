from typing import Any, Union, Final, Generic, TypeVar, overload, Protocol, Self
from math import sin, cos, pi, sqrt
from copy import deepcopy

VertexT = TypeVar("VertexT", bound="VertexArithmetic")

class VertexArithmetic(Protocol):
    pos: "Vec4"

    def __add__(self, other: Union[Self, int, float]) -> Self: ...
    def __sub__(self, other: Union[Self, int, float]) -> Self: ...
    def __mul__(self, other: Union[Self, int, float]) -> Self: ...
    def __truediv__(self, other: Union[Self, int, float]) -> Self: ...

    def UpdatePos(self, pos: "Vec4", src: Self) -> Self: ...

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

    def Len(self):
        return sqrt(self.Dot(self))

    def GetNormalized(self):
        length = self.Len()
        
        x = self.x / length
        y = self.y / length
        z = self.z / length
        
        return Vec3(x, y, z)

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

    def ToVec4(self, w: Union[float, int] = 1.0):
        return Vec4(self.x, self.y, self.z, float(w))

    def Saturate(self):
        x = min(1.0, max(0.0, self.x))
        y = min(1.0, max(0.0, self.y))
        z = min(1.0, max(0.0, self.z))
        
        return Vec3(x, y, z)

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

class Vec4:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    @classmethod
    def FromVec4(cls, vec: "Vec4"):
        return cls(vec.x, vec.y, vec.z, vec.w)

    def MatMul(self, mat: "Mat4"):
        new_vec = Vec4()
            
        new_vec.x = (mat[0][0] * self.x) + (mat[1][0] * self.y) + (mat[2][0] * self.z) + (mat[3][0] * self.w)
        new_vec.y = (mat[0][1] * self.x) + (mat[1][1] * self.y) + (mat[2][1] * self.z) + (mat[3][1] * self.w)
        new_vec.z = (mat[0][2] * self.x) + (mat[1][2] * self.y) + (mat[2][2] * self.z) + (mat[3][2] * self.w)
        new_vec.w = (mat[0][3] * self.x) + (mat[1][3] * self.y) + (mat[2][3] * self.z) + (mat[3][3] * self.w)

        return new_vec

    def VecMul(self, vec: "Vec4"):
        new_vec = Vec4()

        new_vec.x = self.x * vec.x
        new_vec.y = self.y * vec.y
        new_vec.z = self.z * vec.z
        new_vec.w = self.w * vec.w

        return new_vec

    def ScalerMul(self, scaler: Union[int, float]):
        new_vec = Vec4()

        new_vec.x = self.x * scaler
        new_vec.y = self.y * scaler
        new_vec.z = self.z * scaler
        new_vec.w = self.w * scaler

        return new_vec

    def ToVec3(self):
        return Vec3(self.x, self.y, self.z)

    def Saturate(self):
        x = min(1.0, max(0.0, self.x))
        y = min(1.0, max(0.0, self.y))
        z = min(1.0, max(0.0, self.z))
        w = min(1.0, max(0.0, self.w))
        
        return Vec4(x, y, z, w)

    def __repr__(self):
        return f"Vec4({self.x:.3f}, {self.y:.3f}, {self.z:.3f}, {self.w:.3f})"

    def __setattr__(self, name: str, value: float):
        if name in {"x", "y", "z", "w"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

    def __add__(self, other: Union["Vec4", int, float]):
        if isinstance(other, Vec4):
            return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
        else:
            return Vec4(self.x + other, self.y + other, self.z + other, self.w + other)

    def __sub__(self, other: Union["Vec4", int, float]):
        if isinstance(other, Vec4):
            return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
        else:
            return Vec4(self.x - other, self.y - other, self.z - other, self.w - other)

    def __neg__(self):
        return Vec4(-self.x, -self.y, -self.z, -self.w)

    def __mul__(self, other: Union["Mat4", "Vec4", int, float]) -> "Vec4":
        if isinstance(other, Mat4): # Mat-Mat multiplication
            return self.MatMul(other)
        elif isinstance(other, Vec4): # Mat-vec multiplication
            return self.VecMul(other)
        else: # scalar-Mat multiplication
            return self.ScalerMul(other)

    def __truediv__(self, other: Union["Vec4", int, float]):
        if isinstance(other, Vec4):
            return Vec4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)
        else:
            return Vec4(self.x / other, self.y / other, self.z / other, self.w / other)

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

class Mat4:
    def __init__(self, mat: \
                 tuple[\
                     tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]], \
                     tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]], \
                     tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]], \
                     tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]], \
                    ] = \
                    ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))):
        # [row][col]
        self.mat: list[list[Union[int, float]]] = [list(row) for row in mat]

    def __repr__(self) -> str:
        return f"Mat4([\n  {self.mat[0]},\n  {self.mat[1]}\n  {self.mat[2]} {self.mat[3]}\n])"

    def __getitem__(self, idx: int) -> list[Union[int, float]]:
        """Allow access like mat[row][col]."""
        return self.mat[idx]

    def __setitem__(self, idx: int, value: list[Union[int, float]]) -> None:
        """Allow assignment like mat[row] = [..]."""
        if len(value) != 4:
            raise ValueError("Each row must have exactly 4 elements")
        self.mat[idx] = value

    def ScalerMul(self, scaler: Union[int, float]):
        new_mat = Mat4()
        for r, row in enumerate(self.mat):
            for c, val in enumerate(row):
                new_mat.mat[r][c] = scaler * val

        return new_mat

    def MatMul(self, mat: "Mat4"):
        new_mat = Mat4()

        for row_left in range(4):
            for col_rigth in range(4):
                for i in range(4):
                    new_mat.mat[row_left][col_rigth] += self.mat[row_left][i] * mat.mat[i][col_rigth]

        return new_mat

    @overload
    def __mul__(self, other: "Mat4") -> "Mat4": ...

    @overload
    def __mul__(self, other: Vec4) -> Vec4: ...

    @overload
    def __mul__(self, other: Union[int, float]) -> Vec4: ...

    def __mul__(self, other: Union["Mat4", Vec4, int, float]) -> Union[Vec4, "Mat4"]:
        if isinstance(other, Mat4): # Mat-Mat multiplication
            return self.MatMul(other)
        elif isinstance(other, Vec4): # Mat-vec multiplication
            raise TypeError("Mat4 * Vec4 is not supported; Direct3D uses row vectors, so use Vec4 * Mat4 instead.")
        else: # scalar-Mat multiplication
            return self.ScalerMul(other)

    @staticmethod
    def Scale(factor: Union[int, float]):
        return Mat4(
            (
                (factor, 0, 0, 0), 
                (0, factor, 0, 0), 
                (0, 0, factor, 0),
                (0, 0, 0, 1)
            )
        )

    @staticmethod
    def Identity():
        return Mat4(
            (
                (1, 0, 0, 0), 
                (0, 1, 0, 0), 
                (0, 0, 1, 0),
                (0, 0, 0, 1)
            )
        )

    @staticmethod
    def RotationZ(theta: float):
        cos_theta: Final[float] = cos(theta)
        sin_theta: Final[float] = sin(theta)
        return Mat4(
            (
                (cos_theta, -sin_theta, 0.0, 0.0), 
                (sin_theta, cos_theta,  0.0, 0.0), 
                (0.0,       0.0,        1.0, 0.0),
                (0.0,       0.0,        0.0, 1.0)
            )
        )

    @staticmethod
    def RotationY(theta: float):
        cos_theta: Final[float] = cos(theta)
        sin_theta: Final[float] = sin(theta)
        return Mat4(
            (
                (cos_theta, 0.0, -sin_theta, 0.0),
                (0.0,       1.0, 0.0,        0.0),
                (sin_theta, 0.0, cos_theta,  0.0),
                (0.0,       0.0, 0.0,        1.0)
            )
        )

    @staticmethod
    def RotationX(theta: float):
        cos_theta: Final[float] = cos(theta)
        sin_theta: Final[float] = sin(theta)
        return Mat4(
            (
                (1.0, 0.0,        0.0,       0.0),
                (0.0, cos_theta,  sin_theta, 0.0),
                (0.0, -sin_theta, cos_theta, 0.0),
                (0.0, 0.0,        0.0,       1.0)
            )
        )

    @staticmethod
    def Translation(x: Union[int, float], y: Union[int, float], z: Union[int, float]):
        return Mat4(
            (
                (1, 0, 0, 0), 
                (0, 1, 0, 0), 
                (0, 0, 1, 0),
                (x, y, z, 1)
            )
        )

    @staticmethod
    def TranslationVec(vec: Union[Vec3, Vec4]):
        return Mat4.Translation(vec.x, vec.y, vec.z)

class Color:
    White: Color
    Black: Color
    Gray: Color
    LightGray: Color
    Red: Color
    Green: Color
    Blue: Color
    Yellow: Color
    Cyan: Color
    Magenta: Color
    Orange: Color
    Purple: Color
    Brown: Color
    Pink: Color
    Gold: Color
    Silver: Color
    Teal: Color
    Olive: Color
    Maroon: Color
    Navy: Color
    Lime: Color
    Aqua: Color
    Fuchsia: Color
    Indigo: Color
    Violet: Color
    Beige: Color
    Chocolate: Color
    Coral: Color
    Turquoise: Color
    SkyBlue: Color

    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    @classmethod
    def FromVec3(cls, vec: Vec3):
        return Color(int(vec.x), int(vec.y), int(vec.z))

    def ToVec3(self):
        return Vec3(self.r, self.g, self.b)

    def __repr__(self):
        return f"Color(R: {self.r}, G: {self.g}, B: {self.b})"

    def __setattr__(self, name: str, value: int):
        if name in {"r", "g", "b"}:
            super().__setattr__(name, int(value))
        else:
            super().__setattr__(name, value)

Color.White       = Color(255, 255, 255)
Color.Black       = Color(0, 0, 0)
Color.Gray        = Color(0x80, 0x80, 0x80)
Color.LightGray   = Color(0xD3, 0xD3, 0xD3)
Color.Red         = Color(255, 0, 0)
Color.Green       = Color(0, 255, 0)
Color.Blue        = Color(0, 0, 255)
Color.Yellow      = Color(255, 255, 0)
Color.Cyan        = Color(0, 255, 255)
Color.Magenta     = Color(255, 0, 255)
Color.Orange      = Color(255, 165, 0)
Color.Purple      = Color(128, 0, 128)
Color.Brown       = Color(165, 42, 42)
Color.Pink        = Color(255, 192, 203)
Color.Gold        = Color(255, 215, 0)
Color.Silver      = Color(192, 192, 192)
Color.Teal        = Color(0, 128, 128)
Color.Olive       = Color(128, 128, 0)
Color.Maroon      = Color(128, 0, 0)
Color.Navy        = Color(0, 0, 128)
Color.Lime        = Color(50, 205, 50)
Color.Indigo      = Color(75, 0, 130)
Color.Violet      = Color(238, 130, 238)
Color.Beige       = Color(245, 245, 220)
Color.Chocolate   = Color(210, 105, 30)
Color.Coral       = Color(255, 127, 80)
Color.Turquoise   = Color(64, 224, 208)
Color.SkyBlue     = Color(135, 206, 235)

class Triangle(Generic[VertexT]):
    def __init__(self, v0: VertexT, v1: VertexT, v2: VertexT):
        self.v0 = deepcopy(v0)
        self.v1 = deepcopy(v1)
        self.v2 = deepcopy(v2)

class IndexedTriangleList:
    def __init__(self, vertices: list[Any], indices: list[tuple[int, int, int]]) -> None:
        self.vertices: Final[list[Any]] = list(vertices)
        self.indices: Final[list[tuple[int, int, int]]] = indices
