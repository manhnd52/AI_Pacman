# multiAgents.py
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        # Get the successor game state
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # Compute distances to all food
        foodList = newFood.asList()
        foodDistances = [manhattanDistance(newPos, food) for food in foodList]
        minFoodDist = min(foodDistances) if foodDistances else 1  # Avoid divide-by-zero

        # Compute distances to all ghosts
        ghostPositions = [ghost.getPosition() for ghost in newGhostStates]
        ghostDistances = [manhattanDistance(newPos, ghostPos) for ghostPos in ghostPositions]
        minGhostDist = min(ghostDistances) if ghostDistances else float('inf')

        # Score components
        foodScore = -1.5 * minFoodDist  # the closer to food, the better
        ghostScore = 0
        for dist, scare in zip(ghostDistances, newScaredTimes):
            if scare == 0:
                if dist <= 1:
                    ghostScore -= 100  # Very bad to be too close to active ghost
                else:
                    ghostScore += dist  # Farther from active ghosts is better
            else:
                ghostScore += 20 - dist  # Encourage chasing scared ghosts

        stopPenalty = -10 if action == Directions.STOP else 0

        return successorGameState.getScore() + foodScore + ghostScore + stopPenalty


def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'betterEvaluationFunction', depth = '3'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the Minimax action from the current gameState using self.depth
        and self.evaluationFunction.
        """

        def minimax(state, agentIndex, depthSoFar):
            # Terminal or depth-limit check
            if state.isWin() or state.isLose() or depthSoFar == self.depth:
                return self.evaluationFunction(state)

            numAgents = state.getNumAgents()
            nextAgent = (agentIndex + 1) % numAgents
            nextDepth  = depthSoFar + 1 if nextAgent == 0 else depthSoFar

            legalActions = state.getLegalActions(agentIndex)
            # If no legal actions, treat as terminal
            if not legalActions:
                return self.evaluationFunction(state)

            # Pac-Man (max) turn
            if agentIndex == 0:
                return max(
                    minimax(state.generateSuccessor(agentIndex, action),
                            nextAgent, nextDepth)
                    for action in legalActions
                )
            # Ghost (min) turn
            else:
                return min(
                    minimax(state.generateSuccessor(agentIndex, action),
                            nextAgent, nextDepth)
                    for action in legalActions
                )

        # -------- root call: choose the best pac-man action ----------
        bestScore = float("-inf")
        bestAction = None
        for action in gameState.getLegalActions(0):   # Pac-Man is agent 0
            score = minimax(gameState.generateSuccessor(0, action),
                            agentIndex=1, depthSoFar=0)
            if score > bestScore:
                bestScore, bestAction = score, action
        if bestAction is None:
            return Directions.STOP  # If no legal actions, stop
        return bestAction

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Minimax agent with alpha-beta pruning
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """

        def alphabeta(state, agentIndex, depthSoFar, alpha, beta):
            if state.isWin() or state.isLose() or depthSoFar == self.depth:
                return self.evaluationFunction(state)

            numAgents = state.getNumAgents()
            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depthSoFar + 1 if nextAgent == 0 else depthSoFar

            legalActions = state.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(state)

            if agentIndex == 0:  # Pac-Man (maximizer)
                value = float("-inf")
                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    value = max(value, alphabeta(successor, nextAgent, nextDepth, alpha, beta))
                    if value > beta:
                        return value  # beta cutoff
                    alpha = max(alpha, value)
                return value
            else:  # Ghost (minimizer)
                value = float("inf")
                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    value = min(value, alphabeta(successor, nextAgent, nextDepth, alpha, beta))
                    if value < alpha:
                        return value  # alpha cutoff
                    beta = min(beta, value)
                return value

        # Root node: choose the best action for Pac-Man
        bestScore = float("-inf")
        bestAction = None
        alpha = float("-inf")
        beta = float("inf")
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            score = alphabeta(successor, 1, 0, alpha, beta)
            if score > bestScore:
                bestScore = score
                bestAction = action
            alpha = max(alpha, bestScore)
        if bestAction is None:
            return Directions.STOP
        return bestAction


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    Expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction
        """

        def expectimax(state, agentIndex, depthSoFar):
            if state.isWin() or state.isLose() or depthSoFar == self.depth:
                return self.evaluationFunction(state)

            numAgents = state.getNumAgents()
            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depthSoFar + 1 if nextAgent == 0 else depthSoFar

            legalActions = state.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(state)

            if agentIndex == 0:  # Pac-Man (maximizer)
                return max(
                    expectimax(state.generateSuccessor(agentIndex, action),
                               nextAgent, nextDepth)
                    for action in legalActions
                )
            else:  # Ghost (chance node - uniform distribution)
                values = [
                    expectimax(state.generateSuccessor(agentIndex, action),
                               nextAgent, nextDepth)
                    for action in legalActions
                ]
                return sum(values) / len(values)

        # Choose best action for Pac-Man at the root
        bestScore = float("-inf")
        bestAction = None
        for action in gameState.getLegalActions(0):
            score = expectimax(gameState.generateSuccessor(0, action), 1, 0)
            if score > bestScore:
                bestScore = score
                bestAction = action

        return bestAction


def betterEvaluationFunction(currentGameState: GameState):
    from util import manhattanDistance

    pos = currentGameState.getPacmanPosition()
    food = currentGameState.getFood().asList()
    capsules = currentGameState.getCapsules()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]

    # Base score
    score = currentGameState.getScore()

    # Distance to the closest food
    if food:
        minFoodDist = min(manhattanDistance(pos, f) for f in food)
        score += 10.0 / minFoodDist
    else:
        score += 100                # no food left is very good

    # Distance to the closest capsule
    if capsules:
        minCapDist = min(manhattanDistance(pos, cap) for cap in capsules)
        score += 5.0 / (minCapDist + 1)

    # Ghost evaluations
    for i, ghost in enumerate(ghostStates):
        dist = manhattanDistance(pos, ghost.getPosition())
        if scaredTimes[i] > 0:
            score += 10.0 / (dist + 1)  # chase scared ghosts
        else:
            if dist <= 1:
                score -= 100  # avoid dangerous ghosts
            elif dist <= 3:
                score -= 5 / dist

    # Win/Lose conditions
    if currentGameState.isWin():
        return float('inf')
    if currentGameState.isLose():
        return float('-inf')

    return score


# Abbreviation
better = betterEvaluationFunction
