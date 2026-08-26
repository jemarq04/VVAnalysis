#!/bin/bash

lumi=35.87
lepid="Tight"
DATE=$(date +%d%b%Y)
#frfile=/eos/user/k/kelong/WZAnalysisData/FakeRates/fakeRate${DATE}-3LooseLeptons-${lepid}Leps.root
looselepsfile=3LooseLeptons
frfile=/eos/user/k/kelong/WZAnalysisData/FakeRates/fakeRate07Sep2017-${lepid}LepsFrom${looselepsfile}.root
input=Wselection${looselepsfile/3/}
jetselec=j1Pt50-j2Pt50

for mjj in `seq 400 50 600`; do
    for dEtajj in `seq 2 0.5 4`; do
        etajj=${dEtajj/./p}
        output=VBSselection_mjj_${mjj}_detajj_${etajj/p0/}
        histfile=/eos/user/k/kelong/WZAnalysisData/HistFiles/${jetselec}/${output}-${DATE}-${lepid}.root

       cd $CMSSW_BASE/src/Analysis/WZAnalysis
       if [ ! -f $frfile ]; then
            ./Utilities/scripts/makeFakeRates.py -s 3LooseLeptons -l $lumi -o $frfile
            python ScaleFactors/setupScaleFactors.py -t $frfile
        fi
        echo ./Utilities/scripts/makeHistFile.py -l $lumi \
            -s $input -o $histfile --output_selection $output \
            -b "mjj,mjj_jesUp,mjj_jesDown,mjj_jerUp,mjj_jerDown,jetPt[0],jetPt[1],jetPt[2],jetEta[0],jetEta[1],jetEta[2],dEtajj,nJets"

        echo ./Utilities/scripts/prepareCombine.py \
            --input_file $histfile --output_file /eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_MJJ-EtaJJ_Optimization/${jetselec}/`basename $histfile` \
            -l $lumi -s WZxsec2016/VBSselection \
            --folder_name ${jetselec}/mjj${mjj}-dEtajj${dEtajj/./p}/${DATE}
    done
done
