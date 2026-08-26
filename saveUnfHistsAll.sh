#!/bin/bash

#variables="pt dphiz1z2 drz1z2"
variables="zpt leppt"
for var in $variables;do
  echo $var
  ./Utilities/scripts/saveUnfolded.py -a ZZ4l2016 -s TightLeptonsWGen -l 35.9 -f ZZ4l2016 -sf data/scaleFactorsZZ4l2016.root -ls 2016fWUnc_full -vr ${var} --test --makeTotals --noNorm --plotDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/FinalRespMat

  #./Utilities/scripts/saveUnfolded.py -a ZZ4l2017 -s TightLeptonsWGen -l 41.5 -f ZZ4l2017 -sf data/scaleFactorsZZ4l2017.root -ls 2017fWUnc_full -vr ${var} --test --makeTotals --noNorm --plotDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2017/ZZSelectionsTightLeps/ANPlots/ZZ4l2017/FinalRespMat

  #./Utilities/scripts/saveUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 59.7 -f ZZ4l2018 -sf data/scaleFactorsZZ4l2018.root -ls 2018fWUnc_full -vr ${var} --test --makeTotals --noNorm --plotDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/FinalRespMat

done
