import os
import pickle
import random
import shutil
import subprocess
import time
from itertools import combinations
import gc

import numpy as np

from hra.cost import getCosts

tempDir = "temp/LMD"
hstDir = "temp/LMD_HSTS"


def createLMDInputFiles(dataSourceDir, index, nodeFile, euclidean=True, labelFile=None):
    fileDir = os.path.join(tempDir, index)
    try:
        os.mkdir(fileDir)
    except FileExistsError:
        return

    nodeFile.seek(0)
    nodeFile.readline()
    nodes = np.array(nodeFile.readlines())

    problemInstanceDir = os.path.join(dataSourceDir, index)

    locations = set([])

    carFile = open(os.path.join(problemInstanceDir, "car.txt"), 'r')
    carParams = carFile.readline().split()
    nCars = int(carParams[0])
    carCapacity = int(carParams[1])
    carFileLines = carFile.readlines()
    carLocations = list(map(int, carFileLines))
    locations = locations.union(carLocations)

    riderFile = open(os.path.join(problemInstanceDir, "rider.txt"), 'r')
    riderParams = riderFile.readline()
    nRiders = int(riderParams)
    riderLocations = list(map(lambda s: s.strip() + " " + str(1), riderFile.readlines()))

    origins = list(map(lambda l: int(l.split()[0]), riderLocations))
    destinations = list(map(lambda l: int(l.split()[1]), riderLocations))
    locations = locations.union(origins)
    locations = locations.union(destinations)
    locations = list(locations)

    loc2Index = {locations[i]: i for i in range(len(locations))}
    carLocations = [loc2Index[i] for i in carLocations]
    origins = [loc2Index[i] for i in origins]
    destinations = [loc2Index[i] for i in destinations]

    carLocations = ["%d %d\n" % (i, carCapacity) for i in carLocations]
    riderLocations = ["%d %d 1\n" % (origins[i], destinations[i]) for i in range(len(origins))]

    newDataFile = open(os.path.join(fileDir, "data.txt"), 'w')
    newDataFile.write("%d %d\n" % (nCars, nRiders))
    newDataFile.write("".join(carLocations))
    newDataFile.write("".join(riderLocations)+"\n")
    newDataFile.close()

    newLocFile = open(os.path.join(fileDir, "loc.txt"), 'w')
    newLocFile.write("%d\n" % len(locations))
    locationNodes = list(nodes[locations])
    newLocFile.writelines(locationNodes)
    newLocFile.close()

    # write edge file
    if not euclidean:
        labelFile.seek(0)
        labels = pickle.load(labelFile)
        startTime = time.time()
        distMatrix = getCosts(combinations(locations, 2), labels)
        computeTime = time.time()-startTime
        newEdgeFile = open(os.path.join(fileDir, "edge.txt"), 'w')
        newEdgeFile.write("%d\n" % len(distMatrix))
        np.savetxt(newEdgeFile, distMatrix, newline='\n', fmt="%.4f")
        newEdgeFile.write("%f" % computeTime)
        newEdgeFile.close()


def runHST(execName, locFile, edgeFile=None):
    # try:
    #     os.mkdir(hstDir)
    # except FileExistsError:
    #     shutil.rmtree(hstDir)
    #     os.mkdir(hstDir)

    computeTime = 0
    if edgeFile is None:
        assert "Euclidean" in execName
        cmdLine = "./%s %s %s" % (execName, locFile, hstDir)
    else:
        assert "Euclidean" not in execName
        computeTime = float(open(edgeFile, 'r').readlines()[-1])
        cmdLine = "./%s %s %s %s" % (execName, locFile, edgeFile, hstDir)
    cmdLine = cmdLine.split(" ")
    # print(cmdLine)
    subprocess.run(cmdLine, capture_output=True)
    return computeTime


def runLMD(execDir, dataFile, locFile, outFile, edgeFile=None):

    result = []

    while len(result) < 2:
        totalComputeTime = 0
        totalComputeTime += runHST(execDir+"/chst", locFile, edgeFile)
        # print("Dist time %f" % totalComputeTime)

        hstSampleIndex = random.randint(0, 9)
        hstFile = os.path.join(hstDir, ("hst_%02d.txt" % hstSampleIndex))
        hstTimeLine = open(hstFile).readlines()[-1]
        assert "CHST" in hstTimeLine
        hstTime = float(hstTimeLine.split()[1])
        # print("Hst time %f" % hstTime)
        totalComputeTime += hstTime

        if edgeFile is not None:    
            cmdLine = "./%s %s %s %s %s" % (execDir+"/fesif", locFile, edgeFile, dataFile, hstFile)
        else:
            cmdLine = "./%s %s %s %s" % (execDir+"/fesif", locFile, dataFile, hstFile)
        cmdLine = cmdLine.split(" ")
        # print(cmdLine)
        result = subprocess.run(cmdLine, capture_output=True).stdout.decode('utf-8').split(" ")
        # print(result)
    totalServeTime, maxDist, totalDist, minCap, maxCap, runTime = result[1], result[2], result[3], int(result[5]), int(result[6]), float(result[7])
    assert minCap == maxCap
    with open(outFile, "w") as fout:
        fout.write(totalDist + "\n")
        fout.write(maxDist + "\n")
        fout.write(totalServeTime + "\n")
        fout.write(str(totalComputeTime+runTime) + "\n")


def batchRunLMD(execDir, dataSourceDir, resultDir, euclidean, nRepetitions):
    nodeFile = open(os.path.join(dataSourceDir, "node.node"), 'r')

    edgeFile = None

    reached = False
    toReach = "7560_4(3)"

    problemInstanceDir = os.path.join(dataSourceDir, "problemInstances")
    labelFile = None
    if not euclidean:
        labelFile = open(os.path.join(dataSourceDir, "plabel.label"), 'rb')

    problemInstanceDirSorted = os.listdir(problemInstanceDir)
    problemInstanceDirSorted.sort(key=lambda l: int(l.split("_")[0]))

    for index in problemInstanceDirSorted:

        # if int(index) not in list(range(1, 8))+list(range(15, 22))+list(range(36, 43))+list(range(57, 64))+list(range(78, 85)):
        #     continue

        # if index == toReach:
        #     reached = True
        
        # if not reached:
        #     continue

        # if int(index) in [78]:
        #     continue

        # print(index)
        gc.collect()

        createLMDInputFiles(problemInstanceDir, index, nodeFile, euclidean, labelFile)

        dataFile = os.path.join(tempDir, "%s/data.txt" % index)
        locFile = os.path.join(tempDir, "%s/loc.txt" % index)
        if not euclidean:
            edgeFile = os.path.join(tempDir, "%s/edge.txt" % index)

        # pool.apply_async(runLMD, (os.path.join(algoDir, "fesif"), locFile, hstFile, dataFile, outFile))
        for i in range(nRepetitions):
            print(index+"("+str(i)+")")
            # print(i)
            outFile = os.path.join(resultDir, "%s(%d).txt" % (index, i))
            runLMD(execDir, dataFile, locFile, outFile, edgeFile)
        shutil.rmtree(os.path.join(tempDir, index))
        # print(index)


def run(execDir, dataSourceDir, resultDir, euclidean, nRepetitions):

    try:
        os.mkdir(resultDir)
    except FileExistsError:
        pass

    global hstDir

    try:
        os.mkdir(tempDir)
    except FileExistsError:
        shutil.rmtree(tempDir)
        os.mkdir(tempDir)

    batchRunLMD(execDir, dataSourceDir, resultDir, euclidean, nRepetitions)

    shutil.rmtree(tempDir)
