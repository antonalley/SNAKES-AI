#!/usr/bin/env python
# -*- coding: <ASCII> -*-
# AI_v0_2.py


#################################
# ABOUT:
# - Just got a fresh start. Trying to make code cleaner
# - Using numpy arrays for optimization. 
# - Has custom shape to neural network
# - Mutation is based on Bell curve distribution
#
#################################

__author__ = "Anton Alley"
__copyright__ = "None"
__credits__ = ["Anton Alley"] 
__license__ = "None"
__version__ = "0.2.0"
__maintainer__ = "Anton Alley"
__email__ = "Anton.Alley@gmail.com"

# Builtin Imports
import math
import random

# Third Party Imports
import numpy as np

# My Imports
import file as fileHandler

#Global Variables:
MUTATION_RATE = 0.07
MUTATION_RANGE = 0.25
NETWORK_STORAGE_LOCATION = "networks/Dec112018/"

def ReLU(x):
    return max([0, x])

class NetworkError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)


class Network:
    def __init__(self, networkShape=None, file=None):
        '''Uploads File if proper format, else use networkShape as a list of the numer of neurons in each layer, including output and input layers'''
        if file == None and networkShape != None:   
            if type(networkShape) != list:
                raise NetworkError(f"Wrong network shape type: {type(networkShape)}")
            else:
                self.newNetwork(networkShape)
        elif file != None:
            self.networkShape, self.weights, self.biases = fileHandler.f_open(file)
            self.file = file
        else:
            return None

        numBiases = sum(self.networkShape[1:])
        numWeights = sum(networkShape[i - 1] * networkShape[i] for i in range(len(networkShape[1:])))
        self.numDials = numBiases + numWeights

        
    def newNetwork(self, networkShape):
        if len(networkShape) < 2:
            raise NetworkError(f"Must have at least 2 layers. You had: {len(networkShape)}")
        if all([1 if a > 0 else 0 for a in networkShape]) == False:
            raise AIError("Number of neurons must be greater then 0")
        
        self.networkShape = networkShape
        
        self.biases = []
        self.weights = []
        for numNeurons, incomingNeurons in zip(networkShape[1:], networkShape):
            self.weights.append(np.random.uniform(-0.5,0.5,size = (numNeurons, incomingNeurons)))
            self.biases.append(np.random.uniform(-5,6,size = (numNeurons)))

    def openData(self, networkShape, weights, biases):
        self.networkShape = networkShape
        self.weights = weights
        self.biases = biases
                         
    def feedForward(self, inputVector):
        if len(inputVector) != self.networkShape[0]:
            raise NetworkError(f"Wrong size for inputVector: {len(inputVector)}, must be a length of {self.networkShape[0]}")
        for data in inputVector:
            if type(data) != float and type(data) != int:
                raise NetworkError(f"Wrong data type in inputVector: {type(data)}; must by int or float")
        
        forwardData = inputVector
        for b, w in zip(self.biases, self.weights):
            forwardData = [ReLU(i) for i in (np.dot(w, forwardData) + b)]
        return forwardData

    def save(self):
        while 1: # to avoid repeats
            try:
                r_ID = str(random.randint(1000000,9999999))
                fileHandler.save(f"{NETWORK_STORAGE_LOCATION}{r_ID}",[self.networkShape, self.weights, self.biases])
            except fileHandler.OverwriteError:
                continue
            else:
                return r_ID
    def load(self, ID):
        inData = fileHandler.f_open(NETWORK_STORAGE_LOCATION + ID)
        self.networkShape, self.weights, self.biases = inData

    def mutate_DEP(self):
        maxMutations = max(1, round(self.numDials * MUTATION_RATE))
        numMutations = random.randint(1, maxMutations)

        for _ in range(numMutations):
            layerToMute = random.randint(0,len(self.networkShape) - 2)
            neuronToMute = random.randint(0, self.networkShape[layerToMute+1] - 1)
            # -1 means bias, else is the index
            dataToMute = random.randint(-1, self.networkShape[layerToMute] - 1)

            muteAmount = random.uniform(-MUTATION_RATE, MUTATION_RATE)
            if dataToMute != -1:
                self.weights[layerToMute][neuronToMute][dataToMute] += muteAmount
            else:
                self.biases[layerToMute][neuronToMute] += muteAmount * 8 # Biases should swing more then the weightes, hense *8


    def mutate(self):
        for Li, layer in enumerate(self.weights):
            for Ni, neuron in enumerate(layer):
                for Wi, weight in enumerate(neuron):
                    if random.uniform(0,1) < MUTATION_RATE:
                        self.weights[Li][Ni][Wi] += np.random.normal(0, MUTATION_RANGE/2)

        for Li, layer in enumerate(self.biases):
            for Bi, bias in enumerate(layer):
                if random.uniform(0,1) < MUTATION_RATE:
                    self.biases[Li][Bi] += np.random.normal(0,MUTATION_RANGE)# Biases should swing more then the weightes so not /2

        
    @staticmethod
    def crossover(net1, net2, version = "arithmetic"):
        '''Does a cross over with the data given. version can = 'uniform' OR 'arithmetic' OR 'random' '''
        if net1.networkShape != net2.networkShape:
            raise NetworkError(f"Cannot crossover 2 different sized Networks\nAI1: {AI1.networkShape}\nAI2: {AI2.networkShape}")
        if version not in ["uniform", "arithmetic", "random"]:
            raise AIError(f"The {version} version of crossover is supported")
        if version == "random":
            version = r.choice(["uniform", "arithmetic"])

        childBiases = []
        childWeights = []
        if version == "arithmetic":
            net1_weight = random.uniform(0.1, 0.9)
            net2_weight = 1 - net1_weight
            childWeights = [w1+w2 for w1, w2 in zip(
                (w * net1_weight for w in net1.weights),
                (w * net2_weight for w in net2.weights)
                )]
            childBiases = [b1 + b2 for b1, b2 in zip(
                (b * net1_weight for b in net1.biases),
                (b * net2_weight for b in net2.biases)
                )]
        elif version == "uniform":
            raise NetworkError("I am too lazy to program this do it later!!!")

        newNetwork = type(net1)(None) #Network(None), but returns subclass type if in use
        newNetwork.openData(net1.networkShape, childWeights, childBiases)

        return newNetwork
    
