import turtle


class Boss:
    def __init__(self, size, color, hp):
        self.size = size
        self.x = -900
        self.y = 300
        self.color = color
        self.hp = hp
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
