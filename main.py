""" 
TODO: Better running eyes
TODO: Win screen
TODO: Sounds
TODO: Code cleanup
TODO: Code documentation
TODO: Build executables
TODO: Timer for speedruns
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


### FUNCTIONS ##########################################################################################################


def tile_position(tile_ref, tile_size):
    """Returns the x and y coordinates of the top-left corner of a tile, given the tile's row and column.
       tile_ref is a 2-item sequence representing the column and row of the tile
       tile_size is the size of each tile as an int."""
    return tile_ref[0]*tile_size, tile_ref[1]*tile_size


def tile_ref(position, tile_size):
    """Returns the column and row of the tile at the given x and y coordinates.
    position is a pair of x, y coordinates as a 2-item sequence 
    tile_size is the size of each tile as an int"""
    # The coordinates are divided by the tile size and rounded down to the nearest integer
    return int(math.floor(position[0] / tile_size)), int(math.floor(position[1] / tile_size))
    

def tile_type(tile_ref, level, ground_default, sky_default):
    """Returns the tile type at the given column and row in the level. 
       tile_ref is the column and row of a tile as a 2-item sequence
       level is the nested list of tile types representing the level map. 
       ground_default is the tile type to return if the tile_ref is below the bottom of the level. 
       sky_default is the tile type to return if the tile_ref is above, to the left of, or to the right of the bounds of
       the level."""
    #
    #           sky    
    #           default
    #         +--------+
    # sky     | level  | sky
    # default |        | default
    #    - - -+--------+- - -
    #           ground 
    #           default
    #
    # return default 'ground' tile if reference is off the bottom of the level
    if tile_ref[1] >= len(level):
        return ground_default
    # look up tile type in nested level list if reference is inside bounds of level
    elif len(level)>0 and 0 <= tile_ref[0] < len(level[0]) and 0 <= tile_ref[1] < len(level):
        return level[tile_ref[1]][tile_ref[0]]
    # otherwise reference is above, left of or right of the level bounds. return default 'sky' tile
    else:
        return sky_default


def draw_background(screen, background, position, level_size, tile_size):
    """blits the given background graphic to to the screen surface. The background is scrolled according to the player's
       screen is the screen surface to blit onto
       background is the background surface to blit
       position in the level to give a parallax effect as they move around.
       position is a 2-item sequence representing x and y coordinate of the player
       level_size is a 2-item sequence representing tile number of columns and rows in the level
       tile_size is the size of each tile as an int"""
    # establish range of coordinates that the top left of the screen can be at within the background image
    min_x = 0.0
    max_x = background.get_width()-screen.get_width()
    min_y = 0.0
    max_y = background.get_height()-screen.get_height()
    # calculate how far across the level the player is, horizontally and vertically, each as a value from 0 to 1
    x_amount = position[0] / (level_size[0]*tile_size)
    y_amount = position[1] / (level_size[1]*tile_size)
    # apply these amounts to the coordinate ranges to get the top left corner of the section of background graphic to
    # use
    source_x = int(min_x + (max_x-min_x) * x_amount)
    source_y = int(min_y + (max_y-min_y) * y_amount)
    # take a screen-sized section of the background graphic, starting at the calculated position, and blit onto the
    # screen surface
    screen.blit(background, (0,0), (source_x, source_y, screen.get_width(), screen.get_height()))


def draw_tiles(screen, tile_buffer, last_position, position, level, tile_graphics, ground_tile, sky_tile, tile_size):
    """blits the section of level tiles currently visible to the player onto the screen surface.
       screen is the screen surface to blit onto
       tile_buffer is a screen-sized surface onto which the tiles are blitted before being blitted to the screen 
       surface. The buffer should contain the blitted tiles from the previous frame so that they can be reused if
       possible       
       last_position is the x,y position of the player in the level from the previous frame, as a 2-item sequence
       positon is the x,y position of the player in the level this frame, as a 2-item sequence
       level is the nested list of tile types representing the level
       tile_graphics is the list of graphics representing the available tile types
       ground_tile is the tile graphic used to draw tiles below the bottom of the level
       sky_tile is the tile graphic used to draw tiles above, to the left of, and to the right of the level
       tile_size is the size of each tile as an int"""
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
    """blit the appopriate graphic of Sam to the screen surface at the given offset from the centre.
       screen is the screen surface
       idle_graphic is the graphic to use when sam is stationary
       run_graphics is a sequence of animation frames used when sam is running
       jump_graphic is used when sam is jumping upwards
       fall_graphic is used when sam is falling downwards
       offset is the x,y offset from the screen centre at which to draw sam, as a 2-item sequence
       position is the x,y position of the player in the level as a 2-item sequence
       velocity is the current x and y speed of the player as a 2-item sequence
       landed is a boolean indicating whether sam is on a platform or not
       tile_size is the size of each tile, as an integer"""
    # if sam is in mid-air and moving upwards, show jumping graphic
    if not landed and velocity[1] <= 0:
        graphic = jump_graphic
    # if sam is in mid-air and moving downwards, show falling graphic
    elif not landed and velocity[1] > 0:
        graphic = fall_graphic
    # if sam is on the ground and not moving left or right, show idle graphic
    elif velocity[0] == 0.0:
        graphic = idle_graphic
    # if sam is on the ground and moving left or right, show a running graphic. The graphic shown is based on sam's x
    # coordinate so that as she moves faster, the graphics animate faster.
    else:
        num = len(run_graphics)
        graphic = run_graphics[int(position[0]//((tile_size*4)/num)) % num]
        
    # if sam is moving left, flip the graphic so that she is facing left instead of right
    if velocity[0] < 0.0:
        graphic = pygame.transform.flip(graphic, True, False)
        
    # draw the selected graphic to the screen. It's always drawn to the same place on the screen, just below the centre.
    screen.blit(graphic, (screen.get_width()/2-graphic.get_width()/2+offset[0], 
                          screen.get_height()/2-graphic.get_height()/2+offset[1]))
    
    
def find_position(tile_type, level, tile_size):
    """Finds the first occurence of the given tile type found in the level, and returns the x,y coordinates of its
    centre as a 2-tuple. If not found, returns 0,0"""
    # iterate through all the level tiles
    for j, row in enumerate(level):
        for i, tile in enumerate(row):
            # if this tile is the desired type, return its centre coordinates
            if tile == tile_type:
                return (i+0.5)*tile_size, (j+0.5)*tile_size             
    # if we got this far, the tile type wasn't found. Return default of 0,0
    return 0.0, 0.0


##### CONSTANTS ########################################################################################################
    
    
# These constants are just a handy way of refering to some of the special tile types.
TILE_START = 1
TILE_FINISH = 25
TILE_GROUND = 4
TILE_SKY = 0

def define_level():
    """Returns the level definition as a nested list; each item in the list is a row, and each item in a row is a
       column refering to a numerical tile type"""
       
    # We temporarily (just within the scope of this function) define these one-letter variables to refer to each tile
    # type a convenient and compact way of laying out the level definition in the nested list below.
    # This is a pretty cheap and cheerful way of defining the level, as it makes it awkward to add further tile types.
    # To extend the tile types further, you might want to consider using a tile-editor program such as Tiled.
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

    # The level definition
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

# Call the function above and store the result in LEVEL
LEVEL = define_level()

SCREEN_SIZE = 1024, 768     # The screen resolution the game runs at.
TILE_SIZE = 64              # The size of each tile (they're square so width and height use the same value)

# These constants define various aspects of Sam's movement. They were fine-tuned by trial and error.
GRAVITY = 0.64              # The rate at which Sam accellerates downwards due to gravity
JUMP_STRENGTH = 15.2        # Higher jump strength means Sam will jump higher
ACCELERATION = 0.26         # The rate that Sam speeds up to full running speed
DEACCELERATION = 0.26       # The rate that Sam skids to a stop after running
MAX_SPEED = 6.46            # Sam's maximum running speed

SAM_SIZE = 64               # The size of Sam's graphics
FEET_WIDTH = 38             # The width of the bit of Sam that sits on the platform:
                            #       |          |
                            #       |  feet w  | Sam
                            #       |  /    \  | 
                            #       +-+------+-+
                            #-----------+
                            # Platform  |
                            #           |
COLLIDABLE_TILES = {3,7,10,16,18,20}  # The tile types that Sam can stand on (platforms)

# Constants for the different states the game can be in (see below)
STATE_TITLE = 0
STATE_HELP = 1
STATE_GAME = 2
STATE_FAILED = 3
STATE_WON = 4


#### MAIN PROGRAM ######################################################################################################

# Initialise Pygame
pygame.init()
# Set the screen resolution and store the screen surface for drawing on
screen = pygame.display.set_mode(SCREEN_SIZE,pygame.locals.DOUBLEBUF|pygame.locals.HWSURFACE|pygame.locals.FULLSCREEN)
# Hide the mouse cursor
pygame.mouse.set_visible(False)
# Create a clock object for maintaining a consistent framerate
clock = pygame.time.Clock()
# Create an offscreen surface for more efficient tile drawing (see "draw_tiles" function)
tile_buffer = pygame.Surface(SCREEN_SIZE,flags=pygame.locals.SRCALPHA)

# Load graphics and store them in G_* variables. We call "convert" on our opaque background graphics to make pygame
# convert them to an optimal format for the screen buffer, which disables per-pixel alpha on them but makes them faster
# to draw
G_TITLE = pygame.image.load("title.png").convert(screen)
G_HELP = pygame.image.load("help.png").convert(screen)
G_SAM_IDLE = pygame.image.load("sam-idle.png")
G_SAM_RUN = [ pygame.image.load("sam-run1.png"), 
              pygame.image.load("sam-run2.png"), 
              pygame.image.load("sam-run3.png"),
              pygame.image.load("sam-run4.png"), ]
G_SAM_JUMP = pygame.image.load("sam-jump.png")
G_SAM_FALL = pygame.image.load("sam-fall.png")
G_SAM_WIN = pygame.image.load("sam-win.png")
G_SAM_FAIL = pygame.image.load("sam-fail.png")
G_BACKGROUND = pygame.image.load("background.png").convert(screen)
# load the tile graphics, each of which is named according to its numerical type. Type 0 is empty space and type 1 is
# the invisible start position. Neither of these have a graphic so we put None in the list for each of these.
G_TILES = [None, None]
for i in range(2,26):
    G_TILES.append(pygame.image.load("tile{:0>2}.png".format(i)))

# Load the fonts
F_BIG = pygame.font.Font("komika.ttf", 72)
F_SMALL = pygame.font.Font("komika.ttf", 36)

# Find the start and finish tiles in the level definition and store their x,y coordinates in these constants
START_POSITION = find_position(TILE_START, LEVEL, TILE_SIZE)
FINISH_POSITION = find_position(TILE_FINISH, LEVEL, TILE_SIZE)

state = STATE_TITLE   # The game's state - start on the title screen
position = [0.0,0.0]  # Sam's x,y coordinates
velocity = [0.0,0.0]  # Sam's x and y speed. These are added to Sam's position each frame to move her
landed = False        # Stores whether Sam is on a platform or not
last_cam_position = [0.0,0.0]  # Stores the position the "camera" was at for the previous frame. The camera is the 
                               # imaginary object that the viewport is centered on, just above Sam's head

# The main game loop. It loops until the player quits
while True:

    # variables to store whether the escape and space keys became pressed this frame or not. We only want to react to
    # these keys' initial pressed event - we don't care if they're held down.
    escape_pressed = False
    space_pressed = False
    # loop over the system events collected by Pygame
    for event in pygame.event.get():
        # if the player closed the window, quit
        if event.type == pygame.locals.QUIT:
            sys.exit()
        # if the escape or space (or anothe jump button) was pressed down this frame, set the corresponding variable
        if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_ESCAPE:
                escape_pressed = True
            elif event.key in (pygame.locals.K_SPACE, pygame.locals.K_UP, pygame.locals.K_w):
                space_pressed = True

    # The title screen
    if state == STATE_TITLE:  # ----------------------------------------------------------------------------------------

        # if player hits escape, quit the game
        if escape_pressed:
            sys.exit()
            
        # if player hits the jump button, proceed to the "how to play" screen
        if space_pressed:
            state = STATE_HELP
            
        # draw the title screen graphic to the screen surface
        screen.blit(G_TITLE, (0,0))
        
        
    # The "how to play" screen
    elif state == STATE_HELP:  #----------------------------------------------------------------------------------------
    
        # if the player hits the jump button or the escape key, set up the game and proceed to the main game state
        if space_pressed or escape_pressed:
            position = list(START_POSITION)
            velocity = [0.0,0.0]
            landed = False
            state = STATE_GAME
            
        # draw the "how to play" screen graphic to the screen surface
        screen.blit(G_HELP, (0,0))
        
        
    # The main game 
    elif state == STATE_GAME:  # ---------------------------------------------------------------------------------------

        # if the player hits the escape key, go back to the title screen
        if escape_pressed:
            state = STATE_TITLE

        # if the player is holding down one of the "left" keys (left cursor or A), accelerate Sam left
        if pygame.key.get_pressed()[pygame.locals.K_LEFT] or pygame.key.get_pressed()[pygame.locals.K_a]:
            # only accelerate if under max speed
            if velocity[0] > -MAX_SPEED:
                velocity[0] -= ACCELERATION
        # if the player is holding down one of the "right" keys (right cursor or D), accelerate Sam right
        elif pygame.key.get_pressed()[pygame.locals.K_RIGHT] or pygame.key.get_pressed()[pygame.locals.K_d]:
            # only accelerate if under max speed
            if velocity[0] < MAX_SPEED:
                velocity[0] += ACCELERATION
        # if the player isn't holding left or right, deacelerate Sam so she eventually comes to a halt
        else:
            # if moving right and subtracting DEACCELERATION wouldn't push speed past zero, deacelerate
            if velocity[0] > 0 and velocity[0]-DEACCELERATION >= 0:
                velocity[0] -= DEACCELERATION
            # if moving left and adding DEACCELERATION wouldn't push speed past zero, deacelerate
            elif velocity[0] < 0 and velocity[0]+DEACCELERATION <= 0:
                velocity[0] += DEACCELERATION
            # moving slower than DEACCELERATION, so just reduce speed to zero
            else:
                velocity[0] = 0.0
            
        # if player hits a jump button and Sam is on a platform, make Sam jump by setting her vertical speed
        if space_pressed and landed:
            velocity[1] = -JUMP_STRENGTH
            landed = False
    
        # store the column and row of the tile Sam was at before moving - this is used later
        tile_before = tile_ref(position, TILE_SIZE)
        # accelerate Sam downwards to simulate gravity, by increasing vertical speed
        velocity[1] += GRAVITY
        # move Sam by her velocity
        position[0] += velocity[0]
        position[1] += velocity[1]
        # store the column and row of the tile Sam has just moved to (at the middle of her feet)
        tile_after = tile_ref(position, TILE_SIZE)
        # also store column and row of the tiles at the left and right edges of Sam's feet
        tile_after_left = tile_ref((position[0]-FEET_WIDTH/2, position[1]), TILE_SIZE)
        tile_after_right = tile_ref((position[0]+FEET_WIDTH/2, position[1]), TILE_SIZE)
        
        # If Sam's position changed to a lower tile, and it was a collidable tile (i.e. she fell down into a platform).
        # This will happen every frame while Sam is standing on a platform.
        if tile_after[1] > tile_before[1] \
                and (tile_type(tile_after_left, LEVEL, 0, 0) in COLLIDABLE_TILES
                  or tile_type(tile_after_right, LEVEL, 0, 0) in COLLIDABLE_TILES):
            # Stop Sam moving vertically and position her just above the platform she fell into
            velocity[1] = 0.0
            position[1] = tile_position(tile_after, TILE_SIZE)[1] - 0.001
            landed = True
        # Otherwise, Sam isn't standing on a platform - she's in mid-air.
        else:
            landed = False
            
        # If Sam has fallen past the bottom of the level, go to the "game over" screen
        if position[1] >= len(LEVEL)*TILE_SIZE:
            state = STATE_FAILED
            
        # If Sam is on the finish tile, go to the "congratulations" screen
        if FINISH_POSITION[0]-TILE_SIZE/2 < position[0] < FINISH_POSITION[0]+TILE_SIZE/2 \
                and FINISH_POSITION[1]-TILE_SIZE/2 < position[1] < FINISH_POSITION[1]+TILE_SIZE/2:
            state = STATE_WON
    
        # The camera is the imaginary object that the viewport is centered on. Store it's position as just above Sam's
        # head, so the player sees slightly more of the level above Sam than below
        cam_position = [position[0], position[1]-SAM_SIZE]
        # Draw the background graphic
        draw_background(screen, G_BACKGROUND, cam_position, (len(LEVEL[0]), len(LEVEL)), TILE_SIZE)
        # Draw the tiles on top of the background
        draw_tiles(screen, tile_buffer, last_cam_position, cam_position, LEVEL, G_TILES, TILE_GROUND, 
                   TILE_SKY, TILE_SIZE)
        # Finally draw Sam on top of the tiles
        draw_sam(screen, G_SAM_IDLE, G_SAM_RUN, G_SAM_JUMP, G_SAM_FALL, (0, SAM_SIZE/2), position, velocity, landed, 
                 TILE_SIZE)
        
        # Update the last camera position so we can check how far the camera moved next frame
        last_cam_position = cam_position
                 
    # The "game over" screen
    elif state == STATE_FAILED:  # ------------------------------------------------------------------------------------ 
        
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
    #screen.blit(fps_text, (0,0))
                 
    pygame.display.flip()
    clock.tick(60)
