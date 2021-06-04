from Main.UtilClasses import Driver
from OurAlg.tsp.Utils import getRequestLocation
from OurAlg.Utils import getBoundedAssignmentWalks, getRequestGroupWalkCost


def getPathWeight(path, distanceType):
    totalWeight = 0
    for i in range(len(path)-1):
        totalWeight += path[i].getDistance(path[i+1], distanceType)

    return totalWeight


def checkAdjacency(nodeType1, nodeType2):
    if nodeType1 == "driver":
        if nodeType2 == "riderSource":
            return True
    if nodeType1 == "riderSource":
        return True
    if nodeType1 == "riderTarget":
        if nodeType2 != "driver":
            return True
    return False


def getBestDriverRequestGroupCost(driver, requestGroup, distNorm="l2"):

    edgeWeight = 1e9
    for request in requestGroup:
        edgeWeight = min(edgeWeight, request.sourceLocation.getDistance(driver.location, distNorm))

    return edgeWeight


def getTotalRequestServeTime(walks, distNorm="l2"):

    totalServeTime = 0

    for walk in walks:

        currLocation = walk[0].location
        visited = set([])
        runningCost = 0

        for request in walk[1:]:
            nextLocation = getRequestLocation(request, request in visited)
            runningCost += currLocation.getDistance(nextLocation, distNorm)
            currLocation = nextLocation
            if request in visited:
                totalServeTime += runningCost
            visited.add(request)

    return totalServeTime


def getMatchingCosts(problemInstance, matching, exact=True, returnOtherCosts=False):

    totalCost = 0.0
    maxCost = 0.0

    walks = []

    if exact:

        for match in matching:

            if type(match[0]) == tuple:
                riderTuple = match[0]
                driver: Driver = match[1]
            else:
                riderTuple = match[1]
                driver: Driver = match[0]

            walk, cost = getRequestGroupWalkCost(riderTuple, driver, distNorm=problemInstance.distNorm)
            assert len(walk) == 1 + 2*problemInstance.driverCapacity

            walks.append(walk)
            totalCost += cost
            maxCost = max(maxCost, cost)

    else:
        walks, costs = getBoundedAssignmentWalks(matching, problemInstance.distNorm)
        maxCost = max(costs)
        totalCost = sum(costs)

    assert len(walks) == problemInstance.nDrivers

    totalServeTime = getTotalRequestServeTime(walks, problemInstance.distNorm)

    if not returnOtherCosts:
        return totalCost
    else:
        return totalCost, maxCost, totalServeTime
