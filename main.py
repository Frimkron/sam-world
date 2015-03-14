
import sys
import math
import pygame
import pygame.locals


def tile_position(tile_ref, tile_size):
    return tile_ref[0]*tile_size, tile_ref[1]*tile_size


def tile_ref(position, tile_size):
    return int(math.floor(position[0] / tile_size)), int(math.floor(position[1] / tile_size))
    

def tile_type(tile_ref, level):
    if len(level)>0 and 0 <= tile_ref[0] < len(level[0]) and 0 <= tile_ref[1] < len(level):
        return level[tile_ref[1]][tile_ref[0]]
    else:
        return 0


def draw_background(screen, background, position, level_size, tile_size):
    min_x = 0.0
    max_x = -(background.get_width()-screen.get_width())
    min_y = 0.0
    max_y = -(background.get_height()-screen.get_height())
    x_amount = position[0] / (level_size[0]*tile_size)
    y_amount = position[1] / (level_size[1]*tile_size)
    draw_x = int(min_x + (max_x-min_x) * x_amount)
    draw_y = int(min_y + (max_y-min_y) * y_amount)
    screen.blit(background, (draw_x,draw_y))


def draw_tiles(screen, position, level, tile_graphics, tile_size):
    top_left_position = position[0]-screen.get_width()/2, position[1]-screen.get_height()/2
    top_left_tile = tile_ref(top_left_position, tile_size)
    top_left_draw_pos = -(top_left_position[0] % tile_size), -(top_left_position[1] % tile_size)
    rows_to_draw = int(float(screen.get_height()) / tile_size + 1)
    cols_to_draw = int(float(screen.get_width()) / tile_size + 1)
    for j in range(rows_to_draw):
        for i in range(cols_to_draw):
            tile = top_left_tile[0]+i, top_left_tile[1]+j
            type = tile_type(tile, level)
            tile_graphic = tile_graphics.get(type, None)
            if tile_graphic is not None:
                draw_pos = top_left_draw_pos[0]+i*tile_size, top_left_draw_pos[1]+j*tile_size
                screen.blit(tile_graphic, draw_pos)
    
T = 100
H = 1
LEVEL = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,T,T,T,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,T,T,T,T,T,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,H,0,H,0,H,0,H,0,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,H,0,H,0,H,0,H,0,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,H,0,H,0,H,0,H,0,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,H,0,H,0,H,0,H,0,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,H,0,H,0,H,0,H,0,H,0,0,0,0,0,0,0,0,0,0,0],
]
TILE_SIZE = 50
GRAVITY = 0.25
JUMP_STRENGTH = 8.25
MOVE_SPEED = 3.5
FIRST_COLLIDABLE_TILE = 100

pygame.init()
screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

G_SAM = pygame.image.load("sam.png")
G_BACKGROUND = pygame.image.load("background.png")
G_TILES = {
    100: pygame.image.load("platform.png"),
    1: pygame.image.load("support.png"),
}

position = [5*TILE_SIZE, 13*TILE_SIZE]
velocity = [0.0,0.0]
landed = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT \
                or (event.type == pygame.locals.KEYUP and event.key == pygame.locals.K_ESCAPE) :
            sys.exit()
        if event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_SPACE and landed:
            velocity[1] = -JUMP_STRENGTH
            landed = False

    if pygame.key.get_pressed()[pygame.locals.K_LEFT]:
        velocity[0] = -MOVE_SPEED
    elif pygame.key.get_pressed()[pygame.locals.K_RIGHT]:
        velocity[0] = MOVE_SPEED
    else:
        velocity[0] = 0.0

    tile_before = tile_ref(position, TILE_SIZE)
    velocity[1] += GRAVITY
    position[0] += velocity[0]
    position[1] += velocity[1]
    tile_after = tile_ref(position, TILE_SIZE)
    tile_after_left = tile_ref((position[0]-G_SAM.get_width()/2, position[1]), TILE_SIZE)
    tile_after_right = tile_ref((position[0]+G_SAM.get_width()/2, position[1]), TILE_SIZE)
    
    if tile_after[1] > tile_before[1] \
            and (tile_type(tile_after_left, LEVEL) >= FIRST_COLLIDABLE_TILE \
              or tile_type(tile_after_right, LEVEL) >= FIRST_COLLIDABLE_TILE):
        velocity[1] = 0.0
        position[1] = tile_position(tile_after, TILE_SIZE)[1] - 0.001
        landed = True
    else:
        landed = False

    cam_position = [position[0], position[1]-G_SAM.get_height()]
    draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
    draw_tiles(screen, cam_position, LEVEL, G_TILES, TILE_SIZE)
    screen.blit(G_SAM, (screen.get_width()/2-G_SAM.get_width()/2,screen.get_height()/2))

    pygame.display.flip()
    clock.tick(60)
