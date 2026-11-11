#!/bin/bash

source Utilities/scripts/BashArgParse.sh
#@opt -y/--year YEAR
#@optdesc Year for analysis
#@opt -o/--outfile FILE
#@optdesc Output wrapped file (default: fakeScaleFactorsRun3-ZZ4l$year.root)
#@arg infile
#@argdesc Input file to wrap

optstring="h/help*,y/year:,o/outfile:"

parse_args "$0" "$optstring" 1 "$@"
eval set -- "$PARSED"

infile="$1"
[[ ! -f $infile ]] && die "invalid file: $infile"
if [[ -z $year ]]; then
  [[ $infile =~ -ZZ4l[0-9]+.root$ ]] || die "cannot infer year from infile: $infile"
  year=$(echo $infile | sed -E 's|.*-ZZ4l(.*).root|\1|')
fi
[[ -z $outfile ]] && outfile="fakeScaleFactorsRun3-ZZ4l$year.root"

echo Wrapping fake rate for $year
./ScaleFactors/wrapFakeRates.py -o $outfile $infile
echo "$year done!!==================================="
