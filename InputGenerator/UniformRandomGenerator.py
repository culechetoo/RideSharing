from InputGenerator.Utils import getUniformRandomLocation
from Main.UtilClasses import Driver, Rider


def uniformGeneration(problemInstance, driverCapacity, inputPrecision):
    for i in range(problemInstance.nDrivers):
        driverLocation = getUniformRandomLocation(*problemInstance.graphDim, inputPrecision)
        problemInstance.drivers.append(Driver(i, driverCapacity, driverLocation))

    for i in range(problemInstance.nRiders):
        riderSourceLocation = getUniformRandomLocation(*problemInstance.graphDim, inputPrecision)
        riderTargetLocation = getUniformRandomLocation(*problemInstance.graphDim, inputPrecision)
        problemInstance.riders.append(Rider(i, riderSourceLocation, riderTargetLocation))
