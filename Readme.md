Analysis code for ZZTo4l Analyses that is compatible with UWVV ntuples.
****
Primarily focused on using selections to skim Ntuples for Run3 analysis with some selections like trigger different for different years
****
# Current instructions
## Setup

On hep.wisc.edu machine:
```
cmsrel CMSSW_14_0_9
cd CMSSW_14_0_9/src
cmsenv
git clone https://github.com/YourGithubUsername/VVAnalysis -b Run3Skims Analysis/VVAnalysis
```


## Setting up data manager repository:

Then please fork this repository for dataset management:

https://github.com/jemarq04/ZZ4lDatasetManager

and in the same src/ directory above do:

```
git clone https://github.com/YourGithubUsername/ZZ4lDatasetManager -b for_merging_run3 Data_manager/ZZ4lDatasetManager
```

## Complilation
```
cd ${CMSSW_BASE}/src
scram b -j 12
```


## Changing Path Names:

Now please change to the VVAnalysis repository, and in **farmoutNtupleSkim.py**, change the global variable `USER` to your wisc username. 

Next in Data_manager/ZZ4lDatasetManager/FileInfo/ZZ4l2022/ntuples.json (or change 2022 to another available year), please clear the file and add in your ntuple information like the following, one entry for each ntuple sample:

```
{
 "CustomDataSetName": {
        "plot_group": "CustomGroupName",
        "file_path": "/store/user/lxplusUserName/ntuple location.../*.root"
    },
	other entries...
}
```
You can use asterisks in other parts of the file path if you have multiple folders.
 
The file_path format is for UWVV submission with CRAB where the outputs are located in the hdfs directory on hep.wisc.edu. If ntuples are produced parallelly in other approach, you may want to transfer the sample to hep.wisc.edu machine for the remaining processing. CustomDataSetName and CustomGroupName are arbitrary names you can assign to your sample. They will follow the sample in the remaining processing, and it is better that the two names are different and not too general.


## Submitting condor jobs:

You can then run
```
voms-proxy-init --voms=cms --valid=48:00
```
 
and in VVAnalysis repository run 

```
 ./SubmitSkimJobsZZ22.sh
```
or the scripts with same naming for other years. The -e-gen option can be used for MC to keep gen-level results, but needs to be turned off for data.
 

This will create job folder in your /nfs_scratch directory, and submit jobs to condor. You can check the job status with normal condor commands. If error occurs, you will need to remove the corresponding job folder (and maybe use condor_rm), and resubmit the jobs with the same command.

The skimmied ntuple files will be stored in your /hdfs/store/user/wiscUserName folder, so please create one if it doesn't exist, and with the current settings it will be in the folder named ZZ4l2018AnalysisJobs_[current_date].
