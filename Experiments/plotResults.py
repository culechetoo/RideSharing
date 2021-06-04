import matplotlib.pyplot as plt
import os

resultDir = "results"

lmdResults = []
ourResults = []

for i in range(len(os.listdir(resultDir))//2):
    lmdResult = float(open(resultDir+"/lmd_%02d.txt" % (i+1), 'r').read())
    ourResult = float(open(resultDir+"/our_%02d.txt" % (i+1), 'r').read())

print(lmdResults)
print(ourResults)