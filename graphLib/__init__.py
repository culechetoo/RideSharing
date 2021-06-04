from graphLib.graph.NxGraph import NxGraph
from graphLib.graph.GtGraph import GtGraph
from graphLib.algorithm.matchingAlgo import nxMatching


def getMatching(lib="networkx"):
    if lib == "networkx":
        return nxMatching


def getGraph(lib="networkx"):
    if lib == "networkx":
        return NxGraph()
    if lib == "graphLib-tool":
        return GtGraph()
