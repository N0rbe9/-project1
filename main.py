import pygame
import buttons
import os
import time
import random
pygame.font.init()
pygame.init()
import json

pause_upgrade = False
pause = False
lives = 0
player_vel = 5
max_health_plus = 0

with open("lives.txt") as lives_file:
    lives = json.load(lives_file)

with open("speed.txt") as speed_file:
    player_vel = json.load(speed_file)



with open("max_health_plus.txt") as max_health_plus_file:
    max_health_plus = json.load(max_health_plus_file)




#sounds
hit = pygame.mixer.Sound("gun+hit.wav")
hit.set_volume(0.2)

shot = pygame.mixer.Sound("Laser-shot.mp3")
shot.set_volume(0.3)

music = pygame.mixer.music.load("space-age.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)


WIDTH,HEIGHT = 750,750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("SPACE INVADER")

#buttons images
resume_img = pygame.image.load("assets/button_resume.png").convert_alpha()
quit_img = pygame.image.load("assets/quit_button.png").convert_alpha()
play_img = pygame.image.load("assets/button_play.png").convert_alpha()
plus_health_img = pygame.image.load("assets/button_plus_health.png").convert_alpha()
plus_live_img = pygame.image.load("assets/button_plus_live.png").convert_alpha()
plus_speed_img = pygame.image.load("assets/button_plus_speed.png").convert_alpha()
upgrade_img = pygame.image.load("assets/upgrade_button.png").convert_alpha()
back_img = pygame.image.load("assets/button_back.png").convert_alpha()
no_img = pygame.image.load("assets/no_button.png").convert_alpha()
yes_img = pygame.image.load("assets/yes_button.png").convert_alpha()

#load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

#Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#laser
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))

current_coins = 0
all_coins = 0

with open("space_coins.txt") as coin_file:
    all_coins = json.load(coin_file)

class Background():
    def __init__(self):
        self.bgimage = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))
        self.rectBGimg = self.bgimage.get_rect()

        self.bgY1 = 0
        self.bgX1 = 0

        self.bgY2 = self.rectBGimg.height
        self.bgX2 = 0

        self.moving_speed = 8

    def update(self):
        self.bgY1 -= self.moving_speed
        self.bgY2 -= self.moving_speed
        if self.bgY1 <= -self.rectBGimg.height:
            self.bgY1 = self.rectBGimg.height
        if self.bgY2 <= -self.rectBGimg.height:
            self.bgY2 = self.rectBGimg.height

    def render(self):
        WIN.blit(self.bgimage, (self.bgX1, self.bgY1))
        WIN.blit(self.bgimage, (self.bgX2, self.bgY2))



class Laser:
    def __init__(self, x, y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self):
        WIN.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y < height and self.y >=0)

    def collision(self,obj):
        return collide(obj,self)


class Ship(): #parent class
    COOLDOWN = 30

    def __init__(self, x, y, health = 100,armor = 0):
        self.x = x
        self.y = y
        self.health = health
        self.armor = armor
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0


    def draw(self):
        WIN.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw()


    def cooldown(self):        # nato aby sme nestrielali rychlo .Mame pol sekundy delay
        if self.cool_down_counter >=  self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1



    def shoot(self): #vytvarame laser
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return  self.ship_img.get_height()



class Player(Ship):
    def __init__(self, x, y,health=100,armor=0,):
        super().__init__(x,y,health,armor,)

        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) #spravnie textury
        self.max_health = health

    def move_laser(self, vel, objs):  # ked hrac vystreli  laser a zasiahne neriatela alebo zajde za obrazovku
        global current_coins
        global all_coins
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        current_coins += 20
                        all_coins += 20
                        hit.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    def healthbar(self):
        global max_health_plus
        pygame.draw.rect(WIN, (255, 0, 0),(self.x-max_health_plus/2, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()+max_health_plus, 10))
        pygame.draw.rect(WIN, (0, 255, 0), (self.x-max_health_plus/2, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health),10))


    def draw(self):
        super().draw()
        self.healthbar()





class Enemy(Ship):
    COLOR_MAP ={
                "red":(RED_SPACE_SHIP,RED_LASER),
                "green":(GREEN_SPACE_SHIP,GREEN_LASER),
                "blue":(BLUE_SPACE_SHIP,BLUE_LASER)

    }

    def __init__(self, x, y,color,health = 100,armor = 0):
        super().__init__(x,y, health,armor)
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)


    def move(self,vel):
        self.y += vel

    def move_laser(self, vel, obj):  # ked nepriatelsky laser zasiahne hraca
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                hit.play()
                obj.health -= 10 - obj.armor
                self.lasers.remove(laser)


    def shoot(self): #vytvarame laser
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None


player = Player(300, 630)
with open("health.txt") as health_file:
    player.health = json.load(health_file)

def main():
    global current_coins
    global pause_upgrade
    global pause
    run = True
    FPS = 60
    level = 0
    global lives
    main_font = pygame.font.SysFont("comicsans",40)
    lost_font = pygame.font.SysFont("comicsans",80)

    back_ground = Background()

    enemies = []
    wave_lenght = 5
    enemy_vel = 1
    spawn_y = 0
    spawn_x =0

    global player_vel
    laser_vel = 5

    global player
    global enemy

    lost = False
    lost_count = 0





    clock = pygame.time.Clock()

    def redraw_window():
        back_ground.update()
        back_ground.render()
        #draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        coins_label = main_font.render(f"Coins: {current_coins}",1,(255,255,255))
        level_label = main_font.render(f"level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label,(10,80))
        WIN.blit(coins_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10,10))

        for enemy in enemies:
            enemy.draw()

        player.draw()

        if lost:
            lost_label = lost_font.render("You lost !!",1,(255,255,255))
            WIN.blit(lost_label, (WIDTH /2 - (lost_label.get_width()/2),350))




        pygame.display.update()


    while run:

        clock.tick(FPS)
        redraw_window()

        if player.health <= 0 and lives > 0:
            player.health = 100
            lives -= 1

        if player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
                player.health += player.max_health + max_health_plus
                wave_lenght = 5
                level = 0
                current_coins = 0
            else:
                continue


        if len(enemies) == 0 :
            level += 1
            spawn_y -=100
            spawn_x +=20
            wave_lenght += 4
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50+spawn_x, WIDTH - 100),random.randrange(-1500+(spawn_y),-100),
                              random.choice(["red","blue","green"]))
                enemies.append(enemy)






        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0 :
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel +player.get_width() < WIDTH :
            player.x += player_vel
        if keys[pygame.K_w] and  player_vel + player.y > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and  player_vel + player.y + player.get_height() +15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            pygame.mixer.fadeout(1)
            shot.play()
        if keys[pygame.K_p]:
            pause = True
            paused()



        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)
            if random.randrange(0 , 2*60) == 1 :
                enemy.shoot()



            if enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)
            elif collide(enemy, player):
                player.health -= 10
                hit.play()
                enemies.remove(enemy)



        player.move_laser(-laser_vel,enemies)



def unpause():
    global pause
    pause = False


def paused():

    while pause:

        WIN.blit(BG, (0, 0))

        resume_button = buttons.Button(WIDTH / 2 - (resume_img.get_width() / 2), 125, resume_img, 1)
        quit_button = buttons.Button(WIDTH / 2 - (quit_img.get_width() / 2), 375, quit_img, 1)

        if resume_button.draw(WIN):
            unpause()

        if quit_button.draw(WIN):
            quit()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        pygame.display.update()




def game_menu():
    global all_coins
    global pause_upgrade
    global  lives
    global player_vel
    global plus_int
    global max_health_plus


    font = pygame.font.SysFont("arialblack", 40)
    TEXT_COL = (255, 255, 255)

    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        WIN.blit(img, (x, y))



    game_paused = False

    menu_state = "main"
    run = True
    while run:
        WIN.blit(BG, (0,0))

        coins_label = font.render(f"Coins: {all_coins}", 1, (255, 255, 255))
        WIN.blit(coins_label, (10, 10))

        upgrade_button = buttons.Button(WIDTH / 2 - (upgrade_img.get_width() / 2), 250, upgrade_img, 1)
        play_button = buttons.Button(WIDTH / 2 - (play_img.get_width() / 2), 125, play_img, 1)
        quit_button = buttons.Button(WIDTH / 2 - (quit_img.get_width() / 2), 375, quit_img, 1)

        back_button = buttons.Button(WIDTH / 2 - (back_img.get_width() / 2), 500, back_img, 1)
        lives_button = buttons.Button(WIDTH / 2 - (plus_live_img.get_width() / 2), HEIGHT / 4 - 50, plus_live_img, 1)
        speed_button = buttons.Button(WIDTH / 2 - (plus_speed_img.get_width() / 2), HEIGHT / 2, plus_speed_img, 1)
        health_button = buttons.Button(WIDTH / 2 - (plus_health_img.get_width() / 2), HEIGHT / 3, plus_health_img, 1)
        yes_button = buttons.Button(WIDTH / 3 - (yes_img.get_width() / 2), (HEIGHT / 2)-60, yes_img, 1)
        no_button = buttons.Button(WIDTH / 2 - (no_img.get_width() / 2)+140, (HEIGHT / 2)-60, no_img, 1)
        # check if game is paused
        if game_paused == True:
            # check menu state
            if menu_state == "main":
                # draw pause screen buttons
                if play_button.draw(WIN):
                    main()
                if upgrade_button.draw(WIN):
                    menu_state = "upgrade"
                if quit_button.draw(WIN):
                    with open("space_coins.txt", "w") as coin_file:
                        json.dump(all_coins, coin_file)
                    run = False

            if menu_state == "upgrade":
                draw_text("Upgrade your ship", font, TEXT_COL, WIDTH/2 -190, HEIGHT / 4 - 110)
                draw_text("Price: 5000", font, TEXT_COL, WIDTH / 2 - 130, HEIGHT / 4 + 10)
                draw_text("Price: 5000", font, TEXT_COL, WIDTH / 2 - 130, HEIGHT / 2 + 75)
                draw_text("Price: 5000", font, TEXT_COL, WIDTH / 2 - 120, HEIGHT / 3 + 70)

                if lives_button.draw(WIN)and all_coins >= 5000:
                    menu_state = "lives"
                if speed_button.draw(WIN)and all_coins >= 5000:
                    menu_state = "speed"
                if health_button.draw(WIN)and all_coins >= 5000:
                    menu_state = "health"
                if back_button.draw(WIN):
                    menu_state = "main"

            if menu_state == "lives":
                draw_text("Do you really wanna buy lives ?", font, TEXT_COL, 60, 150)
                if yes_button.draw(WIN):
                    lives += 1
                    with open("lives.txt", "w") as lives_file:
                        json.dump(lives, lives_file)
                    print(lives)
                    all_coins -= 5000
                    menu_state = "upgrade"
                if no_button.draw(WIN):
                    menu_state = "upgrade"

            if menu_state == "health":
                draw_text("Do you really wanna buy Health ?", font, TEXT_COL, 60, 150)
                if yes_button.draw(WIN):
                    max_health_plus += 10
                    with open("max_health_plus.txt", "w") as max_health_plus_file:
                        json.dump(max_health_plus, max_health_plus_file)
                    player.health += 10
                    with open("health.txt", "w") as health_file:
                        json.dump(player.health, health_file)
                    print(player.health)
                    all_coins -= 5000
                    menu_state = "upgrade"
                if no_button.draw(WIN):
                    menu_state = "upgrade"

            if menu_state == "speed":
                draw_text("Do you really wanna buy speed ?", font, TEXT_COL, 60, 150)
                if yes_button.draw(WIN):
                    player_vel += 1
                    with open("speed.txt", "w") as speed_file:
                        json.dump(player_vel, speed_file)
                    print(player_vel)
                    all_coins -= 5000
                    menu_state = "upgrade"
                if no_button.draw(WIN):
                    menu_state = "upgrade"

        else:
            draw_text("Space Invader", font, TEXT_COL, 220, 250)
            draw_text("Press SPACE to start", font, TEXT_COL, 160, 300)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = True

            if event.type == pygame.QUIT:
                with open("space_coins.txt","w") as coin_file:
                    json.dump(all_coins,coin_file)
                run = False

        pygame.display.update()

game_menu()




