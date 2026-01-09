#!/bin/bash

combineCards.py eee=WZjj_${sample}_eee.txt eem=WZjj_${sample}_eem.txt emm=WZjj_${sample}_emm.txt mmm=WZjj_${sample}_mmm.txt > WZjj_EWK_${sample}.txt
text2workspace.py WZjj_EWK_${sample}.txt -m 999 -o WZjj_EWK_${sample}.root
combine -M ProfileLikelihood --significance -t -1 --expectSignal 1 -d WZjj_EWK_${sample}.root

if [[ $$1 == "impacts" ]]; then
    rm -rf impact
    mkdir impact
    pushd impact
    card="../WZjj_EWK_${sample}.root"
    #card="../dgh_card.dat.root"
    combineTool.py -M Impacts -m 125 -d $$card -t -1 --expectSignal 1. --doInitialFit
    combineTool.py -M Impacts -m 125 -d $$card -t -1 --expectSignal 1. --allPars --doFits --parallel 12
    combineTool.py -M Impacts -m 125 -d $$card --allPars -o impacts.json
    plotImpacts.py -i impacts.json -o impacts
    popd
fi
