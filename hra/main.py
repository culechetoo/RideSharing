import os
import pickle
import signal
import time
from itertools import combinations, product

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform

from hra.ExactLambdaAlgorithm import run as exactRun
from hra.cost import getMatchingCosts, getCosts

from h5py import File


def timeoutHandler(signum, frame):
    raise Exception("Timed out function")


def loadLabels(labelFile):

    labelFile.seek(0)
    labels = pickle.load(labelFile)

    # hubs = labelFile["hubs"][:]
    # dists = labelFile["dists"][:]
    #
    # labels = np.stack((hubs, dists), axis=2)

    return labels


def getDistMatrices(carLocations, riderSources, riderTargets, labelFile=None, nodeFile=None, labels=False, timeout=0):

    if labels:
        assert labelFile is not None

        labels = loadLabels(labelFile)

        # print("loaded labels")

        signal.signal(signal.SIGALRM, timeoutHandler)
        signal.alarm(timeout)

        currTime = time.time()

        locations = list(set(carLocations).union(riderSources).union(riderTargets))
        loc2IndexMap = {locations[i]: i for i in range(len(locations))}

        nRiders = len(riderSources)
        nCars = len(carLocations)

        if len(locations)**2 < 2*(nRiders**2) + nRiders*nCars:
            dists = squareform(getCosts(combinations(locations, 2), labels))
            carIndex = [loc2IndexMap[carLoc] for carLoc in carLocations]
            riderSourceIndex = [loc2IndexMap[sourceLoc] for sourceLoc in riderSources]
            riderTargetIndex = [loc2IndexMap[targetLoc] for targetLoc in riderTargets]
            carSourceDists = dists[carIndex, :][:, riderSourceIndex]
            interSourceDists = dists[riderSourceIndex, :][:, riderSourceIndex]
            interTargetDists = dists[riderTargetIndex, :][:, riderTargetIndex]
        else:
            carSourceDists, interSourceDists, interTargetDists = loadDistMatrices(carLocations, riderSources,
                                                                                  riderTargets, labels)
            interSourceDists = squareform(interSourceDists)
            interTargetDists = squareform(interTargetDists)

        return (carSourceDists, interSourceDists, interTargetDists), time.time()-currTime

    else:
        assert nodeFile is not None

        nodeFile.seek(0)

        nodes = np.array(list(map(lambda l: list(map(lambda i: float(i), l.split())), nodeFile.readlines()[1:])))
        carLocations = nodes[carLocations, :]
        riderSources = nodes[riderSources, :]
        riderTargets = nodes[riderTargets, :]

        currTime = time.time()

        carSourceDists = cdist(carLocations, riderSources)
        interSourceDists = squareform(pdist(riderSources))
        interTargetDists = squareform(pdist(riderTargets))

        return (carSourceDists, interSourceDists, interTargetDists), time.time()-currTime


def loadDistMatrices(carLocations, riderSources, riderTargets, labels):

    carSourceDists = getCosts(product(carLocations, riderSources), labels).reshape(len(carLocations), len(riderSources))
    # print("Car Done")
    interSourceDists = getCosts(combinations(riderSources, 2), labels)
    # print("Source Done")
    interTargetDists = getCosts(combinations(riderTargets, 2), labels)
    # print("Target Done")

    return carSourceDists, interSourceDists, interTargetDists


def runInstance(carSourceDists, interSourceDists, interTargetDists, showRunTime=False, useMatchingHeuristic=False):

    # hubs = labelFile["hubs"][:]
    # dists = labelFile["dists"][:]
    #
    # labels = np.stack((hubs, dists), axis=2)

    # if labelFile is None:

    currTime = time.time()

    matching = exactRun(carSourceDists, interSourceDists, interTargetDists, showRunTime, useMatchingHeuristic)
    runTime = time.time()-currTime

    if showRunTime:
        print("Algorithm run in %f s" % runTime)

    return matching, runTime


if __name__ == '__main__':
    dataSourceDir = "data/nyc"
    euclidean = True
    if not euclidean:
        labelFile = open(os.path.join(dataSourceDir, "plabel.label"), 'rb')
        # labelFile = File(os.path.join(dataSourceDir, "labels.h5"), 'r')
        nodeFile = None
    else:
        labelFile = None
        nodeFile = open(os.path.join(dataSourceDir, "node.node"), 'r')

    for problemInstanceIndex in range(22, 23):
        problemInstanceDir = os.path.join(dataSourceDir, str(problemInstanceIndex))
        carFile = open(os.path.join(problemInstanceDir, "car.txt"))
        params = carFile.readline().split()
        nCars = int(params[0])
        carCapacity = int(params[1])
        # if carCapacity < 7:
        #     continue
        carLocations = np.array(list(map(int, carFile.readlines())))

        riderFile = open(os.path.join(problemInstanceDir, "rider.txt"))
        riders = riderFile.readlines()[1:]
        riderSources = np.fromiter(map(lambda l: int(l.split()[0]), riders), dtype=int)
        riderTargets = np.fromiter(map(lambda l: int(l.split()[1]), riders), dtype=int)

        assert len(carLocations)*carCapacity == len(riders)

        (carSourceDists, interSourceDists, interTargetDists), distTime = getDistMatrices(carLocations, riderSources, riderTargets,
                                                                                  labelFile=labelFile, nodeFile=nodeFile,
                                                                                  labels=labelFile is not None)

        print(distTime)

        matching, algoTime = runInstance(carSourceDists, interSourceDists, interTargetDists, True, useMatchingHeuristic=True)

        costs, costsTime = getMatchingCosts(matching, carLocations, riderSources, riderTargets, labelFile, nodeFile, returnOtherCosts=True)

        print(costs)
        print(distTime, algoTime, costsTime)


# problemInstanceFile = h5py.File("data/generatedProblemInstances/20/problemInstance.h5", 'r')
# carLocations = problemInstanceFile["carLocations"][:]
# riderSources = problemInstanceFile["riderSources"][:]
# riderTargets = problemInstanceFile["riderTargets"][:]
# carCapacity = int(problemInstanceFile["carCapacity"][:][0])
# pool = multiprocessing.Pool(processes=1)
# pool.apply_async(runInstance, (problemInstance, True, True, True))
# pool.close()
# pool.join()

