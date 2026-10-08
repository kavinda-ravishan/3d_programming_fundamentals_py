from typing import Final
from Utils import IndexedTriangleList, Vec3, Vec2
from Effects import TextureEffect, SolidEffect, VertexPositionColorEffect

class Cube:
    def __init__(self, ) -> None: ...

    @staticmethod
    def GetPlain(size: float = 1.0) -> IndexedTriangleList:
        side: Final[float] = size / 2.0
        vertices: list[Vec3] = [
            Vec3( -side,-side,-side ), # 0
            Vec3( side,-side,-side ), # 1
            Vec3( -side,side,-side ), # 2
            Vec3( side,side,-side ), # 3
            Vec3( -side,-side,side ), # 4
            Vec3( side,-side,side ), # 5
            Vec3( -side,side,side ), # 6
            Vec3( side,side,side ) # 7
        ]

        tverts = [
            SolidEffect.Vertex(position)
            for _, position in enumerate(vertices)
        ]

        return IndexedTriangleList(
            tverts, [
				(0,2,1), (2,3,1),
				(1,3,5), (3,7,5),
				(2,6,3), (3,6,7),
				(4,5,7), (4,7,6),
				(0,4,2), (2,4,6),
				(0,1,4), (1,5,4)
            ])

    @staticmethod
    def GetPlainIndependentFaces(size: float = 1.0) -> IndexedTriangleList:
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
            Vec3(side, -side, side)    # 13
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
            convert_tex_coord(-1.0, 2.0)
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
                (12, 3, 7), (12, 7, 13)
            ])
