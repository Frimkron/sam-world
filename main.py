
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
                
           
def draw_sam(screen, idle_graphic, run_graphics, jump_graphic, offset, position, velocity, landed, tile_size):
    if not landed:
        graphic = jump_graphic
    elif velocity[0] == 0.0:
        graphic = idle_graphic
    else:
        num = len(run_graphics)
        graphic = run_graphics[int(position[0]//(tile_size/num)) % num]
        
    if velocity[0] < 0.0:
        graphic = pygame.transform.flip(graphic, True, False)
        
    screen.blit(graphic, (screen.get_width()/2-graphic.get_width()/2+offset[0], 
                          screen.get_height()/2-graphic.get_height()/2+offset[1]))
    
    
def find_position(tile_type, level, tile_size):
    for j, row in enumerate(level):
        for i, tile in enumerate(row):
            if tile == tile_type:
                return (i+0.5)*tile_size, (j+0.5)*tile_size             
    return 0.0, 0.0
    
    
T = 100
H = 1
S = 2
F = 3
LEVEL = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,F,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,T,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,H,H,T,H,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,T,0,0,0,0,0,0,0,T,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,T,0,0,0,0,T,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,T,T,0,0,T,0,0,0,T,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,0,0,0,0,T,T,0,0,0,0,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,T,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,T,T,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,0,0,T,T,T,T,0,0,T,T,T,T,0,0,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,T,T,T,T,0,0,0,0,0,0,0,0,T,T,T,T,T,T,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,H,H,H,H,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,H,H,T,T,T,T,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,S,0,T,T,T,0,H,H,H,H,H,H,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,0,0,0,0,0,H,0,0,0,0,0,0,0,0,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,0,0,0,0,0,0,0,0,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,0,0,0,0,0,0,0,0,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,0,0,0,0,0,0,0,0,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,0,0,0,0,0,0,0,0,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,0,0,0,0,0,0,0,0,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]
# Sam can jump up 2 tiles and across 6 tiles
TILE_SIZE = 50
GRAVITY = 0.5
JUMP_STRENGTH = 11.8
MOVE_SPEED = 5.0
FIRST_COLLIDABLE_TILE = 100

STATE_TITLE = 0
STATE_HELP = 1
STATE_GAME = 2
STATE_FAILED = 3
STATE_WON = 4

pygame.init()
screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

G_TITLE = pygame.image.load("title.png")
G_HELP = pygame.image.load("help.png")
G_SAM_IDLE = pygame.image.load("sam-idle.png")
G_SAM_RUN = [ pygame.image.load("sam-run1.png"), pygame.image.load("sam-run2.png") ]
G_SAM_JUMP = pygame.image.load("sam-jump.png")
G_SAM_WIN = pygame.image.load("sam-win.png")
G_SAM_FAIL = pygame.image.load("sam-fail.png")
G_BACKGROUND = pygame.image.load("background.png")
G_TILES = {
    T: pygame.image.load("platform.png"),
    H: pygame.image.load("support.png"),
    F: pygame.image.load("exit.png"),
}

F_BIG = pygame.font.Font("komika.ttf", 72)
F_SMALL = pygame.font.Font("komika.ttf", 36)

START_POSITION = find_position(S, LEVEL, TILE_SIZE)
FINISH_POSITION = find_position(F, LEVEL, TILE_SIZE)

state = STATE_TITLE
position = [0.0,0.0]
velocity = [0.0,0.0]
landed = False

while True:

    escape_pressed = False
    space_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            sys.exit()
        if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_ESCAPE:
                escape_pressed = True
            elif event.key == pygame.locals.K_SPACE:
                space_pressed = True

    if state == STATE_TITLE: 

        if escape_pressed:
            sys.exit()
            
        if space_pressed:
            state = STATE_HELP
            
        screen.blit(G_TITLE, (0,0))
        
        press_space_text = F_BIG.render("Press space to start", True, (255,0,0))
        screen.blit(press_space_text, (screen.get_width()/2-press_space_text.get_width()/2,
                                       screen.get_height()/6*5-press_space_text.get_height()/2))

    elif state == STATE_HELP:
    
        if space_pressed or escape_pressed:
            position = list(START_POSITION)
            velocity = [0.0,0.0]
            landed = False
            state = STATE_GAME
            
        screen.blit(G_HELP, (0,0))
        
        line_y = 50
        for line in ["This is some text that explains how to play and why",
                     "Sam is jumping around all over the place and stuff.",
                     "Now this is a story all about how my life got switched",
                     "turned upside-down I'd like to take a minute so sit"]:
            line_text = F_SMALL.render(line, True, (0,0,0))
            screen.blit(line_text, (50,line_y))
            line_y += 50
            
        press_space_text = F_BIG.render("Press space", True, (255,0,0))
        screen.blit(press_space_text, (screen.get_width()/2-press_space_text.get_width()/2,
                                       screen.get_height()/6*5-press_space_text.get_height()/2))
        
    elif state == STATE_GAME: 

        if escape_pressed:
            state = STATE_TITLE

        if pygame.key.get_pressed()[pygame.locals.K_LEFT]:
            velocity[0] = -MOVE_SPEED
        elif pygame.key.get_pressed()[pygame.locals.K_RIGHT]:
            velocity[0] = MOVE_SPEED
        else:
            velocity[0] = 0.0
            
        if space_pressed and landed:
            velocity[1] = -JUMP_STRENGTH
            landed = False
    
        tile_before = tile_ref(position, TILE_SIZE)
        velocity[1] += GRAVITY
        position[0] += velocity[0]
        position[1] += velocity[1]
        tile_after = tile_ref(position, TILE_SIZE)
        tile_after_left = tile_ref((position[0]-G_SAM_IDLE.get_width()/2, position[1]), TILE_SIZE)
        tile_after_right = tile_ref((position[0]+G_SAM_IDLE.get_width()/2, position[1]), TILE_SIZE)
        
        if tile_after[1] > tile_before[1] \
                and (tile_type(tile_after_left, LEVEL) >= FIRST_COLLIDABLE_TILE
                  or tile_type(tile_after_right, LEVEL) >= FIRST_COLLIDABLE_TILE):
            velocity[1] = 0.0
            position[1] = tile_position(tile_after, TILE_SIZE)[1] - 0.001
            landed = True
        else:
            landed = False
            
        if position[1] >= len(LEVEL)*TILE_SIZE:
            state = STATE_FAILED
            
        if FINISH_POSITION[0]-TILE_SIZE/2 < position[0] < FINISH_POSITION[0]+TILE_SIZE/2 \
                and FINISH_POSITION[1]-TILE_SIZE/2 < position[1] < FINISH_POSITION[1]+TILE_SIZE/2:
            state = STATE_WON
    
        cam_position = [position[0], position[1]-G_SAM_IDLE.get_height()]
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        draw_tiles(screen, cam_position, LEVEL, G_TILES, TILE_SIZE)
        draw_sam(screen, G_SAM_IDLE, G_SAM_RUN, G_SAM_JUMP, (0, G_SAM_IDLE.get_height()/2), position, velocity, landed, 
                 TILE_SIZE)
                 
    elif state == STATE_FAILED: 
        
        if space_pressed or escape_pressed:
            state = STATE_TITLE
            
        cam_position = [position[0], position[1]-G_SAM_IDLE.get_height()]
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        draw_tiles(screen, cam_position, LEVEL, G_TILES, TILE_SIZE)
        screen.blit(G_SAM_FAIL, (screen.get_width()/2-G_SAM_FAIL.get_width()/2, screen.get_height()/2))
                 
        gameover_text = F_BIG.render("Whoops!", True, (255,0,0))
        screen.blit(gameover_text, (screen.get_width()/2-gameover_text.get_width()/2, 
                                    screen.get_height()/3-gameover_text.get_height()/2))
                                    
        press_space_text = F_BIG.render("Press space", True, (255,0,0))
        screen.blit(press_space_text, (screen.get_width()/2-press_space_text.get_width()/2,
                                       screen.get_height()/6*5-press_space_text.get_height()/2))
             
    elif state == STATE_WON:
    
        if space_pressed or escape_pressed:
            state = STATE_TITLE
            
        cam_position = [position[0], position[1]-G_SAM_IDLE.get_height()]
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        draw_tiles(screen, cam_position, LEVEL, G_TILES, TILE_SIZE)
        screen.blit(G_SAM_WIN, (screen.get_width()/2-G_SAM_WIN.get_width()/2, screen.get_height()/2))
                 
        congrats_text = F_BIG.render("Congratulations!", True, (255,0,0))
        screen.blit(congrats_text, (screen.get_width()/2-congrats_text.get_width()/2, 
                                    screen.get_height()/3-congrats_text.get_height()/2))
                                    
        press_space_text = F_BIG.render("Press space", True, (255,0,0))
        screen.blit(press_space_text, (screen.get_width()/2-press_space_text.get_width()/2,
                                       screen.get_height()/6*5-press_space_text.get_height()/2))
                 
    pygame.display.flip()
    clock.tick(60)
