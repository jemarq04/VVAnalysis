#!/bin/bash

source Utilities/scripts/BashArgParse.sh
#@opt -h/--help
#@optdesc Print help and exit
#@opt -g/--gen
#@optdesc Enable ZZGenSelector
#@opt -s/--syst
#@optdesc Enable systematic variations
#@opt -m/--responseMatrix
#@optdesc Run ZZResponseMatrixMaker
#@opt --no-background
#@optdesc Disable ZZBackgroundSelector
#@opt --test
#@optdesc Do a debug (test) run
#@opt --frfile FILE
#@optdesc Path for fake rate scale factors file (default: data/fakeScaleFactorsRun3-ZZ4l$year.root)
#@arg year [year ...]
#@argdesc The years for analysis or 'all' to run all of Run 3

optstring="h/help*,g/gen,s/syst,m/responseMatrix,/no-background,/test,/frfile:"
extra_args="--with_background"
all_years="2022 2023 2024 2025"

parse_args "$0" "$optstring" 1 "$@"
eval set -- "$BAP_PARSED"

$no_background && extra_args=""
$gen && extra_args="$extra_args --with_Gen"
$syst && extra_args="$extra_args --doSystematics"
$responseMatrix && extra_args="$extra_args --responseMatrix"
$test && extra_args="$extra_args --test"

years="$@"
[[ $years = all ]] && years="$all_years"
[[ $(echo $years | wc -w) -gt 1 && -n $frfile ]] && die "cannot specify --frfile with multiple years"

# ========== Main Script ==========
for year in $years; do
  if ! [[ $all_years = *$year* ]]; then
    echo "invalid year: $year"
    continue
  fi

  [[ -z $frfile ]] && frtmpfile=data/fakeScaleFactorsRun3-ZZ4l$year.root || frtmpfile=$frfile
  [[ ! -f $frtmpfile ]] && die "invalid file: $frtmpfile"

  echo Running ZZ4l$year
  echo Using FR file $frtmpfile

  echo Running command ./Utilities/scripts/makeHistFile.py -f ZZ4l$year -a ZZ4l$year -s LooseLeptons --year $year -c eeee,eemm,mmee,mmmm -j 12 -sf -F $frtmpfile $extra_args
  ./Utilities/scripts/makeHistFile.py -f ZZ4l$year -a ZZ4l$year -s LooseLeptons --year $year -c eeee,eemm,mmee,mmmm -j 12 -sf -F $frtmpfile $extra_args

  echo "$year done!!==================================="
done
