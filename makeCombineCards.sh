#!/bin/bash

[[ -z $1 ]] && outdir=CombineCards || outdir=$1

years="2022 2023 2024 2025"
for year in $years; do
  echo Making datacard for $year

  infile="HistFiles/SystHists-ZZ4l$year.root"

  #python3 Utilities/scripts/setupZZCombineRun3.py -i $infile -o $outdir -c eeee,eemm,mmee,mmmm -a ZZ4l$year $year
  python3 Utilities/scripts/setupZZCombineRun3.py -i $infile -o $outdir --lumiMatrix -c eeee,eemm,mmee,mmmm -a ZZ4l$year $year
done
