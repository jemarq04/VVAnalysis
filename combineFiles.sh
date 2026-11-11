#!/bin/bash

source Utilities/scripts/BashArgParse.sh
#@opt -h/--help
#@optdesc Print help and exit
#@opt -a/--analysis ANALYSIS
#@optdesc Name of combined analysis (default: ZZ4lRun3Combined)
#@arg infile [infile ...]
#@argdesc Infile(s) to combine

optstring="h/help*,a/analysis:"
analysis=ZZ4lRun3Combined

parse_args "$0" "$optstring" 1 "$@"
eval set -- "$PARSED"

for f in "$@"; do
  [[ ! -f $f ]] && die "invalid file: $f"
done

./Utilities/scripts/combineFiles.py -f -a $analysis $@
