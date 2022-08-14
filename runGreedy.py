import gc
import os
import numpy as np

import baselines.greedyBaseline.main as greedyMain
from hra.cost import getMatchingCosts


def runGreedy(problemInstance, resultDir, labelFile=None, nodeFile=None, useMatchingHeuristic=False):
    index = problemInstance["index"]
    print(index)

    carLocations = problemInstance["carLocations"]
    riderSources = problemInstance["riderSources"]
    riderTargets = problemInstance["riderTargets"]

    labels = None
    if labelFile is not None:
        labels = open(labelFile, 'rb')

    (carSourceDists, interRiderDists), matrixTime = greedyMain.getDistMatrices(carLocations, riderSources, riderTargets,
                                                                            labels, nodeFile, labelFile is not None)
    if labelFile is not None:
        labels.close()

    if labelFile is not None:
        carSourceDists /= 10
        interRiderDists /= 10
    # print("Dist time %f" % matrixTime)

    if carSourceDists is None:
        print("timeout")
        return
    else:
        # print("Dists loaded")
        pass

    matching, algTime = greedyMain.runInstance(carSourceDists, interRiderDists, False, useMatchingHeuristic)
    # print("Alg time %f" % algTime)
    # print(matching)

    if labelFile is not None:
        labels = open(labelFile, 'rb')

    (matchingCost, maxCost, totalServeTime), costTime = getMatchingCosts(matching, carLocations, riderSources,
                                                                         riderTargets, labels, nodeFile,
                                                                         returnOtherCosts=True)
    if labelFile is not None:
        labels.close()

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
        # pool.apply_async(runGreedy, (problemInstance, resultDir, labelFile, nodeFile, useMatchingHeuristic))
        for i in range(nRepetitions):
            # print(i)
            problemInstance["index"] = originalIndex+"(%d)" % i
            runGreedy(problemInstance, resultDir, labelFile, nodeFile, useMatchingHeuristic)


def run(dataSourceDir, resultDir, euclidean, nRepetitions, useMatchingHeuristic=True):

    try:
        os.mkdir(resultDir)
    except FileExistsError:
        pass

    problemInstances = []

    if not euclidean:
        labelFile = os.path.join(dataSourceDir, "plabel.label")
        nodeFile = None
    else:
        labelFile = None
        nodeFile = open(os.path.join(dataSourceDir, "node.node"), 'r')

    problemInstancesDir = os.path.join(dataSourceDir, "problemInstances")

    problemInstanceDirSorted = os.listdir(problemInstancesDir)
    problemInstanceDirSorted.sort(key=lambda l: int(l.split("_")[0]))

    toReach = "5040_6_200_20(1)"
    reached = False

    for index in problemInstanceDirSorted:

        # if index == toReach:
        #     reached = True
        # if not reached:
        #     continue

        problemInstanceDir = os.path.join(problemInstancesDir, index)

        carFile = open(os.path.join(problemInstanceDir, "car.txt"))
        carParams = carFile.readline().split()
        nCars = int(carParams[0])
        carCapacity = int(carParams[1])
        carLocations = np.array(list(map(int, carFile.readlines())))

        riderFile = open(os.path.join(problemInstanceDir, "rider.txt"))
        riderParams = riderFile.readline()
        nRiders = int(riderParams)
        # if int(index) not in list(range(1, 8))+list(range(15, 22))+list(range(36, 43))+list(range(57, 64))+list(range(78, 85)):
        #     continue
        riders = riderFile.readlines()
        riderSources = np.fromiter(map(lambda l: int(l.split()[0]), riders), dtype=int)
        riderTargets = np.fromiter(map(lambda l: int(l.split()[1]), riders), dtype=int)

        assert nCars * carCapacity == nRiders

        problemInstances.append({"carLocations": carLocations, "riderSources": riderSources,
                                 "riderTargets": riderTargets, "index": index})

    batchRunOurAlgo(problemInstances, resultDir, nRepetitions, labelFile, nodeFile, useMatchingHeuristic)