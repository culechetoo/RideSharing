import os
import numpy as np
import pickle
import time
from itertools import combinations, product

from scipy.spatial.distance import cdist, pdist, squareform

from hra.cost import getMatchingCosts, getCosts

from baselines.greedyBaseline.greedyBaseline import run as greedyRun


def timeoutHandler(signum, frame):
    raise Exception("Timed out function")


def loadDistMatrices(carLocations, riderSources, riderTargets, labels):

    carSourceDists = getCosts(product(carLocations, riderSources), labels).reshape(len(carLocations), len(riderSources))
    print("Car Done")
    interRiderDists = getCosts(combinations(np.hstack([riderSources, riderTargets]), 2), labels)
    print("Riders Done")

    return carSourceDists, interRiderDists


def getDistMatrices(carLocations, riderSources, riderTargets, labelFile=None, nodeFile=None, labels=False, timeout=0):

    if labels:
        assert labelFile is not None

        labelFile.seek(0)
        labels = pickle.load(labelFile)

        # print("loaded labels")

        currTime = time.time()

        locations = list(set(carLocations).union(riderSources).union(riderTargets))
        loc2IndexMap = {locations[i]: i for i in range(len(locations))}

        nRiders = len(riderSources)
        nCars = len(carLocations)

        if len(locations)**2 < (2*nRiders)**2 + nRiders*nCars:
            dists = squareform(getCosts(combinations(locations, 2), labels))
            carIndex = [loc2IndexMap[carLoc] for carLoc in carLocations]
            riderSourceIndex = [loc2IndexMap[riderLoc] for riderLoc in riderSources]
            riderIndex = [loc2IndexMap[riderLoc] for riderLoc in np.hstack([riderSources, riderTargets])]
            carSourceDists = dists[carIndex, :][:, riderSourceIndex]
            interRiderDists = dists[riderIndex, :][:, riderIndex]
        else:
            carSourceDists, interRiderDists = loadDistMatrices(carLocations, riderSources, riderTargets, labels)
            interRiderDists = squareform(interRiderDists)

        del labels

        return (carSourceDists, interRiderDists), time.time()-currTime

    else:
        assert nodeFile is not None

        nodeFile.seek(0)

        nodes = np.array(list(map(lambda l: list(map(lambda i: float(i), l.split())), nodeFile.readlines()[1:])))
        carLocations = nodes[carLocations, :]
        riderLocations = nodes[np.concatenate([riderSources, riderTargets]), :]

        currTime = time.time()

        carSourceDists = cdist(carLocations, nodes[riderSources])
        interRiderDists = squareform(pdist(riderLocations))

        return (carSourceDists, interRiderDists), time.time()-currTime


def runInstance(carSourceDists, interRiderDists, showRunTime=False, useMatchingHeuristic=False):

    currTime = time.time()
    matching = greedyRun(carSourceDists, interRiderDists, showRunTime, useMatchingHeuristic)
    runTime = time.time()-currTime

    if showRunTime:
        print("Algorithm run in %f s" % runTime)

    return matching, runTime


if __name__ == '__main__':
    dataSourceDir = "data/randomChengdu"
    try:
        labelFile = open(os.path.join(dataSourceDir, "plabel.label"), 'rb')
        nodeFile = None
    except FileNotFoundError:
        labelFile = None
        nodeFile = open(os.path.join(dataSourceDir, "node.node"), 'r')

    for problemInstanceIndex in range(1, 29):
        problemInstanceDir = os.path.join(dataSourceDir, str(problemInstanceIndex))
        carFile = open(os.path.join(problemInstanceDir, "car.txt"))
        params = carFile.readline().split()
        nCars = int(params[0])
        carCapacity = int(params[1])
        carLocations = np.array(list(map(int, carFile.readlines())))

        riderFile = open(os.path.join(problemInstanceDir, "rider.txt"))
        riders = riderFile.readlines()[1:]
        riderSources = np.fromiter(map(lambda l: int(l.split()[0]), riders), dtype=int)
        riderTargets = np.fromiter(map(lambda l: int(l.split()[1]), riders), dtype=int)

        assert len(carLocations)*carCapacity == len(riders)

        (carSourceDists, interRiderDists), _ = getDistMatrices(carLocations, riderSources, riderTargets, labelFile=labelFile,
                                                               nodeFile=nodeFile, labels=labelFile is not None)

        matching, _ = runInstance(carSourceDists, interRiderDists, True, useMatchingHeuristic=True)

        print(getMatchingCosts(matching, carLocations, riderSources, riderTargets, labelFile, nodeFile, calcPath=True))