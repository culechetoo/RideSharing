import numpy as np
import pandas as pd
import random
import shutil
import os
from scipy.spatial.distance import cdist
from data import genPLabel, procPycgr, createLabels


def genData(parserArgs):
    if not os.path.exists("data/nyc/nyc.pycgr"):
        if not os.path.exists("data/nyc/NewYork.osm"):
            raise FileNotFoundError("Please add New York osm file to data/nyc")
        print("***********Parsing OSM File***********")
        os.system("python3 data/OsmToRoadGraph/run.py -f data/nyc/NewYork.osm --networkType c")
        os.rename("data/nyc/NewYork.pycgr", "data/nyc/nyc.pycgr")
        os.remove("data/nyc/NewYork.pycgr_names")
    if not os.path.exists("data/nyc/node.node"):
        procPycgr.procPycgr("nyc")
    if not os.path.exists("data/nyc/label.label"):
        print("***********Creating Shortest Path Labels***********")
        createLabels.createLabels("nyc")
    if not os.path.exists("data/nyc/plabel.label"):
        print("***********Parsing labels in Python***********")
        genPLabel.genPLabel("nyc")

    randomSelection = False
    nRepetitions = parserArgs.nRepetitions
    capacities = parserArgs.carCapacities
    argTimes = parserArgs.times
    capLCM = np.lcm.reduce(capacities)

    fixedCapacity = parserArgs.fixedCarCapacity
    fixedTime = parserArgs.fixedTime

    nodeFile = open("data/nyc/node.node", 'r')
    nNodes = int(nodeFile.readline())

    nodes = nodeFile.readlines()
    nodes = np.array(list(map(lambda l: [float(l.split()[0]), float(l.split()[1])], nodes)))/10000

    cols = ["tpep_pickup_datetime", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude"]

    print("***********Loading Data***********")
    try:
        data = pd.read_csv("data/nyc/tripData/yellow_tripdata_2016-04.csv", delimiter=",", usecols=cols, header=0)
    except FileNotFoundError:
        raise FileNotFoundError("Please download nyc tripdata")

    if randomSelection:
        dateTimes = data[cols[0]].str.split(" ", n=1, expand=True)
        data["dates"] = dateTimes[0]
        data["times"] = dateTimes[1]

        data.drop(columns=[cols[0]], inplace=True)
        dateCounts = data["dates"].value_counts()
        chosenDate = dateCounts.index[0]

        filteredTrips = data.loc[data["dates"] == chosenDate]

        del data, dateTimes
        # print("filtered data")

        randomTrips = filteredTrips.sample(100000)
        randomTrips = randomTrips[(randomTrips[cols[1]] != 0) & (randomTrips[cols[3]] != 0)]

        originCoords = randomTrips[[cols[2], cols[1]]].astype(float)

        originMins = np.zeros(originCoords.shape[0])

        interval = 300
        start = 0
        end = interval

        print("***********Matching taxi data locations to osm file***********")

        while start != end:
            # print(end)
            dists = cdist(originCoords[start: end], nodes)
            argmins = dists.argmin(axis=1)
            argmins[dists[np.arange(end-start), argmins] > 0.001] = -1
            originMins[start: end] = argmins

            start = end
            end = min(start+interval, originCoords.shape[0])

        originMins = originMins.astype(int)

        destCoords = randomTrips[[cols[4], cols[3]]].astype(float)

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

        j = 1

        for nRiders in range(840, 10920, 840):
            for cap in capacities:

                dirPath = "data/nyc/problemInstance/"+str(j)

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

                j += 1

    else:
        # metaFile = open("meta.txt", 'w')
        data[cols[0]] = pd.to_datetime(data[cols[0]])
        data = data.sort_values(cols[0], ignore_index=True)
        times = data[cols[0]].to_numpy()
        for time in argTimes:
            print("time = "+str(time))
            seconds = time*60+10
            i = j = mostRequests = 0
            bestInterval = [-1, -1]
            while i <= j < len(data):
                # if i % 100000 == 0:
                #     print(i)
                while j < len(data) and times[j] < times[i]+np.timedelta64(seconds, 's'):
                    j += 1
                nRequests = j-i
                if nRequests > mostRequests:
                    # print(j)
                    mostRequests = nRequests
                    bestInterval = [i, j]
                i += 1

            # metaFile.write("interval: %d, start: %s, end: %s\n"
            #                % (time, data.iloc[bestInterval[0]][cols[0]], data.iloc[bestInterval[1]][cols[0]]))

            trips = data.iloc[bestInterval[0]:bestInterval[1]]

            originCoords = trips[[cols[2], cols[1]]].astype(float)

            originMins = np.zeros(originCoords.shape[0])

            print("***********Matching taxi data locations to osm file***********")

            interval = 300
            start = 0
            end = interval

            while start != end:
                # print(end)
                dists = cdist(originCoords[start: end], nodes)
                argmins = dists.argmin(axis=1)
                argmins[dists[np.arange(end - start), argmins] > 0.001] = -1
                originMins[start: end] = argmins

                start = end
                end = min(start + interval, originCoords.shape[0])

            originMins = originMins.astype(int)

            destCoords = trips[[cols[4], cols[3]]].astype(float)

            destMins = np.zeros(destCoords.shape[0])

            start = 0
            end = interval

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
                    if time != fixedTime and cap != fixedCapacity:
                        continue
                    nRiders = requestNodes.shape[0] - toRemove

                    dirPath = "data/nyc/problemInstances/%d_%d(%d)" % (nRiders, cap, i)

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


# if __name__ == '__main__':
#     genData()
