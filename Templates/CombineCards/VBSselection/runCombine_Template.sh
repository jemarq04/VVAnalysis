#!/bin/bash

card="WZjj${sample}.txt"
if [[ "$$1" != "all" && "$$2" != "all" && $$3 != "all" ]]; then
    combineCards.py eee=WZjj${sample}_eee.txt eem=WZjj${sample}_eem.txt emm=WZjj${sample}_emm.txt mmm=WZjj${sample}_mmm.txt > $$card
else
    card="WZjj${sample}_all.txt"
fi
text2workspace.py $$card -m 900 -o $${card/txt/root}
card=$${card/txt/root}

blind="-t -1 --expectSignal 1."
if [[ "$$2" == "unblindExpected" ]]; then
   blind="$$blind --toysFreq"
elif [[ "$$1" == "noBlind" || "$$2" == "noBlind" || "$$3" == "noBlind" ]]; then
   blind=""
fi

if [[ $$1 == "mu" ]]; then
    shapeInfo=""
    if [[ $$4 == "saveShapes" ]]; then
        shapeInfo="--saveShapes --saveOverallShapes --saveNormalizations --saveWithUncertainties"
    fi
    combine -M MaxLikelihoodFit -d $$card $$blind $$2 $$shapeInfo
elif [[ $$1 == "impacts" ]]; then
    rm -rf impact
    mkdir impact
    pushd impact
    combineTool.py -M Impacts -m 125 -d ../$$card $$blind --doInitialFit
    combineTool.py -M Impacts -m 125 -d ../$$card $$blind --allPars --doFits --parallel 12
    combineTool.py -M Impacts -m 125 -d ../$$card --allPars -o impacts.json
    plotImpacts.py -i impacts.json -o impacts
    popd
elif [[ "$$1" == "all" ]]; then
    combine -M Significance $$blind $$card
else
    combine -M Significance $$blind $$card $$1
fi
