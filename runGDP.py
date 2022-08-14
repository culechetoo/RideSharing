import os
import shutil
import subprocess

tempDir = "temp/GDP"


def createGDPInputFiles(dataSourceDir):

    for index in os.listdir(dataSourceDir):
        problemInstanceDir = os.path.join(dataSourceDir, index)

        carFile = open(os.path.join(problemInstanceDir, "car.txt"), 'r')
        carParams = carFile.readline().split()
        nCars = int(carParams[0])
        carCapacity = int(carParams[1])
        carLocations = list(map(lambda s: s.strip()+" "+str(carCapacity), carFile.readlines()))

        riderFile = open(os.path.join(problemInstanceDir, "rider.txt"), 'r')
        riderParams = riderFile.readline()
        nRiders = int(riderParams)
        riderLocations = list(map(lambda s: str(0)+" "+s.strip()+" "+str(1), riderFile.readlines()))

        fileDir = os.path.join(tempDir, index)
        os.mkdir(fileDir)
        newCarFile = open(os.path.join(fileDir, "taxi.txt"), 'w')
        newCarFile.write("%d %d %d %d\n" % (nCars, carCapacity, 10000, 1))
        newCarFile.write("\n".join(carLocations))
        newCarFile.write("\n%d %d\n" % (125000, 100000))

        newRiderFile = open(os.path.join(fileDir, "order.txt"), 'w')
        newRiderFile.write("%d\n" % nRiders)
        newRiderFile.write("\n".join(riderLocations))
        newRiderFile.write("\n")


def runGDP(execName, carFile, riderFile, nodeFile, edgeFile, labelFile, orderFile, outFile):
    cmdLine = "./%s %s %s %s %s %s %s" % (execName, nodeFile, edgeFile, labelFile,
                                           orderFile, carFile, riderFile)
    cmdLine = cmdLine.split(" ")
    # print(cmdLine)
    result = subprocess.run(cmdLine, capture_output=True).stdout.decode('utf-8')
    # print(result)
    result = result.split("\n")[1:]
    rate = float(result[4])
    if rate != 1:
        raise Exception("Re run for %s" % carFile)

    result = "\n".join(result[:4])
    with open(outFile, 'w') as fout:
        fout.write(result+"\n")


def batchRunGDP(execName, nodeFile, edgeFile, labelFile, orderFile, resultDir, nRepetitions):

    reached = False
    toReach = "2640_8(1)"

    for index in sorted(os.listdir(tempDir)):

        # if int(index) not in list(range(1, 8))+list(range(15, 22))+list(range(36, 43))+list(range(57, 64))+list(range(78, 85)):
        #     continue

        # if index == toReach:
        #     reached = True
        
        # if not reached:
        #     continue

        carFile = os.path.join(tempDir, "%s/taxi.txt" % index)
        riderFile = os.path.join(tempDir, "%s/order.txt" % index)
        for i in range(nRepetitions):
            print(index+"("+str(i)+")")
            resultFile = os.path.join(resultDir, "%s(%d).txt" % (index, i))

            runGDP(execName, carFile, riderFile, nodeFile, edgeFile, labelFile, orderFile, resultFile)


def run(execName, dataSourceDir, resultDir, nRepetitions):

    try:
        os.mkdir(resultDir)
    except FileExistsError:
        pass

    try:
        os.mkdir(tempDir)
    except FileExistsError:
        shutil.rmtree(tempDir)
        os.mkdir(tempDir)

    createGDPInputFiles(os.path.join(dataSourceDir, "problemInstances"))

    nodeFile = os.path.join(dataSourceDir, "node.node")
    edgeFile = os.path.join(dataSourceDir, "edge.edge")
    labelFile = os.path.join(dataSourceDir, "label.label")
    orderFile = os.path.join(dataSourceDir, "order.order")

    batchRunGDP(execName, nodeFile, edgeFile, labelFile, orderFile, resultDir, nRepetitions)

    shutil.rmtree(tempDir)
