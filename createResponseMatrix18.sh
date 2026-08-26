#!/bin/bash

variables="pt mass zpt leppt dphiz1z2 drz1z2"
#variables="leppt"
for var in $variables;do
  echo $var
  ./Utilities/scripts/makeResponseMatrix.py -a ZZ4l2018 -s TightLeptonsWGen -l 59.7 -f ZZ4l2018 -sf data/scaleFactorsZZ4l2018.root -ls 2018fWUnc_full -vr ${var} --test --makeTotals
  #--plotResponse
done
