#!/usr/bin/env python
# -*- coding: <ASCII> -*-
# train.py

#####CURRENTLY WORKING ON:
#
# 


#################################
# ABOUT:
#
#
#
# This module is to train the AI for the snakes game
#
#
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

# My Imports
import main as SG
from AI_v0_2 import Network as BACKGROUND_AI


######### CONSTANTS:
SG.ARENA_SIZE = (12, 12)
BOARD_SIZE = 144
ADD_VARIABLES = 7 #+ Head pos(2), Apple pos(2), Length(1), currDir(2)
INPUT_DATA_SIZE = BOARD_SIZE + ADD_VARIABLES
###############

class SnakeAi(BACKGROUND_AI, SG.player):
    def __init__(self, networkShape=[INPUT_DATA_SIZE, 30, 36, 36, 30, 27, 21, 15, 9, 3], file = None):
        BACKGROUND_AI.__init__(self, networkShape=networkShape, file=file)
        SG.player.__init__(self)

    def GetMove(self, inputData):
        vect_board = []
        for col, r in enumerate(inputData[:-1]):
            for data in r:
                vect_board.append(data)
        for d in inputData[-1]:
            vect_board.append(d)
                
        output = self.feedForward(vect_board)
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
    
def play_game(snakePlayer):
    game        = SG.gameMap(snakePlayer)

    currentFrameNumber = 0
    frameOfLastLengthChange = 0
    previousLength = 1
    while True:
        snakePlayer.move(snakePlayer.GetMove(game.grid + [[*snakePlayer.pos,*snakePlayer.direction,
                                                     *game.apple, snakePlayer.length]]))
        result = game.update(snakePlayer)

        if snakePlayer.length > previousLength:
            frameOfLastLengthChange == currentFrameNumber
            previousLength = snakePlayer.length


        ######Stop if stopped:
        if currentFrameNumber - frameOfLastLengthChange > BOARD_SIZE:
            return snakePlayer.length
            
        if result != None:
            finalLength = result[1]

            return finalLength


            
        currentFrameNumber += 1
        

    
def train(numGens, batchSize, numBatchWinners,
          batch = None, extraLosers=0, numCrossovers=0):

    if batch is None:
        batch = []
    else:
        if len(batch) > batchSize:
            raise Exception("Batch given too big")
        
    NUM_TEST_GAMES = 1

    LENGTH_PROGRESSION = []
    HIGH_LENGTH = []
    LOW_LENGTH = []

    if batch == []:
        for i in range(batchSize):
            batch.append(SnakeAi())

    for genNum in range(numGens):
        if genNum % 10 == 0:
            print('Progress:', genNum, '/',numGens)
        lengths = []
        for Ni, network in enumerate(batch):
            for i in range(NUM_TEST_GAMES):
                length = play_game(network)
                if i == 0:
                    lengths.append(length)
                lengths[Ni] = (length + lengths[Ni]) / 2

                
        LENGTH_PROGRESSION.append(sum(lengths) / len(lengths))
        HIGH_LENGTH.append(max(lengths))
        LOW_LENGTH.append(min(lengths))
        
        winners = []
        for i in range(numBatchWinners):
            currHighIndex = lengths.index(max(lengths))
            winners.append(batch.pop(currHighIndex))
            lengths.pop(currHighIndex)
        
        
        
          
        if genNum < numGens - 1:
            for loser in batch[:extraLosers]:
                winners.append(loser)

            batch = deepcopy(winners)
        
            for child in range(numCrossovers):
                batch.append(
                    SnakeAi.crossover(random.choice(winners), random.choice(winners))
                    )
            
            for i in range(batchSize - numBatchWinners - numCrossovers):
                netToMutate = deepcopy(random.choice(batch))
                netToMutate.mutate()
                batch.append(netToMutate)
                

    return winners,[LENGTH_PROGRESSION, HIGH_LENGTH, LOW_LENGTH]
            


def evolve(numPopulations, epochs):
    NUM_GEN_PER_EPOCH = 100
    NUM_BATCH_WINNERS = 10
    populations = [None for i in range(numPopulations)]
    popSettings = [{"xtraLosers":random.randint(0, 3), "numCrossovers":random.randint(3, 15), "batchSize":random.randint(40,65)} for i in range(numPopulations)]
    popLengthHistory = [[] for i in range(numPopulations)]
    
    for e in range(epochs):
        for pI in range(numPopulations):
            rBatch, lengths = train(NUM_GEN_PER_EPOC, popSettings[pI]["batchSize"], NUM_BATCH_WINNERS,
                                                batch = populations(pI), extraLosers = popSettings[pI]["xtraLosers"], numCrossovers = popSettings[pI]["numCrossovers"])
            populations.append(rBatch)

            for length in lengths[1]:
                popLengthHistory[pI].append(length)

        ##### Migrate:
        movers = []
        for population in populations:
            # 1 migrater per population, which has NUM_BATCH_WINNERS each
            movers.append(population.pop(random.randint(0, len(population)-1)))
        random.shuffle(movers)
        for i, snake in enumerate(movers):
            populations[i].append(snake)
        del movers
        ######
    return populations, popLengthHistory
        

def gui(AI):

    FPS =           10 # the speed of the game
    ARENA_SIZE =    (12,16) # DEFAULT FOR AI DON'T CHANGE!!
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
        s.move(s.GetMove(game.grid + [[*s.pos,*s.direction,*game.apple, s.length]]))
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
