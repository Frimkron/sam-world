""" 
fill background, scroll buffer (srcalpha), clear edge tiles, blit edge tiles, blit buffer
    -> 40%
fill background, scroll buffer (colourkey), blit edge tiles, blit buffer
    -> 50%
fill background, clear buffer, draw previous buffer (srcalpha), blit edge tiles, blit buffer, swap buffers
    -> 170%
"""

import time
import sys
import math
import random
import pygame
import pygame.locals


# returns the x and y coordinates of the top-left corner of a tile, given the tile's row and column
def tile_position(tile_ref, tile_size):
    return tile_ref[0]*tile_size, tile_ref[1]*tile_size


# returns 
def tile_ref(position, tile_size):
    return int(math.floor(position[0] / tile_size)), int(math.floor(position[1] / tile_size))
    

def tile_type(tile_ref, level):
    if len(level)>0 and 0 <= tile_ref[0] < len(level[0]) and 0 <= tile_ref[1] < len(level):
        return level[tile_ref[1]][tile_ref[0]]
    else:
        return 0


def draw_background(screen, background, position, level_size, tile_size):
    min_x = 0.0
    max_x = background.get_width()-screen.get_width()
    min_y = 0.0
    max_y = background.get_height()-screen.get_height()
    x_amount = position[0] / (level_size[0]*tile_size)
    y_amount = position[1] / (level_size[1]*tile_size)
    source_x = int(min_x + (max_x-min_x) * x_amount)
    source_y = int(min_y + (max_y-min_y) * y_amount)
    screen.blit(background, (0,0), (source_x, source_y, screen.get_width(), screen.get_height()))


def draw_tiles(screen, tile_buffer, last_position, position, level, tile_graphics, tile_size):
    position = map(int, position)
    last_position = map(int, last_position)
    scrolled_amount = [position[0]-last_position[0], position[1]-last_position[1]]
    tile_buffer.scroll(-int(scrolled_amount[0]), -int(scrolled_amount[1]))
    top_left_position = position[0]-screen.get_width()/2, position[1]-screen.get_height()/2
    top_left_tile = tile_ref(top_left_position, tile_size)
    top_left_draw_pos = -(top_left_position[0] % tile_size), -(top_left_position[1] % tile_size)
    rows_to_draw = int(float(screen.get_height()) / tile_size + 1)
    cols_to_draw = int(float(screen.get_width()) / tile_size + 1)
    buffered_top_left = [0-scrolled_amount[0], 0-scrolled_amount[1]]
    buffered_bottom_right = [buffered_top_left[0]+screen.get_width(), buffered_top_left[1]+screen.get_height()]
    if buffered_top_left[0] > 0:
        tile_buffer.fill((0,0,0,0),(0,0,buffered_top_left[0]-0,screen.get_height()))
    if buffered_top_left[1] > 0:
        tile_buffer.fill((0,0,0,0),(0,0,screen.get_width(),buffered_top_left[1]-0))
    if buffered_bottom_right[0] < screen.get_width():
        tile_buffer.fill((0,0,0,0),(buffered_bottom_right[0],0,
                                    screen.get_width()-buffered_bottom_right[0], screen.get_height()))
    if buffered_bottom_right[1] < screen.get_height():
        tile_buffer.fill((0,0,0,0),(0,buffered_bottom_right[1],
                                    screen.get_width(), screen.get_height()-buffered_bottom_right[1]))
    for j in range(rows_to_draw):
        for i in range(cols_to_draw):
            tile = top_left_tile[0]+i, top_left_tile[1]+j
            type = tile_type(tile, level)
            tile_graphic = tile_graphics.get(type, None)
            if tile_graphic is not None:
                draw_pos = top_left_draw_pos[0]+i*tile_size, top_left_draw_pos[1]+j*tile_size
                if max(draw_pos[0],0) < buffered_top_left[0] \
                        or min(draw_pos[0]+tile_size,screen.get_width()) > buffered_bottom_right[0] \
                        or max(draw_pos[1],0) < buffered_top_left[1] \
                        or min(draw_pos[1]+tile_size,screen.get_height()) > buffered_bottom_right[1]:
                    tile_buffer.blit(tile_graphic, draw_pos)
    screen.blit(tile_buffer, (0,0))
                
           
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
    

# Constants to make the level definition below easier to work with - the letters kind of look like the
# tiles they represent. Tile numbers at or above FIRST_COLLIDABLE_TILE (defined as 100, later) can be jumped on.
T = 100 # platform
H = 1   # support
S = 2   # start positions
F = 3   # finish
Z = 101
O = 4
B = 5

# The tiles of the level, in rows. Each number identifies a tile type. Zero, for example, is empty space
LEVEL = [
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,S,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
    [H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H],
]
"""LEVEL = [
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
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,T,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,H,H,T,H,0,0,0,0,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
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
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,T,T,T,0,0,T,T,T,T,0,0,T,T,T,T,0,0,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,T,Z,Z,T,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,Z,0,0,0,0,0,0,T,T,T,T,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,0,0,0,0,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,Z,Z,Z,Z,0,0,0,0,0,0,0,0,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,H,H,H,H,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,0,H,H,Z,Z,Z,Z,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,S,0,Z,Z,Z,0,H,H,H,H,H,H,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,O,H,O,H,O,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,0,0,0,H,H,0,0,0,0,0,0,0,0,0,0,0],
]"""

# Constants defining various aspects of Sam's movement
SCREEN_SIZE = 1024, 768
TILE_SIZE = 64              # The size of each tile
GRAVITY = 0.64              # The rate at which Sam accellerates downwards due to gravity
JUMP_STRENGTH = 15.1        # Higher jump strength means Sam will jump higher
ACCELERATION = 0.26         # The rate that Sam speeds up to full running speed
DEACCELERATION = 0.26       # The rate that Sam skids to a stop after running
MAX_SPEED = 6.46            # Sam's maximum running speed
FEET_WIDTH = 38             # the width of the bit of Sam that sits on the platform
FIRST_COLLIDABLE_TILE = 100 # tile numbers at or above this value can be jumped on

# Constants for the different states the game can be in
STATE_TITLE = 0
STATE_HELP = 1
STATE_GAME = 2
STATE_FAILED = 3
STATE_WON = 4

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE,pygame.locals.DOUBLEBUF|pygame.locals.HWSURFACE)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
tile_buffer = pygame.Surface(SCREEN_SIZE,flags=pygame.locals.SRCALPHA)

G_TITLE = pygame.image.load("title.png")
G_HELP = pygame.image.load("help.png")
G_SAM_IDLE = pygame.image.load("sam-idle.png")
G_SAM_RUN = [ pygame.image.load("sam-run1.png"), pygame.image.load("sam-run2.png") ]
G_SAM_JUMP = pygame.image.load("sam-jump.png")
G_SAM_WIN = pygame.image.load("sam-win.png")
G_SAM_FAIL = pygame.image.load("sam-fail.png")
G_BACKGROUND = pygame.image.load("background.png").convert(screen)
G_TILES = {
    T: pygame.image.load("platform.png"),
    Z: pygame.image.load("support-platform.png"),
    H: pygame.image.load("support.png"),
    O: pygame.image.load("window.png"),
    B: pygame.image.load("window-bc.png"),
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
last_cam_position = [0.0,0.0]

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
            if velocity[0] > -MAX_SPEED:
                velocity[0] -= ACCELERATION
        elif pygame.key.get_pressed()[pygame.locals.K_RIGHT]:
            if velocity[0] < MAX_SPEED:
                velocity[0] += ACCELERATION
        else:
            if velocity[0] > 0 and velocity[0]-DEACCELERATION >= 0:
                velocity[0] -= DEACCELERATION
            elif velocity[0] < 0 and velocity[0]+DEACCELERATION <= 0:
                velocity[0] += DEACCELERATION
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
        tile_after_left = tile_ref((position[0]-FEET_WIDTH/2, position[1]), TILE_SIZE)
        tile_after_right = tile_ref((position[0]+FEET_WIDTH/2, position[1]), TILE_SIZE)
        
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
        start_time = time.time()
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        """tile_buffer.scroll(64,64)
        tile_buffer.fill((0,0,0,0),((0,0),(1024,64)))
        tile_buffer.fill((0,0,0,0),((0,64),(64,768)))
        i = 0
        while i < 1024:
            tile_buffer.blit(G_TILES[H if random.random()<0.5 else T],(i,0))
            i += 64
        i = 64
        while i < 758:
            tile_buffer.blit(G_TILES[H if random.random()<0.5 else T],(0,i))
            i += 64
        screen.blit(tile_buffer,(0,0))"""
        draw_tiles(screen, tile_buffer, last_cam_position, cam_position, LEVEL, G_TILES, TILE_SIZE)
        draw_sam(screen, G_SAM_IDLE, G_SAM_RUN, G_SAM_JUMP, (0, G_SAM_IDLE.get_height()/2), position, velocity, landed, 
                 TILE_SIZE)
        end_time = time.time()
        print(int((end_time-start_time)/(1.0/60.0)*100))
        
        last_cam_position = cam_position
                 
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

    fps_text = F_SMALL.render(str(int(clock.get_fps())), True, (0,0,0))
    screen.blit(fps_text, (0,0))
                 
    pygame.display.flip()
    clock.tick(60)
