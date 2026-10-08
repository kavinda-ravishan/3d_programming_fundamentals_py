from typing import Union, Generic
from Utils import VertexT, VertexArithmetic, Vec3, Vec2, Mat3, Color, Triangle
from Engine import Surface

class DefaultGeometryShader(Generic[VertexT]):
    def __call__(self, in0: VertexT, in1: VertexT, in2: VertexT, triangle_index: int):
        return Triangle(in0, in1, in2)

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

class VertexFlatEffect(Generic[VertexT]):
    class Vertex(VertexArithmetic):
        def __init__(self, pos: Vec3, n: Vec3):
            self.pos: Vec3 = pos
            self.n: Vec3 = n

        def UpdatePos(self, pos: Vec3, src: "VertexFlatEffect.Vertex"):
            return VertexFlatEffect.Vertex(pos, src.n)

        def __add__(self, other: Union["VertexFlatEffect.Vertex", float, int]):
            if isinstance(other, VertexFlatEffect.Vertex):
                return VertexFlatEffect.Vertex(self.pos + other.pos, self.n)
            else:
                return VertexFlatEffect.Vertex(self.pos + other, self.n)

        def __sub__(self, other: Union["VertexFlatEffect.Vertex", float, int]):
            if isinstance(other, VertexFlatEffect.Vertex):
                return VertexFlatEffect.Vertex(self.pos - other.pos, self.n)
            else:
                return VertexFlatEffect.Vertex(self.pos - other, self.n)

        def __mul__(self, other: Union["VertexFlatEffect.Vertex", float, int]):
            if isinstance(other, VertexFlatEffect.Vertex):
                return VertexFlatEffect.Vertex(self.pos * other.pos, self.n)
            else:
                return VertexFlatEffect.Vertex(self.pos * other, self.n)

        def __truediv__(self, other:Union["VertexFlatEffect.Vertex", float, int]):
            if isinstance(other, VertexFlatEffect.Vertex):
                return VertexFlatEffect.Vertex(self.pos / other.pos, self.n)
            else:
                return VertexFlatEffect.Vertex(self.pos / other, self.n)

    class VSOut(VertexArithmetic):
        def __init__(self, pos: Vec3, color: Vec3):
            self.pos: Vec3 = pos
            self.color: Vec3 = color

        def UpdatePos(self, pos: Vec3, src: "VertexFlatEffect.VSOut"):
            return VertexFlatEffect.VSOut(pos, src.color)

        def __add__(self, other: Union["VertexFlatEffect.VSOut", float, int]):
            if isinstance(other, VertexFlatEffect.VSOut):
                return VertexFlatEffect.VSOut(self.pos + other.pos, self.color + other.color)
            else:
                return VertexFlatEffect.VSOut(self.pos + other, self.color + other)

        def __sub__(self, other: Union["VertexFlatEffect.VSOut", float, int]):
            if isinstance(other, VertexFlatEffect.VSOut):
                return VertexFlatEffect.VSOut(self.pos - other.pos, self.color - other.color)
            else:
                return VertexFlatEffect.VSOut(self.pos - other, self.color - other)

        def __mul__(self, other: Union["VertexFlatEffect.VSOut", float, int]):
            if isinstance(other, VertexFlatEffect.VSOut):
                return VertexFlatEffect.VSOut(self.pos * other.pos, self.color * other.color)
            else:
                return VertexFlatEffect.VSOut(self.pos * other, self.color * other)

        def __truediv__(self, other:Union["VertexFlatEffect.VSOut", float, int]):
            if isinstance(other, VertexFlatEffect.VSOut):
                return VertexFlatEffect.VSOut(self.pos / other.pos, self.color / other.color)
            else:
                return VertexFlatEffect.VSOut(self.pos / other, self.color / other)

    class VertexShader:
        def __init__(self):
            self.rotation: Mat3 = Mat3().Identity()
            self.translation : Vec3 = Vec3()

            self.dir: Vec3 = Vec3(0.0, 0.0, 1.0)
            # this is the intensity if direct light from source
		    # color light so need values per color component
            self.diffuse: Vec3 = Vec3(1.0, 1.0, 1.0)
            # this is intensity of indirect light that bounces off other obj in scene
		    # color light so need values per color component
            self.ambient: Vec3 = Vec3(0.1, 0.1, 0.1)
            # color of material (how much light of each color is reflected)
            self.color: Vec3 = Vec3(0.8, 0.85, 1.0)

        def BindRotation(self, rotation: Mat3):
            self.rotation = rotation

        def BindTranslation(self, translation: Vec3):
            self.translation = translation

        def SetLightDirection(self, dl: Vec3):
            self.dir = dl

        def __call__(self, input: VertexFlatEffect.Vertex) -> VertexFlatEffect.VSOut:

            # calculate intensity based on angle of incidence
            d = self.diffuse * max(0.0, -(input.n * self.rotation).Dot(self.dir))
			# add diffuse+ambient, filter by material color, saturate and scale
            c = (self.color * (d + self.ambient)).Saturate() * 255.0

            pos = (input.pos * self.rotation) + self.translation

            # transform vertices using matrix + vector
            return VertexFlatEffect.VSOut(pos, c)

    class PixelShader:
        def __init__(self): ...

        def __call__(self, input: "VertexFlatEffect.VSOut") -> Color:
            return Color.FromVec3(input.color)

    def __init__(self):
        self.ps: VertexFlatEffect.PixelShader = VertexFlatEffect.PixelShader()
        self.vs: VertexFlatEffect.VertexShader = VertexFlatEffect.VertexShader()
        self.gs: DefaultGeometryShader[VertexT] = DefaultGeometryShader[VertexT]()

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

                # transform vertices using matrix + vector
                return VertexPositionColorEffect.VSOut(pos, color)

    class PixelShader:
        def __init__(self): ...

        def __call__(self, input: "VertexPositionColorEffect.VSOut") -> Color:
            return Color.FromVec3(input.color)

    def __init__(self):
        self.ps: VertexPositionColorEffect.PixelShader = VertexPositionColorEffect.PixelShader()
        self.vs: VertexPositionColorEffect.VertexShader = VertexPositionColorEffect.VertexShader()
        self.gs: DefaultGeometryShader[VertexT] = DefaultGeometryShader[VertexT]()

class SolidEffect(Generic[VertexT]):

    class Vertex(VertexArithmetic):
        def __init__(self, pos: Vec3):
            self.pos: Vec3 = pos

        def UpdatePos(self, pos: Vec3, src: "SolidEffect.Vertex"):
            return SolidEffect.Vertex(pos)

        def __add__(self, other: Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos + other.pos)
            else:
                return SolidEffect.Vertex(self.pos + other)

        def __sub__(self, other: Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos - other.pos)
            else:
                return SolidEffect.Vertex(self.pos - other)

        def __mul__(self, other: Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos * other.pos)
            else:
                return SolidEffect.Vertex(self.pos * other)

        def __truediv__(self, other:Union["SolidEffect.Vertex", float, int]):
            if isinstance(other, SolidEffect.Vertex):
                return SolidEffect.Vertex(self.pos / other.pos)
            else:
                return SolidEffect.Vertex(self.pos / other)

    class GSOut(VertexArithmetic):
        def __init__(self, pos: Vec3, color: Color):
            self.pos: Vec3 = pos
            self.color: Color = color

        def UpdatePos(self, pos: Vec3, src: "SolidEffect.GSOut"):
            return SolidEffect.GSOut(pos, src.color)

        def __add__(self, other: Union["SolidEffect.GSOut", float, int]):
            if isinstance(other, SolidEffect.GSOut):
                return SolidEffect.GSOut(self.pos + other.pos, self.color)
            else:
                return SolidEffect.GSOut(self.pos + other, self.color)

        def __sub__(self, other: Union["SolidEffect.GSOut", float, int]):
            if isinstance(other, SolidEffect.GSOut):
                return SolidEffect.GSOut(self.pos - other.pos, self.color)
            else:
                return SolidEffect.GSOut(self.pos - other, self.color)

        def __mul__(self, other: Union["SolidEffect.GSOut", float, int]):
            if isinstance(other, SolidEffect.GSOut):
                return SolidEffect.GSOut(self.pos * other.pos, self.color)
            else:
                return SolidEffect.GSOut(self.pos * other, self.color)

        def __truediv__(self, other:Union["SolidEffect.GSOut", float, int]):
            if isinstance(other, SolidEffect.GSOut):
                return SolidEffect.GSOut(self.pos / other.pos, self.color)
            else:
                return SolidEffect.GSOut(self.pos / other, self.color)

    class GeometryShader:
        def __init__(self) -> None:
            self.triangle_colors: list[Color] = []

            self.dir: Vec3 = Vec3(0.2, -0.5, 1.0)
            # this is the intensity if direct light from source
		    # color light so need values per color component
            self.diffuse: Vec3 = Vec3(1.0, 1.0, 1.0)
            # this is intensity of indirect light that bounces off other obj in scene
		    # color light so need values per color component
            self.ambient: Vec3 = Vec3(0.1, 0.1, 0.1)


        def BindColors(self, colors: list[Color]):
            self.triangle_colors = colors

        def __call__(self, in0: VertexT, in1: VertexT, in2: VertexT, triangle_index: int):

            color_rgb = self.triangle_colors[(int(triangle_index/2))]
            color: Vec3 = Vec3(color_rgb.r / 255, color_rgb.g / 255, color_rgb.b / 255)

            n = (in1.pos - in0.pos).Cross(in2.pos - in0.pos).GetNormalize()
            d = self.diffuse * max(0.0, -(n.Dot(self.dir)))
            c = Color.FromVec3((color * (d + self.ambient)).Saturate() * 255.0)

            out0 = SolidEffect.GSOut(in0.pos, c)
            out1 = SolidEffect.GSOut(in1.pos, c)
            out2 = SolidEffect.GSOut(in2.pos, c)
            return Triangle(out0, out1, out2)

    class PixelShader:
        def __init__(self): ...

        def __call__(self, input: "SolidEffect.GSOut") -> Color:
            return input.color

    def __init__(self):
        self.ps: SolidEffect.PixelShader = SolidEffect.PixelShader()
        self.vs: DefaultVertexShader[VertexT] = DefaultVertexShader[VertexT]()
        self.gs: SolidEffect.GeometryShader = SolidEffect.GeometryShader()

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
        self.gs: DefaultGeometryShader[VertexT] = DefaultGeometryShader[VertexT]()
