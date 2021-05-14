import time

from PrevPaper.Algorithm import run


def runInstance(problem, showRunTime=False):
    currTime = time.time()

    matching = run(problem)
    if showRunTime:
        print("Algorithm run in %f s" % (time.time() - currTime))

    return matching
