import numpy as np
from h5py import File

from multiprocessing import Pipe, Process


def childProcess(func, args, child_conn):
    val = func(*args)
    child_conn.send(val)
    child_conn.close()


def workerProcess(func, args):

    parent_conn, child_conn = Pipe()
    p = Process(target=childProcess, args=(func, args, child_conn))
    p.start()
    p.join()
    val = parent_conn.recv()
    return val


def mst_v(graphs):

    cost = np.zeros(graphs.shape[0])

    n_trees = graphs.shape[0]
    n_vertices = graphs.shape[1]

    # initialize with node 0:

    visited_vertices = np.expand_dims(np.zeros(n_trees).astype(int), axis=1)
    num_visited = 1
    # exclude self connections:
    diag_indices = np.arange(n_vertices)
    graphs[:, diag_indices, diag_indices] = np.inf

    while num_visited != n_vertices:
        new_edge_q, new_edge_r = np.divmod(
            np.expand_dims(graphs[np.expand_dims(np.arange(n_trees), axis=1), visited_vertices, :]
                           .reshape(graphs[np.expand_dims(np.arange(n_trees), axis=1), visited_vertices, :]
                                    .shape[0], -1).argmin(1), axis=1), n_vertices)

        cost += graphs[np.expand_dims(np.arange(n_trees), axis=1),
                       visited_vertices[np.expand_dims(np.arange(n_trees), axis=1), new_edge_q],
                       new_edge_r].squeeze()

        visited_vertices = np.column_stack([visited_vertices, new_edge_r])

        graphs[np.expand_dims(np.arange(n_trees), axis=1), visited_vertices, new_edge_r] = np.inf
        graphs[np.expand_dims(np.arange(n_trees), axis=1), new_edge_r, visited_vertices] = np.inf
        num_visited += 1

    return cost


def getDistOddRequestGroups_v(requestGroupIndices1, requestGroupIndices2, requestI2, interSourceDists, interTargetDists):

    try:
        mstCacheFile1 = File("mstCacheOdd.h5", 'r')
        mstCacheOld1 = mstCacheFile1["mstCache"][:]
        prevRequestGroupSet1 = mstCacheFile1["requestGroupSet"][:]
        mstCacheFile1.close()
    except FileNotFoundError:
        mstCacheFile1 = File("mstCacheEven.h5", 'r')
        lastIndex = int(mstCacheFile1["lastIndex"][0])
        mstCacheOld1 = mstCacheFile1["mstCache%d" % lastIndex][:]
        prevRequestGroupSet1 = mstCacheFile1["requestGroupSet%d" % lastIndex][:]
        mstCacheFile1.close()

    if requestI2 > 0:
        mstCacheFile2 = File("mstCacheEven.h5", 'r')
        mstCacheOld2 = mstCacheFile2["mstCache%d" % requestI2][:]
        prevRequestGroupSet2 = mstCacheFile2["requestGroupSet%d" % requestI2][:]
        mstCacheFile2.close()
    else:
        mstCacheOld2 = np.zeros(interSourceDists.shape[0])
        prevRequestGroupSet2 = np.arange(interSourceDists.shape[0]).reshape(-1, 1)

    comboIndices = np.concatenate([np.repeat(requestGroupIndices1, len(requestGroupIndices2)).reshape(-1, 1),
                                   np.tile(requestGroupIndices2, len(requestGroupIndices1)).reshape(-1, 1)], axis=1)

    newRequestGroupSet = np.concatenate([prevRequestGroupSet1[comboIndices[:, 0]],
                                         prevRequestGroupSet2[comboIndices[:, 1]]], axis=1)

    costs = mst_v(interSourceDists[newRequestGroupSet[:, None].T, newRequestGroupSet.T].T) \
            + mst_v(interTargetDists[newRequestGroupSet[:, None].T, newRequestGroupSet.T].T)

    mstCacheNew = costs - (mstCacheOld1[comboIndices[:, 0]] + mstCacheOld2[comboIndices[:, 1]])

    mstCacheFile = File("mstCacheOdd.h5", 'w')
    mstCacheFile.create_dataset('mstCache', data=mstCacheNew)
    mstCacheFile.create_dataset("requestGroupSet", data=newRequestGroupSet)
    mstCacheFile.close()
    mstCacheNew = mstCacheNew - np.min(mstCacheNew)
    mstCacheNew = np.max(mstCacheNew) - mstCacheNew + 1
    return np.rint(mstCacheNew).astype(np.uint32)


def getDistEvenRequestGroups_v(requestGroupIndices, interSourceDists, interTargetDists):

    try:
        mstCacheFile = File("mstCacheEven.h5", 'r')
        lastIndex = int(mstCacheFile["lastIndex"][0])
        mstCacheOld = mstCacheFile["mstCache%d" % lastIndex][:]
        prevRequestGroupSet = mstCacheFile["requestGroupSet%d" % lastIndex][:]
        mstCacheFile.close()
        init = False
    except FileNotFoundError:
        init = True
        prevRequestGroupSet = []
        mstCacheOld = []
        lastIndex = 0

    # riderDists_s = pdist(riderSources)
    # riderDists_t = pdist(riderTargets)

    # edges = np.transpose(np.triu_indices(riderSources.shape[0], 1))

    if init:
        requestGroupSet = np.triu_indices(interSourceDists.shape[0], 1)
        mstCacheNew = interSourceDists[requestGroupSet] + interTargetDists[requestGroupSet]
        mstCacheFile = File("mstCacheEven.h5", 'w')
        mstCacheFile.create_dataset("lastIndex", data=[lastIndex+1])
        mstCacheFile.create_dataset('mstCache%d' % (lastIndex+1), data=mstCacheNew)
        mstCacheFile.create_dataset("requestGroupSet%d" % (lastIndex+1), data=np.transpose(requestGroupSet))
        mstCacheFile.close()
        mstCacheNew = mstCacheNew-np.min(mstCacheNew)
        mstCacheNew = np.max(mstCacheNew)-mstCacheNew+1
        return np.rint(mstCacheNew).astype(np.uint32)

    # riderDistMatrix_s = squareform(riderDists_s)
    # riderDistMatrix_t = squareform(riderDists_t)

    comboIndices = np.transpose(np.triu_indices(len(requestGroupIndices), 1)).reshape(-1, 2)

    # prevRequestGroupSetCombos = prevRequestGroupSet[np.squeeze(requestGroupIndices[comboIndices])]
    
    prevShape = comboIndices.shape
    newShape = (prevShape[0], prevRequestGroupSet.shape[1]*2)
    newRequestGroupSet = prevRequestGroupSet[np.squeeze(requestGroupIndices[comboIndices])].reshape(newShape)

    # subgraphs_s = squareform(riderDists_s)[newRequestGroupSet[:, None].T, newRequestGroupSet.T].T
    # subgraphs_t = squareform(riderDists_t)[newRequestGroupSet[:, None].T, newRequestGroupSet.T].T
    costs = mst_v(interSourceDists[newRequestGroupSet[:, None].T, newRequestGroupSet.T].T)\
            + mst_v(interTargetDists[newRequestGroupSet[:, None].T, newRequestGroupSet.T].T)

    # mst_sub = mstCacheOld[comboIndices].sum(1)
    mstCacheNew = costs-mstCacheOld[comboIndices].sum(1)

    mstCacheFile = File("mstCacheEven.h5", 'a')
    del mstCacheFile["lastIndex"]
    mstCacheFile.create_dataset("lastIndex", data=[lastIndex+1])
    mstCacheFile.create_dataset('mstCache%d' %(lastIndex+1), data=mstCacheNew)
    mstCacheFile.create_dataset("requestGroupSet%d" %(lastIndex+1), data=newRequestGroupSet)
    mstCacheFile.close()
    mstCacheNew = mstCacheNew-np.min(mstCacheNew)
    mstCacheNew = np.max(mstCacheNew)-mstCacheNew+1
    return np.rint(mstCacheNew).astype(np.uint32)
