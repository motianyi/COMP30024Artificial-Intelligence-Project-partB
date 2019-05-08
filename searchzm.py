"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

A single-player varient of the game of Chexers does following:
1. read a board configuration from json file (contains color, block ,pieces)
2. find a sequence of action for the palyer to take to win (to exit with all of
    their pieces)

Authors:Tianyi Mo (  ), Yat Yeung (901011)
"""


import time

import sys
import json
from queue import Queue
from queue import PriorityQueue
from copy import deepcopy


MOVE = 'MOVE'
JUMP = 'JUMP'
EXIT = 'EXIT'
EXIT_HEXES = {
    'red' : [(3, -3), (3, -2), (3, -1), (3, 0)],
    'green' : [(-3, 3), (-2, 3), (-1, 3), (0, 3)],
    'blue' : [(0, -3), (-1, -2), (-2, -1), (-3, 0)]
}
SIZE = 3

def isOnBoard(pos):
    """
    Take a position pos in form of(r,q) and return whether the position is
    on board or not
    """
    return pos[0] <= SIZE and \
        pos[0] >= 0 - SIZE and \
        pos[1] <= SIZE and \
        pos[1] >= 0 - SIZE and \
        pos[0] + pos[1] <= SIZE and \
        pos[0] + pos[1] >= 0 - SIZE

def getOpposite(pos1, pos2):
    """
    Take two positions pos1 pos2 in form of (r,q) return a third position in
    form of (r,q) which is the opposite hex over pos2 from pos1's perspective
    """
    return (pos2[0] * 2 - pos1[0],  pos2[1] * 2 - pos1[1])

def getAdjacentHexes(pos):
    """
    Take a position pos in form of(r,q) and return a list of positions which
    are adjacent to the input position
    """
    adjacentHexes = [(pos[0] + 1, pos[1]), \
        (pos[0] - 1, pos[1]), \
        (pos[0], pos[1] + 1), \
        (pos[0], pos[1] - 1), \
        (pos[0] + 1, pos[1] - 1), \
        (pos[0] - 1, pos[1] + 1)]
    return [adjacentHex for adjacentHex in adjacentHexes if isOnBoard(adjacentHex)]

class Chexers:
    """
    A class to represent Chexers board, store the information of the blocks
    position, the player's colour and exit hexes, and keep track of the player's
    pieces position
    """
    def __init__(self, colour, pieces, blocks):
        """
        Create a new board based on given player color, the initial pieces
        positions and blocks positions.
        """
        self.colour = colour
        self.exitHexes = EXIT_HEXES[colour]
        self.pieces = sorted(pieces.copy())
        self.blocks = blocks.copy()

    def getPieces(self):
        """
        Get the copy of current pieces information
        """
        return self.pieces.copy()

    def setPieces(self, pieces):
        """
        Set the board pieces in sorted order
        """
        self.pieces = sorted(pieces.copy())

    def isEmpty(self, pos):
        """
        Take a position pos in form of (r,q), and return whether this position
        is empty or not
        """
        return not (pos in self.blocks or pos in self.pieces)

    def getLegalActions(self):
        legalActions = []
        for piece in self.pieces:
            legalActions += self.getLegalPieceActions(piece)

        return legalActions

    def getLegalPieceActions(self, piece):
        """
        Take a pieces, and return a list of legal action
        [(action_type, start_position, end_position),..,..] which the pieces allow
        to perform)
        """
        legalActions = []
        for adjacentHex in getAdjacentHexes(piece):
            # Check Move
            if self.isEmpty(adjacentHex):
                legalActions.append((MOVE, piece, adjacentHex))
            # Check Jump
            else:
                opposite = getOpposite(piece, adjacentHex)
                if isOnBoard(opposite) and self.isEmpty(opposite):
                    legalActions.append((JUMP, piece, opposite))
        # Check Exit
        if piece in self.exitHexes:
            legalActions.append((EXIT, piece, None))
        return legalActions

    def result(self, action):
        """
        Take a action in form of (action_type, start_position, end_position)
        and return the a sorted list of pieces which is the result of performing
        this action
        """
        pieces = self.getPieces()
        pieces.remove(action[1])
        if (action[0] != EXIT):
            pieces.append(action[2])
        return sorted(pieces)

    def getSuccessors(self):
        """
        Get all resulting pieces condition for all lgeal actions can be perform
        in current board configuration
        """
        return [(self.result(a), a) for a in self.getLegalActions()]

    def isGoalState(self):
        """
        Test whether the goal state is achieved
        """
        return self.pieces == []

def printActions(actions):
    """
    Take a list of actions which action is in form of
    (action_type, start_position, end_position) and print all of them in the
    format required in project discription
    """
    for a in actions[::-1]:
        (action,curPos,nextPos) = a
        if action == EXIT:
            print(f"{action} from {curPos}.")
        else:
            print(f"{action} from {curPos} to {nextPos}.")




def main():
    #Reading data
    with open(sys.argv[1]) as file:
        data = json.load(file)

    pieces = [tuple(piece) for piece in data['pieces']]
    blocks = [tuple(block) for block in data['blocks']]
    game = Chexers(data['colour'], pieces, blocks)

    #switch between different algorithms
    a_star_search(game)
    #bfs(game)
    #ids(game)


def a_star_search(game):
    """
    Solution algorithm
    Run faster than BFS and IDS in most cases
    Graph version of A*, optimal when the heuristic function is consistent
    """
    currPieces = game.getPieces()

    # frontier the nodes in increasing order of 
    # estimated cost to goal node plus cost from root to current node
    frontier = PriorityQueue()
    frontier.put((0, currPieces))

    previous = {}
    previous[tuple(currPieces)] = None

    #the cost from rootto current node
    cost = {}
    cost[tuple(currPieces)] = 0

    while not frontier.empty():
        #get lowest cost node from the priority queue
        (p,currPieces) = frontier.get()
        game.setPieces(currPieces)

        if game.isGoalState():
            break

        for (succPieces, action) in game.getSuccessors():
            # print(succPieces)
            new_cost = cost[tuple(currPieces)] + 1

            # add pieces to previous when it is not in provioue or find a smaller cost for it
            if tuple(succPieces) not in previous or new_cost < cost[tuple(succPieces)]:
                cost[tuple(succPieces)] = new_cost

                # The cost to get node
                # f(n) = g(n) + h(n)
                priority = new_cost + heuristic(succPieces, game)
                frontier.put((priority, succPieces))

                # store the "path" to the succPiece
                previous[tuple(succPieces)] = (currPieces, action)

    # Retrieve actions
    current = previous[tuple(currPieces)]
    actions = []

    while current is not None:
        actions.append(current[1])
        current = previous[tuple(current[0])]
    #print actions
    printActions(actions)
    print(len(actions))

def heuristic(succPieces, game):
    """
    Calculate the estimated cost form a state to goal state
    This heuristic is consistent
    """
    sum = 0
    # addision of heuristic for each piece
    for piece in succPieces:
        sum += heuristic_piece(piece, game.colour)
    return sum

def heuristic_piece(piece, colour):
    """
    Calculate heuristic value for each piece based on their coordinate
    """
    (q,r) = piece

    # handle red case 
    if colour == 'red':
        if q == 3:
            return 1
        elif q == 2 or q == 1:
            return 2
        elif q == 0 or q == -1:
            return 3
        else:
            return 4
    # handle green case
    elif colour == 'green':
        if r == 3:
            return 1
        elif r == 2 or r == 1:
            return 2
        elif r == 0 or r == -1:
            return 3
        else:
            return 4

    #handle blue case
    else:
        if q + r == -3:
            return 1
        elif q + r == -2 or q + r == -1:
            return 2
        elif q + r == 0 or q + r == 1:
            return 3
        else:
            return 4


def bfs(game):
    """
    Try 1: Breadth First search
    (discarded solution -- run faster than ids, slower than A* )
    Keep exloring breadth until we find a solution
    """
    currPieces = game.getPieces()
    frontier = Queue()
    #Set dictionary to help avoid repeatedly exploring different node with same state
    previous = {}
    previous[tuple(currPieces)] = None
    while not game.isGoalState():
        for (succPieces, action) in game.getSuccessors():
            if tuple(succPieces) not in previous:
                frontier.put(succPieces)
                previous[tuple(succPieces)] = (currPieces, action)
        currPieces = frontier.get()
        game.setPieces(currPieces)
    current = previous[tuple(currPieces)]

    # Retrieve actions
    actions = []
    while current is not None:
        actions.append(current[1])
        current = previous[tuple(current[0])]

    printActions(actions)



def ids(game):
    """
    Try 2: Iterative Deepening Search (discarded solution -- run slower than BFS)
    Repeatedly run a depth limited depth first search with increasing depth-limit
    until we find a solution
    """
    depthLimit = 0
    while True:
        #actions = dlsv1(game, depthLimit, [])
        actions = dlsv2(deepcopy(game), depthLimit)
        if actions is not None:
            printActions(actions)
            break
        depthLimit += 1



def dlsv1(game, depthLimit, visited):
    '''
    Try 2a: Depth-Limit search version 1 (discarded version - run too slow)
    Use recursive approach
    '''
    #base cases, start building a path
    if game.isGoalState():
        return []
    elif depthLimit == 0:
        #no path found to goal tsate with current depth limit
        return None

    # recursive cases, try all possible action for current pieces configurtaion
    for piece in game.getPieces():
        if piece in visited:
            continue
        else:
            visited.append(piece)

        for action in game.getLegalPieceActions(piece):
            currPieces = game.getPieces()
            game.pieces = game.result(action)
            actions = dlsv1(game, depthLimit-1, visited.copy())
            game.pieces = currPieces

            if actions is not None:
                # recursively found a sequnce of action to exit the board
                actions.append(action)
                return actions
    return None


def dlsv2(game, depthLimit):
    '''
    Try 2b: Depth-Limit search version 2
    using while loop to achieve
    '''
    currPieces = game.getPieces()
    frontier = [(currPieces, 0)]
    previous = {}
    previous[tuple(currPieces)] = None

    #Until frontier is empty, keep constructing the tree
    while frontier != []:
        currPieces, depth = frontier.pop()
        game.setPieces(currPieces)
        if game.isGoalState():
            break
        depth += 1
        if depth > depthLimit:
            continue
        #Update if there is new information, or a shorter path
        for (succPieces, action) in game.getSuccessors():
            if tuple(succPieces) not in previous or \
               previous[tuple(succPieces)] is not None and \
               previous[tuple(succPieces)][2] > depth:
                frontier.append((succPieces, depth))
                previous[tuple(succPieces)] = (currPieces, action, depth)
    if frontier == []:
        return None
    current = previous[tuple(currPieces)]

    # Retrieve actions
    actions = []
    while current is not None:
        actions.append(current[1])
        current = previous[tuple(current[0])]
    return actions




def print_board(board_dict, message="", debug=False, **kwargs):
    """
    Helper function to print a drawing of a hexagonal board's contents.

    Arguments:

    * `board_dict` -- dictionary with tuples for keys and anything printable
    for values. The tuple keys are interpreted as hexagonal coordinates (using
    the axial coordinate system outlined in the project specification) and the
    values are formatted as strings and placed in the drawing at the corres-
    ponding location (only the first 5 characters of each string are used, to
    keep the drawings small). Coordinates with missing values are left blank.

    Keyword arguments:

    * `message` -- an optional message to include on the first line of the
    drawing (above the board) -- default `""` (resulting in a blank message).
    * `debug` -- for a larger board drawing that includes the coordinates
    inside each hex, set this to `True` -- default `False`.
    * Or, any other keyword arguments! They will be forwarded to `print()`.
    """

    # Set up the board template:
    if not debug:
        # Use the normal board template (smaller, not showing coordinates)
        template = """# {0}
#           .-'-._.-'-._.-'-._.-'-.
#          |{16:}|{23:}|{29:}|{34:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-.
#       |{10:}|{17:}|{24:}|{30:}|{35:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{05:}|{11:}|{18:}|{25:}|{31:}|{36:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{01:}|{06:}|{12:}|{19:}|{26:}|{32:}|{37:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{02:}|{07:}|{13:}|{20:}|{27:}|{33:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{03:}|{08:}|{14:}|{21:}|{28:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{04:}|{09:}|{15:}|{22:}|
#          '-._.-'-._.-'-._.-'-._.-'"""
    else:
        # Use the debug board template (larger, showing coordinates)
        template = """# {0}
#              ,-' `-._,-' `-._,-' `-._,-' `-.
#             | {16:} | {23:} | {29:} | {34:} |
#             |  0,-3 |  1,-3 |  2,-3 |  3,-3 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {10:} | {17:} | {24:} | {30:} | {35:} |
#         | -1,-2 |  0,-2 |  1,-2 |  2,-2 |  3,-2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {05:} | {11:} | {18:} | {25:} | {31:} | {36:} |
#     | -2,-1 | -1,-1 |  0,-1 |  1,-1 |  2,-1 |  3,-1 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {01:} | {06:} | {12:} | {19:} | {26:} | {32:} | {37:} |
# | -3, 0 | -2, 0 | -1, 0 |  0, 0 |  1, 0 |  2, 0 |  3, 0 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {02:} | {07:} | {13:} | {20:} | {27:} | {33:} |
#     | -3, 1 | -2, 1 | -1, 1 |  0, 1 |  1, 1 |  2, 1 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {03:} | {08:} | {14:} | {21:} | {28:} |
#         | -3, 2 | -2, 2 | -1, 2 |  0, 2 |  1, 2 | key:
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' ,-' `-.
#             | {04:} | {09:} | {15:} | {22:} |   | input |
#             | -3, 3 | -2, 3 | -1, 3 |  0, 3 |   |  q, r |
#              `-._,-' `-._,-' `-._,-' `-._,-'     `-._,-'"""

    # prepare the provided board contents as strings, formatted to size.
    ran = range(-3, +3+1)
    cells = []
    for qr in [(q,r) for q in ran for r in ran if -q-r in ran]:
        if qr in board_dict:
            cell = str(board_dict[qr]).center(5)
        else:
            cell = "     " # 5 spaces will fill a cell
        cells.append(cell)

    # fill in the template to create the board drawing, then print!
    board = template.format(message, *cells)
    print(board, **kwargs)


# when this module is executed, run the `main` function:
if __name__ == '__main__':
    main()
