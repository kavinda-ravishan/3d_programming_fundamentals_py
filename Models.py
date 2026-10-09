from typing import Final, Callable, Any
from Utils import IndexedTriangleList, Vec3, Vec2

class Plain:
    def __init__(self) -> None: ...

    @staticmethod
    def GetPlain(vertex_converter: Callable[[list[Vec3], list[Vec2]], list[Any]], divisions: int = 7, size: float = 1.0):
        n_vertices_side = divisions + 1
        vertices: list[Vec3] = []

        side: float = size / 2.0
        division_size: float = size / float(divisions)
        bottom_left: Vec3 = Vec3(-side, -side, 0.0)

        for y in range(n_vertices_side):
            y_pos: float = float(y) * division_size
            for x in range(n_vertices_side):
                vertices.append(bottom_left + Vec3(float(x) * division_size, y_pos, 0.0))

        indices: list[tuple[int, int, int]] = []
        def vxy2i(x: int, y: int):
            return (y * n_vertices_side) + x;

        for y in range(divisions):
            for x in range(divisions):
                index_array: tuple[int, int, int, int] = (vxy2i( x,y ), vxy2i( x + 1,y ), vxy2i( x,y + 1 ), vxy2i( x + 1,y + 1 ))
                indices.append((index_array[0], index_array[2], index_array[1]))
                indices.append((index_array[1], index_array[2], index_array[3]))

        texture_coordinates: list[Vec2] = []
        t_division_size = 1.0 / float( divisions )
        t_bottom_left = Vec2(0.0, 1.0)

        for y in range(n_vertices_side):
            y_t = -float(y) * t_division_size
            for x in range(n_vertices_side):
                texture_coordinates.append(t_bottom_left + Vec2(float(x) * t_division_size, y_t))

        tverts = vertex_converter(vertices, texture_coordinates)

        return IndexedTriangleList(tverts, indices)

class Cube:
    def __init__(self, ) -> None: ...

    @staticmethod
    def GetPlain(vertex_converter: Callable[[list[Vec3]], list[Any]], size: float = 1.0) -> IndexedTriangleList:
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

        tverts = vertex_converter(vertices)

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
    def GetPlainIndependentFaces(vertex_converter: Callable[[list[Vec3], list[Vec3]], list[Any]], size: float = 1.0) -> IndexedTriangleList:
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

        normals: list[Vec3] = [
            Vec3(0.0, 0.0, -1.0),
            Vec3(0.0, 0.0, -1.0),
            Vec3(0.0, 0.0, -1.0),
            Vec3(0.0, 0.0, -1.0),
            Vec3(0.0, 0.0, 1.0),
            Vec3(0.0, 0.0, 1.0),
            Vec3(0.0, 0.0, 1.0),
            Vec3(0.0, 0.0, 1.0),
            Vec3(-1.0, 0.0, 0.0),
            Vec3(-1.0, 0.0, 0.0),
            Vec3(-1.0, 0.0, 0.0),
            Vec3(-1.0, 0.0, 0.0),
            Vec3(1.0, 0.0, 0.0),
            Vec3(1.0, 0.0, 0.0),
            Vec3(1.0, 0.0, 0.0),
            Vec3(1.0, 0.0, 0.0),
            Vec3(0.0, -1.0, 0.0),
            Vec3(0.0, -1.0, 0.0),
            Vec3(0.0, -1.0, 0.0),
            Vec3(0.0, -1.0, 0.0),
            Vec3(0.0, 1.0, 0.0),
            Vec3(0.0, 1.0, 0.0),
            Vec3(0.0, 1.0, 0.0),
            Vec3(0.0, 1.0, 0.0)
        ]

        tverts = vertex_converter(vertices, normals)

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
    def GetSkinned(vertex_converter: Callable[[list[Vec3], list[Vec2]], list[Any]], size: float = 1.0) -> IndexedTriangleList:
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
        
        tverts = vertex_converter(vertices, texture_coordinates)

        return IndexedTriangleList(
            tverts, [
                (0, 2, 1), (2, 3, 1),
                (4, 8, 5), (5, 8, 9),
                (2, 6, 3), (3, 6, 7),
                (4, 5, 7), (4, 7, 6),
                (2, 10, 11), (2, 11, 6),
                (12, 3, 7), (12, 7, 13)
            ])
