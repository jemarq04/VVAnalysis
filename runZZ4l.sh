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

years=$1
[[ $years = all ]] && years="2022 2023 2024"

for year in $years; do
  frfile=data/fakeScaleFactorsRun3-ZZ4l$year.root
  [[ ! -z $2 ]] && frfile=$2
  if [[ ! -f $frfile ]]; then
    echo invalid file: $frfile
    exit 1
  fi
  echo Running ZZ4l$year
  echo Using FR file $frfile

  # Without nonprompt contribution
  #./Utilities/scripts/makeHistFile.py -f ZZ4l$year -a ZZ4l$year -s LooseLeptons --year $year -c eeee,eemm,mmee,mmmm -j 12 -sf #--with_Gen

  # For systematics
  #./Utilities/scripts/makeHistFile.py -f ZZ4l$year -a ZZ4l$year -s LooseLeptons --year $year -c eeee,eemm,mmee,mmmm -j 12 -sf --doSystematics --with_background -F $frfile

  ./Utilities/scripts/makeHistFile.py -f ZZ4l$year -a ZZ4l$year -s LooseLeptons --year $year -c eeee,eemm,mmee,mmmm -j 12 -sf --with_background -F $frfile

  echo "$year done!!==================================="
done
