#!/bin/bash

combineCards.py eee=WZ_eee.txt eem=WZ_eem.txt emm=WZ_emm.txt mmm=WZ_mmm.txt > WZ.txt
text2workspace.py WZ.txt -m 999 -o WZ.root

if [[ $$1 == "impacts" ]]; then
    rm -rf impact
    mkdir impact
    pushd impact
    card="../WZ.root"
    combineTool.py -M Impacts -m 125 -d $$card --doInitialFit
    combineTool.py -M Impacts -m 125 -d $$card --allPars --doFits --parallel 12
    combineTool.py -M Impacts -m 125 -d $$card --allPars -o impacts.json
    plotImpacts.py -i impacts.json -o impacts
    popd
else
    combine -M MaxLikelihoodFit -d WZ.root $$1
fi
