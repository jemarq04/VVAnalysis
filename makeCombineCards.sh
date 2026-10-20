#!/bin/bash

source Utilities/scripts/BashArgParse.sh
#@opt -h/--help
#@optdesc Print help and exit
#@opt -i/--infile FILE
#@optdesc Path to systematics file (default: HistFiles/SystHists-ZZ4l$year.root)
#@opt -o/--outdir DIR
#@optdesc Path to output directory for generated cards (default: CombineCards/)
#@opt --extra-args "ARG [ARG ...]"
#@optdesc Extra arguments to pass directly to setupZZCombineRun3.py
#@arg year [year ...]
#@argdesc The years for analysis or 'all' to run all of Run 3

optstring="h/help*,i/infile:,o/outdir:,/extra-args:"
all_years="2022 2023 2024 2025"
extra_args=""
outdir="CombineCards"

parse_args "$0" "$optstring" 1 "$@"
eval set -- "$BAP_PARSED"

years="$@"
[[ $years = all ]] && years="$all_years"
[[ $(echo $years | wc -w) -gt 1 && -n $infile ]] && die "cannot specify --infile with multiple years"

# ========== Main Script ==========
for year in $years; do
  if ! [[ $all_years = *$year* ]]; then
    echo "invalid year: $year"
    continue
  fi

  [[ -z $infile ]] && tempfile=data/fakeScaleFactorsRun3-ZZ4l$year.root || tempfile=$infile
  [[ ! -f $tempfile ]] && die "invalid file: $tempfile"

  echo Running ZZ4l$year

  python3 Utilities/scripts/setupZZCombineRun3.py -i $tempfile -o $outdir --lumiMatrix -c eeee,eemm,mmee,mmmm -a ZZ4l$year $extra_args $year

  echo "$year done!!==================================="
done
