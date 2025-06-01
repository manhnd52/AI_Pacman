# ghostAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
import heapq


class GhostAgent(Agent):
    def __init__(self, index):
        self.index = index

    def getAction(self, state):
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state):
        "Returns a Counter encoding a distribution over actions from the provided state."
        util.raiseNotDefined()


class RandomGhost(GhostAgent): # Kế thừa từ GhostAgent
    "A ghost that chooses a legal action uniformly at random."
    def __init__(self, index):
        self.index = index
        # ("RandomGhost initialized with index:", index)

    def getDistribution(self, state):
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        # print("RandomGhost distribution:", dist)
        return dist


class DirectionalGhost(GhostAgent):
    "A ghost that prefers to rush Pacman, or flee when scared."

    def __init__(self, index, prob_attack=0.7, prob_scaredFlee=0.5):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state):
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared:
            speed = 0.5

        actionVectors = [Actions.directionToVector(
            a, speed) for a in legalActions]
        
        # print(state.getGhostPosition(self.index))
        # print(state.getLegalActions(self.index)[0])
        # successors = state.generateSuccessor(self.index, state.getLegalActions(self.index)[0])
        # print(successors.getGhostPosition(self.index))
        # print(state.getGhostPosition(self.index))

        newPositions = [(pos[0]+a[0], pos[1]+a[1]) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [manhattanDistance(pos, pacmanPosition) for pos in newPositions]
        if isScared:
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip(
            legalActions, distancesToPacman) if distance == bestScore]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1-bestProb) / len(legalActions)
        dist.normalize()
        return dist

class SuperGhost(GhostAgent):
    "A ghost that prefers to rush Pacman, or flee when scared, with a higher probability."

    def __init__(self, index, prob_attack=0.9, prob_scaredFlee=0.9):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def getDistribution(self, state):
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0
        pacmanPosition = state.getPacmanPosition()

        bestActions = []

        speed = 1
        if isScared:
            speed = 0.5


        
        # Sử dụng thuật toán A* để tìm đường đi đến Pacman
        
        open_set = []
        visited = set()
        walls = state.getWalls()
        heapq.heappush(open_set, (self.heuristic(pos, pacmanPosition), 0, []))

        while open_set:
            f, g, path = heapq.heappop(open_set)
            current = path[-1] if path else pos  # Lấy node hiện tại từ path, nếu path rỗng thì dùng ghost_pos

            if current == pacmanPosition:
                # Khi tìm ra được đường đi đến target, lấy hướng đi tiếp theo bằng cách lấy node đầu tiên trong path - vị trí hiện tại của ghost
                if path:
                    move = (path[0][0] - pos[0], path[0][1] - pos[1])
                    bestActions = [a for a in legalActions if Actions.directionToVector(a, speed) == move]
                    print(path)
                    print("Best actions fousnd:", bestActions)
                else:
                    bestActions = Directions.STOP
            
            if current in visited:
                continue # Nhảy qua vòng lặp nếu đã thăm node này
            visited.add(current)

            rows, cols = walls.height, walls.width

            directions = {
                (-1, 0): "up",
                (1, 0): "down",
                (0, -1): "left",
                (0, 1): "right"
            }
            for d in directions:
                nx, ny = int(current[0] + d[0]), int(current[1] + d[1])
                if 0 <= nx < rows and 0 <= ny < cols and walls[nx][ny] == 0:
                    next_node = (nx, ny)
                    if next_node not in visited:
                        heapq.heappush(open_set, (
                            g + 1 + self.heuristic(next_node, pacmanPosition),
                            g + 1,
                            path + [next_node]
                        ))

        # Construct distribution
        bestProb = self.prob_scaredFlee if isScared else self.prob_attack
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1-bestProb) / len(legalActions)
        dist.normalize()
        return dist
