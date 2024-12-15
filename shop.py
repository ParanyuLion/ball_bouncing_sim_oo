class Shop:
    def __init__(self, x, y, name, price, turtle, state='available'):
        self.x = x
        self.y = y
        self.name = name
        self.price = price
        self.turtle = turtle
        self.state = state

    def draw(self):
        # draw a circle of radius equals to size centered at (x, y) and paint it with color
        self.turtle.hideturtle()
        self.turtle.penup()
        if self.state == 'available':
            self.turtle.color("white")
        else:
            self.turtle.color("red")
        self.turtle.goto(self.x, self.y)
        self.turtle.pendown()
        style = "Comic Sans", 20, "normal"
        for i in range(2):
            self.turtle.pensize(3)
            self.turtle.forward(250)
            self.turtle.left(90)
            self.turtle.pendown()
            self.turtle.forward(100)
            self.turtle.left(90)
        self.turtle.penup()
        self.turtle.goto(self.x+20, self.y+35)
        self.turtle.pendown()
        self.turtle.write(f'{self.name}: ${self.price}', font=style)
