import multiprocessing
import os

import OurAlg.main as ourMain
from Main.Utils import getMatchingCosts

resultDir = "results"


def runOurAlgo(problemInstance, index, exact):
    print(str(index))

    matching = ourMain.runInstance(problemInstance, exact)
    matchingCost, driverMakespan, riderWaitTimes = getMatchingCosts(problemInstance, matching, exact, True)
    outFile = os.path.join(resultDir, "our%s_%02d.txt" % ("Exact" if exact else "Bounded", index+1))
    with open(outFile, "w") as fout:
        fout.write(str(matchingCost)+"\n")
        fout.write(str(driverMakespan)+"\n")
        fout.write(str(riderWaitTimes))


def batchRunOurAlgo(problemInstances, exact, nProcess):

    pool = multiprocessing.Pool(processes=nProcess)

    for index in range(len(problemInstances)):
        problemInstance = problemInstances[index]
        pool.apply_async(runOurAlgo, (problemInstance, index, exact))
        # runOurAlgo(problemInstance, index, exact)

    pool.close()
    pool.join()


def run(problemInstances, exact, nProcess):

    batchRunOurAlgo(problemInstances, exact, nProcess)
