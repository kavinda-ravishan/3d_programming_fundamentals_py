from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Union, overload
from copy import deepcopy
from math import sqrt, cos, sin, tau
import cv2
import numpy as np

class Vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def FromVec3(cls, vec: Vec3):
        return cls(vec.x, vec.y)

    def __repr__(self):
        return f"Vec2({self.x:.3f}, {self.y:.3f})"

    def __setattr__(self, name: str, value: float):
        if name in {"x", "y"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

    def __add__(self, other: Union[Vec2, int, float]):
        if isinstance(other, Vec2):
            return Vec2(self.x + other.x, self.y + other.y)
        else:
            return Vec2(self.x + other, self.y + other)

    def __sub__(self, other: Union[Vec2, int, float]):
        if isinstance(other, Vec2):
            return Vec2(self.x - other.x, self.y - other.y)
        else:
            return Vec2(self.x - other, self.y - other)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    @overload
    def __mul__(self, other: Vec2) -> float: ...

    @overload
    def __mul__(self, other: Union[int, float]) -> Vec2: ...

    def __mul__(self, other: Union[Vec2, int, float]) -> Union[Vec2, int, float]:
        if isinstance(other, Vec2): # vec-vec dot product
            return (self.x * other.x) + (self.y * other.y)
        else: # scalar-vec multiplication
            return Vec2(self.x * other, self.y * other)

    def __rmul__(self, other: Union[int, float]):
        return Vec2(self.x * other, self.y * other)

    def __truediv__(self, other: Union[Vec2, int, float]):
        if isinstance(other, Vec2): # element-wise division
            return Vec2(self.x / other.x, self.y / other.y)
        else: # scalar division
            return Vec2(self.x / other, self.y / other)

    def Mul(self, other: Union[Vec2, int, float]):
        if isinstance(other, Vec2): # vec-vec multiplication
            return Vec2(self.x * other.x, self.y * other.y)
        else: # scalar-vec multiplication
            return Vec2(self.x * other, self.y * other)

    def Len(self):
        return sqrt((self.x * self.x) + (self.y * self.y))

    def Normalize(self):
        length = self.Len()
        if length == 0:
            raise ZeroDivisionError("Cannot normalize a vector of length 0.")
        return Vec2(self.x / length, self.y / length)

    def ClockwiseOrthogonal(self):
        return Vec2(self.y, -self.x)

    def CounterClockwiseOrthogonal(self):
        return Vec2(-self.y, self.x)

    def Rotate(self, angle: float):
        cos_theta = cos(angle)
        sin_theta = sin(angle)

        x = (self.x*cos_theta) - (self.y*sin_theta)
        y = (self.x*sin_theta) + (self.y*cos_theta)
        
        return Vec2(x, y)

    def RotateCosTSinT(self, cos_theta: float, sin_theta: float):
        x = (self.x*cos_theta) - (self.y*sin_theta)
        y = (self.x*sin_theta) + (self.y*cos_theta)
        
        return Vec2(x, y)

class Vec3:
    def __init__(self, x: float = 0, y: float = 0, w: float = 0):
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)

    @classmethod
    def FromVec2(cls, vec: Vec2):
        return cls(vec.x, vec.y, 1.0)

    def __repr__(self):
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.w:.3f})"

    def __setattr__(self, name: str, value: float):
        if name in {"x", "y", "w"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

    @overload
    def __add__(self, other: Vec3) -> Vec3: ...

    @overload
    def __add__(self, other: Union[int, float]) -> Vec3: ...

    def __add__(self, other: Union[Vec3, int, float]):
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.w + other.w)
        else:
            return Vec3(self.x + other, self.y + other, self.w + other)

    @overload
    def __sub__(self, other: Vec3) -> Vec3: ...

    @overload
    def __sub__(self, other: Union[int, float]) -> Vec3: ...

    def __sub__(self, other: Union[Vec3, int, float]):
        if isinstance(other, Vec3):
            return Vec3(self.x - other.x, self.y - other.y, self.w - other.w)
        else:
            return Vec3(self.x - other, self.y - other, self.w - other)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.w)

    @overload
    def __mul__(self, other: Vec3) -> float: ...

    @overload
    def __mul__(self, other: Union[int, float]) -> Vec3: ...

    def __mul__(self, other: Union[Vec3, int, float]) -> Union[Vec3, int, float]:
        if isinstance(other, Vec3): # vec-vec dot product
            return (self.x * other.x) + (self.y * other.y) + (self.w * other.w)
        else: # scalar-vec multiplication
            return Vec3(self.x * other, self.y * other, self.w * other)

    def __rmul__(self, other: Union[int, float]):
        return Vec3(self.x * other, self.y * other, self.w * other)

    def __truediv__(self, other: Union[Vec3, int, float]):
        if isinstance(other, Vec3): # element-wise division
            return Vec3(self.x / other.x, self.y / other.y, self.w / other.w)
        else: # scalar division
            return Vec3(self.x / other, self.y / other, self.w / other)

    def Mul(self, other: Union[Vec3, int, float]):
        if isinstance(other, Vec3): # vec-vec multiplication
            return Vec3(self.x * other.x, self.y * other.y, self.w * other.w)
        else: # scalar-vec multiplication
            return Vec3(self.x * other, self.y * other, self.w * other)

    def Len2D(self):
        return sqrt((self.x * self.x) + (self.y * self.y))

    def Normalize2D(self):
        length = self.Len2D()
        if length == 0:
            raise ZeroDivisionError("Cannot normalize a vector of length 0.")
        return Vec3(self.x / length, self.y / length, self.w)

    def ClockwiseOrthogonal2D(self):
        return Vec3(self.y, -self.x, self.w)

    def CounterClockwiseOrthogonal2D(self):
        return Vec3(-self.y, self.x, self.w)

    def Rotate2D(self, angle: float):
        cos_theta = cos(angle)
        sin_theta = sin(angle)

        x = (self.x*cos_theta) - (self.y*sin_theta)
        y = (self.x*sin_theta) + (self.y*cos_theta)
        
        return Vec3(x, y, self.w)

    def RotateCosTSinT2D(self, cos_theta: float, sin_theta: float):
        x = (self.x*cos_theta) - (self.y*sin_theta)
        y = (self.x*sin_theta) + (self.y*cos_theta)

        return Vec3(x, y, self.w)
        
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

    def ScalerMul(self, scaler: Union[int, float]):
        new_mat = Mat3()
        for r, row in enumerate(self.mat):
            for c, val in enumerate(row):
                new_mat.mat[r][c] = scaler * val

        return new_mat

    def VecMul(self, vec: Vec3):
        new_vec = Vec3()
            
        new_vec.x = (self.mat[0][0] * vec.x) + (self.mat[0][1] * vec.y) + (self.mat[0][2] * vec.w)
        new_vec.y = (self.mat[1][0] * vec.x) + (self.mat[1][1] * vec.y) + (self.mat[1][2] * vec.w)
        new_vec.w = (self.mat[2][0] * vec.x) + (self.mat[2][1] * vec.y) + (self.mat[2][2] * vec.w)

        return new_vec

    def MatMul(self, mat: Mat3):
        new_mat = Mat3()

        for row_left in range(3):
            for col_rigth in range(3):
                for i in range(3):
                    new_mat.mat[row_left][col_rigth] += self.mat[row_left][i] * mat.mat[i][col_rigth]

        return new_mat

    @overload
    def __mul__(self, other: Mat3) -> Mat3: ...

    @overload
    def __mul__(self, other: Vec3) -> Vec3: ...

    @overload
    def __mul__(self, other: Union[int, float]) -> Vec3: ...

    def __mul__(self, other: Union[Mat3, Vec3, int, float]) -> Union[Vec3, Mat3]:
        if isinstance(other, Mat3): # Mat-Mat multiplication
            return self.MatMul(other)
        elif isinstance(other, Vec3): # Mat-vec multiplication
            return self.VecMul(other)
        else: # scalar-Mat multiplication
            return self.ScalerMul(other)

    @staticmethod
    def ScaleIndependent(x: Union[int, float], y: Union[int, float]):
        return Mat3(
            (
                (x, 0, 0), 
                (0, y, 0), 
                (0, 0, 1)
            )
        )

    @staticmethod
    def Scale(factor: Union[int, float]):
        return Mat3.ScaleIndependent(factor, factor)

    @staticmethod
    def Identity():
        return Mat3.Scale(1)

    @staticmethod
    def FlipY():
        return Mat3(
            (
                (1, 0, 0), 
                (0, -1, 0), 
                (0, 0, 1)
            )
        )

    @staticmethod
    def Rotation(theta: float):
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        
        return Mat3(
            (
                (cos_theta, -sin_theta, 0), 
                (sin_theta, cos_theta, 0), 
                (0, 0, 1)
            )
        )

    @staticmethod
    def RotationCosTSinT(cos_theta: float, sin_theta: float):
        return Mat3(
            (
                (cos_theta, -sin_theta, 0), 
                (sin_theta, cos_theta, 0), 
                (0, 0, 1)
            )
        )

    @staticmethod
    def Translation(x: Union[int, float], y: Union[int, float]):
        return Mat3(
            (
                (1, 0, x), 
                (0, 1, y), 
                (0, 0, 1)
            )
        )

    @staticmethod
    def TranslationVec(vec: Vec2):
        return Mat3(
            (
                (1, 0, vec.x), 
                (0, 1, vec.y), 
                (0, 0, 1)
            )
        )

class Rect:
    def __init__(self, left: float, right: float, top: float, bottom: float):
        self.left: float = float(left)
        self.right: float = float(right)
        self.top: float = float(top)
        self.bottom: float = float(bottom)

    def __repr__(self):
        return f"Rect({self.left:.3f}, {self.right:.3f}, {self.top:.3f}, {self.bottom:.3f})"

    def TranslateBy(self, offset: Vec2):
        self.left += offset.x
        self.right += offset.x
        self.top += offset.y
        self.bottom += offset.y

    def SetPosition(self, position: Vec2):
        hw = (self.right - self.left) / 2
        hh = (self.top - self.bottom) / 2

        self.left = position.x - hw
        self.right = position.x + hw
        self.bottom = position.y - hh
        self.top = position.y + hh

    @classmethod
    def FromVec2(cls, top_left: Vec2, bottom_right: Vec2):
        return cls(top_left.x, bottom_right.x, top_left.y, bottom_right.y)

    @classmethod
    def FromWH(cls, middle_point: Vec2, width: float, height: float):
        width_div_2 = width/2
        height_div_2 = height/2
        return cls(
            middle_point.x - width_div_2, 
            middle_point.x + width_div_2, 
            middle_point.y + height_div_2, 
            middle_point.y - height_div_2
        )

    def PointContain(self, point: Vec2):
        return (
            self.left < point.x
            and self.right > point.x
            and self.bottom < point.y
            and self.top > point.y
        )

    def Intersects(self, other: "Rect"):
        return not (self.right < other.left
                    or self.left > other.right
                    or self.top < other.bottom
                    or self.bottom > other.top)

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

class Surface:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
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

def DistancePointLine(l0: Vec2, l1: Vec2, p: Vec2):
    a = l0.y - l1.y
    b = l1.x - l0.x
    c = (l0.x * l1.y) - (l1.x * l0.y)

    return abs( (a * p.x) + (b * p.y) + c ) / sqrt( (a * a) + (b * b) )

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
        self.special_keys = {
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

        self.delay = delay
        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self.window_name = window_name
        self.surface = Surface(frame_width, frame_height)

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

    def VertexInScreen(self, vertex: Vec2):
        return (
            vertex.x > 0 and 
            vertex.y > 0 and 
            vertex.x < self.surface.GetFrameHeight() and 
            vertex.y < self.surface.GetFrameWidth()
        )

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

    def DrawLineSimpleVec(self, p0: Vec2, p1: Vec2, color: Color, clip: bool = False):

        if clip:
            x_max = self.surface.GetFrameWidth() - 1
            y_max = self.surface.GetFrameHeight() - 1

            p0.x = max(p0.x, 0)
            p0.x = min(p0.x, x_max)
            p1.x = max(p1.x, 0)
            p1.x = min(p1.x, x_max)

            p0.y = max(p0.y, 0)
            p0.y = min(p0.y, y_max)
            p1.y = max(p1.y, 0)
            p1.y = min(p1.y, y_max)

        m = 0.0
        if p0.x != p1.x:
            m = (p1.y - p0.y) / (p1.x - p0.x)

        if p0.x != p1.x and abs(m) <= 1.0:
            if(p0.x > p1.x):
                p1, p0 = p0, p1

            b = p0.y - m * p0.x

            for x in range(int(p0.x), int(p1.x)):
                y = (m * x) + b
                self.PutPixel(x, int(y), color)

        elif p0.y != p1.y:
            if(p0.y > p1.y):
                p1, p0 = p0, p1

            m = (p1.x - p0.x) / (p1.y - p0.y)
            b = p0.x - m * p0.y

            for y in range(int(p0.y), int(p1.y)):
                x = (m * y) + b
                self.PutPixel(int(x), y, color)

    def DrawClosePolyline(self, verts: list[Vec2],  color: Color):
        for i in range(len(verts)):
            v_0 = verts[i]
            v_1 = verts[(i + 1)%len(verts)]
            if(self.VertexInScreen(v_0) or self.VertexInScreen(v_1)):
                self.DrawLineVec(v_0, v_1, color)

class Drawable:
    def __init__(self, model: list[Vec2], color: Color):
        self.model: list[Vec2] = model
        self.transform: Mat3 = Mat3.Identity()
        self.color: Color = color

    def ApplyTransformation(self, transformation: Mat3):
        self.transform = transformation * self.transform

    def Render(self, gfx: Graphics):

        for i, v in enumerate(self.model):
            self.model[i] = Vec2.FromVec3(self.transform * Vec3.FromVec2(v))

        gfx.DrawClosePolyline(self.model, self.color)

class CoordinateTransformer:
    def __init__(self, graphics: Graphics):
        self.gfx = graphics

    def Draw(self, drawable: Drawable):
        offset = Vec2(self.gfx.surface.GetFrameWidth() / 2, self.gfx.surface.GetFrameHeight() / 2)
        # Convert vertices from mathematical coordinates to screen coordinates:
        # - In screen space, the origin (0,0) is at the top-left corner.
        # - The +Y axis points downward, so we flip the Y values.
        # - Then we offset all points so that the origin is centered in the frame.
        # drawable.ScaleIndependent(1.0, -1.0)
        # drawable.Translate(offset)
        drawable.ApplyTransformation(
            Mat3.TranslationVec(offset) * Mat3.ScaleIndependent(1.0, -1.0)
        )
        drawable.Render(self.gfx)

class Camera:
    def __init__(self, coordinate_transformer: CoordinateTransformer):
        self.position = Vec2()
        self.zoom = 1.0
        self.angle = 0.0
        self.ct = coordinate_transformer

    def GetPosition(self): return self.position

    def MoveBy(self, offset: Vec2): self.position += offset
    def MoveTo(self, position_in: Vec2): self.position = position_in

    def Zoom(self, val: float):
        self.zoom *= val

    def Rotate(self, angle: float):
        self.angle = (self.angle + angle) % tau

    def GetAngle(self):
        return self.angle

    def GetZoomLevel(self): return self.zoom

    def ScreenToWorldCoordinate(self, c: Vec2):
        if self.zoom == 0:
            raise ValueError("Camera zoom cannot be zero.")

        sw = self.ct.gfx.surface.GetFrameWidth()
        sh = self.ct.gfx.surface.GetFrameHeight()
        screen_offset = Vec2(c.x - sw / 2, -(c.y - sh / 2)) / self.zoom
        return self.position + screen_offset.Rotate(-self.angle)

    def GetViewportRect(self) -> Rect:
        zoom_factor = 1.0 / self.zoom
        screen_width = self.ct.gfx.surface.GetFrameWidth()
        screen_height = self.ct.gfx.surface.GetFrameHeight()

        a = screen_width * zoom_factor
        b = screen_height * zoom_factor

        diagonal = sqrt((a*a) + (b*b))
        return Rect.FromWH(self.position, diagonal, diagonal)

    def Draw(self, drawable: Drawable):
        drawable.ApplyTransformation(
            Mat3.Scale(self.zoom) * Mat3.Rotation(self.angle) * Mat3.TranslationVec(-self.position)
        )
        self.ct.Draw(drawable)

class Scene(ABC):
    def __init__(self):
        self.camera: Union[Camera, None] = None

    @abstractmethod
    def CompsSetupComplete(self): pass
         
    def SetComps(self, camera: Camera):
        self.camera = camera
        self.CompsSetupComplete()

    @abstractmethod
    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float): pass

    @abstractmethod
    def Draw(self): pass

class Game:
    def __init__(self, frame_width: int, frame_height: int, fps: float, scenes : list[Scene]):
        self.main_loop_active = True
        window_name = "Canvas"
        self.dt = 1.0 / fps
        time_per_frame_ms = self.dt * 1000
        self.gfx = Graphics(window_name, frame_width, frame_height, int(time_per_frame_ms))
        self.ct = CoordinateTransformer(self.gfx)
        self.camera = Camera(self.ct)

        self.c_scene_id = 0
        self.scenes = scenes
        for scene in scenes:
            scene.SetComps(self.camera)

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

class Entity(ABC):
    def __init__(self, model: list[Vec2], bbox: Union[Rect, None], position: Vec2, color: Color):
        self.model = model
        self.bbox: Union[Rect, None] = bbox
        self.angle = 0.0
        self.position = position
        self.scale = 1.0
        self.color = color

    def UpdateModel(self, model: list[Vec2]):
        self.model = model

    def GetPosition(self):
        return self.position

    def SetPosition(self, position: Vec2):
        if self.bbox is not None: self.bbox.SetPosition(position)
        self.position = position

    def SetColor(self, color: Color):
        self.color = color

    def Rotate(self, angle: float):
        self.angle = (self.angle + angle) % tau

    def TranslateBy(self, offset: Vec2):
        if self.bbox is not None: self.bbox.TranslateBy(offset)
        self.position += offset

    def ScaleBy(self, val: float):
        self.scale *= val

    def GetBoundingBox(self):
        return self.bbox

    def GetDrawable(self):
        drawable = Drawable(deepcopy(self.model), self.color)
        drawable.ApplyTransformation(
            Mat3.TranslationVec(self.position) * Mat3.Scale(self.scale) * Mat3.Rotation(self.angle)
        )

        return drawable
