#!/bin/bash

#variables="pt mass zpt leppt dphiz1z2 drz1z2"
#variables="mass"
#variables="nJets mjj dEtajj jetPt[0] jetPt[1] absjetEta[0] absjetEta[1] MassAllj Mass0j Mass1j Mass2j Mass3j Mass34j Mass4j MassFull Mass0jFull Mass1jFull Mass2jFull Mass3jFull Mass34jFull Mass4jFull"
#variables="nJets mjj dEtajj jetPt[0] jetPt[1] absjetEta[0] absjetEta[1] MassAllj Mass0j Mass1j Mass2j Mass34j" #MassFull Mass0jFull Mass1jFull Mass2jFull Mass34jFull"
variables="MassFull Mass0jFull Mass1jFull Mass2jFull Mass34jFull"
#variables="MassFull"
unfoldDirName="/afs/hep.wisc.edu/home/hhe62/www_uw/FullvarList_20May2021/20240628_REDO_refereeAlphaDn_m4lFull"

rm pdfConversionTemp.sh

for var in $variables; do
  echo $var

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2016 -s TightLeptonsWGen -l 35.9 -f ZZ4l2016 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/FinalDiffDist_16Apr2020/

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2017 -s TightLeptonsWGen -l 41.5 -f ZZ4l2017 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2017/ZZSelectionsTightLeps/ANPlots/ZZ4l2017/FinalDiffDist_16Apr2020/

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 59.7 -f ZZ4l2018 -vr ${var} --test --makeTotals --unfoldDir /afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/FinalDiffDist_16Apr2020/

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 137.58 -f ZZ4l2018 -vr ${var} --test --makeTotals --scaleymin 0.3 --scaleymax 1.2 --unfoldDir /afs/cern.ch/user/h/hehe/www/FullvarList_20May2021/UnfoldZZ4lFullRun2_oldMC_reg_bugfixedFakeImpl_FullSystFullRange20230112_specBkgTruncated_fixed_adjustedStyle_reprocess_Nothadd_recovered150_StyleReadjusted2/

  #./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 137.58 -f ZZ4l2018 -vr ${var} --test --makeTotals --scaleymin 0.3 --scaleymax 1.2 --unfoldDir /afs/cern.ch/user/h/hehe/www/FullvarList_20May2021/20230505_MiNNLO_temp_allUpdatedPlots_adjusted8_FixdPhi_RemovePre #UnfoldZZ4lFullRun2_oldMC_reg_bugfixedFakeImpl_FullSystFullRange20230227_specBkgTruncated_fixed_adjustedStyle_reprocess_Nothadd_recovered150_firstMiNNLO/

  ./Utilities/scripts/plotUnfolded.py -a ZZ4l2018 -s TightLeptonsWGen -l 137.58 -f ZZ4l2018 -vr ${var} --test --makeTotals --scaleymin 0.3 --scaleymax 1.2 --unfoldDir ${unfoldDirName}
done

chmod u+x pdfConversionTemp.sh

echo './pdfConversionTemp.sh' >moveDir.sh
chmod u+x moveDir.sh
echo "mv ${unfoldDirName} ~/public_html/20210520_unfolded_fullList/" >>moveDir.sh
echo "Run moveDir.sh to finalize and transfer directory to public_html"
