import PrevPaper.main as prevMain
import OurAlg.main as ourMain
from Main.ProblemInstance import ProblemInstance
from Main.LowerBound import getLowerBoundCost
from Main.Utils import getMatchingCost


def run():
    for generatorType in ["uniform", "gaussian"]:
        print("---------------"+generatorType+"---------------")
        for distNorm in ["l1", "l2"]:

            if generatorType == "uniform":
                for n in [10, 20, 30, 40, 50]:
                    for B in [10, 50, 100]:

                        problemInstance = ProblemInstance((B, B), n, 2*n, 2, distNorm)
                        problemInstance.generateParams(generatorType)

                        lowerBoundCost = getLowerBoundCost(problemInstance, 2)

                        matching = prevMain.runInstance(problemInstance)

                        matchingCost = getMatchingCost(problemInstance, matching, 2)
                        ratio = round(matchingCost / lowerBoundCost, 2)

                        print("PrevPaper distNorm: %s| n: %d| B: %d| ratio: %.2f"
                              % (distNorm, n, B, ratio))

                        matching = ourMain.runInstance(problemInstance, 2)

                        matchingCost = getMatchingCost(problemInstance, matching, 2)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("OurAlg distNorm: %s| n: %d| B: %d| lambda: %d| ratio: %.2f"
                              % (distNorm, n, B, 2, ratio))

            elif generatorType == "gaussian":
                for nCenters in [1, 5, 10]:
                    for variance in [1, 5, 10]:

                        problemInstance = ProblemInstance((100, 100), 50, 100, 2, distNorm)
                        problemInstance.generateParams(generatorType, {"nCenters": 5, "variance": variance})

                        lowerBoundCost = getLowerBoundCost(problemInstance, 2)

                        matching = prevMain.runInstance(problemInstance)

                        matchingCost = getMatchingCost(problemInstance, matching, 2)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print("PrevPaper distNorm: %s| nCenters: %d| variance: %d| ratio: %.2f"
                              % (distNorm, nCenters, variance, ratio))

                        matching = ourMain.runInstance(problemInstance, 2)

                        matchingCost = getMatchingCost(problemInstance, matching, 2)
                        ratio = round(matchingCost / lowerBoundCost, 2)
                        print(
                            "OurAlg distNorm: %s| nCenters: %d| variance: %d| lambda: %d| ratio: %.2f"
                            % (distNorm, nCenters, 2, variance, ratio))


run()
