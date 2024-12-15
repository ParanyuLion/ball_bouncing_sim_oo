import ball
import my_event
import turtle
import random
import heapq
import paddle
import time
import math
import enemies
import winsound
import shop
import boss
import Player


class BouncingSimulator:
    def __init__(self):
        self.ball_list = []
        self.t = 0.0
        self.pq = []
        self.HZ = 4
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)
        self.canvas_width = 350
        self.canvas_height = 400
        self.shot_time = 0
        self.time = time.time()
        self.enemies_move_time = 0
        self.enemies = []
        self.score = 0
        self.HP = 10
        self.money = 0
        self.bullet_size = 10
        self.gun_state = 1
        self.boss_get_hit = 0
        self.boss_shoot_time = 0
        self.parry_state = False
        self.player_get_hit_time = 0
        # print(self.canvas_width, self.canvas_height)
        self.tom = turtle.Turtle()
        self.player_turtle = turtle.Turtle()
        self.my_paddle = paddle.Paddle(100, 30, (255, 0, 0), self.tom)
        self.my_paddle.set_location([350, 950])
        self.player = Player.Player(50, 50, 'red', self.player_turtle)
        self.player.set_location([1, -350])
        self.boss = boss.Boss(100, 'purple', 10)
        self.boss.alive = False
        self.jerry = turtle.Turtle()
        self.jerry.hideturtle()
        self.hp_turtle = turtle.Turtle()
        self.hp_turtle.hideturtle()
        self.boss_hp_turtle = turtle.Turtle()
        self.boss_hp_turtle.hideturtle()
        self.money_turtle = turtle.Turtle()
        self.money_turtle.hideturtle()
        self.start_turtle = turtle.Turtle()
        self.start_turtle.hideturtle()
        self.screen = turtle.Screen()
        self.shop_turtle = turtle.Turtle()
        self.shop_turtle.hideturtle()
        self.shop_list = [shop.Shop(-650, -200, 'Better Gun', 3500, self.shop_turtle),
                          shop.Shop(-650, -350, '+5 HP', 2000, self.shop_turtle)]

        self.game_turtle = turtle.Turtle()
        self.game_turtle.hideturtle()
        self.__run_game = False
        self.start_game_color = 'cyan'

    def kill_enemy(self):
        for j in range(len(self.enemies)):
            for i in range(len(self.ball_list)):
                if ((abs(self.ball_list[i].x - self.enemies[j].x) < self.enemies[j].size * 2 and
                     (abs(self.ball_list[i].y - self.enemies[j].y) < self.enemies[j].size * 2)) or
                    (abs(self.my_paddle.location[0] - self.enemies[j].x) < self.my_paddle.width and
                     (abs(self.my_paddle.location[1] - self.enemies[j].y) < self.my_paddle.height * 2))) and \
                        self.enemies[j].y < 400:
                    self.enemies[j].y = 700
                    self.enemies[j].x = random.randint(-250, 250)
                    self.score += 1
                    self.money += 100
                    self.__draw_money(self.money_turtle)
                    self.__draw_scores(self.jerry)

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
        dtx = a_ball.time_to_hit_vertical_wall()
        heapq.heappush(self.pq, my_event.Event(self.t + dtx, a_ball, None, None))

    def __draw_border(self):
        turtle.penup()
        turtle.goto(-self.canvas_width, -self.canvas_height)
        turtle.pensize(10)
        turtle.pendown()
        turtle.color('white')
        for i in range(2):
            turtle.penup()
            turtle.forward(2 * self.canvas_width)
            turtle.left(90)
            turtle.pendown()
            turtle.forward(2 * self.canvas_height)
            turtle.left(90)

    def __draw_shop(self):
        self.shop_turtle.clear()
        for i in self.shop_list:
            i.draw()

    def __draw_scores(self, score):
        score.color("yellow")
        style = ("Comic Sans", 30, "normal")
        score.penup()
        score.goto(-550, 300)
        score.clear()
        score.write(f"Points:{self.score} ", font=style)
        score.hideturtle()

    def __draw_hp(self, HP):
        HP.color("red")
        style = ("Comic Sans", 30, "normal")
        HP.penup()
        HP.goto(400, 300)
        HP.clear()
        HP.write(f"HP:{self.HP} ", font=style)
        HP.hideturtle()

    def __draw_money(self, money):
        money.color("green")
        style = ("Comic Sans", 30, "normal")
        money.penup()
        money.goto(400, 100)
        money.clear()
        money.write(f"$:{self.money} ", font=style)
        money.hideturtle()

    def __draw_boss_hp(self, boss_hp):
        boss_hp.color("purple")
        style = ("Comic Sans", 30, "normal")
        boss_hp.penup()
        boss_hp.goto(400, 200)
        boss_hp.clear()
        if self.boss.hp <= 0:
            boss_hp.write(f"Boss HP: Dead ", font=style)
        else:
            boss_hp.write(f"Boss HP:{self.boss.hp} ", font=style)
        boss_hp.hideturtle()

    def __redraw(self):
        turtle.clear()
        if self.__run_game:
            self.my_paddle.clear()
            self.__draw_border()
            self.my_paddle.draw()
            self.player.clear()
            self.player.draw()
            self.boss.draw()
            for i in self.enemies:
                i.draw()
            for i in range(len(self.ball_list)):
                self.ball_list[i].draw()
        turtle.update()
        heapq.heappush(self.pq, my_event.Event(self.t + 1.0 / self.HZ, None, None, None))

    def __paddle_predict(self):
        for i in range(len(self.ball_list)):
            a_ball = self.ball_list[i]
            dtp = a_ball.time_to_hit_paddle(self.my_paddle)
            heapq.heappush(self.pq, my_event.Event(self.t + dtp, a_ball, None, self.my_paddle))

    # move_left, move_right, move_up, and move_down handlers update paddle positions
    def move_left(self):
        if (self.player.location[0] - self.player.width / 2 - 40) >= -self.canvas_width and not self.parry_state:
            self.player.set_location([self.player.location[0] - 40, self.player.location[1]])

    def move_right(self):
        if (self.player.location[0] + self.player.width / 2 + 40) <= self.canvas_width and not self.parry_state:
            self.player.set_location([self.player.location[0] + 40, self.player.location[1]])

    def move_up(self):
        if (self.player.location[1] + self.player.height / 2 + 40) <= self.canvas_height and not self.parry_state:
            self.player.set_location([self.player.location[0], self.player.location[1] + 40])

    def move_down(self):
        if (self.player.location[1] - self.player.height / 2 - 40) >= -self.canvas_height and not self.parry_state:
            self.player.set_location([self.player.location[0], self.player.location[1] - 40])

    def shoot_ball(self, mouse_x=None, mouse_y=None):
        if self.parry_state:
            return None
        turtle.update()
        current_time = time.time()
        if self.gun_state == 1:
            speed = 50 + (0.5 * self.score)
        else:
            speed = 50 + (1 * self.score)
        if (current_time - self.shot_time > 0.7 and self.HP > 0) and self.__run_game:
            winsound.PlaySound("gun-gunshot-01.wav", winsound.SND_ASYNC)
            x = self.player.location[0]
            y = self.player.location[1] + self.player.height / 2 + self.bullet_size
            if mouse_x == x:
                if mouse_y != y:
                    zeta = math.pi / 2
                else:
                    zeta = -math.pi / 2
            else:
                zeta = math.atan((mouse_y - y) / (mouse_x - x))

            if mouse_x < x:
                vx = -(math.cos(zeta)) * speed
                vy = -(math.sin(zeta)) * speed
            else:
                vx = (math.cos(zeta)) * speed
                vy = (math.sin(zeta)) * speed
            ball_color = (255, 0, 0)
            if self.gun_state == 1:
                ammo = ball.Ball(self.bullet_size, x, y, vx, vy, ball_color, len(self.ball_list))
                self.ball_list.append(ammo)
                self.__predict(ammo)
            if self.gun_state == 2:
                ammo1 = ball.Ball(self.bullet_size, x + 20, y, vx, vy, ball_color, len(self.ball_list))
                self.ball_list.append(ammo1)
                self.__predict(ammo1)
                ammo2 = ball.Ball(self.bullet_size, x - 20, y, vx, vy, ball_color, len(self.ball_list))
                self.ball_list.append(ammo2)
                self.__predict(ammo2)
            self.enemies_move()
            self.shot_time = current_time

    def enemies_move(self):
        current_time = time.time()
        if (current_time - self.enemies_move_time > abs(0.2 / (1 + 0.4 * len(self.ball_list)))) and self.__run_game:
            for i in self.enemies:
                i.y -= 20
                if i.y < -400:
                    if self.HP != 0:
                        self.HP -= 1
                    self.__draw_hp(self.hp_turtle)
                    i.y = 700
                self.enemies_move_time = current_time
                self.kill_enemy()

    def player_get_shoot(self):
        current_time = time.time()
        for i in self.ball_list:
            if (((abs(i.x - self.player.location[0]) < self.player.width and
                 (abs(i.y - self.player.location[1]) < self.player.height))
                 and current_time - self.player_get_hit_time >= 0.5) and i.color == 'blue'):
                self.HP -= 1
                self.__draw_hp(self.hp_turtle)
                self.player_get_hit_time = current_time

    def shoot_boss(self):
        current_time = time.time()
        for i in self.ball_list:
            if self.boss.get_hit(i) and current_time - self.boss_get_hit >= 0.7:
                self.boss.hp -= 1
                self.boss_get_hit = current_time
                self.__draw_boss_hp(self.boss_hp_turtle)
                if self.boss.dead():
                    self.boss.x = -900
                    self.score += 10
                    self.boss.alive = False
                    self.__draw_scores(self.jerry)

    def boss_shooting(self):
        turtle.update()
        current_time = time.time()
        speed = 30 + (0.5 * self.score)
        if current_time - self.boss_shoot_time > 1 and self.boss.alive:
            x = self.boss.x
            y = self.boss.y - 2 * self.boss.size
            if self.player.location[0] == x:
                if self.player.location[1] != y:
                    zeta = math.pi / 2
                else:
                    zeta = -math.pi / 2
            else:
                zeta = math.atan((self.player.location[1] - y) / (self.player.location[0] - x))

            if self.player.location[0] < x:
                vx = -(math.cos(zeta)) * speed
                vy = -(math.sin(zeta)) * speed
            else:
                vx = (math.cos(zeta)) * speed
                vy = (math.sin(zeta)) * speed
            boss_ammo = ball.Ball(20, x, y, vx, vy, 'blue', len(self.ball_list))
            self.ball_list.append(boss_ammo)
            self.__predict(boss_ammo)
            self.boss_shoot_time = current_time

    def click(self, mouse_x=None, mouse_y=None):
        if (-650 < mouse_x < -400) and (-200 < mouse_y < -100):
            if self.money >= self.shop_list[0].price:
                self.money -= self.shop_list[0].price
                self.__draw_money(self.money_turtle)
                self.gun_state = 2
                self.shop_list[0] = shop.Shop(-650, -200, 'Better Gun', 'Sold', self.shop_turtle, 'SOLD')
                self.__draw_shop()
        elif (-650 < mouse_x < -400) and (-350 < mouse_y < -250):
            if self.money >= self.shop_list[1].price:
                self.money -= self.shop_list[1].price
                self.__draw_money(self.money_turtle)
                self.HP += 5
                self.__draw_hp(self.hp_turtle)
        else:
            self.shoot_ball(mouse_x, mouse_y)

    def run_game_over(self, tao):
        tao.penup()
        tao.hideturtle()
        tao.color("red")
        tao.goto(0, 100)
        style1 = "Comic Sans Ms", 80, "normal"
        tao.pendown()
        tao.write("GAME OVER", font=style1, align='center')
        tao.goto(0, -100)
        style2 = "Comic Sans", 30, "normal"
        tao.write(f"Your score is {self.score}", font=style2, align='center')
        tao.hideturtle()

    def run_start_game(self, tao):
        turtle.Screen().bgcolor(self.start_game_color)
        tao.penup()
        tao.hideturtle()
        tao.color("red")
        tao.goto(0, -100)
        style1 = "Comic Sans", 30, "normal"
        tao.pendown()
        tao.write("Press R to start", font=style1, align='center')
        tao.penup()
        tao.goto(0, 100)
        tao.pendown()
        style2 = "Comic Sans Ms", 60, "normal"
        tao.write("Defender's Last Stand", font=style2, align='center')
        tao.hideturtle()

    def parry(self):
        self.parry_state = True
        self.my_paddle.location = [self.player.location[0], self.player.location[1] + 50]

    def release(self):
        self.parry_state = False
        self.my_paddle.location = [-900, -900]

    def start_game(self):
        self.__run_game = True
        self.game_turtle.clear()

    def run(self):
        # initialize pq with collision events and redraw event
        for i in range(3):
            self.enemies.append((enemies.Enemies(50, random.randint(-250, 250), 300, 'green')))
        for i in self.enemies:
            i.draw()
        self.run_start_game(self.game_turtle)
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))
        # listen to keyboard events and activate move_left and move_right handlers accordingly
        self.screen.listen()
        self.screen.onkeypress(self.move_left, "a")
        self.screen.onkeypress(self.move_right, "d")
        self.screen.onkeypress(self.move_up, "w")
        self.screen.onkeypress(self.move_down, "s")
        self.screen.onkeypress(self.parry, "space")
        self.screen.onkeyrelease(self.release, "space")
        self.screen.onclick(self.click)
        self.screen.onkeypress(self.start_game, "r")

        while True:
            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue
            if self.__run_game:
                turtle.Screen().bgcolor('black')
                self.__draw_money(self.money_turtle)
                self.__draw_scores(self.jerry)
                self.__draw_hp(self.hp_turtle)
                self.__draw_shop()
            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle
            if self.__run_game:
                self.enemies_move()
                self.shoot_boss()
                self.boss_shooting()
                self.player_get_shoot()
            if self.score in range(30, 33):
                self.boss.alive = True
                self.boss.x = 0
            if self.score in range(180, 183):
                self.boss.hp = 10
                self.boss.alive = True
                self.__draw_boss_hp(self.boss_hp_turtle)
                self.boss.x = 0
            if self.HP < 1:
                break

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

            # regularly update the prediction for the paddle as its position may always be changing due to
            # keyboard events
            self.__paddle_predict()
            # hold the window; close it by clicking the window close 'x' mark
        turtle.clearscreen()
        turtle.Screen().bgcolor('black')
        self.run_game_over(self.game_turtle)
        turtle.done()


my_simulator = BouncingSimulator()
my_simulator.run()
