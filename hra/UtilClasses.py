from math import sqrt


class Location:

    __slots__ = ['x', 'y']

    def __init__(self, x, y):
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
    
    def getDistance(self, location, distanceType="l2"):
        assert distanceType in ["l1", "l2"]

        if distanceType == "l1":
            return abs(self.x - location.x) + abs(self.y - location.y)
        if distanceType == "l2":
            return sqrt((self.x - location.x)**2 + (self.y - location.y)**2)

    def __str__(self):
        return str(self.x)+" "+str(self.y)


class Car:

    __slots__ = ['index', 'capacity', 'location']

    def __init__(self, index, capacity, location):
        self.index = index
        self.capacity = capacity
        self.location = location


class Rider:

    __slots__ = ['index', 'sourceLocation', 'targetLocation']

    def __init__(self, index, sourceLocation, targetLocation):
        self.index = index
        self.sourceLocation = sourceLocation
        self.targetLocation = targetLocation
