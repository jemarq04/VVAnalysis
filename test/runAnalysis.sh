#!/bin/bash

lumi=35.87
lepid="Tight"
DATE=$(date +%d%b%Y)
DATE_MONTHONLY=$(date +%b%Y)
#looselepsfile=3MediumLeptons
looselepsfile=3LooseLeptons

input=Wselection${looselepsfile/3/}
output=Wselection
if [[ "$1" == *Full ]]; then
    input=${looselepsfile}
fi

if [[ $1 == VBS* ]]; then
    output=$1
elif [[ $1 == "Inclusive2Jet" ]]; then
    output=$1
elif [[ $1 == "3lDYControl" ]]; then
    if [[ $looselepsfile == "3MediumLeptons" ]]; then
        input=3lDYControl${looselepsfile/3/}
    else
        input=3lDYControl
    fi
    output=3lDYControl
elif [[ $1 == "3lTTbarControl" ]]; then
    if [[ $looselepsfile == "3MediumLeptons" ]]; then
        input=3lTTbarControl${looselepsfile/3/}
    else
        input=3lTTbarControl
    fi
    output=3lTTbarControl
elif [[ $1 == "Zselection" ]]; then
    input=Zselection${looselepsfile/3/}
    output=Zselection
elif [[ $1 == "FakeRateSelectionLoose" ]]; then
    input=${looselepsfile}
    output=FakeRateSelectionLoose
elif [[ $1 == "FakeRateSelectionTight" ]]; then
    input=${looselepsfile}
    output=FakeRateSelectionTight
elif [[ $1 == "Wselection_"* ]]; then
    output=$1
else
    echo "INFO: Using default selection 'Wselection'"
fi

frpath=$(./Utilities/scripts/getConfigValue.py fakeRate_output)
histpath=$(./Utilities/scripts/getConfigValue.py hist_output)
frfile=${frpath}/fakeRateFinal-${lepid}LepsFrom${looselepsfile}.root
histfile=${histpath}/${output}-${DATE}.root

if [[ "$3" != "" ]]; then
    histfile=${histfile/.root/_${3}.root}
fi

cd $CMSSW_BASE/src/Analysis/VVAnalysis
if [ -f $frfile ] && [ "$2" != "RedoFakeRates" ]; then
    echo "INFO: Fake rate file $frfile exists! Using exisiting file."
    if [ "$2" != "combineOnly" ]; then
        python ScaleFactors/setupScaleFactors.py -t $frfile
    fi
else
    echo "INFO: Fake rate file $frfile not found. It will be created."
    python ScaleFactors/setupScaleFactors.py
    frfile=${frpath}/fakeRate${DATE_MONTHONLY}-${lepid}LepsFrom${looselepsfile}.root
    ./Utilities/scripts/makeFakeRates.py -s ${looselepsfile} -l $lumi -o $frfile
    python ScaleFactors/setupScaleFactors.py -t $frfile
fi

if [ "$2" != "combineOnly" ]; then
    ./Utilities/scripts/makeHistFile.py -l $lumi -s $input -o $histfile --output_selection $output
    if [ -f $histfile ]; then
        echo "Histogram file $histfile produced"
    else
        echo "ERROR: $histfile was not produced!"
    fi
fi

if [ "$2" != "noCombine" ]; then
    combine_selection=WZxsec2016/${output}
    combine_folder=${DATE}
    if [[ "$3" != "" ]]; then
        combine_folder=${combine_folder}_${3}
    fi
    if [[ $output == *_* ]]; then
        combine_selection=WZxsec2016/${output/_*/}
        combine_folder=${output/*_/}/$combine_folder
    fi

    if [[ "$2" != "combineOnly" && "$1" == "VBSselection"* ]]; then
        if [[ "$3" == "*aQGC" ]]; then
            python ./Utilities/scripts/addaQGCHistsToFile.py -i $histfile
        fi
        python ./Utilities/scripts/addUnrolledHistsToFile.py -i $histfile
    fi
    if [ "$1" != "FakeRate"* ]; then
        combine_path=$(./Utilities/scripts/getConfigValue.py combine_output)
        combine_file=${combine_path}/$(basename $histfile)
        echo ./Utilities/scripts/prepareCombine.py \
            --input_file $histfile \
            -s $combine_selection \
            --folder_name $combine_folder \
            -l 35.9 \
            --combineChannels \
            --addControlRegion \
            --output_file $combine_file
        echo "Info: File $combine_file created"
    fi
fi
