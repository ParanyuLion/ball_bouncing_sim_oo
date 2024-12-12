import turtle
class Boss:
    def __init__(self, size, color, hp, id=None):
        self.size = size
        self.x = -900
        self.y = 300
        # self.vx = vx
        # self.vy = vy
        self.color = color
        self.count = 0
        self.hp = hp
        self.id = id
        self.alive = True

    def get_hit(self, ball):
        if abs(ball.x - self.x) < self.size * 2 and (abs(ball.y - self.y) < self.size) * 2:
            return True

    def dead(self):
        if self.hp <= 0:
            return True

    def draw(self):
        turtle.hideturtle()
        turtle.penup()
        turtle.color(self.color)
        turtle.fillcolor(self.color)
        turtle.goto(self.x, self.y - self.size)
        turtle.pendown()
        turtle.begin_fill()
        turtle.circle(self.size)
        turtle.end_fill()