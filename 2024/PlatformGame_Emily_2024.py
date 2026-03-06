#Term 3 Assessment file Emily Siemon
import pygame

from pygame.locals import*
from pygame.sprite import*
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#clock and frame rate for animations
clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Hollow Zone")

#define font
font = pygame.font.SysFont('OCR A Extended', 70)
font_score = pygame.font.SysFont("OCR A Extended", 30)

#define game variables
tile_size = 40
game_over = 0
main_menu = True
level = 1
max_levels = 3
score = 0

#define colours
purple = (73, 46, 99)
purple2 = (51, 19, 71)

#load images
sky_img = pygame.image.load("2024 one/cloud.png")
sky_img = pygame.transform.scale(sky_img, (800,800))
bg_img = pygame.image.load("2024 one/sky.png")
restart_img = pygame.image.load("2024 one/restart.png")
start_img = pygame.image.load("2024 one/start.png")
exit_img = pygame.image.load("2024 one/exit.png")

#load sounds
coin_fx = pygame.mixer.Sound("2024 one/bounce.wav")
coin_fx.set_volume(0.10)
attack_fx = pygame.mixer.Sound("2024 one/Sword Slash.mp3")
attack_fx.set_volume(0.15)
pygame.mixer.music.load("2024 one/Zelda Lullaby edit.mp3")
pygame.mixer.music.play(-1, 0.0, 5000)

#draw text function
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function to reset level
def reset_level(Level):
    player.reset(100, screen_height - 100)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    boss_group.empty()
    if level == 1:
        world = World(world1_data)
    elif level == 2:
        world = World(world2_data)
    elif level == 3:
        world = World(world3_data)
    return world

#button class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draw button
        screen.blit(self.image, self.rect)
        return action    

#Classes
class Player():
    def __init__(self, x, y):
        self.reset(x, y)
    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        if game_over == 0:
            #get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False:
                self.vel_y = -15
                self.jumped = True
                self.counter +=1
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            elif key[pygame.K_LEFT] == False and key[pygame.K_SPACE] == False and key[pygame.K_RIGHT] == False:
                self.image = self.images_idle[self.index]
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            elif key[pygame.K_RIGHT] == False and key[pygame.K_SPACE] == False and key[pygame.K_LEFT] == False:
                self.image = self.images_idle[self.index]
            #jump animations
            if key[pygame.K_SPACE] and key[pygame.K_LEFT]:
                self.image = self.images_jumpL[self.index]
            if key[pygame.K_SPACE] and key[pygame.K_RIGHT]:
                self.image = self.images_jumpR[self.index]
            #attack animations
            if key[pygame.K_RETURN]:
                self.image = self.images_attackL[self.index]
                attack_fx.play()
                #on keypress shoot projectile
                if len(slices) < 5:
                    slices.append(Slice(self.width +self.width //2, round(self.height +self.height //2), 6, (0, 0, 0), -1))
            if key [pygame.K_RETURN] and key[pygame.K_LEFT]:
                self.image = self.images_attackL[self.index]
            if key [pygame.K_RETURN] and key[pygame.K_RIGHT]:
                self.image = self.images_attackR[self.index]
            #animations
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_left):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            #add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            #check for collisions
            for tile in world.tile_list:
                #check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if belowew the ground - jumping
                    if self.vel_y < 0 :
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if above the ground - falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
            #check for collisions with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, boss_group, False):
                game_over = -1
            #check collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER', font, purple2, (screen_width // 2) - 175, screen_height //2)
            self.rect.y -= -5
        #draw player onto screen
        screen.blit(self.image, self.rect)
        return game_over
    def reset(self, x, y):
        #load in the walking frames
        self.images_left = []
        self.images_right = []
        self.images_jumpL = []
        self.images_jumpR = []
        self.images_idle = []
        self.images_attackL = []
        self.images_attackR = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_left = pygame.image.load(f"2024 one/run{num}.png")
            img_left = pygame.transform.scale(img_left, (32,64))
            img_right = pygame.transform.flip(img_left, True, False)
            img_jumpL = pygame.image.load("2024 one/jump1.png")
            img_jumpL = pygame.transform.scale(img_jumpL, (32,64))
            img_jumpR = pygame.image.load("2024 one/jumpR1.png")
            img_jumpR = pygame.transform.scale(img_jumpR, (32,64))
            img_idle = pygame.image.load ("2024 one/sprite1.png")
            img_idle = pygame.transform.scale(img_idle, (32,64))
            img_attackL = pygame.image.load("2024 one/attack1.png")
            img_attackL = pygame.transform.scale(img_attackL, (32,64))
            img_attackR = pygame.image.load("2024 one/attackR1.png")
            img_attackR = pygame.transform.scale(img_attackR, (32,64))
            self.images_left.append(img_left)
            self.images_right.append(img_right)
            self.images_jumpL.append(img_jumpL)
            self.images_jumpR.append(img_jumpR)
            self.images_idle.append(img_idle)
            self.images_attackL.append(img_attackL)
            self.images_attackR.append(img_attackR)
        self.image = self.images_left[self.index]
        self.dead_image = pygame.image.load("2024 one/dead1.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (32,64))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

class World():
    def __init__(self, data):
        self.tile_list = []
        #load images
        stone_img = pygame.image.load("2024 one/stone.png")
        mossy_img = pygame.image.load("2024 one/mossy.png")
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(stone_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(mossy_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 6)
                    blob_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size //2))
                    lava_group.add(lava)
                if tile == 4:
                    coin = Coin(col_count * tile_size, row_count * tile_size + (tile_size // 30))
                    coin_group.add(coin) 
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 1))
                    exit_group.add(exit)
                if tile == 9:
                    boss = Boss(col_count * tile_size, row_count * tile_size + (tile_size //1))
                    boss_group.add(boss)
                col_count += 1
            row_count += 1
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("2024 one/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("2024 one/boss.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if pygame.sprite.spritecollide(self, slices, False):
            boss_group.pop(boss_group.index(boss_group))
        
        
class Slice(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color, facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.vel = 8 * facing
    def draw(screen, self):
        pygame.draw.circle(screen, self.color, (self.x, self.y, self.radius))
        for slice in slices:
            slice.draw(screen)


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('2024 one/lava1.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size //2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('2024 one/chrome.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('2024 one/portal1.png')
        self.image = pygame.transform.scale(img, (80,120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
world1_data = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 4, 0, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], 
[1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 2, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 2, 1, 1, 0, 0, 0, 2, 1, 2, 2], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0], 
[0, 0, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0], 
[0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 0, 0, 1, 2, 0, 0, 0, 4], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[1, 2, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1], 
[0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0], 
[6, 6, 6, 6, 6, 6, 6, 6, 1, 1, 6, 6, 2, 2, 6, 6, 6, 6, 6, 6]
]

world2_data = [
[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 4, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0], 
[0, 0, 0, 0, 0, 0, 2, 0, 4, 0, 0, 0, 0, 1, 2, 2, 1, 2, 0, 0], 
[1, 1, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], 
[0, 0, 0, 2, 0, 0, 2, 1, 1, 1, 1, 0, 0, 0, 0, 4, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 4, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 0, 0], 
[0, 0, 0, 0, 0, 0, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[1, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 4, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 4, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0], 
[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 1, 2, 1, 2, 2], 
[0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
]

world3_data = [
[9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[1, 1, 2, 1, 1, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 0, 0, 0],
[1, 2, 1, 2, 1, 1, 1, 2, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[0, 0, 4, 0, 0, 0, 0, 1, 2, 2, 1, 1, 0, 1, 2, 2, 1, 2, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 1, 2, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 4],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[1, 1, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1],
]

player = Player(100, screen_height - 100)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

#create dummy coin for score count
score_coin = Coin(tile_size //2, tile_size // 8)
coin_group.add(score_coin)

#create buttons
restart_button = Button(screen_width // 2 - 60, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width //2 - 290, screen_height // 2, start_img)
exit_button = Button(screen_width //2 +40, screen_height // 2, exit_img)

#load world data
if level == 1:
    world = World(world1_data)
elif level == 2:
    world = World(world2_data)
elif level == 3:
    world = World(world3_data)
elif level > max_levels:
    if restart_button.draw():
        level = 1
        world_data = []
        world = reset_level(level)
        game_over = 0

#Main game loop
run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0,0))
    screen.blit(sky_img, (0,0))

    #only shows buttons when menu is true
    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()
        slices = []
        if game_over == 0:
            blob_group.update()
            #update score and check if coins collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text("X " + str(score), font_score, purple, tile_size - 10, 10)
            #move the projectiles
            for slice in slices:
                if slice.x < 800 and slice.x > 0:
                    slice.x += slice.vel
                else:
                    #delete if off screen
                    slices.pop(slices.index(slice))
        blob_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        boss_group.draw(screen)

        game_over = player.update(game_over)

        #if player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        #if player has completed the level
        if game_over == 1:
            #reset game and go to next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                #restart game
                draw_text("WIPE OUT!", font, purple2, (screen_width //2) - 170, screen_height //2)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()