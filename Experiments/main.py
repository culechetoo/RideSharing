import os
import pickle

from Experiments import runLMD, runOurAlgParallel

nProcess = 4
problemInstanceDir = "../data/problemInstance"

problemInstances = []
for i in range(len(os.listdir(problemInstanceDir))):

    problemInstanceFile = "%d.pkl" % (i+1)
    problemInstances.append(pickle.load(open(os.path.join(problemInstanceDir, problemInstanceFile), 'rb')))

print("LMD")
# runLMD.run(problemInstances, nProcess)

print("Our Algo Exact")
runOurAlgParallel.run(problemInstances[10:], True, nProcess)

print("Our Algo Bounded")
runOurAlgParallel.run(problemInstances, False, nProcess)
