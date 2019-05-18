
from queue import PriorityQueue
from copy import deepcopy
import random
import time

import math

EXIT_HEXES = {
    'red' : [(3, -3), (3, -2), (3, -1), (3, 0)],
    'green' : [(-3, 3), (-2, 3), (-1, 3), (0, 3)],
    'blue' : [(0, -3), (-1, -2), (-2, -1), (-3, 0)]
}

INI_HEXES = {
    'red' : [(-3, 3), (-3, 2), (-3, 1), (-3, 0)],
    'green' : [(3, -3), (2, -3), (1, -3), (0, -3)],
    'blue' : [(0, 3), (1, 2), (2, 1), (3, 0)]
}


MOVE = 'MOVE'
JUMP = 'JUMP'
EXIT = 'EXIT'
PASS = 'PASS'
SIZE = 3

def isOnBoard(pos):
    return pos[0] <= SIZE and \
        pos[0] >= 0 - SIZE and \
        pos[1] <= SIZE and \
        pos[1] >= 0 - SIZE and \
        pos[0] + pos[1] <= SIZE and \
        pos[0] + pos[1] >= 0 - SIZE


def getOpposite(pos1, pos2):
    return (pos2[0] * 2 - pos1[0],  pos2[1] * 2 - pos1[1])

def getAdjacentHexes(pos):
    adjacentHexes = [(pos[0] + 1, pos[1]), \
        (pos[0] - 1, pos[1]), \
        (pos[0], pos[1] + 1), \
        (pos[0], pos[1] - 1), \
        (pos[0] + 1, pos[1] - 1), \
        (pos[0] - 1, pos[1] + 1)]
    return [adjacentHex for adjacentHex in adjacentHexes if isOnBoard(adjacentHex)]

def nextPlayer(playerColor):
    if playerColor == 'red':
        return 'green'
    elif playerColor == 'green':
        return 'blue'
    else:
        return 'red'
    # playerList = ['red','green','blue']
    # if len(hexes['red']) == 0:
    #     playerList.remove('red')
    # if len(hexes['green']) == 0:
    #     playerList.remove('green')
    # if len(hexes['blue']) == 0:
    #     playerList.remove('blue')

    # if len(playerList) == 3:
    #     if playerColor == playerList[0]:
    #         return playerList[1]
    #     elif playerColor == playerList[1]:
    #         return playerList[2]
    #     else:
    #         return playerList[0]

    # elif len(playerList) == 2:
    #     if playerColor == playerList[1]:
    #         return playerList[0]
    #     else:
    #         return playerList[1]

    # return playerList[0]

# return list of (succHexes, succNumExits, move)
def getSuccessors(hexes, numExits, colour):
    succ = []
    for a in getLegalActions(hexes.copy(),colour):
        succ.append(result(deepcopy(hexes), numExits.copy(),colour, a))
    return succ

# return (succHexes, succNumExits, move)
def result(hexes, numExits, colour, action):
    # print("\n\n")
    # print(hexes)
    # print(id(hexes))
    # print("\n\n")
    # print(numExits)
    # print("\n\n")
    # print(colour)
    # print("\n\n")
    # print(action)
    # print("\n\n")
    # piece for this player
    piece = hexes[colour]

    if action[0] == MOVE:
        piece.remove(action[1][0])
        piece.append(action[1][1])
    elif action[0] == JUMP:
        piece.remove(action[1][0])
        piece.append(action[1][1])

        #find the piece being jumped
        mid = ((action[1][0][0] + action[1][1][0]) // 2, 
            (action[1][0][1] + action[1][1][1]) // 2)

        # change color of of the piece
        if mid in hexes['red']:
            hexes['red'].remove(mid)
            piece.append(mid)
        elif mid in hexes['green']:
            hexes['green'].remove(mid)
            piece.append(mid)
        elif mid in hexes['blue']:
            hexes['blue'].remove(mid)
            piece.append(mid)
        else:
            print("error\n")
    elif action[0] == EXIT:
        piece.remove(action[1])
        numExits[colour] += 1
    return(hexes,numExits,action)

def isEmpty(hexes, pos):
    # no any piece on pos location
    return not (pos in hexes['red'] or pos in hexes['green'] or pos in hexes['blue'])



def getLegalActions(hexes, colour):
    legalActions = []
    for piece in hexes[colour]:
        for adjacentHex in getAdjacentHexes(piece):
            # move
            if isEmpty(hexes,adjacentHex):
                legalActions.append((MOVE, (piece, adjacentHex)))
            # jump
            else:
                opposite = getOpposite(piece, adjacentHex)
                if isOnBoard(opposite) and isEmpty(hexes,opposite):
                    legalActions.append((JUMP, (piece, opposite)))
        # exit
        if piece in EXIT_HEXES[colour]:
            legalActions.append((EXIT, piece))
    return legalActions


def isGoalState(numExits, colour):
    return numExits[colour] >= 4


def exit_dist(qr, colour):
    """how many hexes away from a coordinate is the nearest exiting hex?"""
    q, r = qr
    if colour == 'red':
        return 3 - q
    if colour == 'green':
        return 3 - r
    if colour == 'blue':
        return 3 - (-q-r)

# def heuristic(hexes, numExits):
#     result = {'red':0, 'green':0, 'blue': 0}
#     w1 = 10
#     w2 = 200
#     w3 = 100
#     w4 = 0
#     for colour in result.keys():
#         value1 = f1(hexes, numExits, colour)
#         value2 = f2(hexes, numExits, colour)
#         value3 = f3(hexes, numExits, colour)
#         value4 = f4(hexes, numExits, colour)
#         result[colour] = w1*value1 + w2*value2 + w3*value3 +w4*value4
#     return result

# def f1(hexes, numExits, colour):
#     pieces = hexes[colour]
#     return -sum(exit_dist(qr, colour)for qr in pieces)

# def f2(hexes, numExits, colour):
#     #number of pieces
    
#     return -len(hexes['red'])-len(hexes['green'])-len(hexes['blue'])+3*len(hexes[colour])
    

# def f3(hexes, numExits, colour):

#     return -numExits['red']-numExits['green']-numExits['blue']+3*numExits[colour]

# def f4(hexes, numExits, colour):
#     return 0

def heuristic(hexes, numExits):
    result = {'red':0, 'green':0, 'blue': 0}
    # result['red'] = -sum(math.ceil(exit_dist(qr,'red') / 2) + 1 for qr in hexes['red'])
    # result['green'] = -sum(math.ceil(exit_dist(qr,'green') / 2) + 1 for qr in hexes['green'])
    # result['blue'] = -sum(math.ceil(exit_dist(qr,'blue') / 2) + 1 for qr in hexes['blue'])


    for colour in result.keys():
        result[colour] = -sum(exit_dist(qr,colour) for qr in hexes[colour])*10
        # print(-sum(exit_dist(qr,colour) for qr in hexes[colour]))
        result[colour]+= len(hexes[colour])*1250+ numExits[colour]*1500

        panalty = 0
        panalty2 = 20
        if(colour == 'red'):
            result[colour] -= numExits['blue']*panalty
            result[colour] -= numExits['green']*panalty
            result[colour] -= len(hexes['blue'])*panalty2
            result[colour] -= len(hexes['green'])*panalty2
        elif(colour == 'green'):
            result[colour] -= numExits['blue']*panalty
            result[colour] -= numExits['red']*panalty
            result[colour] -= len(hexes['blue'])*panalty2
            result[colour] -= len(hexes['red'])*panalty2
        elif(colour == 'blue'):
            result[colour] -= numExits['red']*panalty
            result[colour] -= numExits['green']*panalty
            result[colour] -= len(hexes['red'])*panalty2
            result[colour] -= len(hexes['green'])*panalty2


    # # # print(sum(math.ceil(exit_dist(qr) / 2) + 1 for qr in pieces))
    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxresult\n\n")
    # print(result)
    # return sum(math.ceil(self.exit_dist(qr) / 2) + 1 for qr in pieces)
    return result

class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (Red, Green or Blue). The value will be one of the 
        strings "red", "green", or "blue" correspondingly.
        """
        self.colour = colour
        self.hexes = {'red' : [(-3, 3), (-3, 2), (-3, 1), (-3, 0)],
                      'green' : [(3, -3), (2, -3), (1, -3), (0, -3)],
                      'blue' : [(0, 3), (1, 2), (2, 1), (3, 0)]}
        self.exitedPieces = {'red':0, 'green':0, 'blue': 0}        

        self.exitHexes = EXIT_HEXES[colour]
        self.tree = Tree(deepcopy(self.hexes))


        # TODO: Set up state representation.




    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. If there are no allowed 
        actions, your player must return a pass instead. The action (or pass) 
        must be represented based on the above instructions for representing 
        actions.
        """
        # TODO: Decide what action to take.
        # bestMove = [('PASS', None)]
        # h = None
        # for (succPieces, move) in self.getSuccessors():
        #     curr_h = self.heuristic(succPieces)
        #     if h == None or curr_h < h:
        #         h = curr_h
        #         bestMove = [move]
        #     elif h == curr_h:
        #         bestMove.append(move)
        # return random.choice(bestMove)
        self.tree.setRoot(deepcopy(self.hexes))
        depth = 3
        return self.maxN(self.hexes.copy(),self.exitedPieces.copy(), depth, self.colour)[1]


    def maxN(self, hexes, numExits, depth, colour):
        # TODO, never goal state,
        if (depth == 0 or isGoalState(numExits, colour)):
            return (heuristic(hexes,numExits),[('PASS', None)])

        # inintial value dictionary
        vMax = {'red':-100000, 'green':-100000, 'blue': -100000}
        bestActionList = []
        # bestAction = ('PASS', None)
        succ = getSuccessors(hexes.copy(), numExits.copy(), colour)
        
        if(len(succ) == 0):
            (valuesVector, action) = self.maxN(hexes.copy(), numExits.copy(), depth-1, nextPlayer(colour))
            return (valuesVector, ('PASS', None))
        for (succHexes, succNumExits, move) in succ:
            # print(move)
            (valuesVector, action) = self.maxN(succHexes.copy(), succNumExits.copy(), depth-1, nextPlayer(colour))
            # print(valuesVector[colour])
            if valuesVector[colour] > vMax[colour]:
                vMax = valuesVector
                bestAction = move
                bestActionList = []
                bestActionList.append(move)
            elif valuesVector[colour] == vMax[colour]:
               
                bestAction = move
                bestActionList.append(move)
        #add randomness
        # print(bestAction)

        # print("\n")
        # print(bestActionList)
        return (vMax, random.choice(bestActionList))

            

    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (Red, Green or Blue). The value will be one of the strings "red", 
        "green", or "blue" correspondingly.

        The parameter action is a representation of the most recent action (or 
        pass) conforming to the above in- structions for representing actions.

        You may assume that action will always correspond to an allowed action 
        (or pass) for the player colour (your mpiecesethod does not need to validate 
        the action/pass against the game rules).
        """
        # TODO: Update state representation in response to action.
        piece = self.hexes[colour]
        if action[0] == MOVE:
            piece.remove(action[1][0])
            piece.append(action[1][1])
        elif action[0] == JUMP:
            piece.remove(action[1][0])
            piece.append(action[1][1])

            #find the piece being jumped
            mid = ((action[1][0][0] + action[1][1][0]) // 2, 
                (action[1][0][1] + action[1][1][1]) // 2)

            # change color of of the piece
            if mid in self.hexes['red']:
                self.hexes['red'].remove(mid)
                piece.append(mid)
            elif mid in self.hexes['green']:
                self.hexes['green'].remove(mid)
                piece.append(mid)
            elif mid in self.hexes['blue']:
                self.hexes['blue'].remove(mid)
                piece.append(mid)
            else:
                print("error\n")
        elif action[0] == EXIT:
            piece.remove(action[1])
            self.exitedPieces[colour] += 1

        # print("red"+str(self.hexes['red'])+"\n")
        # print("green"+str(self.hexes['green'])+"\n")
        # print("blue"+str(self.hexes['blue'])+"\n")
        # print(self.exitedPieces)
        # print("\n")
        
        print(str(heuristic(self.hexes, self.exitedPieces)))
       


    def delete(self, piece, colour):
        colour = None
        keys = ['red', 'green', 'blue']
        keys.remove(colour)

        for k in keys:
            if piece in self.hexes[k]:
                self.hexes[k].remove(piece)
                break
    
    def findNextMove(self):
        #one second
        t_end = time.time() + 1


        rootnode = Node(self.hexes,None)

        while time.time() < t_end:
            curr = selectNode(rootnode)

            node = curr
            if len(curr.children.keys()) > 0:
                action = random.choice(curr.children.keys())
                node = (curr.children)[action]

            result = simulation(node)
            backProgation(node, result)
        
        bestNode = rootnode.getBestChild()
        tree.setRoot(bestNode)

        return 
    
    def selectNode(rootnode):
        node = rootnode
        while len(node.children.keys())!=0:
            node = uctFindNode(node)
        return node

def uctFindNode(node):
    if node.isVisit == 0:
        return Integer.MAX_VALUE
    return 
    
def uctValue(node):



class Node:
    def __init__(self,state,parent):
        self.state = state
        self.parent = parent
        self.children = {}
        self.totalVisit = 0
        self.isVisit = 0
        #R,G,B scores
        self.score = [0,0,0]

# class Tree:
#     def __init__(self,root):
#         self.root = root

#     def setRoot(root):
#         self.root


    

