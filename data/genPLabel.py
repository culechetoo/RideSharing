import os.path
import pickle
from struct import unpack

import numpy as np


def genPLabel(dataset):

    dataDir = "data/"+dataset

    labelFile = open(os.path.join(dataDir, "label.label"), 'rb')
    nVertices = unpack("<i", labelFile.read(4))[0]

    labels = []

    maxHubs = 0
    maxMin = 0

    totalSize = 0

    for i in range(nVertices):
        # if i % 10000 == 0:
        #     print(i)
        #     print(maxHubs)
        nHubs = unpack("<i", labelFile.read(4))[0]
        maxHubs = max(maxHubs, nHubs)
        label = {}
        hubs = []
        dists = []
        for j in range(nHubs):
            hub = unpack("<2i", labelFile.read(8))[0]
            dist = unpack("<d", labelFile.read(8))[0]
            hubs.append(hub)
            dists.append(dist)
            label[hub] = dist

        maxMin = max(maxMin, min(hubs))

        labels.append([np.array(hubs), np.array(dists)])

    pickle.dump(labels, open(os.path.join(dataDir, "plabel.label"), 'wb'))


if __name__ == '__main__':
    dataset = "sfo"
    genPLabel(dataset)
