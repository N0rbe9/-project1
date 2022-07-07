import pygame
import os
import time
import random
pygame.font.init()
pygame.init()

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


class Ship: #parent class
    COOLDOWN = 30
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0


    def draw(self):
        WIN.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw()

    def move_laser(self,vel,obj):   #ked nepriatelsky laser zasiahne hraca
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)




    def cooldown(self):                 # nato aby sme nestrielali rychlo .Mame pol sekundy delay
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
    def __init__(self, x, y,health=100):
        super().__init__(x,y,health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) #spravnie textury
        self.max_health = health

    def move_laser(self, vel, objs):  # ked hraco vystreli  laser a zasiahne neriatela alebo zajde za obrazovku
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        hit.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    def healthbar(self):
        pygame.draw.rect(WIN,(255,0,0), (self.x,self.y +self.ship_img.get_height() + 10,self.ship_img.get_height(),10))
        pygame.draw.rect(WIN,(0,255,0), (self.x,self.y +self.ship_img.get_height() + 10,self.ship_img.get_height() * (self.health / self.max_health),10))
    def draw(self):
        super().draw()
        self.healthbar()

class Enemy(Ship):
    COLOR_MAP ={
                "red":(RED_SPACE_SHIP,RED_LASER),
                "green":(GREEN_SPACE_SHIP,GREEN_LASER),
                "blue":(BLUE_SPACE_SHIP,BLUE_LASER)

    }

    def __init__(self, x, y,color, health = 100):
        super().__init__(x,y, health)
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel

    def shoot(self): #vytvarame laser
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans",40)
    lost_font = pygame.font.SysFont("comicsans",80)

    enemies = []
    wave_lenght = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300,630)

    lost = False
    lost_count = 0

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0,0))
        #draw text
        lives_label = main_font.render(f"lives: {lives}",1,(255,255,255))
        level_label = main_font.render(f"level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10,10))
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

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_lenght += 5
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100),random.randrange(-1500,-100), random.choice(["red","blue","green"]))
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







        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel,player)
            if random.randrange(0 , 2*60) == 1 :
                enemy.shoot()


            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            elif collide(enemy, player):
                player.health -= 10
                hit.play()
                enemies.remove(enemy)

        player.move_laser(-laser_vel,enemies)









def main_menu():
    title_font = pygame.font.SysFont("comicsans",40)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_lable = title_font.render("Press the mouse to begin...",1,(255,255,255))
        WIN.blit(title_lable, (WIDTH/2 - title_lable.get_width()/2,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()