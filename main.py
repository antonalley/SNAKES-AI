#!/usr/bin/env python
# -*- coding: <ASCII> -*-
# main.py


#################################
# ABOUT:
#
# The main file for snake game
# Run This file to manualy play the game
#
#################################

__author__ = "Anton Alley"
__copyright__ = "None"
__credits__ = ["Anton Alley"] 
__license__ = "None"
__version__ = "0.0.0"
__maintainer__ = "Anton Alley"
__email__ = "Anton.Alley@gmail.com"

# Builtin Imports
from random import randint
import time
import sys, os

# Third Party Imports
import pygame
from pygame.locals import *

# My Imports


# USE GRAPHICS:
##from platform import platform
##from os import environ
##
##if 'Windows' in platform():
##    environ['SDL_VIDEODRIVER'] = 'directx'


######### CONSTANTS:
FPS =           8 # the speed of the game
ARENA_SIZE =    (12,16) # DEFAULT FOR AI DON'T CHANGE!!
SQUARE_SIZE =   45
BOX_THICKNESS = int(SQUARE_SIZE / 10)

EMPTY = 0
SNAKE = 1
APPLE = 2

LIGHT_GRAY = (100,100,100)
PALE_RED   = (200, 40, 40)
WHITE      = (255,255,255)
###############

os.environ["SDL_VIDEO_CENTERED"] = '1' # Centers Screen


class player:
    def __init__(self):
        self.pos = (1, int(ARENA_SIZE[1] / 2))
        self.length = 1
        self.direction = (1,0)

    def getDir(self, direction):
        if direction == 'up':
            return (-1,0)
        elif direction == 'down':
            return (1,0)
        elif direction == 'left':
            return (0,-1)
        elif direction == 'right':
            return (0,1)
        elif direction == 'turnRight':
            tempDir = self.direction
            if tempDir[0] != 0:
                tempDir = (tempDir[0] * -1, tempDir[1])
            return (tempDir[1],tempDir[0])
        elif direction == 'turnLeft':
            tempDir = self.direction
            if tempDir[1] != 0:
                tempDir = (tempDir[0], tempDir[1] * -1)
            return (tempDir[1],tempDir[0])
        elif direction == 'continueStraight':
            return self.direction
        else:
            raise Exception(f"False Direction Given, no: {direction}")
        
    def move(self, direction):
        self.direction = self.getDir(direction)
            
    def update(self):
        posUD = self.direction[0] + self.pos[0]
        posLR = self.direction[1] + self.pos[1]
        self.pos = (posUD,posLR)



class gameMap:
    def __init__(self, snake):
        player.__init__(snake) # Re-intialize position, length etc. In case it changed

        self.grid = [[0 for i in range(ARENA_SIZE[1])] for i in range(ARENA_SIZE[0])]
        # 0 is empty, 1 is snake, 2 is apple
        self.apple = snake.pos
        while self.apple == snake.pos: # So apple doesn't overlap initially with snake
            self.apple = (randint(0,ARENA_SIZE[0]-1),randint(0,ARENA_SIZE[1]-1))
        self.grid[self.apple[0]][self.apple[1]] = APPLE
        
        self.ticker = []
        self.frame = 0
        self.update(snake)

    def __str__(self):
        toprint = ""
        for i in self.grid:
            for a in i:
                toprint += str(a)+" "
            toprint += "\n"
        print(toprint)
        return ""

    def update(self,snake):
        snake.update()
        # New begginning of snake, or DEATH:
        try:
            if snake.pos[0] >= 0 and snake.pos[0] < ARENA_SIZE[0] and snake.pos[1] >= 0 and snake.pos[1] < ARENA_SIZE[1] and self.grid[snake.pos[0]][snake.pos[1]] != SNAKE:
                    self.grid[snake.pos[0]][snake.pos[1]] = SNAKE
            else:
                return "ENDGAME", snake.length
        except:
            return "ENDGAME", snake.length
        

        # UPDATE SNAKE:
        self.ticker.append([snake.pos,self.frame])
        toDeleteIndicies = []
        for index, box in enumerate(self.ticker): # delete the end of the snake
            if self.frame - box[1] >= snake.length:
                self.grid[box[0][0]][box[0][1]] = EMPTY
                toDeleteIndicies.append(index)  #deletes the old positions that it has moved out of
                
        for index in toDeleteIndicies:
            del self.ticker[index]
            

        # APPLE SPAWN:
        if snake.pos == self.apple:
            self.apple = (randint(0,ARENA_SIZE[0]-1),randint(0,ARENA_SIZE[1]-1))
            snake.length += 1
            # So the apple can't spawn where the snake is:
            while self.grid[self.apple[0]][self.apple[1]] == 1:
                self.apple = (randint(0,ARENA_SIZE[0]-1),randint(0,ARENA_SIZE[1]-1))
            self.grid[self.apple[0]][self.apple[1]] = 2
                
                
        self.frame += 1
        return None


def test():
    s = player()
    g = gameMap(s)
    str(g)
    time.sleep(3)
    s.move("right")
    g.update(s)
    str(g)
    time.sleep(3)
    s.move('down')
    g.update(s)
    str(g)
    


def main():
    ######## Game Setup:
    s = player()
    g = gameMap(s)
    WIDTH, HEIGHT = ((SQUARE_SIZE * ARENA_SIZE[1]) , (SQUARE_SIZE * ARENA_SIZE[0]))
    ########
    
    DISPLAY = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
    pygame.display.set_caption(" ~SNAKE~")
    pygame.init()
    nextChangeDirection = []
    gameClock = pygame.time.Clock()
    pause = False
    while True:
        DISPLAY.fill((0,0,0))

        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    nextChangeDirection.append("down")
                    #s.move("down")
                if event.key == K_UP:
                    nextChangeDirection.append("up")
                    #s.move("up")
                if event.key == K_RIGHT:
                    nextChangeDirection.append("right")
                    #s.move("right")
                if event.key == K_LEFT:
                    nextChangeDirection.append("left")
                    #s.move("left")
                if event.key == K_p:
                    pause = not pause
                
            elif event.type == QUIT:
                print(f"The snake had a final length of: {s.length}")
                pygame.quit()
                sys.exit()


       
        ##################### The game:
        if not pause:
            if nextChangeDirection != []:
                s.move(nextChangeDirection[0])
                del nextChangeDirection[0]
            result = g.update(s)
            if result != None:
                print(f"The snake had a final length of: {result[1]}")
                if result[1] < 15:
                    print("Nice going stupid!")
                else:
                    print("Great Job!")
                pygame.quit()
                sys.exit()
        for c, C in enumerate(g.grid):
            for r, R in enumerate(C):
                if R == 1:  # Snake
                    rect = ((r * SQUARE_SIZE, c * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(DISPLAY, WHITE, rect)
                elif R == 2: # Apple
                    rect = ((r * SQUARE_SIZE, c * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(DISPLAY, PALE_RED, rect)

        #########################
        

        # The grid:
        for R in range(ARENA_SIZE[1]):
            for D in range(ARENA_SIZE[0]):
                rect = ((R * SQUARE_SIZE, D * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(DISPLAY, LIGHT_GRAY, rect, BOX_THICKNESS)

        pygame.display.flip()
        gameClock.tick(FPS)

    

                
    return None


if __name__ == "__main__":
    main()
