import math
import random

import numpy as np

from UtilClasses import Location


def getUniformRandomLocation(dimX, dimY, precision=2):
    precisionHelper = math.pow(10, precision)

    driverX = float(random.randrange(0, dimX * precisionHelper)) / precisionHelper
    driverY = float(random.randrange(0, dimY * precisionHelper)) / precisionHelper

    return Location(driverX, driverY)


def getGaussianRandomLocation(center: Location, covariance):
    locationCoordinates: np.ndarray = np.random.multivariate_normal(center.getArray(), covariance)
    return Location(*locationCoordinates.tolist())
