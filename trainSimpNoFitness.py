#!/usr/bin/env python
# -*- coding: <ASCII> -*-
# train.py

#####CURRENTLY WORKING ON:
# 
# Different setups for training model, different fitnesses
# Trying diff setups with same random seed to eliminate differences


#################################
# ABOUT:
#
# 
#
# This module is to train the AI for the snakes game
#
# Run __main__ will run a visual instance of the best trained AI playing the game
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
import random
import time
import sys, os
import math
from copy import deepcopy

# Third Party Imports
import pygame
from pygame.locals import *
import matplotlib.pyplot as plt
import numpy as np

# My Imports
import main as SG
from AI_v0_2 import Network as BACKGROUND_AI
#from trainOG import evolve

######### CONSTANTS:
SG.ARENA_SIZE = (12, 12)
BOARD_SIZE = 144
INPUT_DATA_SIZE = 9
EMPTY = 0
SNAKE = 1
APPLE = 2
###############

class SnakeAi(BACKGROUND_AI, SG.player):
    def __init__(self, networkShape=[INPUT_DATA_SIZE, 12,16,9,3], file = None):
        BACKGROUND_AI.__init__(self, networkShape=networkShape, file=file)
        SG.player.__init__(self)

    def GetMove(self, inputData):                
        output = self.feedForward(inputData)
        resultingMove = output.index(max(output))
        if resultingMove == 0:
            return "continueStraight"
        elif resultingMove == 1:
            return "turnRight"
        elif resultingMove == 2:
            return "turnLeft"
        else:
            raise Exception(f"IMPROPER OUTPUT FROM the Neural Network: {output}")
        

def distance(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def GetInputs(game, snakePlayer):
    applePos = game.apple
    distanceToApple = distance(applePos, snakePlayer.pos)
    ###Input figuring out:
    inputs = [0] * INPUT_DATA_SIZE
    
    #Staying alive (0-5):
    directions = ['continueStraight', 'turnLeft', 'turnRight']
    
    for DIR, index in zip(directions, range(0, 6, 2)):
        stepper = snakePlayer.pos
        stepper = (stepper[0] + snakePlayer.getDir(DIR)[0],
               stepper[1] + snakePlayer.getDir(DIR)[1])
        while stepper[0] >= 0 and stepper[1] >= 0 and stepper[0] < SG.ARENA_SIZE[0] and stepper[1] < SG.ARENA_SIZE[1] and game.grid[stepper[0]][stepper[1]] == EMPTY:
            stepper = (stepper[0] + snakePlayer.getDir(DIR)[0],
                       stepper[1] + snakePlayer.getDir(DIR)[1])

        #Distance - 1 for 0 if right in front
        inputs[index] = (distance(stepper, snakePlayer.pos) - 1) / max(SG.ARENA_SIZE) # To keep 0-1
        try:
            inputs[index + 1] = 1 if game.grid[stepper[0]][stepper[1]] == APPLE else 0
        except:
            inputs[index + 1] = 0
        

    #####Food ( 6-8):
    aheadPos = (snakePlayer.pos[0] + snakePlayer.direction[0],
                 snakePlayer.pos[1] + snakePlayer.direction[1])
    leftPos = (snakePlayer.pos[0] + snakePlayer.getDir('turnLeft')[0],
                 snakePlayer.pos[1] + snakePlayer.getDir('turnLeft')[1])
    rightPos = (snakePlayer.pos[0] + snakePlayer.getDir('turnRight')[0],
                 snakePlayer.pos[1] + snakePlayer.getDir('turnRight')[1])
    
    if distance(applePos, aheadPos) < distanceToApple:
        inputs[6] = 1
    else:
        inputs[6] = 0
    if distance(applePos, leftPos) < distanceToApple:
        inputs[7] = 1
    else:
        inputs[7] = 0
    if distance(applePos, rightPos) < distanceToApple:
        inputs[8] = 1
    else:
        inputs[8] = 0

    #inputs[9] = snakePlayer.pos[0]
    #inputs[10] = snakePlayer.pos[1]
        
    return inputs
    
def play_game(snakePlayer):
    game        = SG.gameMap(snakePlayer)

    currentFrameNumber = 0
    frameOfLastLengthChange = 0
    previousLength = 1
    while True:
        inputs = GetInputs(game, snakePlayer)

        snakePlayer.move(snakePlayer.GetMove(inputs))
        result = game.update(snakePlayer)

        ####Fitness Function:
        # Just the length of the snake!
        
        if snakePlayer.length > previousLength:
            frameOfLastLengthChange == currentFrameNumber
            previousLength = snakePlayer.length


        ######Stop if stopped:
        if currentFrameNumber - frameOfLastLengthChange > BOARD_SIZE:
            #Got stuck in a loop, not going anywhere
            return snakePlayer.length
            
        if result != None:
            finalLength = result[1]
            return finalLength

   
        currentFrameNumber += 1
        

    
def train(numGens, batchSize, numBatchWinners,
          batch = None, extraLosers=0, numCrossovers=0, networkShape="Default",
          q = None):
    '''Don't forget to set it to variables i.e. [a,b = train()]!!!!'''

    #random.seed(1) # REMOVE!! ONLY FOR TESTING!!!
    #np.random.seed(1)
    if batch is None:
        batch = []
    else:
        if len(batch) > batchSize:
            raise Exception("Batch given too big")
        
    NUM_TEST_GAMES = 2
    
    LENGTH_PROGRESSION = []
    HIGH_LENGTH = []
    LOW_LENGTH = []

    if batch == []:
        for i in range(batchSize):
            if networkShape == "Default":
                batch.append(SnakeAi())
            elif type(networkShape) == list:
                batch.append(SnakeAi(networkShape=networkShape))
            else:
                raise Exception(f"Wrong type of net shape: {networkShape}")

    for genNum in range(numGens):
        if genNum % 10 == 0:
            print("Progress:", genNum, "/", numGens)
            
        lengths = []
        for Ni, network in enumerate(batch):
            for i in range(NUM_TEST_GAMES):
                length = play_game(network)
                if i == 0:
                    lengths.append(length)
                else:
                    lengths[-1] = (length + lengths[Ni]) / 2
                
        LENGTH_PROGRESSION.append(sum(lengths) / len(lengths))
        HIGH_LENGTH.append(max(lengths))
        LOW_LENGTH.append(min(lengths))
        
        winners = []
        for i in range(numBatchWinners):
            currHighIndex = lengths.index(max(lengths))
            winners.append(batch.pop(currHighIndex))
            lengths.pop(currHighIndex)
        
        if genNum < numGens - 1: # If not on last iteration
            for loser in batch[:extraLosers]:
                winners.append(loser)
            batch = deepcopy(winners)
            
            for child in range(numCrossovers):
                batch.append(
                    SnakeAi.crossover(random.choice(winners), random.choice(winners))
                    )
            for i in range(batchSize - numBatchWinners - numCrossovers):
                netToMutate = deepcopy(random.choice(batch)) # batch or winners?
                netToMutate.mutate()
                batch.append(netToMutate)
                

    finalData = (winners,[LENGTH_PROGRESSION, HIGH_LENGTH, LOW_LENGTH])  
    if q is None:
        return finalData # If not multiprocessing
    else:
        q.put(finalData) # If using multiprocessing


def plot(lengths):
    for i in lengths:
        plt.plot(i)

    plt.show()

def gui(AI):
    #random.seed(100)

    FPS =           12 # the speed of the game
    ARENA_SIZE =    (12,12) # DEFAULT FOR AI DON'T CHANGE!!
    SQUARE_SIZE =   45
    BOX_THICKNESS = int(SQUARE_SIZE / 10)

    LIGHT_GRAY = (100,100,100)
    PALE_RED   = (200, 40, 40)
    WHITE      = (255,255,255)
    BLACK      = (  0,  0,  0)
    os.environ["SDL_VIDEO_CENTERED"] = '1' # Centers Screen

    ######## Game Setup:
    s = AI
    game = SG.gameMap(s)
    WIDTH, HEIGHT = ((SQUARE_SIZE * ARENA_SIZE[1]) , (SQUARE_SIZE * ARENA_SIZE[0]))
    ########

    DISPLAY = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
    pygame.display.set_caption(" ~SNAKE~")
    pygame.init()
    nextChangeDirection = []
    gameClock = pygame.time.Clock()
    while True:
        DISPLAY.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                print(f"The snake had a final length of: {s.length}")
                pygame.quit()
                sys.exit()



        ###THE Game:
        ins = GetInputs(game, s)
        s.move(s.GetMove(ins))
        result = game.update(s)
        if result != None:
            print(f"The snake had a final length of: {result[1]}")
            pygame.quit()
            return None
            #sys.exit()

        for c, C in enumerate(game.grid):
            for r, R in enumerate(C):
                if R == 1:  # Snake
                    rect = ((r * SQUARE_SIZE, c * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(DISPLAY, WHITE, rect)
                elif R == 2: # Apple
                    rect = ((r * SQUARE_SIZE, c * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(DISPLAY, PALE_RED, rect) 

        ####



        # The Grid:
        for R in range(ARENA_SIZE[1]):
            for D in range(ARENA_SIZE[0]):
                rect = ((R * SQUARE_SIZE, D * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(DISPLAY, LIGHT_GRAY, rect, BOX_THICKNESS)

        pygame.display.flip()
        gameClock.tick(FPS)


if __name__ == '__main__':
    AI = SnakeAi(file="networks/BEST24000")  # large")
    gui(AI)

