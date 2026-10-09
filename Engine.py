from abc import ABC, abstractmethod
from typing import Any, Union, Final, Generic, Optional
from math import ceil
import numpy as np
import cv2
from typing import Union, Generic
from Utils import VertexT, Vec2, Color, IndexedTriangleList, Triangle, Interpolate

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
        for i, triangle_indices in enumerate(indices):
            v0 = vertices[triangle_indices[0]]
            v1 = vertices[triangle_indices[1]]
            v2 = vertices[triangle_indices[2]]

            if((v1.pos - v0.pos).Cross(v2.pos - v0.pos).Dot(v0.pos) <= 0.0):
                self._ProcessTriangle(v0, v1, v2, i)

    def _ProcessTriangle(self, v0: VertexT, v1: VertexT, v2: VertexT, triangle_index: int):
        self._PostProcessTriangleVertices(self.effect.gs(v0, v1, v2, triangle_index))

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
            if it_edge1.pos.x == it_edge0.pos.x: continue
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
