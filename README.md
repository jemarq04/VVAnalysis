# VVAnalysis: Run 3 Analysis

This branch of the repository is used for ZZ selection and histogram filling after skimming the UWVV ntuples in the **Run3Skims** branch. To avoid conflicts with that
environment, this branch should be used in a brand-new CMSSW environment. In other words, follow the [setup instructions](#setup) even if you have the skimming
code working elsewhere.

## Setup

To set up this code, make a fork of this repository (including branches Run3Skims and Run3Analysis) and the [ZZ4lDatasetManager]() repository (including 
branches for_skimming_Run3 and for_merging_Run3). Then, run the following code replacing `YourGithubUsername` accordingly.

```bash
cmsrel CMSSW_14_0_9
cd CMSSW_14_0_9/src
cmsenv
git clone https://github.com/YourGithubUsername/VVAnalysis -b Run3Analysis Analysis/VVAnalysis
git clone https://github.com/YourGithubUsername/ZZ4lDatasetManager -b for_merging_Run3 Dataset_manager/ZZ4lDatasetManager
scram build -j 12
```

Then go to [`Analysis/VVAnalysis/Templates`](Templates/) copy `config.template` to `config.YourUserName`, and modify its first 3 lines to your username and 
data manager path (after setting it up in the next step). Note that this username is your UW HEP username. 

## Running jobs

**In the following instructions, we use year 2022 as an example.**

In `Dataset_manager/ZZ4lDatasetManager/FileInfo/ZZ4l2022`, edit `LooseLeptons.json` to specify your desired plot groups and their corresponding skimmed ntuples.
For example,

 ```json
{
  "Sample1_Name" : {
    "plot_group": "sample1_plotgroup",
    "file_path": "path to skimmed root files for sample1/*"
  },
  "..."
}
```
Afterwards, copy `LooseLeptons.json` to to `ZZSelectionsTightLeps.json`. Note that for Data/MC comparisons, `ZZSelectionsTightLeps.json` needs two additional entries
at the end:

```json
"AllData" : {
    "file_path" : "",
    "plot_group" : "data_all"
},
"DataEWKCorrected" : {
    "file_path" : "",
    "plot_group" : "nonprompt"
}
```

Finally, to run the job, simply run the following while in this directory:

```bash
./runZZ4l2022.sh
```

It will produce a series of temporary files, and eventually merge them into one single output root file, which contains the set of histograms we need and we can feed them 
into the [**ZZPlotting**](https://github.com/jemarq04/ZZPlotting/) repository for final plots. With the updated codes it will also fill the selected events 
into ntuple files.

## Configuring the jobs

(WIP)

