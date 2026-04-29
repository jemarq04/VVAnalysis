#!/bin/bash

[[ -z $1 ]] && outdir=CombineCards || outdir=$1

years="2022 2023 2024"
for year in $years; do
  echo Making datacard for $year

  infile="HistFiles/Hists26Feb2026-ZZ4l$year.root"

  python3 Utilities/scripts/setupZZCombineRun3.py -i $infile -o $outdir --rebin 100,200,250,300,350,400,500,600,800,1000 -c eeee,eemm,mmee,mmmm -a ZZ4l$year $year
done
