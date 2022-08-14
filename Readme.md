# Hierarchical Rider Allocation

This repository consists of the codebase used for the experiments in "The Multi-vehicle Ride-Sharing Problem".

## Datasets

Apart from generating synthetic datasets using distributions, we also run our experiments on 2 publicly available
datasets: 

1. New York City Taxi Dataset: https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2016-04.csv
2. San Francisco Cab Spotting Data: https://crawdad.org/epfl/mobility/20090224/cab/

Before running the algorithms on these datasets, please download these datasets and place them in the appropriate
locations.

1. For NYC: Download the csv file and put it into "data/nyc/tripData"
2. For SFO: Download the dataset and after extracting, put the folder "cabspottingdata" into "data/sfo" 

Further, for both datasets, please download the osm data from the following links and put them in the appropriate
locations:

1. For NYC: Download https://download.bbbike.org/osm/bbbike/NewYork/NewYork.osm.gz and after extracting the
   OSM File, put it into "data/nyc"
2. For SFO: https://download.bbbike.org/osm/bbbike/SanFrancisco/SanFrancisco.osm.gz and after extracting the
   OSM File, put it into "data/sfo"
   
## Requirements

python >= 3.8.10

numpy >= 1.20.3

graph_tool >= 2.37

networkx >= 2.5.1

scipy >= 1.6.2

pandas >= 1.2.4

h5py >= 3.2.1

sortednp >= 0.4.0

## Instructions

First enter the root directory of the repository such that the "baselines", "data" etc. are in the working directory.
Run the following command to change the PYTHONPATH

`$ export PYTHONPATH=.`

Run the following command to make all the cpp modules

`$ python3 setup.py`

Run the following command to generate problem instances

`$ python3 data/genData.py`

Please run the command with `--help` option to understand the available options. For example, to generate problem
instances in the San Francisco dataset with 840 riders, 7 car capacity, run

`$ python3 data/genData.py --dataset sfo --numRiders 840 --carCapacity 7`

To run one of the included algorithms, run

`$ python3 run.py`

Please run the command with `--help` option to understand the available options. For example, to run the hra algorithm
on the above generated instances of sfo dataset with shortest path distance metric, run

`$ python3 run.py --algorithm hra --dataset sfo --distanceMetric shortestPath`

All results are stored in the "results" directory within the appropriate dataset folder. Further, a subfolder for each
algorithm is created. For example, the result for the above run would be stored at "results/sfo/hra/840_7(1)(1).txt"

All result files have the following format:

`{total distance}\n{driver makespan}\n{total latency}\n{run time}`

## Code References

Instead of the O(n^3) optimal maximum matching algorithm, we use a O(n) heuristic maximum matching algorithm available
with the graph-tool library. This algorithm can be found at:

1. B. Hendrickson and R. Leland. “A Multilevel Algorithm
for Partitioning Graphs.” In S. Karin, editor, Proc. Supercomputing ’95,
San Diego. ACM Press, New York, 1995, [DOI: 10.1145/224170.224228](https://dx.doi.org/10.1145/224170.224228)

We have used the following 2 pre-existing repositories to implement our baselines. Both these repositories are 
meant for solving the dial-a-ride problem. We have adapted these slightly so that they run on the multi-vehicle 
ride sharing problem.

2. LMD: https://github.com/BUAA-BDA/ridesharing-LMD
3. pruneGDP: https://github.com/BUAA-BDA/ridesharing-GreedyDP

To implement a better, more robust and fast route finding algorithm, we have implemented the linear insertion
algorithm in pruneGDP.

To implement a fast shortest path calculation algorithm for large osm data, we have used the following repository.

4. https://github.com/BUAA-BDA/sspexp_clone

This codebase has been included in our codebase for completeness and ease.

To convert osm files to a more readable graph format, we have used the following repository.

5. https://github.com/AndGem/OsmToRoadGraph
