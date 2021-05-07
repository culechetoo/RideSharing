import math


class Location:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, otherLocation):
        if isinstance(otherLocation, Location):
            if self.x == otherLocation.x:
                if self.y == otherLocation.y:
                    return True
        return False

    def getArray(self):
        return [self.x, self.y]
    
    def getDistance(self, location, distanceType):
        if distanceType == "l1":
            return abs(self.x - location.x) + abs(self.y - location.y)
        if distanceType == "l2":
            return math.sqrt(abs(self.x ** 2 - self.x ** 2) + abs(self.y ** 2 - location.y ** 2))
        if distanceType == "graph":
            pass

    def __str__(self):
        return str(self.getArray())


class GraphNode:
    index: int
    location: Location
    nodeType: str

    def __init__(self, index: int, location: Location, nodeType: str):
        self.index = index
        self.location = location
        self.nodeType = nodeType

    def __eq__(self, otherNode):
        if isinstance(otherNode, GraphNode):
            if self.index == otherNode.index:
                if self.location == otherNode.location:
                    if self.nodeType == otherNode.nodeType:
                        return True
        return False


class Driver:
    index: int
    capacity: int
    location: Location

    def __init__(self, index: int, capacity: int, location: Location):
        self.index = index
        self.capacity = capacity
        self.location = location


class Rider:
    index: int
    sourceLocation: Location
    targetLocation: Location

    def __init__(self, index: int, sourceLocation: Location, targetLocation: Location):
        self.index = index
        self.sourceLocation = sourceLocation
        self.targetLocation = targetLocation
