import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screenWidth = 800
screenHeight = 800

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Game')

#game variables
tileSize = 20
gameOver = 0

#load images
sky = pygame.image.load('2024/cloud.png')
sky = pygame.transform.scale(sky, (800, 800))

class Player():
    def __init__(self, x,y):
        self.imagesRight = []
        self.imagesLeft = []
        self.imagesIdle = []
        self.imagesJumpL = []
        self.imagesJumpR = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            imgR = pygame.image.load(f"2024/runR{num}.png")
            imgR = pygame.transform.scale(imgR, (20, 40))
            self.imagesRight.append(imgR)
            imgL = pygame.image.load(f"2024/run{num}.png")
            imgL = pygame.transform.scale(imgL, (20, 40))
            self.imagesLeft.append(imgL)
            imgIdle = pygame.image.load (f"2024/sprite{num}.png")
            imgIdle = pygame.transform.scale(imgIdle, (20, 40))
            self.imagesIdle.append(imgIdle)
            imgJumpL = pygame.image.load ("2024/jump1.png")
            imgJumpL = pygame.transform.scale(imgJumpL, (20, 40))
            self.imagesJumpL.append(imgJumpL)
            imgJumpR = pygame.image.load ("2024/jumpR1.png")
            imgJumpR = pygame.transform.scale(imgJumpR, (20, 40))
            self.imagesJumpR.append(imgJumpR)
        self.deadImage = pygame.image.load('2024/dead1.png')
        self.deadImage = pygame.transform.scale(self.deadImage, (20, 40))
        self.image = self.imagesIdle[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def update(self, gameOver):
        dx = 0
        dy = 0
        walkCooldown = 15

        if gameOver == 0:
            

            #get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False:
                self.vel_y = -8.5
                self.jumped = True
                self.counter += 1
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 2.5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 2.5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False and key[pygame.K_SPACE] == False:
                self.counter += 1
                self.direction = 0
            #jump animations
            if key[pygame.K_SPACE] and key[pygame.K_LEFT]:
                self.image = self.imagesJumpL[self.index]
            if key[pygame.K_SPACE] and key[pygame.K_RIGHT]:
                self.image = self.imagesJumpR[self.index]

            #handle animation
            if self.counter > walkCooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.imagesRight):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.imagesRight[self.index]
                if self.direction == -1:
                    self.image = self.imagesLeft[self.index]
                if self.direction == 0:
                    self.image = self.imagesIdle[self.index]

            #add gravity
            self.vel_y += 0.5
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #check for collision
            for tile in world.tileList:
                #check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #check for collison in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if above the ground
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
            
            #check for collision with enemy
            if pygame.sprite.spritecollide(self, blobGroup, False):
                gameOver = -1
            
            #check for collision with lava
            if pygame.sprite.spritecollide(self, lavaGroup, False):
                gameOver = -1

            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy

            #check for screen boundaries
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > screenWidth:
                self.rect.right = screenWidth
        
        elif gameOver == -1:
            self.image = self.deadImage
            if self.rect.y > 0:
                self.rect.y += 3

        #draw player on screen
        screen.blit(self.image, self.rect)

        return gameOver

class World():
    def __init__(self, data):
        self.tileList = []

        #load images
        stone = pygame.image.load('2024/stone.png')
        moss = pygame.image.load('2024/mossy.png')

        rowCount = 0
        for row in data:
            colCount = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(stone, (tileSize, tileSize))
                    imgRect = img.get_rect()
                    imgRect.x = colCount * tileSize
                    imgRect.y = rowCount * tileSize
                    tile = (img, imgRect)
                    self.tileList.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(moss, (tileSize, tileSize))
                    imgRect = img.get_rect()
                    imgRect.x = colCount * tileSize
                    imgRect.y = rowCount * tileSize
                    tile = (img, imgRect)
                    self.tileList.append(tile)
                if tile == 3:
                    blob = Enemy(colCount * tileSize, rowCount * tileSize + 5)
                    blobGroup.add(blob)
                if tile == 4:
                    lava = Lava(colCount * tileSize, rowCount * tileSize + (tileSize // 2))
                    lavaGroup.add(lava)
                colCount += 1
            rowCount += 1

    def draw(self):
        for tile in self.tileList:
            screen.blit(tile[0], tile[1])
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('2024/blob.png')
        self.image = pygame.transform.scale(self.image, (20, 15))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moveDirection = 1
        self.moveCounter = 0

    def update(self):
        self.rect.x += self.moveDirection
        self.moveCounter += 1
        if abs(self.moveCounter) > 40:
            self.moveDirection *= -1
            self.moveCounter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('2024/lava1.png')
        self.image = pygame.transform.scale(self.image, (tileSize, tileSize // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

worldData = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 2, 2, 1, 1, 1, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[1, 2, 2, 2, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
]

player = Player(650, screenHeight - 60)
blobGroup = pygame.sprite.Group()
lavaGroup = pygame.sprite.Group()
world = World(worldData)

run = True
while run:

    clock.tick(fps)

    screen.blit(sky, (0, 0))

    world.draw()

    if gameOver == 0:
        blobGroup.update()

    blobGroup.draw(screen)
    lavaGroup.draw(screen)

    gameOver = player.update(gameOver)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()