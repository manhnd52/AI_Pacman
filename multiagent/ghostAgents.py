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
from pacman import GameState
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

    def a_star_search(self, state, goal):
        open_set = []
        path = []
        visited = set()
        start = state.getGhostPosition(self.index)
        heapq.heappush(open_set, (self.heuristic(start, goal), 0, []))
        legalStartDirections = [Actions.directionToVector(a) for a in state.getLegalActions(self.index)]
        while open_set:
            f, g, path = heapq.heappop(open_set)
            current = path[-1] if path else start
            if current == goal:
                # if len(path) == 0:
                #     print("_____A* search failed_____")
                #     print("Pacman position:", state.getPacmanPosition())
                #     print("Ghost position:", state.getGhostPosition(self.index))
                #     print("Goal position:", goal)
                #     print("______")
                return path
            
            if current in visited:
                continue
            visited.add(current)

            directions = [(-1,0), (1,0), (0,-1), (0,1)]
            for d in directions:
                if d not in legalStartDirections and current == start:
                    continue
                # print("Current direction:", d)
                nx, ny = self.nextIntPosition(current, d)
                nx, ny = int(nx), int(ny)
                if self.checkValidPosition(state, (nx, ny)):
                    next_node = (nx, ny)
                    if next_node not in visited:
                        heapq.heappush(open_set, (
                            g + 1 + self.heuristic(next_node, goal),
                            g + 1,
                            path + [next_node]
                        ))
        return []


    def nextIntPosition(self, pos, direction):
        if direction == (0, -1):
            return pos[0], ceil(pos[1] - 1)  # South
        elif direction == (0, 1):
            return pos[0], floor(pos[1] + 1)  # North
        elif direction == (-1, 0):
            return ceil(pos[0] - 1), pos[1]
        elif direction == (1, 0):
            return floor(pos[0] + 1), pos[1]

    def checkValidPosition(self, state, pos):
        walls = state.getWalls()
        nx = int(pos[0])
        ny = int(pos[1])
        cols, rows = walls.width, walls.height
        if 0 < nx < cols and 0 < ny < rows and not walls[nx][ny]:
            return True
        return False

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
    
    def getDistribution(self, state):
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        isScared = ghostState.scaredTimer > 0
        pacmanPosition = state.getPacmanPosition()
        pos = state.getGhostPosition(self.index)

        conf = ghostState.configuration
        reverse = Actions.reverseDirection(conf.direction)
        reverse = Actions.directionToVector(reverse)
        

        # Sử dụng thuật toán A* để tìm đường đi đến Pacman
        searchPath = self.a_star_search(state, pacmanPosition)
        bestAction = (searchPath[0][0] - pos[0], searchPath[0][1] - pos[1])  if searchPath else Directions.STOP
        bestAction = Actions.vectorToDirection(bestAction)

        # Construct distribution
        dist = util.Counter()
        if isScared:
            if (len(legalActions) == 1):
                dist[bestAction] = 1
            else:
                for a in legalActions:
                    if a != bestAction:
                        dist[a] = 1/(len(legalActions) - 1)
        else:
            dist[bestAction] = 1

        if bestAction not in legalActions:
            input()
            
        return dist

    
class SuperGhost2(GhostAgent):
    "A ghost that prefers to rush Pacman, or flee when scared, with a higher probability."

    def __init__(self, index, prob_attack=1, prob_scaredFlee=1):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    
    def predictPacmanPosition(self, state : GameState, max_steps=5):
        pos = state.getPacmanPosition()
        successor = state
        
        for _ in range(max_steps):
            
            direction = successor.getPacmanState().configuration.direction
            if direction in successor.getLegalActions(0): # Nếu Pacman có thể tiếp tục đi hướng đang đi
                successor = successor.generateSuccessor(0, direction)
                pos = successor.getPacmanPosition()
                continue
            else:
                pacman_legal_actions = successor.getLegalActions(0)
                if len(pacman_legal_actions) == 0:
                    break
                elif len(pacman_legal_actions) == 1:  # Nếu Pacman chỉ có một hành động hợp lệ
                    best_action = pacman_legal_actions[0]
                else:  # Nếu Pacman có nhiều hành động hợp lệ
                    scores = self.scoreForPacmanAction(successor, pacman_legal_actions)
                    best_score = max(scores) if scores else 0
                    best_actions = [action for action, score in zip(pacman_legal_actions, scores) if score == best_score]
                    best_action = random.choice(best_actions)

                successor = successor.generateSuccessor(0, best_action)
                pos = successor.getPacmanPosition()
        return pos

    def scoreForPacmanAction(self, state : GameState, actions):
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPositions()
        nextPacmanPos = [Actions.getSuccessor(pacmanPos, action) for action in actions]

        # Tính khoảng cách từ vị trí của Pacman sau khi thực hiện action đến vị trí của capsule
        distanceToCapsules = [[manhattanDistance(nextPacmanPos, capsule) for capsule in state.getCapsules()] for nextPacmanPos in nextPacmanPos]
        capsuleScore = [min(distanceToCapsules[i]) if len(distanceToCapsules[i]) > 0 else 0 for i in range(len(nextPacmanPos))]
        
        # Tính khoảng cách từ vị trí của Pacman sau khi thực hiện action đến vị trí của ghost
        distanceToGhosts = [[manhattanDistance(nextPacmanPos, ghost) for ghost in ghostPos] for nextPacmanPos in nextPacmanPos]
        ghostScore = [sum(distanceToGhosts[i]) / len(distanceToGhosts[i]) if len(distanceToGhosts[i]) > 0 else 0 for i in range(len(nextPacmanPos))]

        # Tính khoảng cách đến vị trí của food
        foodPositions = state.getFood().asList()
        distanceToFood = [[manhattanDistance(nextPacmanPos, food) for food in foodPositions] for nextPacmanPos in nextPacmanPos]
        foodScore = [sum(distanceToFood[i]) / len(distanceToFood[i]) if len(distanceToFood[i]) > 0 else 0 for i in range(len(nextPacmanPos))]

        # Sum score
        scores = [1/(capsuleScore[i]+0.1)*2 - 1/ghostScore[i] + 1/foodScore[i] for i in range(len(nextPacmanPos))]
        return scores

    
    def blockPacmanRoute(self, state, max_prediction_steps=10):
        """
        Tìm đường đi ngắn nhất đến một vị trí PACMAN có thể đến mà ma có thể đến trước/ cùng lúc với PACMAN để chặn PACMAN di chuyển đến đó.
        Trả về đường đi dưới dạng một danh sách các tọa độ (x, y) mà ma có thể đi đến.
        Nếu không tìm thấy đường đi nào, trả về một danh sách rỗng.
        """
        path = self.a_star_search(state, state.getPacmanPosition())
        first_step = path[0] if path else None
        if len(path) == 1:
            return path
        pacmanStep = 0
        while len(path) > pacmanStep and pacmanStep < max_prediction_steps:
            pacmanStep += 1
            nextPacmanPosition = self.predictPacmanPosition(state, max_steps=pacmanStep)
            path = self.a_star_search(state, nextPacmanPosition)
        return path if path else [first_step]               # Khi vị trí PACMAN dự định tới trùng với vị trí của ma, trả về đường đi từ vị trí hiện tại của ma đến vị trí PACMAN hiện tại.
    
    def getDistribution(self, state):
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        isScared = ghostState.scaredTimer > 0
        pacmanPosition = state.getPacmanPosition()
        pos = state.getGhostPosition(self.index)

        # Dự đoán vị trí của Pacman trong tương lai
        predictposition = self.predictPacmanPosition(state, max_steps=5)
        # print("Predicted Pacman position:", predictposition)

        conf = ghostState.configuration
        reverse = Actions.reverseDirection(conf.direction)
        reverse = Actions.directionToVector(reverse)
        
        speed = 1
        if isScared:
            speed = 0.5

        # Sử dụng thuật toán A* để tìm đường đi đến Pacman
        searchPath = self.blockPacmanRoute(state)
        bestAction = (searchPath[0][0] - pos[0], searchPath[0][1] - pos[1])  if searchPath else Directions.STOP
        if bestAction == Directions.STOP:
            print("Ghost index:", self.index, conf.direction)
            ghost1 = state.getGhostPosition(1)
            ghost2 = state.getGhostPosition(2)
            map = state.getWalls()
            for i in range(map.width):
                    for j in range(map.height):
                        if (i, j) == pacmanPosition:
                            map[i][j] = "O"
                        elif (i, j) == ghost1:
                            map[i][j] = "1"
                        elif (i, j) == ghost2:
                            map[i][j] = "2"
                        elif map[i][j] == 0:
                            map[i][j] = " "
                        else:
                            map[i][j] = "#"
            print(map)
            print(searchPath)
            print("Ghost and PACMAN position: ", ghost2, pacmanPosition)
            input()
        bestAction = Actions.vectorToDirection(bestAction)

        # Construct distribution
        dist = util.Counter()
        if isScared:
            if (len(legalActions) == 1):
                dist[bestAction] = 1
            else:
                for a in legalActions:
                    if a != bestAction:
                        dist[a] = 1/(len(legalActions) - 1)

        else:
            dist[bestAction] = 1

        if bestAction not in legalActions:
            input()
            
        return dist

#----------------------------------------------------------------------------------------------------------------------------
class MinimaxGhost(GhostAgent):
    """
    Ghost dùng thuật toán minimax.
    Ghost sẽ chọn hành động sao cho khi tính đến các lượt đi:
        - Pac-Man (agent 0) là MAX: tìm cách tăng giá trị đánh giá (trạng thái tốt cho Pac-Man).
        - Các ghost (bao gồm ghost này) là MIN: tìm cách giảm giá trị đánh giá (trạng thái xấu cho Pac-Man).
    Chúng ta giả sử hàm đánh giá (evaluationFunction) được thiết kế phù hợp với mục tiêu của ghost.
    """

    def __init__(self, index, depth=2, evaluationFunction=None):
        self.index = index
        self.depth = depth
        if evaluationFunction is None:
            self.evaluationFunction = self.defaultEvaluationFunction
        else:
            self.evaluationFunction = evaluationFunction

    def defaultEvaluationFunction(self, state):
        """
        Một ví dụ hàm đánh giá cho ghost.
        Hàm đánh giá này có thể dựa trên khoảng cách giữa ghost và Pac-Man:
            - Nếu ghost càng gần Pac-Man, thì giá trị càng thấp (tốt cho ghost).
            - Cần nhớ: Ở các nút lá của cây minimax,
              giá trị cao biểu thị trạng thái tốt cho Pac-Man.
        Do đó, ghost hướng đến việc chọn các trạng thái có giá trị nhỏ.
        """
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(self.index)
        # Sử dụng khoảng cách Manhattan
        dist = util.manhattanDistance(pacmanPos, ghostPos)
        # Nếu ghost gần Pac-Man, trạng thái tốt (giá trị thấp).
        return dist

    def getAction(self, state):
        """
        Phương thức này sẽ duyệt qua các hành động hợp lệ của ghost hiện hành
        và chọn hành động mà cho kết quả minimax là nhỏ nhất, theo mục tiêu của ghost.
        """
        legalActions = state.getLegalActions(self.index)
        if not legalActions:
            return Directions.STOP

        bestScore = float("inf")
        bestAction = None
        # Ở gốc (depth = 0) ta duyệt qua các nước đi của ghost này
        for action in legalActions:
            successor = state.generateSuccessor(self.index, action)
            score = self.minimax(successor, self.getNextAgent(state, self.index), 0)
            if score < bestScore:
                bestScore = score
                bestAction = action
        if bestAction is None:
            return Directions.STOP
        return bestAction

    def minimax(self, state, agentIndex, depthSoFar):
        """
        Hàm minimax đa tác nhân:
          - Pac-Man (agent 0) là MAX.
          - Các ghost (agent != 0) là MIN.
        Lưu ý: Một "ply" được định nghĩa là 1 lượt của Pac-Man và tất cả ghost.
        """
        # Điều kiện dừng: nếu game kết thúc hoặc đạt giới hạn độ sâu
        if state.isWin() or state.isLose() or depthSoFar == self.depth:
            return self.evaluationFunction(state)

        numAgents = state.getNumAgents()
        nextAgent = self.getNextAgent(state, agentIndex)
        nextDepth = depthSoFar + 1 if nextAgent == 0 else depthSoFar

        legalActions = state.getLegalActions(agentIndex)
        if not legalActions:
            return self.evaluationFunction(state)

        # Nếu là lượt của Pac-Man (agent 0): MAX node
        if agentIndex == 0:
            value = float("-inf")
            for action in legalActions:
                successor = state.generateSuccessor(agentIndex, action)
                value = max(value, self.minimax(successor, nextAgent, nextDepth))
            return value
        else:
            # Là lượt của ghost (các tác nhân khác bao gồm cả ghost hiện hành): MIN node
            value = float("inf")
            for action in legalActions:
                successor = state.generateSuccessor(agentIndex, action)
                value = min(value, self.minimax(successor, nextAgent, nextDepth))
            return value

    def getNextAgent(self, state, currentAgent):
        numAgents = state.getNumAgents()
        return (currentAgent + 1) % numAgents


#----------------------------------------------------------------------------------------------------------------------------
class AlphaBetaGhost(GhostAgent):
    """
    Ghost sử dụng thuật toán minimax kết hợp với alpha-beta pruning.
    Pac-Man (agent 0) là MAX node (tìm cách làm điểm cao – tốt cho Pac-Man),
    còn Ghost (agent != 0) là MIN node (tìm cách làm điểm thấp – tốt cho Ghost).
    """
    def __init__(self, index, depth=2, evaluationFunction=None):
        self.index = index
        self.depth = depth
        # Nếu không có hàm đánh giá nào được cung cấp, sử dụng hàm mặc định.
        if evaluationFunction is None:
            self.evaluationFunction = self.defaultEvaluationFunction
        else:
            self.evaluationFunction = evaluationFunction

    def defaultEvaluationFunction(self, state):
        """
        Hàm đánh giá mặc định cho ghost sử dụng khoảng cách Manhattan giữa ghost và Pac-Man.
        - Giá trị thấp (khoảng cách ngắn) là tốt cho ghost.
        """
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(self.index)
        return util.manhattanDistance(pacmanPos, ghostPos)

    def getAction(self, state):
        """
        Lựa chọn hành động cho ghost dựa trên thuật toán alpha-beta search.
        Quá trình:
          1. Lấy danh sách các hành động hợp lệ.
          2. Với mỗi hành động, sinh ra trạng thái kế tiếp (successor)
             và đánh giá điểm thông qua hàm alphabeta.
          3. Vì ghost là MIN node, ta chọn hành động có điểm đánh giá nhỏ nhất.
          4. Alpha-beta ban đầu được thiết lập với alpha = -∞, beta = +∞.
        """
        legalActions = state.getLegalActions(self.index)
        if not legalActions:
            return Directions.STOP  # Nếu không có hành động hợp lệ, ghost đứng yên.

        bestAction = None
        bestScore = float("inf")  # Ghost muốn giá trị đánh giá thấp nhất.
        alpha = float("-inf")
        beta = float("inf")

        # Duyệt qua các hành động hợp lệ của ghost.
        for action in legalActions:
            successor = state.generateSuccessor(self.index, action)
            score = self.alphabeta(successor, self.getNextAgent(state, self.index), 0, alpha, beta)
            # Nếu hành động này cho điểm thấp hơn, cập nhật bestScore và bestAction.
            if score < bestScore:
                bestScore = score
                bestAction = action
            # Khi ghost chọn hành động, nó là MIN node nên cập nhật beta.
            beta = min(beta, bestScore)
        if bestAction is None:
            return Directions.STOP
        return bestAction

    def alphabeta(self, state, agentIndex, depthSoFar, alpha, beta):
        """
        Thuật toán alpha-beta search đệ quy cho trò chơi đa tác nhân.
        - Nếu đạt điều kiện dừng (trạng thái thắng/thua hoặc đạt độ sâu tối đa),
          trả về giá trị của state theo hàm đánh giá.
        - Nếu đến lượt của Pac-Man (agentIndex == 0, MAX node):
            Giá trị được tối đa hoá; cập nhật alpha.
            Nếu value > beta, cắt bỏ (prune) nhánh.
        - Nếu đến lượt của ghost (agentIndex != 0, MIN node):
            Giá trị được tối thiểu hoá; cập nhật beta.
            Nếu value < alpha, cắt bỏ nhánh.
        """
        # Điều kiện dừng: game đã kết thúc hoặc đạt tới độ sâu quy định.
        if state.isWin() or state.isLose() or depthSoFar == self.depth:
            return self.evaluationFunction(state)

        numAgents = state.getNumAgents()
        nextAgent = self.getNextAgent(state, agentIndex)
        # Tăng depth: mỗi khi lượt của Pac-Man đến, chúng ta coi đó là một "ply".
        nextDepth = depthSoFar + 1 if nextAgent == 0 else depthSoFar

        legalActions = state.getLegalActions(agentIndex)
        if not legalActions:
            return self.evaluationFunction(state)

        # Nếu đến lượt của Pac-Man: MAX node
        if agentIndex == 0:
            value = float("-inf")
            for action in legalActions:
                successor = state.generateSuccessor(agentIndex, action)
                value = max(value, self.alphabeta(successor, nextAgent, nextDepth, alpha, beta))
                # Nếu giá trị vượt quá beta, không cần duyệt thêm, cắt nhánh.
                if value > beta:
                    return value
                alpha = max(alpha, value)
            return value
        else:
            # Nếu đến lượt của ghost: MIN node
            value = float("inf")
            for action in legalActions:
                successor = state.generateSuccessor(agentIndex, action)
                value = min(value, self.alphabeta(successor, nextAgent, nextDepth, alpha, beta))
                # Nếu giá trị nhỏ hơn alpha, cắt nhánh (prune).
                if value < alpha:
                    return value
                beta = min(beta, value)
            return value

    def getNextAgent(self, state, currentAgent):
        numAgents = state.getNumAgents()
        return (currentAgent + 1) % numAgents
