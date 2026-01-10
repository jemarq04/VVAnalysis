#!/bin/bash

if [[ $# -eq 0 ]]; then
  echo "usage: $0 INFILE [INFILE...]"
  echo
  echo INFILE: list of files to combine
  exit 1
fi

for f in "$@"; do
  filetype=none
  if [[ ! -f $f ]]; then
    echo invalid file: $f
    exit 1
  else
    if [[ $filetype = none ]]; then
      [[ $(basename $f) = Hists*.root ]] && filetype=hists || filetype=fakes
    else
      if [[ $filetype = hists && $(basename $f) = fake*.root ]]; then
        echo cannot combine histogram files and fake files!
        exit 1
      elif [[ $filetype = fakes && $(basename $f) = Hists*.root ]]; then
        echo cannot combine histogram files and fake files!
        exit 1
      fi
    fi
  fi
done

[[ $filetype = hists ]] && analysis=ZZ4lRun3Combined || analysis=ZplusLRun3Combined
./Utilities/scripts/combineFiles.py -f -a $analysis $@
