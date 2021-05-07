from ProblemInstance import ProblemInstance
from PrevPaper import Algorithm, LowerBound

import time


def runInstance(problem, showRunTime=False):
    currTime = time.time()

    matching = Algorithm.run(problem)
    if showRunTime:
        print("Algorithm run in %f s" % (time.time() - currTime))
    currTime = time.time()

    matchingCost = Algorithm.getMatchingCost(problem, matching)

    lowerBoundCost = LowerBound.getLowerBoundCost(problem)
    if showRunTime:
        print("Lower Bound cost calculated in %f s" % (time.time() - currTime))

    return round(matchingCost / lowerBoundCost, 2)


for generatorType in ["uniform", "gaussian"]:
    print("---------------"+generatorType+"---------------")
    for distNorm in ["l1", "l2"]:
        problemInstance = None

        if generatorType == "uniform":
            for n in [10, 20, 30, 40, 50]:
                for B in [10, 50, 100]:

                    problemInstance = ProblemInstance((B, B), n, 2*n, 2, distNorm)
                    problemInstance.generateParams(generatorType)

                    ratio = runInstance(problemInstance)

                    print("distNorm: %s| n: %d| B: %d| ratio: %.2f" % (distNorm, n, B, ratio))

        elif generatorType == "gaussian":
            for nCenters in [1, 5, 10]:
                for variance in [1, 5, 10]:

                    problemInstance = ProblemInstance((100, 100), 50, 100, 2, distNorm)
                    problemInstance.generateParams(generatorType, {"nCenters": 5, "variance": variance})

                    ratio = runInstance(problemInstance)

                    print("distNorm: %s| nCenters: %d| variance: %d| ratio: %.2f" % (distNorm, nCenters, variance,
                                                                                     ratio))
