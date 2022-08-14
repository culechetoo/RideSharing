import os
import shutil

import numpy as np


def genData(args):

    problemInstanceDir = "data/random/problemInstances"

    try:
        shutil.rmtree(problemInstanceDir)
    except FileNotFoundError:
        pass
    os.mkdir(problemInstanceDir)

    gridSize = args.gridSize
    nRepetitions = args.nRepetitions

    variances = args.variances
    numCenters = args.numCenters
    nRiders = args.numRiders
    carCapacities = args.carCapacities

    fixedVariance = args.fixedVariance
    fixedCarCapacity = args.fixedCarCapacity
    fixedRiders = args.fixedRiders
    fixedNCenters = args.fixedNumCenters

    nodes = np.random.uniform(0.0, gridSize, size=(1, 2))

    def generateInstance(nRequests, carCap, nCenters, variance, nodes):
        currNodes = nodes.shape[0]

        done = False

        instanceNumber = 1
        config = "%d_%d_%d_%d(%d)" % (nRequests, carCap, nCenters, variance, instanceNumber)
        while not done and instanceNumber <= nRepetitions:

            try:
                os.mkdir(problemInstanceDir+"/"+config)
                done = True
            except FileExistsError:
                instanceNumber += 1
            config = "%d_%d_%d_%d(%d)" % (nRequests, carCap, nCenters, variance, instanceNumber)

        if instanceNumber > nRepetitions:
            return nodes

        nCars = nRequests // carCap
        requiredPoints = 2 * nRequests + nCars

        covMatrix = np.zeros((requiredPoints, requiredPoints))
        np.fill_diagonal(covMatrix, variance)
        xCenters = np.random.uniform(0.0, gridSize, size=int(nCenters * requiredPoints))
        sampledXCenters = np.random.choice(xCenters, size=requiredPoints)

        pointsX = []
        for sampledXCenter in sampledXCenters:
            pointsX.append(np.random.normal(sampledXCenter, variance))

        yCenters = np.random.uniform(0.0, gridSize, size=int(nCenters * requiredPoints))
        sampledYCenters = np.random.choice(yCenters, size=requiredPoints)

        np.fill_diagonal(covMatrix, variance)

        pointsY = []
        for sampledYCenter in sampledYCenters:
            pointsY.append(np.random.normal(sampledYCenter, variance))

        nodes = np.concatenate([nodes, np.stack([pointsX, pointsY], axis=1)])

        carLocations = [str(i) for i in range(currNodes, currNodes+nCars)]
        riders = [str(i)+" "+str(i+nRequests) for i in range(currNodes+nCars, currNodes+nCars+nRequests)]

        carFile = open(os.path.join(problemInstanceDir, config, "car.txt"), 'w')
        carFile.write(str(nCars)+" "+str(carCap)+"\n")
        carFile.write('\n'.join(carLocations)+"\n")

        riderFile = open(os.path.join(problemInstanceDir, config, "rider.txt"), 'w')
        riderFile.write(str(len(riders)) + "\n")
        riderFile.write('\n'.join(riders) + '\n')

        print(config)

        return nodes

    for _ in range(nRepetitions):
        # vary number of requests
        for numRiders in nRiders:
            nodes = generateInstance(numRiders, fixedCarCapacity, fixedNCenters, fixedVariance, nodes)

        # vary car capacity
        for carCapacity in carCapacities:
            nodes = generateInstance(fixedRiders, carCapacity, fixedNCenters, fixedVariance, nodes)

        # vary number of centers
        for centers in numCenters:
            nodes = generateInstance(fixedRiders, fixedCarCapacity, centers, fixedVariance, nodes)

        # vary gamma
        for gamma in variances:
            nodes = generateInstance(fixedRiders, fixedCarCapacity, fixedNCenters, gamma, nodes)

    nodes = list(map(lambda l: "%f %f\n" % (l[0], l[1]), nodes))
    nodeFile = open("data/random/node.node", 'w')
    nodeFile.write("%d\n" % len(nodes))
    nodeFile.writelines(nodes)
    nodeFile.close()


if __name__ == '__main__':
    genData()
