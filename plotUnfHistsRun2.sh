#!/bin/bash

#variables="pt mass zpt leppt dphiz1z2 drz1z2"
variables="mass"
for var in $variables; do
  echo $var

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2016 -s TightLeptonsWGen -l 35.9 -f ZZ4l2016 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/FinalDiffDist_16Apr2020/

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2017 -s TightLeptonsWGen -l 41.5 -f ZZ4l2017 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2017/ZZSelectionsTightLeps/ANPlots/ZZ4l2017/FinalDiffDist_16Apr2020/

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 59.7 -f ZZ4l2018 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/FinalDiffDist_16Apr2020/

  ./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 137.1 -f ZZ4l2018 -vr ${var} --test --makeTotals --titleOffset 0.7 --scaleymin 0.5 --scaleymax 1.0 --scalelegy 1.45 --scalelegx 1.7 --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/FullRun2/FinalDiffDist_21Apr2020/

done
Leftvariables="dphiz1z2 drz1z2"
#for var in $Leftvariables;do
echo $var

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2016 -s TightLeptonsWGen -l 35.9 -f ZZ4l2016 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/FinalDiffDist_16Apr2020/

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2017 -s TightLeptonsWGen -l 41.5 -f ZZ4l2017 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2017/ZZSelectionsTightLeps/ANPlots/ZZ4l2017/FinalDiffDist_16Apr2020/

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 59.7 -f ZZ4l2018 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/FinalDiffDist_16Apr2020/

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 137.1 -f ZZ4l2018 -vr ${var} --test --makeTotals --titleOffset 0.7 --scaleymin 0.5 --scaleymax 1.0 --scalelegy 1.45 --scalelegx 1.75 --legend_left --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/FullRun2/FinalDiffDist_21Apr2020/

#done

#Leftvariables="leppt"
#for var in $Leftvariables;do
echo $var

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2016 -s TightLeptonsWGen -l 35.9 -f ZZ4l2016 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/FinalDiffDist_16Apr2020/

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2017 -s TightLeptonsWGen -l 41.5 -f ZZ4l2017 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2017/ZZSelectionsTightLeps/ANPlots/ZZ4l2017/FinalDiffDist_16Apr2020/

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 59.7 -f ZZ4l2018 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/FinalDiffDist_16Apr2020/

#./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 137.1 -f ZZ4l2018 -vr ${var} --test --makeTotals --legend_left --scalelegy 1.6 --scalelegx 1.2 --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/FullRun2/FinalDiffDist_21Apr2020/

#done
