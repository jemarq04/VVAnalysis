#!/bin/bash

dataset_manager=$(./Utilities/scripts/getConfigValue.py dataset_manager_path)/ZZ4lDatasetManager
pushd $CMSSW_BASE/src/Analysis/VVAnalysis/Cuts

echo "INFO: Linking alias files"
for folder in $(ls -d */); do
    analysis_name=${folder/\//}
    alias_file=${dataset_manager}/Aliases/${analysis_name}.json 
    if [ -f $alias_file ]; then
        pushd $analysis_name
        ln -s $alias_file aliases.json
        echo "INFO: Linked analysis $analysis_name to alias file"
        popd
    fi
done

popd

echo "INFO: Downloading scale factor files"
pushd ScaleFactors
bash setup.sh
popd

if [ -d PileupWeights ]; then
    echo "INFO: Producing pileup weight distribution files"
    pushd PileupWeights
    bash getDataDistribution.sh
    python calculatePileupCorrections.py
    popd
else
    echo "WARNING! PileupWeights repository not found. You should clone with"
    echo ' --recursive, or run "git submodule update --init" now'
fi
