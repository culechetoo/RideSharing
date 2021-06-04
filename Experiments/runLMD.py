import multiprocessing
import random
import shutil
import subprocess

import os

algoDir = "../../ridesharing-LMD/algorithm"
tempDir = "temp"
resultDir = "results"


def convertToLMDInput(problemInstance):

    locations = []
    drivers = []
    riders = []

    for driver in problemInstance.drivers:
        drivers.append("%d %d\n" % (len(locations), problemInstance.driverCapacity))
        locations.append("%d %d\n" % (driver.location.x, driver.location.y))

    for rider in problemInstance.riders:
        riders.append("%d %d %d\n" % (len(locations), len(locations)+1, 1))
        locations.append("%d %d\n" % (rider.sourceLocation.x, rider.sourceLocation.y))
        locations.append("%d %d\n" % (rider.targetLocation.x, rider.targetLocation.y))

    return locations, drivers, riders


def writeLMDInputFiles(problemInstances):

    dataId = 1
    for problemInstance in problemInstances:
        locations, drivers, riders = convertToLMDInput(problemInstance)

        f = open(os.path.join(tempDir, "loc_%02d.txt" % dataId), 'w')
        f.write("%d\n" % len(locations))
        f.writelines(locations)
        f.close()

        f = open(os.path.join(tempDir, "data_%02d.txt" % dataId), 'w')
        f.write("%d %d\n" % (len(drivers), len(riders)))
        f.writelines(drivers)
        f.writelines(riders)
        f.close()

        dataId += 1


def runHST(execName, locFile, dataFile):
    cmdLine = "./%s %s %s" % (execName, locFile, dataFile)
    cmdLine = cmdLine.split(" ")
    print(cmdLine)
    subprocess.run(cmdLine, capture_output=True)


def batchRunHST(nProcess):

    pool = multiprocessing.Pool(processes=nProcess)

    for locFile in os.listdir(tempDir):

        if "data" in locFile:
            continue

        srcFileName = os.path.join(tempDir, locFile)
        hstDir = os.path.join(tempDir, locFile.split(".")[0])

        os.mkdir(hstDir)

        pool.apply_async(runHST, (os.path.join(algoDir, "chst"), srcFileName, hstDir))

    pool.close()
    pool.join()


def getDataFiles():

    files = []

    for i in range(len(os.listdir(tempDir))//3):
        locFile = os.path.join(tempDir, "loc_%02d.txt" % (i+1))
        dataFile = os.path.join(tempDir, "data_%02d.txt" % (i+1))

        hstDir = locFile.split(".")[0]
        hstSampleIndex = random.randint(0, 9)
        hstFile = os.path.join(hstDir, ("hst_%02d.txt" % hstSampleIndex))

        files.append((locFile, dataFile, hstFile))

    return files


def runLMD(execName, locFile, hstFile, dataFile, outFile):
    cmdLine = "./%s %s %s %s" % (execName, locFile, dataFile, hstFile)
    cmdLine = cmdLine.split(" ")
    print(cmdLine)
    result = subprocess.run(cmdLine, capture_output=True).stdout.decode('utf-8').split(" ")
    with open(outFile, "w") as fout:
        fout.write(str(result[3])+"\n")
        fout.write(str(result[4])+"\n")
        fout.write(str(result[1])+"\n")
        fout.write(str(result[-3]))


def batchRunLMD(nProcess):

    files = getDataFiles()

    pool = multiprocessing.Pool(processes=nProcess)

    for locFile, dataFile, hstFile in files:

        outFile = os.path.join(resultDir, "lmd_"+dataFile[dataFile.index("_")+1: dataFile.index(".")]+".txt")

        pool.apply_async(runLMD, (os.path.join(algoDir, "fesif"), locFile, hstFile, dataFile, outFile))

    pool.close()
    pool.join()


def run(problemInstances, nProcess):

    try:
        os.mkdir(tempDir)
    except FileExistsError:
        shutil.rmtree(tempDir)
        os.mkdir(tempDir)

    writeLMDInputFiles(problemInstances)
    batchRunHST(nProcess)
    batchRunLMD(nProcess)
