from abc import ABC, abstractmethod
import cv2
import numpy as np

class Vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)

    def __setattr__(self, name, value):
        if name in {"x", "y"}:
            super().__setattr__(name, float(value))
        else:
            super().__setattr__(name, value)

class Color:
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    def __setattr__(self, name, value):
        if name in {"r", "g", "b"}:
            super().__setattr__(name, int(value))
        else:
            super().__setattr__(name, value)

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
        self.canvas[int(y),int(x)] = (color.b, color.g, color.r)

    def GetFrameWidth(self): return self.width
    def GetFrameHeight(self): return self.height

class Mouse:
    def __init__(self):
        self.pos = (0, 0)
        self.lb_down = False
        self.rb_down = False

    def _Callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.pos = (x, y)
            
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.lb_down = True

        elif event == cv2.EVENT_LBUTTONUP:
            self.lb_down = False

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.rb_down = True

        elif event == cv2.EVENT_RBUTTONUP:
            self.rb_down = False
    
    # out: (pos, lb down, rb down)
    def GetState(self) -> tuple[tuple[int, int], bool, bool]:
        return self.pos, self.lb_down, self.rb_down
        
class Keyboard:
    def __init__(self):
        self.key: str | None = None
        # Map special non-printable keys
        self.special_keys = {
            27: "esc",
            32: "space",
            13: "enter",
            9: "tab",
            8: "backspace"
        }

    def _Callback(self, key_code: int):
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
        cv2.setMouseCallback(window_name, self.mouse._Callback)

    def __del__(self):
        cv2.destroyAllWindows()

    def GetFrameWidth(self): return self.surface.GetFrameWidth()
    def GetFrameHeight(self): return self.surface.GetFrameHeight()

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
        self.keyboard._Callback(key_code)

    def GetKey(self):
        return self.keyboard.GetKey()

    def GetMouseState(self):
        return self.mouse.GetState()

    def DrawLine(self, p0: Vec2, p1: Vec2, c: Color):
        x_max = self.GetFrameWidth() - 1
        y_max = self.GetFrameHeight() - 1

        p1.x = max(p1.x, 0)
        p1.x = min(p1.x, x_max)

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
                self.PutPixel(x, y, c)

        elif p0.y != p1.y:
            if(p0.y > p1.y):
                p1, p0 = p0, p1

            m = (p1.x - p0.x) / (p1.y - p0.y)
            b = p0.x - m * p0.y

            for y in range(int(p0.y), int(p1.y)):
                x = (m * y) + b
                self.PutPixel(x, y, c)

class Scene(ABC):
    def __init__(self):
        self.gfx: Graphics | None = None

    @abstractmethod
    def GraphicsSetupComplete(self): pass
         
    def SetGraphics(self, graphics: Graphics):
        self.gfx = graphics
        self.GraphicsSetupComplete()

    @abstractmethod
    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float): pass

    @abstractmethod
    def Draw(self): pass

class Game:
    def __init__(self, frame_width, frame_height, scene: Scene):
        self.main_loop_active = True
        window_name = "Canvas"
        fps = 60.0
        self.dt = 1.0 / fps
        time_per_frame_ms = self.dt * 1000
        self.graphics = Graphics(window_name, frame_width, frame_height, int(time_per_frame_ms))
        self.scene = scene
        self.scene.SetGraphics(self.graphics)

    def UpdateModel(self):
        key = self.graphics.GetKey()
        mouse_stat = self.graphics.GetMouseState()

        self.scene.Update(key, mouse_stat, self.dt)
        self.ManageInputs(key)

    def ComposeFrame(self):
        self.scene.Draw()

    def ManageInputs(self, key: str):
            if(key == 'esc'):
                self.main_loop_active = False

    def Go(self):
        print("Game loop started")
        while self.main_loop_active:
            self.graphics.BeginFrame()

            self.ComposeFrame()

            self.graphics.EndFrame()
            self.graphics.Wait()

            self.UpdateModel()

        print("Game loop ended")
