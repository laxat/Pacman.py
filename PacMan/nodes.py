import pygame
from typing import*
from vector import Vector2
from constants import *
from stack import Stack

class Node:

    """
     A Node is really anything you want it to be. It's a very abstract thing.
     It's basically an abstract object that contains information.
     Usually when you're talking about nodes in video games, one of the most
     important pieces of information is the position of the node.
     You can also represent a node any way you like, we're going to represent
     a node as a red circle.

    Being a neighbor to any particular node has nothing to do with proximity.
    Two nodes can be right next to each other, but if they are not linked together,
    then they are not neighbors. If two nodes are connected to each other,
    then they are connected by a path. We'll represent a path by a straight line that joins two nodes together.
    That's how we can know visually that two nodes are connected to each other.

    """
    row: int
    column: int
    portalval = 0

    def __init__(self, row, column):
        """
        When we create a Node we pass in the row and column values and then
        compute the x and y position we want to place the Node on the screen.
        We also set up the neighbors as a dictionary. This way it's really easy
        to know which node is in which direction to this Node.
        """

        self.row, self.column = row, column
        self.position = Vector2(column * WIDTH, row * HEIGHT)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None}
        self.portals = None
        self.portalval = 0

    def render(self, screen):
        """
        Render the Node so it appears on the screen.
        We draw all of the paths to the neighbors first as WHITE lines, and we
        draw the Node itself as a RED circle.
        """
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                pygame.draw.line(screen, WHITE, self.position.toTuple(),
                                 self.neighbors[n].position.toTuple(), 4)
                pygame.draw.circle(screen, RED, self.position.toTuple(True), 12)


class NodeGroup:

    """
    This class links all the Nodes and ther pathhs to create a sort of
    Nodegroup to visually represent the pacman board for pacman to move around
    in.
    """
    nodeList: List[Node]
    level: int
    grid: List
    nodeStack: Stack
    portalSymbols: List
    nodeSymbols: List

    def __init__(self, level):
        self.nodeList = []
        self.level = level
        self.grid = None
        self.nodeStack = Stack()
        self.portalSymbols = ["1"]
        self.nodeSymbols = ["+"] + self.portalSymbols
        self.createNodeList(level, self.nodeList)
        self.createPortals()

    def readMazeFile(self, textfile):
        """
        Get information from files
        """
        f = open(textfile, "r")
        lines = [line.rstrip('\n') for line in f]
        grid = [line.split(' ') for line in lines]
        return grid

    def createNodeList(self, textFile, nodeList):
        """
        This method creates a map based on text file passed into the
        function
        """

        self.grid = self.readMazeFile(textFile)
        startNode = self.getFirstNode(len(self.grid), len(self.grid[0]))
        self.nodeStack.push(startNode)
        while not self.nodeStack.is_empty():
            node = self.nodeStack.pop()
            self.addNode(node, nodeList)
            left = self.getPath(LEFT, node.row, node.column-1, nodeList)
            right = self.getPath(RIGHT, node.row, node.column+1, nodeList)
            top = self.getPath(UP, node.row - 1, node.column, nodeList)
            bottom = self.getPath(DOWN, node.row + 1, node.column, nodeList)
            node.neighbors[LEFT] = left
            node.neighbors[RIGHT] = right
            node.neighbors[UP] = top
            node.neighbors[DOWN] = bottom
            self.addToStack(left, nodeList)
            self.addToStack(right,  nodeList)
            self.addToStack(top, nodeList)
            self.addToStack(bottom, nodeList)

    def getFirstNode(self, rows, cols):
        """
        This method will go into the grid list and find the first instance of a Node.
        This serves as our starting point before we go into the while loop.
        """
        nodeFound = False
        for i in range(rows):
            for j in range(cols):
                if self.grid[i][j] in self.nodeSymbols:
                    node = Node(i, j)
                    if self.grid[i][j] in self.portalSymbols:
                        node.portalval = self.grid[i][j]
                    return node
        return None

    def getNode(self, x, y, nodeList):
        """
        This method simply looks for a node in the nodeList at the specified x and y position.
        If a node at this position exists, then it returns that Node object.
        If it doesn't exist, then it will return None.
        """
        for node in nodeList:
            if node.position.x == x and node.position.y == y:
                return node

        return None

    def getNodeFromNode(self, node, nodeList):
        """
        what this method doesis look for the specified node in the nodeList.
        If the node exists in the nodeList, then the method will return the Node
        object from the nodeList. If it doesn't exist in the nodeList, then it
        will just return the node that was initially inputted.
        This is needed in order to avoid having duplicate Nodes, because we will
        visit a node more than once.
        """

        if node is not None:
            for inode in nodeList:
                if node.row == inode.row and node.column == inode.column:
                    return inode

        return node

    def getPath(self, direction, row, col, nodeList):
        """
        This method returns either a Node object or None. It follows a path in
        the specified direction and returns the Node object that is connected to
        the current node we're dealing with if there is one and if it already
        doesn't exist in the nodeList.
        """
        tempNode = self.followPath(direction, row, col)
        return self.getNodeFromNode(tempNode, nodeList)

    def addNode(self, node, nodeList):
        """
        This method simply adds a Node object to the nodeList if it already does
        not exist in the nodeList.
        """
        nodeInList = self.nodeInList(node, nodeList)
        if not nodeInList:
            nodeList.append(node)

    def addToStack(self, node, nodeList):
        """
        This method adds a node to the stack if it already hasn't been added to
        the nodeList.
        """
        if node is not None and not self.nodeInList(node, nodeList):
            self.nodeStack.push(node)

    def nodeInList(self, node, nodeList):
        """
        This method is similar to the getNode method but instead of returning Nodes
        or None, it will return either True or False whether the specified node
        is in the nodeList or not.
        """
        for i in nodeList:
            if node.position.x == i.position.x and node.position.y == i.position.y:
                return True
        return False

    def createPortals(self):
        """
        Since we have already created all the nodes in the list, all we have to
        do is loop through and create a new link/path between the portals on the
        screen using the portalval variable.
        """
        d = {}
        for i in range(len(self.nodeList)):
            if self.nodeList[i].portalval != 0:
                if self.nodeList[i].portalval not in d.keys():
                    d[self.nodeList[i].portalval] = [i]
                else:
                    d[self.nodeList[i].portalval] += [i]
        for key in d.keys():
            node1, node2 = d[key]
            self.nodeList[node1].portals = self.nodeList[node2]
            self.nodeList[node2].portals = self.nodeList[node1]

    def pathToFollow(self, direction, row, col, path):
        """
        Looks for certain items in the grid, until we run into a node
        with a different value
        """
        tempSymbols = [path] + self.nodeSymbols
        if self.grid[row][col] in tempSymbols:
            while self.grid[row][col] not in self.nodeSymbols:
                if direction is RIGHT:
                    col += 1
                elif direction is LEFT:
                    col -= 1
                elif direction is UP:
                    row -= 1
                elif direction is DOWN:
                    row += 1
            node = Node(row, col)
            if self.grid[row][col] in self.portalSymbols:
                node.portalval = self.grid[row][col]
            return node
        else:
            return None

    def followPath(self, direction, row, col):
        """
        Follows path in all four directions
        """
        rows = len(self.grid)
        columns = len(self.grid[0])

        if direction == LEFT and col >= 0:
            return self.pathToFollow(LEFT, row, col, '-')
        elif direction == RIGHT and col < columns:
            return self.pathToFollow(RIGHT, row, col, "-")
        elif direction == UP and row >= 0:
            return self.pathToFollow(UP, row, col, "|")
        elif direction == DOWN and row < rows:
            return self.pathToFollow(DOWN, row, col, "|")
        else:
            return None

    def render(self, screen):
        """
        draw all the nodes and paths in the NodeList
        """
        for node in self.nodeList:
            node.render(screen)

