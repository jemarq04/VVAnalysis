#!/bin/bash

# Get directory of script (rather than directory the script is run from)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export zzt="${DIR}"
#echo $zzt
#if [ ! -d "$zzt"/recipe/cmssw ]; then
#    pushd "$zzt"/recipe
#    scram pro -n cmssw CMSSW CMSSW_8_0_26
#    popd
#fi
#pushd "$zzt"/recipe/cmssw/src
#cmsenv
#popd

#echo "Activating python virtual environment"
#source "$zzt"/recipe/setupPython.sh
#echo $zzt
#export PYTHONPATH="$zzt":"$PYTHONPATH"
#echo $PYTHONPATH

#if [ -d "$zzt"/RooUnfold-1.1.1 ]; then
#  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH":"$zzt"/RooUnfold-1.1.1
#  echo "Does it get RooUnfold 1.1"
#elif [ -d "$zzt"/RooUnfold ]; then
#  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH":"$zzt"/RooUnfold
#  echo "Does it get RooUnfold"
#fi

echo "ZZTools setup complete"
