import gc
import os

import numpy as np

import hra.main as algMain
from hra.cost import getMatchingCosts


def runOurAlgo(problemInstance, resultDir, labelFile=None, nodeFile=None, useMatchingHeuristic=False):
    index = problemInstance["index"]
    print(index)

    carLocations = problemInstance["carLocations"]
    riderSources = problemInstance["riderSources"]
    riderTargets = problemInstance["riderTargets"]

    (carSourceDists, interSourceDists, interTargetDists), matrixTime = algMain.getDistMatrices(carLocations,
                                                riderSources, riderTargets, labelFile, nodeFile, labelFile is not None)
    # print("Dist time %f" % matrixTime)

    if carSourceDists is None:
        print("timeout")
        return
    else:
        # print("Dists loaded")
        pass

    matching, algTime = algMain.runInstance(carSourceDists, interSourceDists, interTargetDists, False, useMatchingHeuristic)
    # print("Algorithm time %f" % algTime)
    # print(matching)

    (matchingCost, maxCost, totalServeTime), costTime = getMatchingCosts(matching, carLocations, riderSources,
                                                                         riderTargets, labelFile, nodeFile,
                                                                         returnOtherCosts=True)
    # print("Cost time %f" % costTime)
    runTime = matrixTime+algTime+costTime
    outFile = os.path.join(resultDir, "%s.txt" % index)
    with open(outFile, "w") as fout:
        fout.write(str(matchingCost)+"\n")
        fout.write(str(maxCost)+"\n")
        fout.write(str(totalServeTime)+"\n")
        fout.write(str(runTime)+"\n")

    # print(index)


def batchRunOurAlgo(problemInstances, resultDir, nRepetitions, labelFile=None, nodeFile=None, useMatchingHeuristic=False):

    for index in range(len(problemInstances)):
        gc.collect()
        problemInstance = problemInstances[index]
        originalIndex = problemInstance["index"]
        for i in range(nRepetitions):
            # print(i)
            problemInstance["index"] = originalIndex + "(%d)" % i
            runOurAlgo(problemInstance, resultDir, labelFile, nodeFile, useMatchingHeuristic)


def run(dataSourceDir, resultDir, euclidean, nRepetitions, useMatchingHeuristic=True):

    try:
        os.mkdir(resultDir)
    except FileExistsError:
        pass

    problemInstances = []

    if not euclidean:
        labelFile = open(os.path.join(dataSourceDir, "plabel.label"), 'rb')
        nodeFile = None
    else:
        labelFile = None
        nodeFile = open(os.path.join(dataSourceDir, "node.node"), 'r')

    # toReach = 7
    # reached = False

    problemInstancesDir = os.path.join(dataSourceDir, "problemInstances")

    problemInstanceDirSorted = os.listdir(problemInstancesDir)
    problemInstanceDirSorted.sort(key=lambda l: int(l.split("_")[0]))

    for index in problemInstanceDirSorted:

        problemInstanceDir = os.path.join(problemInstancesDir, index)

        # if int(index) == toReach:
        #     reached = True

        # if not reached:
        #     continue

        # if "5040" not in index:
        #     continue

        carFile = open(os.path.join(problemInstanceDir, "car.txt"))
        carParams = carFile.readline().split()
        nCars = int(carParams[0])
        carCapacity = int(carParams[1])
        carLocations = np.array(list(map(int, carFile.readlines())))

        riderFile = open(os.path.join(problemInstanceDir, "rider.txt"))
        riderParams = riderFile.readline()
        nRiders = int(riderParams)
        riders = riderFile.readlines()
        riderSources = np.fromiter(map(lambda l: int(l.split()[0]), riders), dtype=int)
        riderTargets = np.fromiter(map(lambda l: int(l.split()[1]), riders), dtype=int)

        assert nCars * carCapacity == nRiders

        problemInstances.append({"carLocations": carLocations, "riderSources": riderSources,
                                 "riderTargets": riderTargets, "index": index})

    batchRunOurAlgo(problemInstances, resultDir, nRepetitions, labelFile, nodeFile, useMatchingHeuristic)
