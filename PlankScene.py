from __future__ import annotations
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
        self.spawn_point = Vec2(300, -300)

        self.balls: list[Ball] = []

    def GetBalls(self): return self.balls

    def SpawnNewBall(self, ):
        # Base velocity (general direction)
        base_velocity = Vec2(-300, 300)

        # Add small random variation
        variation_x = uniform(-100, 100)
        variation_y = uniform(-100, 100)

        new_velocity = Vec2(
            base_velocity.x + variation_x,
            base_velocity.y + variation_y
        )

        self.balls.append(
            Ball(self.spawn_point, 10, new_velocity, Color.Red)
        )

    def RemoveOutOfBoundBall(self, index: int):
        ball = self.balls[index]
        pos = ball.GetPosition()
        if(abs(pos.x) > self.limit or abs(pos.y) > self.limit):
            self.balls.pop(index)
            return True

        return False

class Plank(Entity):
    def __init__(self, anchor_point: Vec2, free_point: Vec2):
        super().__init__(Plank.Make(anchor_point, free_point), Plank.BoundingBox(), Vec2(0, 0), Color.Yellow)
        self.anchor_point = anchor_point
        self.free_point = free_point

    def GetLinePoints(self):
        return (self.anchor_point, self.free_point)

    def MoveFreeY(self, val: float):
        self.free_point += Vec2(0, val)
        self.UpdateModel(Plank.Make(self.anchor_point, self.free_point))

    @staticmethod
    def Make(anchor_point: Vec2, free_point: Vec2):
        thickness = 5.0

        plank: list[Vec2] = []
        plank.append(anchor_point)
        plank.append(free_point)
        plank.append(Vec2(free_point.x, free_point.y + thickness))
        plank.append(Vec2(anchor_point.x, anchor_point.y + thickness))

        return plank

    @staticmethod
    def BoundingBox() -> Rect | None:
        return None

class PlankScene(Scene):
    def __init__(self):
        super().__init__()
        anchor_point = Vec2(300, 300)
        free_point = Vec2(-350, 0)
        self.plank = Plank(anchor_point, free_point)
        
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
        
        elif 'r' == key: self.plank.MoveFreeY( 5.0)
        elif 'f' == key: self.plank.MoveFreeY(-5.0)

        if m_lb: self.balls.SpawnNewBall()

        plank_points = self.plank.GetLinePoints()
        plank_p0 = plank_points[0]
        plank_p1 = plank_points[1]

        for i in range(len(self.balls.GetBalls()) - 1, -1, -1):

            if(self.balls.RemoveOutOfBoundBall(i)): 
                continue

            ball = self.balls.GetBalls()[i]
            ball_position = self.balls.GetBalls()[i].GetPosition()

            dy = plank_p1.y - plank_p0.y
            dx = plank_p1.x - plank_p0.x

            plank_normal = Vec2()
            if dy == 0.0:
                plank_normal = Vec2(0.0, 1.0 if ball_position.y > plank_p0.y else -1.0)
            elif dx == 0.0:
                plank_normal = Vec2(1.0 if ball_position.x > plank_p0.x else -1.0, 0.0)
            else:
                m = dy / dx
                w = -(dx / dy)
                b = plank_p0.y - (m * plank_p0.x)
                p = ball_position.y - (w * ball_position.x)
                x = (p-b)/(m-w)
                y = (m * x) + b
                plank_normal = ball_position - Vec2(x, y)

            v = ball.GetVelocity()
            if plank_normal * v < 0.0:
                if(DistancePointLine(plank_p0, plank_p1, ball_position) < ball.GetRadius()):
                    w = (plank_p1 - plank_p0).Normalize()
                    new_velocity = (w * (v*w) * 2.0) - v
                    self.balls.GetBalls()[i].SetVelocity(new_velocity)

            self.balls.GetBalls()[i].Update(dt)

    def Draw(self):
        self.entities: list[Entity] = [self.plank, *self.balls.GetBalls()]

        vp_rect = self.camera.GetViewportRect()
        for entity in self.entities:
            if entity.GetBoundingBox() is None or vp_rect.Intersects(entity.GetBoundingBox()):
                self.camera.Draw(entity.GetDrawable())
