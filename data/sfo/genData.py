import numpy as np
import random
import shutil
import os
from scipy.spatial.distance import cdist
import datetime
from data import genPLabel, procPycgr, createLabels


def genData(parserArgs):
    if not os.path.exists("data/sfo/sfo.pycgr"):
        if not os.path.exists("data/sfo/SanFrancisco.osm"):
            raise FileNotFoundError("Please add San Francisco osm file to data/sfo")
        print("***********Parsing OSM File***********")
        os.system("python3 data/OsmToRoadGraph/run.py -f data/sfo/SanFrancisco.osm --networkType c")
        os.rename("data/sfo/SanFrancisco.pycgr", "data/sfo/sfo.pycgr")
        os.remove("data/sfo/SanFrancisco.pycgr_names")
    if not os.path.exists("data/sfo/node.node"):
        procPycgr.procPycgr("sfo")
    if not os.path.exists("data/sfo/label.label"):
        print("***********Creating Shortest Path Labels***********")
        createLabels.createLabels("sfo")
    if not os.path.exists("data/sfo/plabel.label"):
        print("***********Parsing labels in Python***********")
        genPLabel.genPLabel("sfo")

    randomSelection = True
    nRepetitions = parserArgs.nRepetitions
    capacities = parserArgs.carCapacities
    requests = parserArgs.numRiders
    capLCM = np.lcm.reduce(capacities)

    fixedCapacity = parserArgs.fixedCarCapacity
    fixedRiders = parserArgs.fixedRiders

    nodeFile = open("data/sfo/node.node", 'r')
    nNodes = int(nodeFile.readline())

    nodes = nodeFile.readlines()
    nodes = np.array(list(map(lambda l: [float(l.split()[0]), float(l.split()[1])], nodes)))/10000

    trips = []

    i = 0

    print("***********Loading Data***********")
    if not os.path.exists("data/sfo/cabspottingdata"):
        raise FileNotFoundError("please add sfo cab data")

    for file in os.listdir("data/sfo/cabspottingdata"):
        i += 1
        # print(i)
        file = os.path.join("data/sfo/cabspottingdata", file)
        if "new" not in file:
            continue

        data = list(map(lambda l: [float(l.split()[0]), float(l.split()[1]), int(l.split()[2]),
                                   np.datetime64(datetime.datetime.fromtimestamp(int(l.split()[3])))],
                        open(file).readlines()))

        started = False
        dest = None
        prev = None
        for entry in data:
            if entry[2] == 1 and not started:
                dest = entry[:2]+entry[3:]
                started = True
            elif entry[2] == 0 and started:
                trips.append([prev[:2]+prev[3:], dest])
                started = False

            prev = entry

    trips = np.array(trips)

    if randomSelection:
        sampledTrips = np.random.choice(trips.shape[0], 100000)
        randomTrips = trips[sampledTrips, :]

        originCoords = randomTrips[:, 0, :2].astype(float)

        originMins = np.zeros(originCoords.shape[0])

        print("***********Matching taxi data locations to osm file***********")

        interval = 1000
        start = 0
        end = interval

        while start != end:
            # print(end)
            dists = cdist(originCoords[start: end], nodes)
            argmins = dists.argmin(axis=1)
            argmins[dists[np.arange(end-start), argmins] > 0.001] = -1
            originMins[start: end] = argmins

            start = end
            end = min(start+interval, originCoords.shape[0])

        originMins = originMins.astype(int)

        destCoords = randomTrips[:, 1, :2].astype(float)

        destMins = np.zeros(destCoords.shape[0])

        start = 0
        end = interval

        while start != end:
            # print(end)
            dists = cdist(destCoords[start: end], nodes)
            argmins = dists.argmin(axis=1)
            argmins[dists[np.arange(end-start), argmins] > 0.001] = -1
            destMins[start: end] = argmins

            start = end
            end = min(start+interval, destCoords.shape[0])

        destMins = destMins.astype(int)

        requestNodes = np.stack((originMins, destMins), axis=1)
        requestNodes = requestNodes[requestNodes[:, 0] != -1]
        requestNodes = requestNodes[requestNodes[:, 1] != -1]

        for nRiders in requests:
            for cap in capacities:
                if nRiders != fixedRiders and cap != fixedCapacity:
                    continue
                for i in range(nRepetitions):

                    dirPath = "data/sfo/problemInstances/%d_%d(%d)" % (nRiders, cap, i)

                    if os.path.exists(dirPath):
                        shutil.rmtree(dirPath)

                    os.mkdir(dirPath)

                    nCars = nRiders // cap

                    cars = list(map(str, random.choices(list(range(nNodes)), k=nCars)))
                    sampledRequestNodes = np.random.choice(requestNodes.shape[0], nRiders)
                    sampledRequestNodes = requestNodes[sampledRequestNodes, :]
                    riderSources = sampledRequestNodes[:, 0]
                    riderTargets = sampledRequestNodes[:, 1]
                    riders = [str(riderSources[i]) + " " + str(riderTargets[i]) for i in range(len(riderSources))]

                    carFile = open(os.path.join(dirPath, "car.txt"), 'w')
                    carFile.write(str(len(cars)) + " " + str(cap) + "\n")
                    carFile.write('\n'.join(cars) + '\n')

                    riderFile = open(os.path.join(dirPath, "rider.txt"), 'w')
                    riderFile.write(str(len(riders)) + "\n")
                    riderFile.write('\n'.join(riders) + '\n')

    else:
        # metaFile = open("meta.txt", 'w')
        times = trips[:, 0, -1]
        times.sort()
        for time in [15]:
            seconds = time*60+10
            i = j = mostRequests = 0
            bestInterval = [-1, -1]
            while i <= j < trips.shape[0]:
                # if i % 100000 == 0:
                #     print(i)
                while j < trips.shape[0] and times[j] < times[i]+np.timedelta64(seconds, 's'):
                    j += 1
                nRequests = j-i
                if nRequests > mostRequests:
                    # print(j)
                    mostRequests = nRequests
                    bestInterval = [i, j]
                i += 1

            # metaFile.write("interval: %d, start: %s, end: %s\n"
            #                % (time, trips[bestInterval[0], 0, 2], trips[bestInterval[1], 0, 2]))

            chosenTrips = trips[bestInterval[0]:bestInterval[1], :2]

            originCoords = chosenTrips[:, 0, :2].astype(float)

            originMins = np.zeros(originCoords.shape[0])

            interval = 300
            start = 0
            end = min(interval, originCoords.shape[0])

            while start != end:
                # print(end)
                dists = cdist(originCoords[start: end], nodes)
                argmins = dists.argmin(axis=1)
                argmins[dists[np.arange(end - start), argmins] > 0.001] = -1
                originMins[start: end] = argmins

                start = end
                end = min(start + interval, originCoords.shape[0])

            originMins = originMins.astype(int)

            destCoords = chosenTrips[:, 1, :2].astype(float)

            destMins = np.zeros(destCoords.shape[0])

            start = 0
            end = min(interval, originCoords.shape[0])

            while start != end:
                # print(end)
                dists = cdist(destCoords[start: end], nodes)
                argmins = dists.argmin(axis=1)
                argmins[dists[np.arange(end - start), argmins] > 0.001] = -1
                destMins[start: end] = argmins

                start = end
                end = min(start + interval, destCoords.shape[0])

            destMins = destMins.astype(int)

            requestNodes = np.stack((originMins, destMins), axis=1)
            requestNodes = requestNodes[requestNodes[:, 0] != -1]
            requestNodes = requestNodes[requestNodes[:, 1] != -1]

            toRemove = requestNodes.shape[0] % capLCM

            for i in range(nRepetitions):
                for cap in capacities:
                    nRiders = requestNodes.shape[0] - toRemove

                    dirPath = "problemInstances/%d_%d(%d)" % (nRiders, cap, i)

                    if os.path.exists(dirPath):
                        shutil.rmtree(dirPath)

                    os.mkdir(dirPath)

                    nCars = nRiders//cap

                    cars = list(map(str, random.choices(list(range(nNodes)), k=nCars)))
                    sampledRequestNodes = np.random.choice(requestNodes.shape[0], nRiders)
                    sampledRequestNodes = requestNodes[sampledRequestNodes, :]
                    riderSources = sampledRequestNodes[:, 0]
                    riderTargets = sampledRequestNodes[:, 1]
                    riders = [str(riderSources[i]) + " " + str(riderTargets[i]) for i in range(len(riderSources))]

                    carFile = open(os.path.join(dirPath, "car.txt"), 'w')
                    carFile.write(str(len(cars)) + " " + str(cap) + "\n")
                    carFile.write('\n'.join(cars) + '\n')

                    riderFile = open(os.path.join(dirPath, "rider.txt"), 'w')
                    riderFile.write(str(len(riders)) + "\n")
                    riderFile.write('\n'.join(riders) + '\n')


if __name__ == '__main__':
    genData()
