from OurAlg.graphLib.NxGraph import NxGraph
from OurAlg.graphLib.GtGraph import GtGraph


def getGraph(lib="networkx"):
    if lib == "networkx":
        return NxGraph()
    if lib == "graphLib-tool":
        return GtGraph()
