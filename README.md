# VVAnalysis: Run 3 Skimming

This branch of the reposirory is used to skim [**UWVV**](https://github.com/jemarq04/UWVV/tree/Run3) ZZ4l ntuples with further selections and trigger cuts. 
There is also a script used for choosing the best ZZ candidate in a given ZZ4l event found [here](src/disambiguateFinalStates.cc).

The skimmed ntuples are then used as inputs in the **Run3Analysis** branch of this repository to create final histograms.

## Setup

To set up this code, make a fork of this repository (including branches Run3Skims and Run3Analysis) and the 
[ZZ4lDatasetManager](https://github.com/jemarq04/ZZ4lDatasetManager/) repository (including branches `for_skimming_Run3` and `for_merging_Run3`). 
Then, run the following code replacing `YourGithubUsername` accordingly.

```bash
cmsrel CMSSW_14_0_9
cd CMSSW_14_0_9/src
cmsenv
git clone https://github.com/YourGithubUsername/VVAnalysis -b Run3Skims Analysis/VVAnalysis
git clone https://github.com/YourGithubUsername/ZZ4lDatasetManager -b for_skimming_run3 Data_manager/ZZ4lDatasetManager
scram build -j 12
```

## Running jobs

**In the following instructions, we use year 2022 as an example.**

In `Dataset_manager/ZZ4lDatasetManager/FileInfo/ZZ4l2022`, clear `ntuples.json` and add in your ntuple information in the same format as the following:

```json
{
 "CustomDataSetName": {
    "plot_group": "CustomGroupName",
    "file_path": "/store/user/lxplusUserName/ntuple location.../*.root"
  },
  "..."
}
```

You can use asterisks in other parts of the file path if you have multiple folders.
 
The `file_path` points to the ntuples created from UWVV jobs. For submission with CRAB, these ntuples are often located in the `hdfs` directory.
If ntuples are produced in parallel on another server, you may want to transfer the sample to hep.wisc.edu machine for this skimming (and later processing).
`CustomDataSetName` and `CustomGroupName` are arbitrary names you can assign to your sample. They will follow the sample in the remaining processing, 
and it is better that the two names are different and not too general. There can be multiple datasets to a given plot group (e.g. `ZZZ_preEE` and `ZZZ_postEE`).

## Submitting condor jobs:

First, make sure your grid certificate is authenticated. You can do so by running the following:

```bash
voms-proxy-init --voms=cms --valid=48:00
```
 
Then, to run the job, simply run the following while in this directory:

```bash
 ./submitSkim_ZZ.sh <YEAR>
```

where `<YEAR>` is the year for the desired ZZ4l analysis. To see a help screen for this script, run `./submitSkim_ZZ.sh` without any agruments. A common option is
`--e-gen`, which can be used for MC to keep gen-level results. However, it needs to be turned off for data.
 
This will create job folder in your `/nfs_scratch/` directory, and submit jobs to condor. You can check the job status with normal condor commands. 
If an error occurs, you will need to remove the corresponding job folder (and maybe use `condor_rm`), and resubmit the jobs with the same command.

The skimmied ntuple files will be stored in your `/hdfs/store/user/wiscUserName` folder, so create that directory if it doesn't exist. 
By default, it will be in the folder named `ZZ4l<YEAR>AnalysisJobs_<DATE>`.

### Fake rates

Similar to the above instructions, there is a helper script to submit Z+L skimming jobs: [`submitSkim_ZL.sh`](submitSkim_ZL.sh). This requires
updating the JSON files present in the appropriate directories (e.g. `FileData/ZplusL2022`). 
