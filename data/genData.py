import argparse

from data.nyc.genData import genData as nycData
from data.sfo.genData import genData as sfoData
from data.random.genData import genData as randomData


def parseArgs():
    defaultVariances = [10, 50, 100, 200]
    defaultNumCenters = [5, 10, 20, 50]
    defaultNumRiders = [840, 2520, 5040, 7560, 10080]
    defaultCarCapacities = [2, 4, 5, 6, 8]
    defaultTimes = [1, 2, 5, 10, 15]
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", nargs="?", help="dataset on which problem instances have to be generated "
                                                     "('nyc', 'sfo' or 'random') (default=random)",
                        default="random")
    parser.add_argument("--gridSize", type=int, nargs="?", help="grid size for sampling (default=4000)", default=4000)
    parser.add_argument("--nRepetitions", type=int, nargs="?", help="number of repetitions in sampling (default=1)",
                        default=1)
    parser.add_argument("--variances", type=float, nargs="+", help="set of variances for problem instances "
                                                                   "(default=[10, 50, 100, 200])",
                        default=defaultVariances)
    parser.add_argument("--fixedVariance", type=float, nargs="?", help="fixed variance "
                                                                       "(default=<middle element of variances>)",
                        default=defaultVariances[len(defaultVariances)//2])
    parser.add_argument("--numCenters", type=int, nargs="+",
                        help="set of number of centers in GMM for problem instances (default=[5, 10, 20, 50])",
                        default=defaultNumCenters)
    parser.add_argument("--fixedNumCenters", type=int, nargs="?", help="fixed number of centers"
                                                                       "(default=<middle element of numCenters>)",
                        default=defaultNumCenters[len(defaultNumCenters)//2])
    parser.add_argument("--numRiders", type=int, nargs="+", help="set of number of riders for problem instances"
                                                                 "default=([840, 2520, 5040, 7560, 10080])",
                        default=defaultNumRiders)
    parser.add_argument("--fixedRiders", type=int, nargs="?", help="fixed number of riders"
                                                                   "(default=<middle element of numRiders>)",
                        default=defaultNumRiders[len(defaultNumRiders)//2])
    parser.add_argument("--carCapacities", type=int, nargs="+", help="set of car capacities for problem instances"
                                                                     "default=([2, 4, 5, 6, 8])",
                        default=defaultCarCapacities)
    parser.add_argument("--fixedCarCapacity", type=int, nargs="?", help="fixed car capacity"
                                                                        "(default=<middle element of carCapacities>)",
                        default=defaultCarCapacities[len(defaultCarCapacities)//2])
    parser.add_argument("--times", type=int, nargs="+", help="time intervals (in minutes) to extract data from for NYC"
                                                             "default=([1, 2, 5, 10, 15])",
                        default=defaultTimes)
    parser.add_argument("--fixedTime", type=int, nargs="?", help="fixed time interval"
                                                                 "(default=<middle element of times>)",
                        default=defaultTimes[len(defaultTimes)//2])
    args = parser.parse_args()
    if args.fixedTime not in args.times:
        raise AttributeError("fixedTime should be in times")
    if args.fixedCarCapacity not in args.carCapacities:
        raise AttributeError("fixedCarCapacity should be in carCapacities")
    if args.fixedRiders not in args.numRiders:
        raise AttributeError("fixedRiders should be in numRiders")
    if args.fixedNumCenters not in args.numCenters:
        raise AttributeError("fixedNumCenters should be in numCenters")
    if args.fixedVariance not in args.variances:
        raise AttributeError("fixedVariance should be in variances")
    return args


args = parseArgs()
if args.dataset == "nyc":
    nycData(args)
elif args.dataset == "sfo":
    sfoData(args)
elif args.dataset == "random":
    randomData(args)
else:
    raise AttributeError("Choose dataset from 'nyc', 'sfo' or 'random'")
