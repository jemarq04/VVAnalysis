#!/bin/bash

combineCards.py eeee=ZZ2018_eeee.txt eemm=ZZ2018_eemm.txt mmee=ZZ2018_mmee.txt mmmm=ZZ2018_mmmm.txt > ZZ2018.txt
text2workspace.py ZZ2018.txt -m 999 -o ZZ2018.root

if [[ $$1 == "impacts" ]]; then
    rm -rf impact
    mkdir impact
    pushd impact
    card="../ZZ2018.root"
    combineTool.py -M Impacts -m 125 -d $$card --doInitialFit
    combineTool.py -M Impacts -m 125 -d $$card --allPars --doFits --parallel 12
    combineTool.py -M Impacts -m 125 -d $$card --allPars -o impacts.json
    plotImpacts.py -i impacts.json -o impacts
    popd
else
    combine -M MaxLikelihoodFit -d ZZ2018.root $$1
fi
