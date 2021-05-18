import PrevPaper.main as prevMain
import OurAlg.main as ourMain
from Main.ProblemInstance import ProblemInstance
from Main.LowerBound import getLowerBoundCost
from Main.Utils import getMatchingCost


def exactRun():
    for generatorType in ["uniform", "gaussian"]:
        print("---------------"+generatorType+"---------------")
        for distNorm in ["l1", "l2"]:

            if generatorType == "uniform":
                for n in [10, 20, 30, 40, 50]:
                    for B in [10, 50, 100]:

                        problemInstance = ProblemInstance((B, B), n, 2*n, 2, distNorm=distNorm)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = prevMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCost(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)

                        print("PrevPaper distNorm: %s| n: %d| B: %d| ratio: %.2f"
                              % (distNorm, n, B, ratio))

                        matching = ourMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCost(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, n, B, 2, ratio))

                        for lamb in [4, 8, 16]:

                            problemInstance = ProblemInstance((B, B), n, lamb*n, lamb, distNorm=distNorm)
                            problemInstance.generateParams(generatorType)

                            lowerBoundCost = getLowerBoundCost(problemInstance)

                            matching = ourMain.runInstance(problemInstance, True)

                            matchingCost = getMatchingCost(problemInstance, matching)
                            ratio = round(matchingCost / lowerBoundCost, 2)
                            print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                                  % (distNorm, n, B, lamb, ratio))

            elif generatorType == "gaussian":
                for nCenters in [1, 5, 10]:
                    for variance in [1, 5, 10]:

                        problemInstance = ProblemInstance((100, 100), 50, 100, 2, distNorm=distNorm)
                        problemInstance.generateParams(generatorType, {"nCenters": 5, "variance": variance})

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = prevMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCost(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("PrevPaper distNorm: %s| nCenters: %d| variance: %d| ratio: %.2f"
                              % (distNorm, nCenters, variance, ratio))

                        matching = ourMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCost(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print(
                            "OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                            % (distNorm, nCenters, 2, variance, ratio))

                        for lamb in [4, 8, 16]:

                            problemInstance = ProblemInstance((100, 100), 50, 50*lamb, lamb, distNorm=distNorm)
                            problemInstance.generateParams(generatorType)

                            lowerBoundCost = getLowerBoundCost(problemInstance)

                            matching = ourMain.runInstance(problemInstance, True)

                            matchingCost = getMatchingCost(problemInstance, matching)
                            ratio = round(matchingCost / lowerBoundCost, 2)
                            print(
                                "OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                                % (distNorm, nCenters, 2, variance, ratio))


def boundedRun():
    for generatorType in ["uniform", "gaussian"]:
        print("---------------"+generatorType+"---------------")
        for distNorm in ["l1", "l2"]:
            B = 100

            if generatorType == "uniform":
                for n in [10, 20, 30, 40, 50]:
                    for lamb in [2, 4, 8, 16]:

                        problemInstance = ProblemInstance((B, B), n, lamb*n, lamb, exact=False, distNorm=distNorm)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = ourMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCost(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, n, B, lamb, ratio))

            elif generatorType == "gaussian":
                nCenters = 5

                for variance in [1, 5, 10]:
                    for lamb in [2, 4, 8, 16]:

                        problemInstance = ProblemInstance((B, B), 50, 50*lamb, lamb, exact=False, distNorm=distNorm)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = ourMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCost(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, nCenters, 2, variance, ratio))


# exactRun()
boundedRun()
