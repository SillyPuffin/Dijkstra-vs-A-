import sys
import heapq
import pygame
import time
import math
import random
from pygame.math import Vector2

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800

pygame.init()
old_time = time.time()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

cellSize = 10

MAP_WIDTH = WINDOW_WIDTH // 2 // cellSize

if MAP_WIDTH % 2 == 0:
    MAP_WIDTH -= 1

MAP_HEIGHT = WINDOW_HEIGHT // cellSize

if MAP_HEIGHT % 2 == 0:
    MAP_HEIGHT -= 1

class Node:
    def __init__(self, pos, distance, reached_from):
        self.pos = pos
        self.ReachedFrom = reached_from
        self.distanceFromZero = distance

class Anode:
    def __init__(self, f,g,h, parent, pos):
        self.f = f#total
        self.g = g#distance from start
        self.h = h#heuristic
        self.parent = parent
        self.pos = pos

class Maze:
    def __init__(self, width, height):
        self.map = [[1 for _ in range(height)] for _ in range(width)]
        self.stack = []
        self.map[1][0] = 0
        self.map[len(self.map)-2][len(self.map[0])-1] = 0

        self.width = width
        self.height = height


        self.directions = [
            [0, 2],
            [0,-2],
            [2, 0],
            [-2,0]
        ]

        self.singlesDirection = [
            (0,1),
            (0,-1),
            (1,0),
            (-1,0),
            (-1,1),
            (-1,-1),
            (1,1),
            (1,-1)
        ]

    def setCell(self,x,y):
        if x < 0 or y < 0 or x > len(self.map)-1 or y > len(self.map[0])-1:
            return False
        if self.map[x][y] == 0:
            self.map[x][y] = 1
            return True
        else:
            return False

    def clearCell(self,x,y):
        if x < 0 or y < 0 or x > len(self.map)-1 or y > len(self.map[0])-1:
            return False
        if self.map[x][y] == 1:
            self.map[x][y] = 0
            return True
        else:
            return False

    def getInput(self):
        keys = pygame.key.get_pressed()

        #reset the map
        if keys[pygame.K_r]:
            self.resetMap()
            self.generateMap()

        if keys[pygame.K_c]:
            self.resetMap()
            self.map = [[0 for _ in range(self.height)] for _ in range(self.width)]

    def resetMap(self):
        self.map = [[1 for _ in range(self.height)] for _ in range(self.width)]
        self.stack = []
        self.map[1][0] = 0
        self.map[len(self.map) - 2][len(self.map[0]) - 1] = 0

    def generateMap(self):
        current = [random.randrange(1,MAP_WIDTH-2,2),random.randrange(1,MAP_HEIGHT-2,2)]
        self.stack.append(current)

        while len(self.stack) > 0:
            random.shuffle(self.directions)
            foundPath = False
            for item in self.directions:
                nextCell = [current[0] + item[0], current[1] + item[1]]
                x = int(nextCell[0])
                y = int(nextCell[1])

                if x < 0 or y < 0 or x >= len(self.map) or y >= len(self.map[0]):
                    continue

                if self.map[x][y] == 0:
                    continue

                #set the path
                foundPath = True
                self.map[x][y] = 0
                self.map[int(current[0] + item[0]/2)][int(current[1] + item[1]/2)] = 0
                self.stack.append(nextCell)
                current = nextCell[:]
                break

            if not foundPath and len(self.stack) > 0:
                current = self.stack.pop()


        copy_list = []
        for item in self.map:
            copy_list.append(item.copy())

        return copy_list

    def allowPassThrough(self,current, coords):
        vertical = (current[0],coords[1]+current[1])
        horizontal = (coords[0]+current[0],current[1])

        if self.map[vertical[0]][vertical[1]] == 1 and self.map[horizontal[0]][horizontal[1]] == 1:
            return False
        else:
            return True

class Dmaze(Maze):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.visitedNodes = {}
        self.unvisitedNodes = []
        self.indexHash = {}
        self.finalPath = []
        self.finalIncrement = 0
        self.solveState = 0
        self.solved = False
        self.steps = 0

    def solveMaze(self):
        if self.solveState == 0:
            current = Node((1,0), 0, (1,0))
            self.unvisitedNodes.append(current)
            self.indexHash[f"{1}:{0}"] = 0

            self.solveState = 1

        if self.solveState == 1:
            current = min(self.unvisitedNodes, key=lambda x :x.distanceFromZero)
            del self.unvisitedNodes[self.unvisitedNodes.index(current)]
            self.visitedNodes[f"{current.pos[0]}:{current.pos[1]}"] = current

            self.map[current.pos[0]][current.pos[1]] = 3#set to three to show that it is visited

            self.steps += 1

            random.shuffle(self.singlesDirection)
            for item in self.singlesDirection:
                newx = current.pos[0] + item[0]
                newy = current.pos[1] + item[1]

                increase = item[0] ** 2 + item[1] ** 2
                if increase > 1:
                    increase = math.sqrt(increase)  # properly find diagonal distance

                if newx < 0 or newy < 0 or newx >= len(self.map) or newy >= len(self.map[0]):
                    continue
                if self.map[newx][newy] == 1 or self.map[newx][newy] == 3:#if wall or visited dont come back to it
                    continue

                # make sure that its not jumping through walls
                if not self.allowPassThrough(current.pos, item):
                    continue

                if self.map[newx][newy] == 2:
                    #idx = self.indexHash[f"{newx}:{newy}"]
                    for index, item in enumerate(self.unvisitedNodes):
                        if item.pos == (newx,newy):
                            idx = index
                            break
                    if self.unvisitedNodes[idx].distanceFromZero > current.distanceFromZero + increase:
                        del self.unvisitedNodes[idx]

                    elif self.unvisitedNodes[idx].distanceFromZero <= current.distanceFromZero + increase:
                        continue

                if self.map[newx][newy] == 0: #newly registered
                    self.map[newx][newy] = 2

                if self.unvisitedNodes == []:
                    self.unvisitedNodes.append(Node((newx,newy), current.distanceFromZero+increase, current.pos))
                else:
                    for index, item in enumerate(self.unvisitedNodes): #add in order from smallest to largest
                        distance = item.distanceFromZero
                        if distance > current.distanceFromZero + 1: #once you find something with a greater distance insert into the list
                            self.unvisitedNodes.insert(index, Node((newx, newy), current.distanceFromZero+increase, current.pos))
                            break

                        elif index == len(self.unvisitedNodes) - 1:# if it is the biggest distance in the list add it to the back
                            self.unvisitedNodes.append(Node((newx, newy), current.distanceFromZero+increase, current.pos))
                            break

        #check to see if we have finished
            if self.unvisitedNodes == [] or current.pos == (len(self.map)-2, len(self.map[0])-1):
                self.solveState = 2
                if current.pos == (len(self.map)-2, len(self.map[0])-1):
                    self.solved = True
                    print(f"Solution solved in {self.steps} steps using Dijkstra")
                
                if not self.solved:
                    print(f"Solution was not solved after using {self.steps} steps with Dijkstra")

                if self.solved:
                    node = self.visitedNodes[f"{len(self.map) - 2}:{len(self.map[0]) - 1}"]
                    while node.distanceFromZero != 0:
                        self.finalPath.append(node)
                        node = self.visitedNodes[f"{node.ReachedFrom[0]}:{node.ReachedFrom[1]}"]
                    self.finalPath.append(node)
                    
                    self.finalPath.reverse()

                

        if self.solveState == 2 and self.solved:
            if self.finalIncrement < len(self.finalPath):
                x = self.finalPath[self.finalIncrement].pos[0]
                y = self.finalPath[self.finalIncrement].pos[1]

                self.map[x][y] = 4
                self.finalIncrement += 1

    def resetMap(self):
        self.map = [[1 for _ in range(self.height)] for _ in range(self.width)]
        self.stack = []
        self.map[1][0] = 0
        self.map[len(self.map) - 2][len(self.map[0]) - 1] = 0

        self.visitedNodes = {}
        self.unvisitedNodes = []
        self.indexHash = {}
        self.finalPath = []
        self.finalIncrement = 0
        self.solveState = 0
        self.solved = False
        self.steps = 0

    def DrawMap(self):
        count = 0
        increment = 0
        if self.finalPath != []:
            increment = 255/len(self.finalPath)

        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                colour = int(increment*count)
                if self.map[i][j] == 0:
                    pygame.draw.rect(screen, (255, 255, 255), [i*cellSize, j*cellSize, cellSize, cellSize])
                if self.map[i][j] == 2: #orange
                    pygame.draw.rect(screen, (255, 125, 10), [i*cellSize, j*cellSize, cellSize, cellSize])
                if self.map[i][j] == 3:#red for visited
                    pygame.draw.rect(screen, (0, 0, 255), [i*cellSize, j*cellSize, cellSize, cellSize])
                if self.map[i][j] == 4:
                    count += 1
                    pygame.draw.rect(screen, (int(255-colour), colour, 0), [i * cellSize, j * cellSize, cellSize, cellSize])

class Amaze(Maze):
    def __init__(self, MAP_WIDTH, MAP_HEIGHT):
        super().__init__(MAP_WIDTH, MAP_HEIGHT)
        self.openList = []
        self.cellDetails = {}
        self.finalPath = []
        self.count = 0
        self.solveState = 0
        self.solved = False
        self.steps = 0

    def resetMap(self):
        self.map = [[1 for _ in range(self.height)] for _ in range(self.width)]
        self.stack = []
        self.map[1][0] = 0
        self.map[len(self.map) - 2][len(self.map[0]) - 1] = 0

        self.openList = []
        self.cellDetails = {}
        self.count = 0
        self.finalPath = []
        self.solveState = 0
        self.solved = False
        self.steps = 0

    def DrawMap(self, offset=0):
        count = 0
        increment = 0
        if self.finalPath != []:
            increment = 255/len(self.finalPath)

        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                colour = int(increment*count)
                if self.map[i][j] == 0:
                    pygame.draw.rect(screen, (255, 255, 255), [i*cellSize+offset, j*cellSize, cellSize, cellSize])
                if self.map[i][j] == 2: #orange
                    pygame.draw.rect(screen, (255, 125, 10), [i*cellSize+offset, j*cellSize, cellSize, cellSize])
                if self.map[i][j] == 3:#red for visited
                    pygame.draw.rect(screen, (0, 0, 255), [i*cellSize+offset, j*cellSize, cellSize, cellSize])
                if self.map[i][j] == 4:
                    count += 1
                    pygame.draw.rect(screen, (int(255-colour), colour, 0), [i * cellSize+offset, j * cellSize, cellSize, cellSize])

    def solveMaze(self):
        #f is the total of g and h
        #h is the distance from the goal
        #g is the number of moves to get to current
        #oppen list heap format is (f, x, y)
        #node format is f,g,h,parent,pos

        goal = (len(self.map)-2, len(self.map[0])-1)
        if self.solveState == 0:
            startNode = Anode(0,0,0, (1,0), (1,0))
            self.cellDetails[f"{1}:{0}"] = startNode
            heapq.heappush(self.openList, (0, 1, 0))
            self.solveState = 1

        if self.solveState == 1:
            #pop smallest f node off open and get neighbours
            current = heapq.heappop(self.openList)

            self.map[current[1]][current[2]] = 3

            self.steps += 1

            random.shuffle(self.singlesDirection)
            for direction in self.singlesDirection:
                newx = current[1] + direction[0]
                newy = current[2] + direction[1]

                if (newx, newy) == goal:
                    self.solveState = 2
                    self.solved = True

                    #update cell details and the map
                    self.map[newx][newy] = 3

                    increase = direction[0]**2 + direction[1]**2
                    if increase > 1:
                        increase = math.sqrt(increase)#properly find diagonal distance

                    g = self.cellDetails[f"{current[1]}:{current[2]}"].g + increase#set new distance
                    self.cellDetails[f"{newx}:{newy}"] = Anode(g,g,0,(current[1],current[2]),(newx,newy))

                    #get the shortest path to start to draw
                    node = self.cellDetails[f"{len(self.map)-2}:{len(self.map[0])-1}"]
                    self.finalPath.append(node)
                    while node.pos != (1,0):
                        node = self.cellDetails[f"{node.parent[0]}:{node.parent[1]}"]
                        self.finalPath.append(node)

                    self.finalPath.reverse()

                    print(f"Solution found in {self.steps} steps using A*")
                    break

                if newx < 0 or newy < 0 or newx >= len(self.map) or newy >= len(self.map[0]): #check if the cel is within the grid
                    continue
                if self.map[newx][newy] == 1 or self.map[newx][newy] == 3:
                    continue #make sure the cell not a path or already visited

                # make sure that its not jumping through walls
                if not self.allowPassThrough((current[1],current[2]), direction):
                    continue

                increase = direction[0]**2 + direction[1]**2
                if increase > 1:
                    increase = math.sqrt(increase)#properly find diagonal distance

                g = self.cellDetails[f"{current[1]}:{current[2]}"].g + increase#set new distance

                #DIFFERENT HEURISTIC OPTIONS
                #h = (len(self.map)-3- newx) + (len(self.map[0])-1-newy)#manhattan distance
                h = math.sqrt((len(self.map)-3 - newx)**2 + (len(self.map[0])-1-newy)**2)#diagonal distance
                #h = (len(self.map)-2 - newx) #horizontal distance

                #chebychev distance
                # horizontal = abs((len(self.map)-2 - newx))
                # vertical = abs((len(self.map[0]) - newy))
                # h = max([horizontal, vertical]) 


                f =  g + h

                #if cell is the lowest f of all cells at that option then add to open list
                if f"{newx}:{newy}" not in self.cellDetails:
                    #add the cell to cell details and open list
                    #also change colour in the map to be the opened cell colour
                    self.cellDetails[f"{newx}:{newy}"] = Anode(f,g,h,(current[1],current[2]), (newx,newy))
                    heapq.heappush(self.openList, (f, newx,newy))

                    self.map[newx][newy] = 2
                if  self.cellDetails[f"{newx}:{newy}"].f <= f:
                    continue #path is the same so there is no need to update

                #if current successor gets the fastest path

                #remove further path from the openlist
                for index, successor in enumerate(self.openList):
                    if successor[1] == newx and successor[2] == newy:
                        del self.openList[index]

                heapq.heapify(self.openList)
                heapq.heappush(self.openList, (f, newx, newy))

                self.cellDetails[f"{newx}:{newy}"] = Anode(f,g,h,(current[1],current[2]), (newx,newy))

            if self.openList == []:
                self.solveState = 2

                print(f"solution not found after {self.steps} steps using A*")

                #get the final path as a list
                if self.solved:
                    node = self.cellDetails[f"{len(self.map)-2}:{len(self.map[0])-1}"]
                    self.finalPath.append(node)
                    while node.pos != (1,0):
                        node = self.cellDetails[f"{node.parent[0]}:{node.parent[1]}"]
                        self.finalPath.append(node)

                    self.finalPath.reverse()

        if self.solveState == 2 and self.solved:
            self.map[self.finalPath[self.count].pos[0]][self.finalPath[self.count].pos[1]] = 4
            self.count += 1
            if self.count == len(self.finalPath):
                self.solveState = 3

maze = Dmaze(MAP_WIDTH, MAP_HEIGHT)
newmap = maze.generateMap()

maze2 = Amaze(MAP_WIDTH, MAP_HEIGHT)
maze2.map = newmap

timer = 0
run = False
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                run = not run

    new_time = time.time()
    dt = new_time - old_time
    old_time = new_time

    timer += dt

    keys = pygame.key.get_pressed()

    if keys[pygame.K_r]:
        maze.resetMap()
        newmap = maze.generateMap()
        maze2.resetMap()
        maze2.map = newmap

    if keys[pygame.K_c]:
        maze.resetMap()
        maze2.resetMap()
        map = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        map2 = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        maze.map = map
        maze2.map = map2

    if run:
        maze.solveMaze()
        maze2.solveMaze()
    else:
        mouse = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            x = mouse[0]
            y = mouse[1]
            x //= cellSize
            y //= cellSize
            maze.setCell(x,y)
            maze2.setCell(x,y)
        elif pygame.mouse.get_pressed()[2]:
            x = mouse[0]
            y = mouse[1]
            x //= cellSize
            y //= cellSize
            maze.clearCell(x, y)
            maze2.clearCell(x, y)

    screen.fill((0, 0, 0))
    if timer >= 0.0 or maze.solveState == 2:
        maze.DrawMap()
        maze2.DrawMap(MAP_WIDTH * cellSize)
        timer = 0


        pygame.display.update()