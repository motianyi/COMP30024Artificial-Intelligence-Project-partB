import sys
import json
import random
import math


from queue import Queue




MOVE = 'MOVE'
JUMP = 'JUMP'
EXIT = 'EXIT'
EXIT_HEXES = {
    'red' : [(3, -3), (3, -2), (3, -1), (3, 0)],
    'green' : [(-3, 3), (-2, 3), (-1, 3), (0, 3)],
    'blue' : [(0, -3), (-1, -2), (-2, -1), (-3, 0)]
}
INIT_HEXES = {
    'red' : [(-3, 3), (-3, 2), (-3, 1), (-3, 0)],
    'green' : [(3, -3), (2, -3), (1, -3), (0, -3)],
    'blue' : [(0, 3), (1, 2), (2, 1), (3, 0)]
}
SIZE = 3 

#Basic function
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

def updateHelper(pieces, blocks, action):
    if action[0] == MOVE:
        pieces.remove(action[1][0])
        pieces.append(action[1][1])
    elif action[0] == JUMP:
        pieces.remove(action[1][0])
        pieces.append(action[1][1])
        mid = ((action[1][0][0] + action[1][1][0]) // 2, 
            (action[1][0][1] + action[1][1][1]) // 2)
        if mid in blocks:
            pieces.append(mid)
            blocks.remove(mid)
    elif action[0] == EXIT:
        pieces.remove(action[1])

#Our class
class ExamplePlayer:
    def __init__(self, colour):
        self.colour = colour
        self.exitHexes = EXIT_HEXES[colour]
        self.pieces = INIT_HEXES[colour].copy()
        self.blocks = []
        for key in INIT_HEXES:
            if key == colour:
                continue
            for piece in INIT_HEXES[key]:
                self.blocks.append(piece)

    def getPieces(self):
        return self.pieces.copy()

    def isEmpty(self, pos):
        return not (pos in self.blocks or pos in self.pieces)

    def getLegalActions(self):
        legalActions = []
        for piece in self.pieces:
            for adjacentHex in getAdjacentHexes(piece):
                # move
                if self.isEmpty(adjacentHex):
                    legalActions.append((MOVE, (piece, adjacentHex)))
                # jump
                else:
                    opposite = getOpposite(piece, adjacentHex)
                    if isOnBoard(opposite) and self.isEmpty(opposite):
                        legalActions.append((JUMP, (piece, opposite)))
            # exit
            if piece in self.exitHexes:
                legalActions.append((EXIT, piece))
        return legalActions

    def result(self, move):
        pieces = self.pieces.copy()
        if (move[0] != EXIT):
            pieces.remove(move[1][0])
            pieces.append(move[1][1])
        else:
            pieces.remove(move[1])
        return pieces

    def getSuccessors(self):
        succ = []
        for a in self.getLegalActions():
            succ.append((self.result(a), a))
        return succ

    def isGoalState(self):
        return self.pieces == []

    '''
    def heuristic(self, pieces):
        """
        Returns the sum of pieces' distance to the closest exit
        """
        
        h = 0
        for piece in pieces:
            h += min([abs(e[0] - piece[0]) + abs(e[1] - piece[1]) for e in self.exitHexes])
        return h
    '''

    def heuristic(self, pieces):
        return sum(math.ceil(self.exit_dist(qr) / 2) + 1 for qr in pieces)



    def exit_dist(self, qr):
        """how many hexes away from a coordinate is the nearest exiting hex?"""
        q, r = qr
        if self.colour == 'red':
            return 3 - q
        if self.colour == 'green':
            return 3 - r
        if self.colour == 'blue':
            return 3 - (-q-r)

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
        bestMove = [('PASS', None)]
        # h = None
        if len(self.getSuccessors()) == 0:
            return bestMove[0]
        else:
            bestMove = []
            for (succPieces, move) in self.getSuccessors():
                # curr_h = self.heuristic(succPieces)
                # if h == None or curr_h < h:
                #     h = curr_h
                #     bestMove = [move]
                # elif h == curr_h:
                
                bestMove.append(move)
        return random.choice(bestMove)

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
        (or pass) for the player colour (your method does not need to validate 
        the action/pass against the game rules).
        """
        if colour == self.colour:
            updateHelper(self.pieces, self.blocks, action)
        else:
            updateHelper(self.blocks, self.pieces, action)
        print("self"+str(self.pieces)+"\n")
        print("blocks"+str(self.blocks)+"\n")
        

