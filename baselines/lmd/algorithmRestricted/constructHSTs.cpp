/**
	\Author: Trasier
	\Date:	2019/05/27
**/
#include <bits/stdc++.h>
#include "global.h"
#include "HST.h"
using namespace std;

#ifdef WATCH_MEM
#include "monitor.h"
#endif

char buf[1024];

string getHSTFileName(string& src, string& des, int id) {
	sprintf(buf, "%s/hst_%02d.txt", des.c_str(), id);
	
	return string(buf);
}

void dumpInfo(string& des) {
	FILE *fout = fopen(des.c_str(), "a");
	
	if (fout == NULL) {
		fprintf(stderr, "Fail to open %s\n", des.c_str());
		exit(1);
	}
	
	fprintf(fout, "CHST %.6lf %.6lf\n", usedTime, usedMemory/1024.0);
		
	fclose(fout);
}

void trainHST(string src, string edge, string des) {
	const int MAX_SAMPLE = 10;
	
	initLocation(src, edge);
#ifdef WATCH_MEM
	watchSolutionOnce(getpid(), usedMemory);
#endif
	for (int i=0; i<MAX_SAMPLE; ++i) {
		string desFileName = getHSTFileName(src, des, i);
		
		clock_t t0 = clock(), t1;
		
		constructHST(false);
		
		t1 = clock();
		
		usedTime = 1.0*(t1-t0)/CLOCKS_PER_SEC;
#ifdef WATCH_MEM
		watchSolutionOnce(getpid(), usedMemory);
#endif
	
		dumpHST(desFileName);
		dumpInfo(desFileName);
	}
}

int main(int argc, char **argv) {
	string vertexFileName, edgeFileName, desFileName;


    vertexFileName = string(argv[1]);
    edgeFileName = string(argv[2]);
    desFileName = string(argv[3]);
	
	trainHST(vertexFileName, edgeFileName, desFileName);
	freeMemory();
	
	return 0;
}
