from OurAlg.matchingLib.matchingAlgo import nxMatching


def getMatching(lib="networkx"):
    if lib == "networkx":
        return nxMatching
