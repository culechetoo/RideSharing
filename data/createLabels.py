import os
import subprocess


def createLabels(dataset):
    dataDir = "data/"+dataset

    tempEdgeFile = open("tempEdgeFile.txt", "w")
    tempEdgeFile.writelines(open(os.path.join(dataDir, "edge.edge"), 'r').readlines()[1:])
    tempEdgeFile.close()

    labelFileExec = "data/sspexp_codes/bin/sspexp_run"

    options = ["-x", "-d", "0", "-w", "1", "-m", "2", "-s", "1", "-e", "label", "-g", "tempEdgeFile.txt"]

    cmdLine = ["./"+labelFileExec]+options
    subprocess.run(cmdLine)
    os.rename("label.label", os.path.join(dataDir, "label.label"))
    os.rename("label.order", os.path.join(dataDir, "order.order"))

    os.remove("tempEdgeFile.txt")


if __name__ == '__main__':
    dataset = "sfo"
    createLabels(dataset)
