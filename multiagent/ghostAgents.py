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
from math import ceil, floor


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

    def __init__(self, index, prob_attack=1, prob_scaredFlee=1):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def nextIntPosition(self, pos, direction):
        if direction == (0, -1):
            return pos[0], ceil(pos[1] - 1)  # South
        elif direction == (0, 1):
            return pos[0], floor(pos[1] + 1)  # North
        elif direction == (-1, 0):
            return ceil(pos[0] - 1), pos[1]
        elif direction == (1, 0):
            return floor(pos[0] + 1), pos[1]

    
    def getDistribution(self, state):
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        legalActionsVector = [Actions.directionToVector(a) for a in legalActions]
        # print(legalActions)  # Loại bỏ hành động dừng lại
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0
        pacmanPosition = state.getPacmanPosition()
        # print(f"Ghost index: {self.index} Ghost Position: {pos} Pacman Position: {pacmanPosition}")

        conf = ghostState.configuration
        reverse = Actions.reverseDirection(conf.direction)
        # print("Reverse: " + reverse)
        reverse = Actions.directionToVector(reverse)
        
        speed = 1
        if isScared:
            speed = 0.5


        # Sử dụng thuật toán A* để tìm đường đi đến Pacman
        open_set = []
        visited = set()
        ghostPos = state.getGhostPositions()
        walls = state.getWalls()
        # for pos in ghostPos:
        #     walls[int(pos[0])][int(pos[1])] = 1  # Đánh dấu vị trí của ghost là tường

        heapq.heappush(open_set, (self.heuristic(pos, pacmanPosition), 0, []))

        bestAction = "hello"  # Mặc định là không di chuyển

        while open_set:
            f, g, path = heapq.heappop(open_set)
            current = path[-1] if path else pos  # Lấy node hiện tại từ path, nếu path rỗng thì dùng ghost_pos
            if current == pacmanPosition:
                # Khi tìm ra được đường đi đến target, lấy hướng đi tiếp theo bằng cách lấy node đầu tiên trong path - vị trí hiện tại của ghost
                if path:
                    move = (path[0][0] - pos[0], path[0][1] - pos[1])
                    bestAction = Actions.vectorToDirection(move)
                    # print(path)
                    # print("$Best actions found:", bestAction)
                    break
            
            if current in visited:
                continue # Nhảy qua vòng lặp nếu đã thăm node này
            visited.add(current)

            rows, cols = walls.height, walls.width
            directions = {
                (-1, 0): "west",
                (1, 0): "east",
                (0, -1): "south",
                (0, 1): "north"
            }
            # print("Current node:", current, end="->")
            for d in directions:
                if d not in legalActionsVector and current == pos:  # Tránh di chuyển ngược lại hướng hiện tại
                    continue
                nx, ny = self.nextIntPosition(current, d)
                nx = int(nx)
                ny = int(ny)
                # print(nx, ny, end=" ")
                if 0 < nx < cols and 0 < ny < rows and not walls[nx][ny] :
                    next_node = (nx, ny)
                    if next_node not in visited:
                        # print(next_node, end=" ")
                        heapq.heappush(open_set, (
                            g + 1 + self.heuristic(next_node, pacmanPosition),
                            g + 1,
                            path + [next_node]
                        ))
            # print()

        # Construct distribution
        dist = util.Counter()
        if isScared:
            if (len(legalActions) ==1):
                dist[bestAction] = 1
            else:
                for a in legalActions:
                    if a != bestAction:
                        dist[a] = 1/(len(legalActions) - 1)

        else:
            dist[bestAction] = 1

        # print(legalActions)
        if bestAction not in legalActions:
            input()
          # Debugging pause
        return dist
