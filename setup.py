import os

os.system("cd data/sspexp_codes && make")

os.system("cd baselines/gdp/algorithmRestricted && make")

os.system("cd baselines/gdp/algorithmRestrictedEuclidean && make")

os.system("cd baselines/lmd/algorithmRestricted && make")

os.system("cd baselines/lmd/algorithmRestrictedEuclidean && make")
