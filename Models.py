from typing import Final, Callable, Any
from math import pi
from Utils import IndexedTriangleList, Vec3, Vec2, Mat3

class Sphere:
    def __init__(self) -> None:
        ...

    @staticmethod
    def GetPlain(vertex_converter: Callable[[list[Vec3], list[Vec3]], list[Any]], 
                 radius: float = 1.0, latDiv: int = 12, longDiv: int = 24):
        base = Vec3(0.0, 0.0, radius)
        latitude_angle = pi / latDiv
        longitude_angle = 2.0 * pi / longDiv

        vertices: list[Vec3] = []
        for iLat in range(1, latDiv):
            lat_base = base * Mat3.RotationX(latitude_angle * iLat)
            for iLong in range(longDiv):
                vertices.append(lat_base * Mat3.RotationZ(longitude_angle * iLong))

        # add the cap vertices
        i_north_pole = len(vertices)
        vertices.append(base)
        i_south_pole = len(vertices)
        vertices.append(-base)

        def calc_idx(iLat: int, iLong: int) -> int:
            return iLat * longDiv + iLong

        indices: list[tuple[int, int, int]] = []
        for iLat in range(latDiv - 2):
            for iLong in range(longDiv - 1):
                indices.append((calc_idx(iLat, iLong), calc_idx(iLat, iLong + 1), calc_idx(iLat + 1, iLong)))
                indices.append((calc_idx(iLat, iLong + 1), calc_idx(iLat + 1, iLong + 1), calc_idx(iLat + 1, iLong)))
            # wrap band
            indices.append((calc_idx(iLat, longDiv - 1), calc_idx(iLat, 0), calc_idx(iLat + 1, longDiv - 1)))
            indices.append((calc_idx(iLat, 0), calc_idx(iLat + 1, 0), calc_idx(iLat + 1, longDiv - 1)))

        # cap fans
        for iLong in range(longDiv - 1):
            # north
            indices.append((i_north_pole, calc_idx(0, iLong + 1), calc_idx(0, iLong)))
            # south
            indices.append((calc_idx(latDiv - 2, iLong + 1), i_south_pole, calc_idx(latDiv - 2, iLong)))

        # wrap triangles
        indices.append((i_north_pole, calc_idx(0, 0), calc_idx(0, longDiv - 1)))
        indices.append((calc_idx(latDiv - 2, 0), i_south_pole, calc_idx(latDiv - 2, longDiv - 1)))

        normals: list[Vec3] = []
        for v in vertices:
            normals.append(v.GetNormalized())

        tverts = vertex_converter(vertices, normals)

        return IndexedTriangleList(tverts, indices)

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
