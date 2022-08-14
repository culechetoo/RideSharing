import argparse

from runGDP import run as runGDP
from runGreedy import run as runGreedy
from runLMD import run as runLMD
from runHRA import run as runHRA


def parseArgs():
    defaultAlgorithm = "hra"
    defaulDataset = "random"
    defaultDistanceMetric = "euclidean"
    defaultNRepetitions = 1
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", nargs="?", help="select algorithm ('hra', 'greedy', 'pruneGdp' or 'lmd')"
                                                       "default=(hra)",
                        default=defaultAlgorithm)
    parser.add_argument("--dataset", nargs="?", help="dataset on which problem instances have to be generated "
                                                     "('nyc', 'sfo' or 'random') (default=random)",
                        default=defaulDataset)
    parser.add_argument("--distanceMetric", nargs="?", help="distance metric to use for dataset "
                                                            "('euclidean' or 'shortestPath') (default=euclidean)",
                        default=defaultDistanceMetric)
    parser.add_argument("--nRepetitions", type=int, nargs="?", help="number of times the experiment should be repeated"
                                                                    "(default=1)",
                        default=defaultNRepetitions)

    args = parser.parse_args()
    if args.algorithm not in ["hra", "greedy", "pruneGdp", "lmd"]:
        raise AttributeError("Choose algorithm from 'hra', 'greedy', 'pruneGdp' or 'lmd'")
    if args.dataset not in ["random", "sfo", "nyc"]:
        raise AttributeError("Choose dataset from 'nyc', 'sfo' or 'random'")
    if args.distanceMetric not in ["euclidean", "shortestPath"]:
        raise AttributeError("Choose distanceMetric from 'euclidean' or 'shortestPath'")

    return args


args = parseArgs()
dataSourceDir = "data/"+args.dataset
euclidean = True if args.distanceMetric == "euclidean" else False
nRepetitions = args.nRepetitions
resultBaseDir = "results/"+args.dataset+"/"
if args.algorithm == "hra":
    runHRA(dataSourceDir, resultBaseDir+"hra", euclidean, nRepetitions)
elif args.algorithm == "greedy":
    runGreedy(dataSourceDir, resultBaseDir+"greedy", euclidean, nRepetitions)
elif args.algorithm == "pruneGdp":
    runGDP("baselines/gdp/algorithmRestricted"+("Euclidean" if euclidean else "")+"/pruneGDP",
           dataSourceDir, resultBaseDir+"gdp", nRepetitions)
else:
    runLMD("baselines/lmd/algorithmRestricted"+("Euclidean" if euclidean else ""),
           dataSourceDir, resultBaseDir+"lmd", euclidean, nRepetitions)
