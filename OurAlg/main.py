import time

from OurAlg.ExactLambdaAlgorithm import run


def runInstance(problem, lamb, showRunTime=False):
    currTime = time.time()

    matching = run(problem, lamb)
    if showRunTime:
        print("Algorithm run in %f s" % (time.time() - currTime))

    return matching
