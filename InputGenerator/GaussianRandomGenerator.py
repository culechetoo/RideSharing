import random
from typing import List

from InputGenerator.Utils import getUniformRandomLocation, getGaussianRandomLocation
from Main.UtilClasses import Location, Driver, Rider


def gaussianMixtureGeneration(problemInstance, generatorArgs, driverCapacity, inputPrecision=2):

    nCenters = generatorArgs["nCenters"]
    variance = generatorArgs["variance"]

    covarianceMatrix = [[variance, 0], [0, variance]]

    centers: List[Location] = []

    for i in range(nCenters):
        centerLocation = getUniformRandomLocation(*problemInstance.graphDim, inputPrecision)
        centers.append(centerLocation)

    for i in range(problemInstance.nDrivers):
        randomCenter = random.choice(centers)
        driverLocation = getGaussianRandomLocation(randomCenter, covarianceMatrix)
        problemInstance.drivers.append(Driver(i, driverCapacity, driverLocation))

    for i in range(problemInstance.nRiders):
        randomCenter = random.choice(centers)
        riderSourceLocation = getGaussianRandomLocation(randomCenter, covarianceMatrix)
        randomCenter = random.choice(centers)
        riderTargetLocation = getGaussianRandomLocation(randomCenter, covarianceMatrix)
        problemInstance.riders.append(Rider(i, riderSourceLocation, riderTargetLocation))
