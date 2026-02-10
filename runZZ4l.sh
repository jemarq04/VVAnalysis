#!/bin/bash

if [[ $# -eq 0 ]]; then
  echo "usage: $0 YEAR/ALL [FRFILE]"
  echo
  echo "YEAR/ALL: year for analysis or 'all' to run all Run 3"
  echo "FRFILE: optional path to fake rate scale factors file"
  exit 1
elif [[ $# -eq 2 && ! -f $2 ]]; then
  echo invalid file: $2
  exit 1
fi

year=$1
[[ $year = all ]] && year="2022 2023 2024"

for yr in $year; do
  frfile=data/fakeScaleFactorsRun3-ZZ4lRun3Combined.root
  [[ ! -z $2 ]] && frfile=$2

  # Without nonprompt contribution
  #./Utilities/scripts/makeHistFile.py -f ZZ4l$yr -a ZZ4l$yr -s LooseLeptons --year $yr --uwvv -c eeee,eemm,mmee,mmmm -j 12 -sf #--with_Gen

  ./Utilities/scripts/makeHistFile.py -f ZZ4l$yr -a ZZ4l$yr -s LooseLeptons --year $yr --uwvv -c eeee,eemm,mmee,mmmm -j 12 -sf --with_background -F $frfile

  echo "$yr done!!==================================="
done
