from __future__ import annotations
from typing import Union
from math import pi, sin, cos
from random import uniform
from Utils import Entity, Vec2, Rect, Color, Scene, DistancePointLine
from PolylinesScene import Star

class Ball(Entity):
    def __init__(self, position: Vec2, radius: float, velocity: Vec2, color: Color):
        super().__init__(Star.Make(radius, radius, 8), Ball.BoundingBox(), position, color)
        self.radius = radius
        self.mass = pi * radius * radius
        self.velocity = velocity

    def Update(self, dt: float):
        self.TranslateBy(self.velocity * dt)

    def GetMass(self):
        return self.mass

    def GetRadius(self):
        return self.radius

    def GetVelocity(self):
        return self.velocity

    def SetVelocity(self, velocity: Vec2):
        self.velocity = velocity

    @staticmethod
    def BoundingBox() -> Union[Rect, None]:
        return None

class Balls:
    def __init__(self):
        self.spawn_point = Vec2(0, 0)
        self.colors = [
            Color.White,
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
        radius = uniform(20, 100)

        # Velocity components with magnitude velocity
        new_velocity = Vec2(velocity * cos(angle), velocity * sin(angle))

        color = self.colors[len(self.balls)%len(self.colors)]
        self.balls.append(Ball(self.spawn_point, radius, new_velocity, color))

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

        # Carromboard 1
        p_top_right = Vec2(size_div_2, size_div_2)
        p_top_left = Vec2(-size_div_2, size_div_2)
        p_bottom_left = Vec2(-size_div_2, -size_div_2)
        p_bottom_right = Vec2(size_div_2, -size_div_2)

        # Carromboard 2
        # p_top_right = Vec2(0, size_div_2)
        # p_top_left = Vec2(-size_div_2, 0)
        # p_bottom_left = Vec2(0, -size_div_2)
        # p_bottom_right = Vec2(size_div_2, 0)

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

    def HandleGravity(self, i: int, dt: float):
        ball = self.balls.GetBalls()[i]
        ball_velocity = ball.GetVelocity()
        gravity = Vec2(0, -2000)
        ball.SetVelocity(ball_velocity + (gravity * dt))

    def HandleBallBallCollision(self, i: int):
        for j in range(i+1, len(self.balls.GetBalls())):
            ball_i = self.balls.GetBalls()[i]
            ball_j = self.balls.GetBalls()[j]

            ball_i_velocity = ball_i.GetVelocity()
            ball_i_position = ball_i.GetPosition()
            ball_i_mass = ball_i.GetMass()
            ball_i_radius = ball_i.GetRadius()

            ball_j_velocity = ball_j.GetVelocity()
            ball_j_position = ball_j.GetPosition()
            ball_j_mass = ball_j.GetMass()
            ball_j_radius = ball_j.GetRadius()

            balls_position_delta_vec = ball_i_position - ball_j_position
            balls_dist = balls_position_delta_vec.Len()
            balls_overlap = (ball_i_radius + ball_j_radius) - balls_dist
            balls_overlap_div_by_2 = balls_overlap / 2
            
            # Prevent division by zero if balls are exactly on top of each other
            if balls_dist == 0:
                ball_i.SetPosition(ball_i_position + balls_overlap_div_by_2)
                ball_j.SetPosition(ball_j_position - balls_overlap_div_by_2)
                continue
            
            if balls_overlap > 0:
                # 1. Normalize direction
                correction_dir = balls_position_delta_vec.Normalize()

                # 2. Push each ball half the overlap distance (Positional Correction)
                ball_i.SetPosition(ball_i_position + (correction_dir * balls_overlap_div_by_2))
                ball_j.SetPosition(ball_j_position - (correction_dir * balls_overlap_div_by_2))

                # 3. Relative Velocity
                rel_velocity = ball_i_velocity - ball_j_velocity

                # 4. Project relative velocity onto the collision normal vector (Dot Product)
                vel_along_normal = rel_velocity * correction_dir

                # 5. Only resolve if they are actually moving toward each other
                if vel_along_normal < 0:
                    m_sum = ball_i_mass + ball_j_mass

                    # Calculate impulse vector
                    impulse = correction_dir * vel_along_normal

                    # 6. Apply impulse to update velocities
                    ball_i.SetVelocity(ball_i_velocity - ((impulse*2*ball_j_mass)/m_sum))
                    ball_j.SetVelocity(ball_j_velocity + ((impulse*2*ball_i_mass)/m_sum))

    def HandleBallPlankCollision(self, i: int):
        # ball-plank collision 
        for plank in self.carromboard.GetPlanks():
            plank_surface_vec = plank.GetSurfaceVec().Normalize()
            plank_normal = plank.GetClockwiseOrthogonalVec()

            ball = self.balls.GetBalls()[i]
            ball_velocity = ball.GetVelocity()
            ball_position = ball.GetPosition()
            ball_radius = ball.GetRadius()

            if plank_normal * ball_velocity < 0.0:
                plank_points = plank.GetLinePoints()
                plank_p0 = plank_points[0]
                plank_p1 = plank_points[1]
                if(DistancePointLine(plank_p0, plank_p1, ball_position) < ball_radius):
                    v = ball_velocity
                    w = plank_surface_vec
                    ball_new_velocity = (w * (v*w) * 2.0) - v
                    ball.SetVelocity(ball_new_velocity)

    def Update(self, key: Union[str, None], mouse_stat: tuple[Vec2, bool, bool], dt: float):
        # m_c = mouse_stat[0]
        m_lb = mouse_stat[1]
        # m_rb = mouse_stat[2]

        speed = 10.0
        camera = self.camera
        if camera is None:
            raise Exception("Camera is not initialized for this scene.")

        if 'w' == key: camera.MoveBy(Vec2(0.0, speed))
        elif 's' == key: camera.MoveBy(Vec2(0.0, -speed))
        elif 'd' == key: camera.MoveBy(Vec2(speed, 0.0))
        elif 'a' == key: camera.MoveBy(Vec2(-speed, 0.0))

        elif 'q' == key: camera.Zoom(0.95)
        elif 'e' == key: camera.Zoom(1.05)

        if m_lb: self.balls.SpawnNewBall()

        for i in range(len(self.balls.GetBalls())):
            # self.HandleGravity(i, dt)
            self.HandleBallBallCollision(i)
            self.HandleBallPlankCollision(i)
            self.balls.GetBalls()[i].Update(dt)

    def Draw(self):
        self.entities: list[Entity] = [self.carromboard, *self.balls.GetBalls()]
        
        camera = self.camera
        if camera is None:
            raise Exception("Camera is not initialized for this scene.")

        vp_rect = camera.GetViewportRect()
        for entity in self.entities:
            bbox = entity.GetBoundingBox() 
            if bbox is None or vp_rect.Intersects(bbox):
                camera.Draw(entity.GetDrawable())
