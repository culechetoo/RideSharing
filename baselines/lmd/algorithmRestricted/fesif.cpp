/**
	\Author: 	Trasier
	\Date:		2019/05/22
	\Note: 		A fast implementation of my draft for VLDB'20.
**/
#include <bits/stdc++.h>
#include "global.h"
#include "HST.h"
#include "utils.h"
using namespace std; 

#ifdef WATCH_MEM
#include "monitor.h"
#endif

int nP = 0;
int* reqPool;
int* reqPos;
const double step = 2.0;
double rho = 1, delta = rho;

void localInit() {
	delta = rho;
	
	reqPos = new int[nR];
	reqPool = new int[nR];
	for (int i=0; i<nR; ++i) {
		reqPool[i] = i;
		reqPos[i] = i;
	}
	nP = nR;
}

void localFree() {
	delete[] reqPos;
	delete[] reqPool;
}

void budget(int wid, vector<int>& Rw, vector<int>& Sw, double delta) {
	worker_t& w = workers[wid];
	Rw.clear();
	Sw.clear();	
	vector<int> sorted;

	if (w.cap == w.picked) return;
	
	for (int i=0; i<nP; ++i) {
		request_t& r = requests[reqPool[i]];
		if (localDist(w.oid, r.oid)+localDist(r.oid, r.did) > delta)
			continue;
		sorted.push_back(reqPool[i]);
	}
	if (sorted.empty()) return ;

 	genLabel(w, H);
	genVec(sorted);
	sortPath(sorted);
	
	double tot = 0.0, inc;
	int oPos, dPos, rid;
	
	worker_t wtmp;
	wtmp.oid = w.oid;
	wtmp.cap = w.cap;
	wtmp.S.push_back(wtmp.oid);
	
	for (int i=0; i<sorted.size(); ++i) {
		rid = sorted[i];
		insertDist(wtmp, rid, oPos, dPos, inc);
		tot += inc;
		if (tot > delta) break;
		
		insert(wtmp, rid, oPos, dPos);
		Rw.push_back(rid);
		if (Rw.size() == (w.cap-w.picked)) break;
	}
	Sw = wtmp.S;
}

void updateRoute(int wid, vector<int>& Rw, vector<int>& Sw) {
	worker_t& w = workers[wid];
	w.S.insert(w.S.end(), Sw.begin()+1, Sw.end());
	w.picked += Rw.size();
	
	for (int i=0; i<Rw.size(); ++i) {
		int rid = Rw[i], pos = reqPos[rid];
		swap(reqPool[pos], reqPool[nP-1]);
		reqPos[reqPool[pos]] = pos;
		--nP;
	}
}

vector<int> getRequest(int wid) {
	worker_t& w = workers[wid];
	vector<int>& S = w.S;
	int n = S.size();
	vector<int> ret;
	
	for (int i=1; i<n; ++i) {
		if (S[i] & 1)
			ret.push_back(S[i]>>1);
	}
	
	return ret;
}

void FESI() {
	vector<pair<double,int> > vpi(nW, make_pair(0,0));
	delta = rho;

	localInit();
	
	int assigned = 0;
	vector<int> Rw, Sw;
	
	for (int i=0; i<nW; ++i) {
		vpi[i].second = i;
	}
	while (assigned < nR) {
		for (int i=0; i<nW; ++i) {
			int j = vpi[i].second;
			budget(j, Rw, Sw, delta);
			if (!Rw.empty()) {
				assigned += Rw.size();
				updateTree(Rw);
				updateRoute(j, Rw, Sw);
				if (assigned == nR)
					break;
			}
		}
		delta *= step;
		for (int i=0; i<nW; ++i) {
			vpi[i].first = getRouteDist(i);
			vpi[i].second = i;
		}
		sort(vpi.begin(), vpi.end());
	}
	
#ifdef WATCH_MEM
	watchSolutionOnce(getpid(), usedMemory);
#endif
}

int main(int argc, char** argv) {
	string locFileName, edgeFileName, inputFileName, hstFileName, outputFileName;

    locFileName = argv[1];
    edgeFileName = argv[2];
    inputFileName = argv[3];
    hstFileName = argv[4];
//    outputFileName = argv[5];

	readFromFiles(locFileName, edgeFileName, hstFileName, inputFileName);
	
	clock_t t1,t0;
	
	t0 = clock();    
    FESI();
    t1 = clock();
	
    usedTime = 1.0*(t1-t0)/CLOCKS_PER_SEC;

	dumpResult(outputFileName, "FESI"); 
	freeGlobalMemory();
	localFree();
	
	return 0;
}
