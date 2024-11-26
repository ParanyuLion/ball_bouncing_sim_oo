import copy
import ball
import my_event
import turtle
import random
import heapq
import paddle
import time
import math
import enemies
import os
import winsound

class BouncingSimulator:
    def __init__(self, num_balls):
        self.num_balls = num_balls
        self.ball_list = []
        self.t = 0.0
        self.pq = []
        self.HZ = 4
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)
        self.canvas_width = 550
        self.canvas_height = 350
        self.shot_time = 0
        self.time = time.time()
        self.enemies_move_time = 0
        self.enemies = []
        self.score = 0
        print(self.canvas_width, self.canvas_height)

        ball_radius = 50
        for i in range(self.num_balls):
            x = -self.canvas_width + (i+1)*(2*self.canvas_width/(self.num_balls+1))
            # y = 0
            # vx = 10*random.uniform(-1.0, 1.0)
            # vy = 10*random.uniform(-1.0, 1.0)
            y = 350
            vx = 0
            vy = -1
            ball_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.ball_list.append(ball.Ball(ball_radius, x, y, vx, vy, ball_color, i))

        tom = turtle.Turtle()
        self.my_paddle = paddle.Paddle(200, 50, (255, 0, 0), tom)
        self.my_paddle.set_location([0, -150])
        for i in range(3):
            self.enemies.append((enemies.Enemies(50, random.randint(-400, 400), 300, 0, 10, 'green')))

        # self.enemies1 = (enemies.Enemies(50, 0, 300, 0, 10, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
        # self.enemies1.draw()
        for i in self.enemies:
            i.draw()
        self.jerry = turtle.Turtle()
        self.__draw_scores(self.jerry)
        self.screen = turtle.Screen()

    def kill_enemy(self):
        for j in range(len(self.enemies)):
            for i in range(len(self.ball_list)):
                if abs(self.ball_list[i].x - self.enemies[j].x) < 50 and (abs(self.ball_list[i].y - self.enemies[j].y)< 50):
                    self.enemies[j].y = 700
                    self.enemies[j].x = random.randint(-400, 400)
                    self.score += 1
                    self.__draw_scores(self.jerry)
        # for i in range(len(self.ball_list)):
        #     if abs(self.ball_list[i].x - self.enemies1.x) < 50 and (abs(self.ball_list[i].y - self.enemies1.y)< 50):
        #         self.enemies1.y = 450
        #         self.score += 1
        #         self.__draw_scores(self.jerry)

    # updates priority queue with all new events for a_ball
    def __predict(self, a_ball):
        if a_ball is None:
            return

        # particle-particle collisions
        for i in range(len(self.ball_list)):
            dt = a_ball.time_to_hit(self.ball_list[i])
            # insert this event into pq
            heapq.heappush(self.pq, my_event.Event(self.t + dt, a_ball, self.ball_list[i], None))

        # particle-wall collisions
        dtX = a_ball.time_to_hit_vertical_wall()
        # dtY = a_ball.time_to_hit_horizontal_wall()
        heapq.heappush(self.pq, my_event.Event(self.t + dtX, a_ball, None, None))
        # heapq.heappush(self.pq, my_event.Event(self.t + dtY, None, a_ball, None))

    def __draw_border(self):
        turtle.penup()
        turtle.goto(-self.canvas_width, -self.canvas_height)
        turtle.pensize(10)
        turtle.pendown()
        turtle.color((0, 0, 0))
        for i in range(2):
            turtle.forward(2 * self.canvas_width)
            turtle.left(90)
            turtle.forward(2 * self.canvas_height)
            turtle.left(90)

    def __draw_scores(self, score):
        score.color("red")
        style = ("Comic Sans", 30, "normal")
        score.penup()
        score.goto(-500, 300)
        score.clear()
        score.write(f"Points:{self.score} ", font=style)
        score.hideturtle()

    def __redraw(self):
        turtle.clear()
        self.my_paddle.clear()
        self.__draw_border()
        self.my_paddle.draw()
        # self.enemies1.draw()

        for i in self.enemies:
            i.draw()
        for i in range(len(self.ball_list)):
            self.ball_list[i].draw()
        turtle.update()
        heapq.heappush(self.pq, my_event.Event(self.t + 1.0 / self.HZ, None, None, None))

    def __paddle_predict(self):
        for i in range(len(self.ball_list)):
            a_ball = self.ball_list[i]
            dtP = a_ball.time_to_hit_paddle(self.my_paddle)
            heapq.heappush(self.pq, my_event.Event(self.t + dtP, a_ball, None, self.my_paddle))

    # move_left and move_right handlers update paddle positions
    def move_left(self):
        if (self.my_paddle.location[0] - self.my_paddle.width/2 - 40) >= -self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] - 40, self.my_paddle.location[1]])

    # move_left and move_right handlers update paddle positions
    def move_right(self):
        if (self.my_paddle.location[0] + self.my_paddle.width/2 + 40) <= self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] + 40, self.my_paddle.location[1]])

    def move_up(self):
        if (self.my_paddle.location[1] + self.my_paddle.height / 2 + 40) <= self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] + 40])

    def move_down(self):
        if (self.my_paddle.location[1] - self.my_paddle.height / 2 - 40) >= -self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] - 40])

    def shoot_ball(self, mouse_x=None, mouse_y=None):
        turtle.update()
        current_time = time.time()
        speed = 40
        if current_time - self.shot_time > 0.5:
            winsound.PlaySound("gun-gunshot-01.wav", winsound.SND_ASYNC)
            ball_radius = 10
            x = self.my_paddle.location[0]
            y = self.my_paddle.location[1] + self.my_paddle.height / 2 + ball_radius
            # tan_v = math.sqrt(mouse_y ** 2 / mouse_x ** 2)
            if mouse_x == x:  # Handle vertical shooting (x == x)
                if mouse_y != y:
                    zeta = math.pi / 2
                else:
                    zeta = -math.pi / 2
            else:
                zeta = math.atan((mouse_y - y) / (mouse_x - x))  # Calculate angle

            if mouse_x < x:
                vx = -(math.cos(zeta)) * speed
                vy = -(math.sin(zeta)) * speed
            else:
                vx = (math.cos(zeta))*speed
                vy = (math.sin(zeta))*speed
            ball_color = (255, 0, 0)
            ammo = ball.Ball(ball_radius, x, y, vx, vy, ball_color, len(self.ball_list))
            # self.ball_list.append(ammo)
            # if len(self.ball_list) > 15:
            #     # self.ball_list[0].vx = 0
            #     # self.ball_list[0].vy = 0
            #     # self.ball_list[0] = ammo
            #     # self.__predict(ammo)
            #     self.ball_list.pop(0)
            # else:
            #     self.ball_list.append(ammo)
            #     self.__predict(ammo)
            self.ball_list.append(ammo)
            self.__predict(ammo)
            self.enemies_move()
            self.shot_time = current_time

    def enemies_move(self):
        current_time = time.time()
        if current_time - self.enemies_move_time > abs(0.2 /(1+ 0.1*self.score)):
            for i in self.enemies:
                i.y -= 20
                if i.y < -400:
                    i.y = 700
                self.enemies_move_time = current_time
                self.kill_enemy()
            # self.enemies1.x = 0
            # self.enemies1.y -= 20
            # self.enemies1.draw()
            # self.enemies_move_time = current_time
            # self.kill_enemy()


    def parry(self):
        pass

    def run(self):
        # initialize pq with collision events and redraw event
        for i in range(len(self.ball_list)):
            self.__predict(self.ball_list[i])
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))

        # listen to keyboard events and activate move_left and move_right handlers accordingly
        self.screen.listen()
        self.screen.onkeypress(self.move_left, "a")
        self.screen.onkeypress(self.move_right, "d")
        self.screen.onkeypress(self.move_up, "w")
        self.screen.onkeypress(self.move_down, "s")
        self.screen.onkeypress(self.parry, "space")
        self.screen.onclick(self.shoot_ball)



        while (True):

            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue

            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle
            self.enemies_move()
            # update positions, and then simulation clock
            for i in range(len(self.ball_list)):
                self.ball_list[i].move(e.time - self.t)
            self.t = e.time

            if (ball_a is not None) and (ball_b is not None) and (paddle_a is None):
                ball_a.bounce_off(ball_b)
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is None):
                ball_a.bounce_off_vertical_wall()
            elif (ball_a is None) and (ball_b is not None) and (paddle_a is None):
                ball_b.bounce_off_horizontal_wall()
            elif (ball_a is None) and (ball_b is None) and (paddle_a is None):
                self.__redraw()
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is not None):
                ball_a.bounce_off_paddle()

            self.__predict(ball_a)
            self.__predict(ball_b)

            # regularly update the prediction for the paddle as its position may always be changing due to keyboard events
            self.__paddle_predict()
            # hold the window; close it by clicking the window close 'x' mark
        turtle.done()

# num_balls = int(input("Number of balls to simulate: "))
num_balls = 0
my_simulator = BouncingSimulator(num_balls)
my_simulator.run()
