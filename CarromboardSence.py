from __future__ import annotations
from math import pi, sin, cos
from random import uniform
from Utils import Entity, Vec2, Rect, Color, Scene, DistancePointLine
from PolylinesScene import Star

class Ball(Entity):
    def __init__(self, position: Vec2, radius: float, velocity: Vec2, color: Color):
        super().__init__(Star.Make(radius, radius, 8), Ball.BoundingBox(), position, color)
        self.radius = radius
        self.velocity = velocity

    def Update(self, dt: float):
        self.TranslateBy(self.velocity * dt)

    def GetRadius(self):
        return self.radius

    def GetVelocity(self):
        return self.velocity

    def SetVelocity(self, velocity: Vec2):
        self.velocity = velocity

    @staticmethod
    def BoundingBox() -> Rect | None:
        return None

class Balls:
    def __init__(self):
        self.limit = 600.0
        self.spawn_point = Vec2(0, 0)
        self.colors = [
            Color.White,
            Color.Black,
            Color.Gray,
            Color.LightGray,
            Color.Red,
            Color.Green,
            Color.Blue,
            Color.Yellow,
            Color.Cyan,
            Color.Magenta
        ]
        self.balls: list[Ball] = []

    def GetBalls(self): return self.balls

    def SpawnNewBall(self):
        # Pick a random angle in radians (0 to 2π)
        angle = uniform(0, 2 * pi)
        velocity = uniform(300, 600)

        # Velocity components with magnitude velocity
        vx = velocity * cos(angle)
        vy = velocity * sin(angle)

        new_velocity = Vec2(vx, vy)

        color = self.colors[len(self.balls)%len(self.colors)]
        self.balls.append(
            Ball(self.spawn_point, 25, new_velocity, color)
        )

class Plank:
    def __init__(self, p0: Vec2, p1: Vec2):
        self.p0: Vec2 = p0
        self.p1: Vec2 = p1
        self.surface_vec: Vec2 = self.p0 - self.p1
        self.clockwise_orthogonal_vec: Vec2 = self.surface_vec.ClockwiseOrthogonal()

    def GetLinePoints(self):
        return (self.p0, self.p1)

    def GetSurfaceVec(self) -> Vec2:
        return self.surface_vec

    def GetClockwiseOrthogonalVec(self) -> Vec2:
        return self.clockwise_orthogonal_vec

class Carromboard(Entity):
    def __init__(self, size: float):
        size_div_2 = size / 2
        p_top_right = Vec2(size_div_2, size_div_2)
        p_top_left = Vec2(-size_div_2, size_div_2)
        p_bottom_left = Vec2(-size_div_2, -size_div_2)
        p_bottom_right = Vec2(size_div_2, -size_div_2)

        super().__init__(Carromboard.Make(
            p_top_right,
            p_top_left,
            p_bottom_left,
            p_bottom_right
        ), Carromboard.BoundingBox(), Vec2(0, 0), Color.Yellow)

        self.planks = [
            Plank(p_top_right, p_top_left), # plank_top
            Plank(p_top_left, p_bottom_left), # plank_left
            Plank(p_bottom_left, p_bottom_right), # plankp_bottom
            Plank(p_bottom_right, p_top_right) # plankp_left
        ]

    def GetPlanks(self) -> list[Plank]:
        return self.planks

    @staticmethod
    def Make(
        p_top_right: Vec2,
        p_top_left: Vec2,
        p_bottom_left: Vec2,
        p_bottom_right: Vec2
    ):
        carromboard: list[Vec2] = []
        carromboard.append(p_top_right)
        carromboard.append(p_top_left)
        carromboard.append(p_bottom_left)
        carromboard.append(p_bottom_right)

        return carromboard

    @staticmethod
    def BoundingBox() -> Rect | None:
        return None

class CarromboardSence(Scene):
    def __init__(self):
        super().__init__()
        self.carromboard = Carromboard(750)
        
        self.balls = Balls()

    def CompsSetupComplete(self): ...

    def Update(self, key: str, mouse_stat: tuple[tuple[int, int], bool, bool], dt: float):
        m_x = mouse_stat[0][0]
        m_y = mouse_stat[0][1]
        m_lb = mouse_stat[1]
        m_rb = mouse_stat[2]

        speed = 10.0

        if 'w' == key: self.camera.MoveBy(Vec2(0.0, speed))
        elif 's' == key: self.camera.MoveBy(Vec2(0.0, -speed))
        elif 'd' == key: self.camera.MoveBy(Vec2(speed, 0.0))
        elif 'a' == key: self.camera.MoveBy(Vec2(-speed, 0.0))

        elif 'q' == key: self.camera.Zoom(0.95)
        elif 'e' == key: self.camera.Zoom(1.05)
        
        if m_lb: self.balls.SpawnNewBall()

        for i in range(len(self.balls.GetBalls())):

            # ball-ball collision 
            for j in range(len(self.balls.GetBalls())):
                if(i == j): continue

                ball_i = self.balls.GetBalls()[i]
                ball_j = self.balls.GetBalls()[j]
                ball_i_velocity = ball_i.GetVelocity()
                ball_j_velocity = ball_j.GetVelocity()
                ball_i_position = ball_i.GetPosition()
                ball_j_position = ball_j.GetPosition()
                ball_i_radius = ball_i.GetRadius()
                ball_j_radius = ball_j.GetRadius()

                balls_delta_position = ball_i_position - ball_j_position
                balls_dist = balls_delta_position.Len()
                balls_overlap = (ball_i_radius + ball_j_radius) - balls_dist
                
                if balls_overlap > 0:
                    # Normalize direction
                    correction_dir = balls_delta_position.Normalize()

                    # Push each ball half the overlap distance
                    ball_i.SetPosition(ball_i_position + correction_dir * (balls_overlap / 2))
                    ball_j.SetPosition(ball_j_position - correction_dir * (balls_overlap / 2))

                if((ball_i_position - ball_j_position).Len() < (ball_i_radius + ball_j_radius)):
                    self.balls.GetBalls()[i].SetVelocity(ball_j_velocity)
                    self.balls.GetBalls()[j].SetVelocity(ball_i_velocity)

            # ball-plank collision 
            for plank in self.carromboard.GetPlanks():
                plank_surface_vec = plank.GetSurfaceVec().Normalize()
                ball = self.balls.GetBalls()[i]
                ball_position = self.balls.GetBalls()[i].GetPosition()
                plank_normal = plank.GetClockwiseOrthogonalVec()

                ball_velocity = ball.GetVelocity()
                if plank_normal * ball_velocity < 0.0:
                    plank_points = plank.GetLinePoints()
                    plank_p0 = plank_points[0]
                    plank_p1 = plank_points[1]
                    if(DistancePointLine(plank_p0, plank_p1, ball_position) < ball.GetRadius()):
                        v = ball_velocity
                        w = plank_surface_vec
                        ball_new_velocity = (w * (v*w) * 2.0) - v
                        self.balls.GetBalls()[i].SetVelocity(ball_new_velocity)

            self.balls.GetBalls()[i].Update(dt)

    def Draw(self):
        self.entities: list[Entity] = [self.carromboard, *self.balls.GetBalls()]

        vp_rect = self.camera.GetViewportRect()
        for entity in self.entities:
            if entity.GetBoundingBox() is None or vp_rect.Intersects(entity.GetBoundingBox()):
                self.camera.Draw(entity.GetDrawable())
