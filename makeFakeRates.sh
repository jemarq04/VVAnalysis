#!/bin/bash

source Utilities/scripts/BashArgParse.sh
#@opt -h/--help
#@optdesc Print help and exit
#@opt -o/--outfile FILE
#@optdesc Output fake rates file (default: fakeRates-ZZ4l$year.root)
#@arg year
#@argdesc Target year for fake rates

optstring="h/help*,o/outfile:"

parse_args "$0" "$optstring" 1 "$@"
eval set -- "$PARSED"

year="$1"
[[ -z $outfile ]] && outfile=fakeRates-ZZ4l$year.root

echo "Making fake rate for $year"
./Utilities/scripts/makeFakeRates.py -a ZZ4l$year -f ZZ4l$year --year $year -s ZplusLSkim -j 12 --noHistConfig --output_file $outfile
echo "$year done!!==================================="
