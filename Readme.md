# Current instructions
We use the current branch of the repository for ZZ selection and histogram filling, after skimming the UWVV ntuples in the **Run2LegacySkims** branch. You may want to do the setup in a different folder than the skimming one.

## Setup
On hep.wisc.edu machine (previously done in uwlogin)
```
cmsrel CMSSW_10_3_1
cd CMSSW_10_3_1/src
cmsenv
mkdir Analysis
cd Analysis
git clone https://github.com/YourGithubUsername/VVAnalysis -b For_testing_original
cd VVAnalysis
```
Then in VVAnalysis/Templates please copy config.oldName to config.YourUserName, and modify its first 3 lines to your user name and data manager path (after setting it up in the next step). In VVAnalysis/src/ZZSelector.cc, set "doSystematics_ = false;" if you don't need the systematics yet.



Next set up the data manager repository like before:

Back in  CMSSW_10_3_1/src directory do:

```
mkdir Data_manager
cd Data_manager
git clone https://github.com/YourGithubUsername/ZZ4lRun2DatasetManager -b for_merging
```

**In the following instructoins, we use year 2018 as an example (but works the same for 2016 and 17).**

In ZZ4lRun2DatasetManager/FileInfo/ZZ4l2018, edit **LooseLeptons.json** so that it becomes something like the following (you can use names consistent with your choice in the skimming step), where you specify the path to your skimmed ntuple files for each sample:

 ```

{

"Sample1_Name" : {

"plot_group": "sample1_plotgroup",

"file_path": "path to skimmed root files for sample1/*"

},

other entries...

}
```
 

and copy **LooseLeptons.json** to to **ZZSelectionsTightLeps.json** also. 
 

Finally build the codes in  CMSSW_10_3_1/src directory: 

```
scram b -j 12
```
 

Then to perform the selection, in VVAnalysis, run

```
./runZZ4l2018.sh
```
 
before running you will need to create/find the VVAnalysis/data/ folder and put the required data files into it.

It will produce a series of temporary files, and eventually merge them into one single output root file, which contains the set of histograms we need and we can feed them into the [**ZZPlotting**](https://github.com/hhe62/ZZPlotting/) repository for final plots. With the updated codes it will also fill the selected events into ntuple files. Please create a directory called HistFiles in VVAnalysis and move the resulting histogram root file inside.

# Previous instructions
Analysis code for WZ/ZZ analyses. Some scripts using selections to skim Ntuples and C++ code to make histogram files for WZ.

+ [Setup](#setup)
+ [Overview](#overview)
+ [Specifics](#overview)
    + [NanoAOD](#nanoaod)
        + [Skimming NanoAOD](#skimming-nanoaod)
     + [UWVV nutples](#producing-uwvv-ntuples)
        + [Skimming UWVV ntuples](#skimming-uwvv-ntuples)
    + [Producing processed histogram file](#running-analysis-code)
        + [Z selector example](#the-z-selector-example)
        + [Writing your own selector](#implementing-your-own-selector)
        + [WZ selector](#the-wz-selector)
        + [WZ Background estimation](#nonprompt-background-estimate-for-wz)
    + [Statistical analysis](#running-statistical-analysis)
    + [Producing plots](#plotting)
    

# Setup
-----------
CMSSW version: CMSSW_10_4_0 # or CMSSW_9_2_14
```bash
X_Y_Z="10_4_0" # or 9_2_14
username="kdlong" # or your username
```

To checkout and compile:

```console
cmsrel CMSSW_version
cd CMSSW_X_Y_Z/src
mkdir Analysis
cd Analysis
git clone git@github.com:<username>/VVAnalysis.git
scram b -j 8
```

You will also want to install a separate package that contains information on the datasets used and histograms and binning. It is not required that you use this file, but it will be convenient for managing larger datasets (e.g., for getting the correct cross sections). It's recommended that you fork this into your github because some files/settings will be user specific.

install_path = ~username/work/ (or whatever you prefer)

```console
cd install_path
git clone git@github.com:<username>/AnalysisDatasetManager.git
```

You should create a new configuration file following the example [here](../master/Templates/config.kdlong) to have settings specific to you. Use the name config.<username>.

# Overview
-----------
This repository includes scripts to run all steps (starting with [UWVV ntuples](https://github.com/uwcms/UWVV])) to produce the results of [SMP-18-001](http://cms.cern.ch/iCMS/analysisadmin/cadilines?line=SMP-18-001). Many steps should be trivially modifiable for other analyses.

Current developement is in progress to also allow the use of NanoAOD in place of the UWVV ntuples. NanoAOD is a centrally-maintained ntuple which can signficantly reduce manpower needed to maintain private ntuples. More detail is given in the [NanoAOD](#nanoaod) section.

The analysis processeeds in several steps.

1. Produce ntuples using [UWVV](https://github.com/uwcms/UWVV]). See this package for further documentation. NanoAOD is also supported for some processes. In principle other packages could be used without much trouble, but variable names etc would need to be modified. Output is generally stored on a distributed storage system, e.g. /hdfs at UW or /eos at CERN.
2. Skim ntuples or NanoAOD to create smaller files that can be copied to a "local" storage disk, such as /data at uwlogin or /nfs_scratch at Wisconsin. 
3. Run analysis code to estimate backgrounds and produce histograms with final selections.
4. Plotting code combines histograms by scaling with cross section and luminosity information. Colors and CMS style are implemented.

# Specifics
-----------
Each step deserves some degree of explanation. They are also all driven by independent scripts, and can be run separately. The ntuple skimming is generally run independently. It is not required, but is advantageous to reduce files sizes for convenience in storage and processing. It is absolutely necessary that the tightest condition you use in your skim be looser the selection you implement in a later selector, however. For a fully MC driven analysis, one can often implement the full selection at the skim step and produce plots from here. Note, however, that the statistical tools are designed to run over the output of the histogram files produced by the selector.

## NanoAOD

https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD

### Skimming NanoAOD

https://github.com/cms-nanoAOD/nanoAOD-tools

Dilepton and 3 lepton specific skimming tools:

https://github.com/kdlong/NanoVVSkims

## Producing UWVV Ntuples

See the documentation in [UWVV](https://github.com/uwcms/UWVV]). It is possible to use other ntuples, but you will need to make extensive changes to variable names in the skimming step and branch names in the analysis code.

## Skimming UWVV Ntuples

This code is based on ["cut strings"](https://root.cern.ch/doc/v608/classTCut.html) applied to ROOT TTrees. It is driven by the script [skimNtuples.py](skimNtuples.py). This script takes as argument the analysis name and a list of selections to be applied. These selections are defined in the [Cuts folder](Cuts) of this repository. To implement a new analysis, one should create a new folder in this repository. To add a selection, a new selection.json file should be added. Follow the example of e.g. [3LooseLeptonsNoVeto.json](Cuts/WZxsec2016/3LooseLeptonsNoVeto.json). Conditions can be object specific (e.g. pt for each muon or elector) or state specific.

Run ```./skimNtuples.py --help``` for a full list of arguments to this script.

Generally you will want to farm this step out to condor, as it's real utility is to take files on hdfs, skim them, and produce output which can be copied locally. The script [farmoutNtupleSkim.py](farmoutNtupleSkim.py) is intended for this. It reads information about the input datasets from [AnalysisDatasetManager](https://github.com/kdlong/AnalysisDatasetManager) and configures jobs to be submitted to condor using ```farmoutAnalysisJobs.sh```, a script which is UW condor specific. Modifications would be required for use with other resources.

Run ```./farmoutNtupleSkim.py --help``` for a full list of arguments to this script.

An example to produce the output for the WZ inclusive analysis, with loosely IDed leptons (necessary for the fake rate step) would be

```./farmoutNtupleSkim.py -f data* -s 3MediumLeptonsNoVeto```

This will submit jobs for each file with a name matching the pattern "data*", defined in AnalysisDatasetManager, creating a skim of events passing the [3LooseLeptonsNoVeto.json](Cuts/WZxsec2016/3LooseLeptonsNoVeto.json) selection. The script creates submit folders for each dataset, by default in the location ```/<storage>/<username>/YYYY-MM-DD_VVAnalysisJobs```, where <storage> is either /nfs_scratch or /data. It will produce output files copied to ```/store/user/<username>/VVAnalysisJobs_YYYY-MM-DD```. If you want to copy these locally, you can use the script [copyFromHdfs.py](https://github.com/kdlong/AnalysisDatasetManager/blob/master/copyFromHdfs.py).
  
```./copyFromHdfs.py /hdfs/store/user/<username>/...```

## Running analysis code

### The Z selector example

See [this commit](https://github.com/kdlong/VVAnalysis/commit/18a1d903e149653fff3985b43f1acc834632a7ac) for an example of how to add histograms to a selector using the configuration setup. [These corresponding changes](https://github.com/kdlong/AnalysisDatasetManager/commit/39909f6e76046b6ab39b293fa3ea209d1cd202a8) to the [AnalysisDatasetManager repository](https://github.com/kdlong/AnalysisDatasetManager) are necessary.

### Implementing your own selector

### The WZ selector

### Nonprompt background estimate for WZ

## Running Statistical Analysis 

## Plotting

