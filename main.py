""" 
TODO: Better running eyes
TODO: Title screen
TODO: Win screen
TODO: Help screen
TODO: Sounds
TODO: Code cleanup
TODO: Code documentation
TODO: Build executables
TODO: WASD keys
TODO: Second fall frame
TODO: Music
TODO: Teeter graphics

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
    

def tile_type(tile_ref, level, ground_default, sky_default):
    if tile_ref[1] >= len(level):
        return ground_default
    elif len(level)>0 and 0 <= tile_ref[0] < len(level[0]) and 0 <= tile_ref[1] < len(level):
        return level[tile_ref[1]][tile_ref[0]]
    else:
        return sky_default


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


def draw_tiles(screen, tile_buffer, last_position, position, level, tile_graphics, ground_tile, sky_tile, tile_size):
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
            type = tile_type(tile, level, ground_tile, sky_tile)
            tile_graphic = tile_graphics[type]
            if tile_graphic is not None:
                draw_pos = top_left_draw_pos[0]+i*tile_size, top_left_draw_pos[1]+j*tile_size
                if max(draw_pos[0],0) < buffered_top_left[0] \
                        or min(draw_pos[0]+tile_size,screen.get_width()) > buffered_bottom_right[0] \
                        or max(draw_pos[1],0) < buffered_top_left[1] \
                        or min(draw_pos[1]+tile_size,screen.get_height()) > buffered_bottom_right[1]:
                    tile_buffer.blit(tile_graphic, draw_pos)
    screen.blit(tile_buffer, (0,0))
                
           
def draw_sam(screen, idle_graphic, run_graphics, jump_graphic, fall_graphic, offset, position, velocity, landed, 
        tile_size):
    if not landed and velocity[1] <= 0:
        graphic = jump_graphic
        
    elif not landed and velocity[1] > 0:
        graphic = fall_graphic
    elif velocity[0] == 0.0:
        graphic = idle_graphic
    else:
        num = len(run_graphics)
        graphic = run_graphics[int(position[0]//((tile_size*4)/num)) % num]
        
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
    
    
TILE_START = 1
TILE_FINISH = 25
TILE_GROUND = 4
TILE_SKY = 0

def define_level():
    S = TILE_START
    N = 2 # concrete
    Z = 3 # concreate platform
    W = 4 # window
    C = 5 # window sign
    H = 6 # brick
    E = 7 # brick platform
    M = 8 # brick sign
    G = 9 # plate
    P = 10 # plate platform
    Q = 11 # plate porthole
    J = 12 # plate left
    K = 13 # plate right
    V = 14 # plate white
    D = 15 # books
    B = 16 # books platform
    X = 17 # circuits
    Y = 18 # circuits platform
    I = 19 # tesla
    T = 20 # tesla platform
    O = 21 # tesla top
    L = 22 # sign left
    R = 23 # sign right
    U = 24 # sign up
    F = TILE_FINISH

    return [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,J,K,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,J,G,G,K,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,W,C,G,G,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,J,V,V,V,V,K,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,G,Q,G,G,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,V,V,V,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,G,Q,G,G,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,J,V,V,F,V,K,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,Z,Z,Z,Z,Z,Z,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,W,C,W,W,C,C,W,W,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,N,N,N,N,N,N,N,Z,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Y,Y,H,M,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,Y,Y,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Y,Y,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,P,0,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,I,0,0,0,H,H,C,H,0,0,0,0,L,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,I,P,0,0,H,H,E,H,0,0,0,0,P,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,I,I,0,0,H,H,H,H,0,0,0,0,0,0,0,0,P,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,I,I,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,I,I,0,0,H,H,M,H,0,0,0,0,0,0,0,0,0,0,B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,I,I,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,D,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,X,X,X,X,X,X,G,X,0,0,H,H,H,H,0,0,0,0,0,0,0,0,0,0,D,B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,I,0,0,X,G,X,X,X,X,P,X,0,0,H,H,H,H,K,0,0,0,0,0,0,0,0,0,D,D,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,X,X,X,X,P,X,X,X,X,X,X,0,0,H,H,H,H,G,G,G,X,X,X,P,G,0,0,D,D,B,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,G,X,X,X,X,X,X,X,X,X,X,0,0,H,W,H,H,0,G,G,X,X,X,G,Q,0,0,D,D,D,U,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,P,X,X,0,0,0,0,0,0,0,0,0,0,H,E,H,H,0,G,P,X,X,0,G,Q,0,0,Y,Y,Y,Y,Y,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,R,0,X,X,X,0,0,0,0,0,L,0,0,0,0,H,H,I,H,0,0,0,0,X,0,0,0,0,0,0,V,X,V,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,B,0,I,0,I,0,0,0,0,0,B,0,0,0,0,I,H,I,I,0,0,0,0,0,0,0,0,0,0,0,V,X,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,D,0,I,0,I,0,0,B,0,0,D,0,0,B,0,0,I,0,0,0,O,0,0,0,0,O,0,0,0,0,X,X,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,E,0,I,0,0,0,0,D,0,0,D,0,0,P,K,0,0,0,0,0,I,0,0,0,0,I,0,0,0,0,X,X,O,0,O,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,I,0,0,0,0,D,0,0,D,0,0,0,G,P,0,0,0,0,T,0,0,0,0,T,0,0,0,L,X,X,T,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,T,0,0,0,0,D,0,0,D,0,0,0,0,0,0,0,0,0,I,0,0,0,0,I,0,0,0,Y,X,X,I,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,I,0,0,0,0,D,0,0,D,0,0,0,0,0,0,0,0,O,I,0,0,O,0,I,0,0,0,X,X,X,I,0,T,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,D,0,0,D,0,0,0,R,0,0,0,0,I,I,0,0,I,0,I,0,0,0,X,0,X,I,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,D,0,0,D,0,0,0,E,0,0,0,0,T,T,0,0,T,0,I,0,Y,X,X,X,X,Y,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,D,0,0,D,0,0,0,0,0,0,0,0,I,I,0,0,I,0,I,0,0,0,X,X,X,0,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,D,0,P,P,0,0,0,0,0,0,0,0,I,I,0,0,I,L,I,0,0,0,X,X,X,0,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,D,J,G,G,0,0,0,0,0,0,0,0,I,I,0,0,P,P,P,0,0,0,X,X,0,0,0,I,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,P,P,G,G,0,0,0,0,0,0,0,0,E,E,0,0,G,G,G,0,0,P,P,P,0,0,0,I,D,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,G,G,G,G,0,0,0,0,0,0,0,0,H,H,0,0,V,G,V,0,0,G,V,Q,0,0,P,P,P,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,D,0,0,0,P,P,0,0,0,0,0,0,0,0,V,V,0,0,G,V,G,0,0,I,0,0,0,0,G,G,G,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,E,E,0,0,0,0,0,0,0,0,0,P,P,0,V,V,0,0,V,0,V,0,0,I,0,0,0,0,G,P,P,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,G,G,0,V,V,0,0,G,V,G,0,0,I,0,0,0,0,G,G,G,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,E,E,0,0,0,0,I,I,0,V,V,R,0,V,G,V,0,0,I,0,0,0,0,G,X,P,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,M,0,0,0,0,I,I,0,V,V,P,P,G,V,G,0,P,P,0,0,0,0,G,X,G,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,R,0,0,0,0,0,H,H,0,0,0,0,I,I,0,V,V,G,G,V,G,V,0,G,G,0,0,0,0,G,G,P,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,Z,N,N,N,N,Z,Z,N,N,N,N,Z,Z,N,V,V,G,G,G,V,G,0,G,G,0,0,0,0,G,G,G,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,J,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,E,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,Z,Z,Z,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,E,E,E,E,E,E,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,J,H,H,W,C,W,C,W,C,W,W,H,H,W,W,C,W,C,W,C,W,W,H,H,W,W,C,W,C,W,C,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,Z,Z,Z,H,H,W,W,C,W,C,W,C,W,H,H,W,C,W,C,W,C,W,C,W,H,H,W,C,W,C,W,C,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,Z,Z,Z,Z,Z,Z,N,N,H,H,Z,Z,Z,Z,N,N,N,N,N,M,H,N,N,N,N,N,N,N,N,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,Z,Z,Z,Z,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,N,N,N,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,M,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,Z,Z,Z,Z,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,E,E,E,E,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,M,H,H,H,H,H,H,H,H,E,E,E,E,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,Z,Z,Z,Z,W,W,H,H,W,W,W,W,Z,Z,Z,Z,W,H,H,W,W,W,W,W,Z,Z,Z,Z,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,H,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,Z,Z,Z,Z,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,Z,Z,Z,N,N,N,N,N,N,Z,Z,Z,Z,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,Z,Z,Z,Z,W,H,H,W,W,W,W,W,Z,Z,Z,Z,Z,Z,Z,Z,Z,Z,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,N,N,N,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,H,H,W,W,W,W,W,Z,Z,Z,Z,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,R,S,0,H,H,Z,Z,Z,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,E,E,E,E,E,E,E,E,E,E,E,E,E,E,E,E,N,N,N,N,N,N,N,N,N,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,W,W,W,W,H,H,H,H,H,H,H,H,H,H,H,H,N,N,N,N,N,N,N,N,N,H,H,H,H,H,H,H,H,H,H,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,W,W,W,W,H,H,W,W,W,W,C,W,W,C,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,N,N,N,N,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,W,W,W,W,H,H,N,N,N,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,N,H,H,N,N,N,N,N,N,N,N,H,H,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,W,H,H,W,W,W,W,W,W,W,W,H,H,0,0,0,0,0,0,0,0,0,0],
    ]

LEVEL = define_level()

# Constants defining various aspects of Sam's movement
SCREEN_SIZE = 1024, 768
TILE_SIZE = 64              # The size of each tile
GRAVITY = 0.64              # The rate at which Sam accellerates downwards due to gravity
JUMP_STRENGTH = 15.2        # Higher jump strength means Sam will jump higher
ACCELERATION = 0.26         # The rate that Sam speeds up to full running speed
DEACCELERATION = 0.26       # The rate that Sam skids to a stop after running
MAX_SPEED = 6.46            # Sam's maximum running speed
SAM_SIZE = 64
FEET_WIDTH = 38             # the width of the bit of Sam that sits on the platform
COLLIDABLE_TILES = {3,7,10,16,18,20}

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

G_TITLE = pygame.transform.scale(pygame.image.load("title.png"),SCREEN_SIZE)
G_HELP = pygame.transform.scale(pygame.image.load("help.png"),SCREEN_SIZE)
G_SAM_IDLE = pygame.image.load("sam-idle.png")
G_SAM_RUN = [ pygame.image.load("sam-run1.png"), 
              pygame.image.load("sam-run2.png"), 
              pygame.image.load("sam-run3.png"),
              pygame.image.load("sam-run4.png"), ]
G_SAM_JUMP = pygame.image.load("sam-jump.png")
G_SAM_FALL = pygame.image.load("sam-fall.png")
G_SAM_WIN = pygame.transform.scale(pygame.image.load("sam-win.png"),(64,64))
G_SAM_FAIL = pygame.transform.scale(pygame.image.load("sam-fail.png"),(64,64))
G_BACKGROUND = pygame.image.load("background.png").convert(screen)
G_TILES = [None, None]
for i in range(2,26):
    G_TILES.append(pygame.image.load("tile{:0>2}.png".format(i)))

F_BIG = pygame.font.Font("komika.ttf", 72)
F_SMALL = pygame.font.Font("komika.ttf", 36)

START_POSITION = find_position(TILE_START, LEVEL, TILE_SIZE)
FINISH_POSITION = find_position(TILE_FINISH, LEVEL, TILE_SIZE)

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
                and (tile_type(tile_after_left, LEVEL, 0, 0) in COLLIDABLE_TILES
                  or tile_type(tile_after_right, LEVEL, 0, 0) in COLLIDABLE_TILES):
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
    
        cam_position = [position[0], position[1]-SAM_SIZE]
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        draw_tiles(screen, tile_buffer, last_cam_position, cam_position, LEVEL, G_TILES, TILE_GROUND, 
                   TILE_SKY, TILE_SIZE)
        draw_sam(screen, G_SAM_IDLE, G_SAM_RUN, G_SAM_JUMP, G_SAM_FALL, (0, SAM_SIZE/2), position, velocity, landed, 
                 TILE_SIZE)
        
        last_cam_position = cam_position
                 
    elif state == STATE_FAILED: 
        
        if space_pressed or escape_pressed:
            state = STATE_TITLE
            
        cam_position = [position[0], position[1]-SAM_SIZE]
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        draw_tiles(screen, tile_buffer, last_cam_position, cam_position, LEVEL, G_TILES, TILE_GROUND, 
                   TILE_SKY, TILE_SIZE)
        screen.blit(G_SAM_FAIL, (screen.get_width()/2-G_SAM_FAIL.get_width()/2, screen.get_height()/2))
                 
        gameover_text = F_BIG.render("Whoops!", True, (255,0,0))
        screen.blit(gameover_text, (screen.get_width()/2-gameover_text.get_width()/2, 
                                    screen.get_height()/3-gameover_text.get_height()/2))
                                    
        press_space_text = F_BIG.render("Press space", True, (255,0,0))
        screen.blit(press_space_text, (screen.get_width()/2-press_space_text.get_width()/2,
                                       screen.get_height()/6*5-press_space_text.get_height()/2))
                                       
        last_cam_position = cam_position
             
    elif state == STATE_WON:
    
        if space_pressed or escape_pressed:
            state = STATE_TITLE
            
        cam_position = [position[0], position[1]-SAM_SIZE]
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        draw_tiles(screen, tile_buffer, last_cam_position, cam_position, LEVEL, G_TILES, TILE_GROUND, 
                   TILE_SKY, TILE_SIZE)
        screen.blit(G_SAM_WIN, (screen.get_width()/2-G_SAM_WIN.get_width()/2, screen.get_height()/2))
                 
        congrats_text = F_BIG.render("Congratulations!", True, (255,0,0))
        screen.blit(congrats_text, (screen.get_width()/2-congrats_text.get_width()/2, 
                                    screen.get_height()/3-congrats_text.get_height()/2))
                                    
        press_space_text = F_BIG.render("Press space", True, (255,0,0))
        screen.blit(press_space_text, (screen.get_width()/2-press_space_text.get_width()/2,
                                       screen.get_height()/6*5-press_space_text.get_height()/2))
                                       
        last_cam_position = cam_position

    fps_text = F_SMALL.render(str(int(clock.get_fps())), True, (0,0,0))
    screen.blit(fps_text, (0,0))
                 
    pygame.display.flip()
    clock.tick(60)
