import time

from OurAlg.ExactLambdaAlgorithm import run as exactRun
from OurAlg.BoundedLambdaAlgorithm import run as boundedRun


def runInstance(problem, showRunTime=False):
    currTime = time.time()

    if problem.exact:
        matching = exactRun(problem, showRunTime)
    else:
        matching = boundedRun(problem, showRunTime)
    if showRunTime:
        print("Algorithm run in %f s" % (time.time() - currTime))

    return matching
