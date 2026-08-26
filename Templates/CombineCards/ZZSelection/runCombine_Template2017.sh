#!/bin/bash

combineCards.py eeee=ZZ2017_eeee.txt eemm=ZZ2017_eemm.txt mmee=ZZ2017_mmee.txt mmmm=ZZ2017_mmmm.txt > ZZ2017.txt
text2workspace.py ZZ2017.txt -m 999 -o ZZ2017.root

if [[ $$1 == "impacts" ]]; then
    rm -rf impact
    mkdir impact
    pushd impact
    card="../ZZ2017.root"
    combineTool.py -M Impacts -m 125 -d $$card --doInitialFit
    combineTool.py -M Impacts -m 125 -d $$card --allPars --doFits --parallel 12
    combineTool.py -M Impacts -m 125 -d $$card --allPars -o impacts.json
    plotImpacts.py -i impacts.json -o impacts
    popd
else
    combine -M MaxLikelihoodFit -d ZZ2017.root $$1
fi
