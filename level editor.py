#video part 3 beginning

import pygame

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

#define game variables
ROWS =  40
MAX_COLS = 160
TILE_SIZE = SCREEN_HEIGHT // ROWS

scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

#load images
sky_img = pygame.image.load('2024/cloud.png').convert_alpha()
cloud_img = pygame.image.load('images/cloudfluff.png').convert_alpha()

#define colours
PURPLE = (221, 171, 225)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

#create function for drawing background
def draw_bg():
    screen.fill(PURPLE)
    width = sky_img.get_width()
    for x in range(4):
        screen.blit(sky_img, ((x * width) -scroll * 0.5, 0))
        screen.blit (cloud_img, ((x * width) -scroll * 0.6, SCREEN_HEIGHT - cloud_img.get_height()))

#draw grid
def draw_grid():
    #vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    #horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()

    #scroll the map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True:
        scroll += 5 * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1
    
    pygame.display.update()

pygame.quit()