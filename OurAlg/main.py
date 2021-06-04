import time

from OurAlg.ExactLambdaAlgorithm import run as exactRun
from OurAlg.BoundedLambdaAlgorithm import run as boundedRun


def runInstance(problem, exact=True, showRunTime=False):
    currTime = time.time()

    if exact:
        matching = exactRun(problem, showRunTime)
    else:
        matching = boundedRun(problem, showRunTime)
    if showRunTime:
        print("Algorithm run in %f s" % (time.time() - currTime))

    return matching
