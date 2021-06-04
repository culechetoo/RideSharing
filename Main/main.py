import PrevPaper.main as prevMain
import OurAlg.main as ourMain
from Main.ProblemInstance import ProblemInstance
from Main.LowerBound import getLowerBoundCost
from Main.Utils import getMatchingCosts
import pickle


def generateProblemInstances():
    it = 1

    for generatorType in ["uniform", "gaussian"]:
        print("---------------" + generatorType + "---------------")
        inputPrecision = 0

        for distNorm in ["l2"]:

            if generatorType == "uniform":
                for n in [50, 100, 200, 400, 1000]:
                    for B in [500]:
                        for lamb in [2, 4, 8]:
                            problemInstance = ProblemInstance((B, B), n, lamb * n, lamb, distNorm=distNorm,
                                                              inputPrecision=inputPrecision)
                            problemInstance.generateParams(generatorType)
                            pickle.dump(problemInstance, open("../data/problemInstance/%d.pkl" % it, "wb"))
                            it += 1

            elif generatorType == "gaussian":
                for nCenters in [20]:
                    for variance in [1, 5, 10]:
                        for lamb in [2, 4, 8]:
                            problemInstance = ProblemInstance((500, 500), 50, 50 * lamb, lamb, distNorm=distNorm,
                                                              inputPrecision=inputPrecision)
                            problemInstance.generateParams(generatorType, {"nCenters": nCenters, "variance": variance})
                            pickle.dump(problemInstance, open("../data/problemInstance/%d.pkl" % it, "wb"))
                            it += 1


def exactRun():
    for generatorType in ["uniform", "gaussian"]:
        print("---------------"+generatorType+"---------------")
        inputPrecision = 0

        for distNorm in ["l2"]:

            if generatorType == "uniform":
                for n in [50, 100, 200, 400, 1000]:
                    for B in [500]:

                        problemInstance = ProblemInstance((B, B), n, 2*n, 2, distNorm=distNorm,
                                                          inputPrecision=inputPrecision)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = prevMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCosts(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)

                        print("PrevPaper distNorm: %s| n: %d| B: %d| ratio: %.2f"
                              % (distNorm, n, B, ratio))

                        matching = ourMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCosts(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, n, B, 2, ratio))

                        for lamb in [4, 8]:

                            problemInstance = ProblemInstance((B, B), n, lamb*n, lamb, distNorm=distNorm,
                                                              inputPrecision=inputPrecision)
                            problemInstance.generateParams(generatorType)

                            lowerBoundCost = getLowerBoundCost(problemInstance)

                            matching = ourMain.runInstance(problemInstance, True)

                            matchingCost = getMatchingCosts(problemInstance, matching)
                            ratio = round(matchingCost / lowerBoundCost, 2)
                            print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                                  % (distNorm, n, B, lamb, ratio))

            elif generatorType == "gaussian":
                for nCenters in [20]:
                    for variance in [1, 5, 10]:

                        problemInstance = ProblemInstance((100, 100), 50, 100, 2, distNorm=distNorm,
                                                          inputPrecision=inputPrecision)
                        problemInstance.generateParams(generatorType, {"nCenters": nCenters, "variance": variance})

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = prevMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCosts(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("PrevPaper distNorm: %s| nCenters: %d| variance: %d| ratio: %.2f"
                              % (distNorm, nCenters, variance, ratio))

                        matching = ourMain.runInstance(problemInstance, True)

                        matchingCost = getMatchingCosts(problemInstance, matching)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print(
                            "OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                            % (distNorm, nCenters, variance, 2, ratio))

                        for lamb in [4, 8]:

                            problemInstance = ProblemInstance((500, 500), 50, 50*lamb, lamb, distNorm=distNorm,
                                                              inputPrecision=inputPrecision)
                            problemInstance.generateParams(generatorType, {"nCenters": nCenters, "variance": variance})

                            lowerBoundCost = getLowerBoundCost(problemInstance)

                            matching = ourMain.runInstance(problemInstance, True)

                            matchingCost = getMatchingCosts(problemInstance, matching)
                            ratio = round(matchingCost / lowerBoundCost, 2)
                            print(
                                "OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                                % (distNorm, nCenters, variance, lamb, ratio))


def boundedRun():
    for generatorType in ["uniform", "gaussian"]:
        print("---------------"+generatorType+"---------------")
        for distNorm in ["l1", "l2"]:
            B = 100

            if generatorType == "uniform":
                for n in [10, 20, 30, 40, 50]:
                    for lamb in [2, 4, 8, 16]:

                        problemInstance = ProblemInstance((B, B), n, lamb*n, lamb, distNorm=distNorm)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = ourMain.runInstance(problemInstance, False, True)

                        matchingCost = getMatchingCosts(problemInstance, matching, False)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, n, B, lamb, ratio))

            elif generatorType == "gaussian":
                nCenters = 5

                for variance in [1, 5, 10]:
                    for lamb in [2, 4, 8, 16]:

                        problemInstance = ProblemInstance((B, B), 50, 50*lamb, lamb, distNorm=distNorm)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance)

                        matching = ourMain.runInstance(problemInstance, False, True)

                        matchingCost = getMatchingCosts(problemInstance, matching, False)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, nCenters, 2, variance, ratio))


exactRun()
# boundedRun()
# generateProblemInstances()
