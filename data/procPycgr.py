import os

import numpy as np


def procPycgr(dataset):
    baseDir = "data/"+dataset

    pyFile = open(os.path.join(baseDir, dataset+".pycgr"), 'r')

    data = pyFile.readlines()[7:]

    nNodes = int(data[0])
    nEdges = int(data[1])

    nodes = data[2:nNodes+2]
    edges = data[nNodes+2:]

    nodes = list(map(lambda l: " ".join(l.split(" ")[1:]), nodes))
    edges = list(map(lambda l: " ".join(l.split(" ")[:3])+"\n", edges))

    nodesNumeric = np.array(list(map(lambda l: [float(l.split()[0]), float(l.split()[1])], nodes)))
    nodesNumeric *= 10000

    nodes = list(map(lambda l: "%f %f\n" % (l[0], l[1]), nodesNumeric))

    nodeFile = open(os.path.join(baseDir, "node.node"), 'w')
    nodeFile.write("%d\n" % nNodes)
    nodeFile.writelines(nodes)

    edgeFile = open(os.path.join(baseDir, "edge.edge"), 'w')
    edgeFile.write("%d\n" % nEdges)
    edgeFile.writelines(edges)


if __name__ == '__main__':
    dataset = "sfo"
    procPycgr(dataset)
