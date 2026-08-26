This is specifically for unfolding branch.
# Setup
-----------
CMSSW version: CMSSW_8_0_26

To checkout and compile:

```console
cmsrel CMSSW_version
cd CMSSW_8_0_26/src
mkdir Analysis
cd Analysis
git clone -b UnfoldingMaster git@github.com:uhussain/VVAnalysis.git
scram b -j 8
```

You will also want to install a separate package that contains information on the datasets used and histograms and binning. It is not required that you use this file, but it will be convenient for managing larger datasets (e.g., for getting the correct cross sections). It's recommended that you fork this into your github because some files/settings will be user specific.

install_path = ~username/work/ (or whatever you prefer)
Once again in case of this branch and ZZ analysis you might need my version:

```console
cd install_path
git clone git@github.com:uhussain/ZZ4lRun2DatasetManager.git
```


## Running analysis code

```
cd CMSSW_8_0_26/src/Analysis/VVAnalysis
source setup.sh
./createResponseMatrix16.sh
```
