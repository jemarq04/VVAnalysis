#!/bin/bash

# Parsing Strings
optstring="hi:o:"
loptstring="help,infile:,outdir:,extra-args:"

# Variables
all_years="2022 2023 2024 2025"
outdir="CombineCards"
extra_args=""

# ========== Argument Parsing Helper Functions ==========
function print_usage() {
  # Prints usage based on opts/args defined with '#--:' comments
  local opts="[OPTS]"
  local reqopts=$(egrep -i '#\-\-:\s+reqopt\s' $0 | sed -E 's/^\s*#\-\-:\s+@reqopt\s+(.*)/\1/' | xargs)
  [[ -n $reqopts ]] && local opts="$opts $reqopts"
  local args=$(egrep -i '#\-\-:\s+@arg\s' $0 | sed -E 's/^\s*#\-\-:\s+@arg\s+(.*)/\1/' | xargs)
  echo "usage: $0 $opts $args"
}

function print_help() {
  # Prints help based on opts/args defined with '#--:' comments
  local optshelp=$(egrep -i '#\-\-: @(req)?opt' $0 | sed -E 's/^\s*#\-\-:\s+@(req)?optdesc\s+(.*)/   \2\n/' | sed -E 's/^\s*#\-\-: @(req)?opt\s+(.*)/ \2/')
  local argshelp=$(egrep -i '#\-\-: @arg' $0 | sed -E 's/^\s*#\-\-:\s+@argdesc\s+(.*)/   \1\n/' | sed -E 's/^\s*#\-\-: @arg\s+(.*)/ \1/')

  print_usage
  if [[ -n $optshelp ]]; then
    echo
    echo OPTS
    echo "$optshelp"
  fi
  if [[ -n $argshelp ]]; then
    echo
    echo ARGS
    echo "$argshelp"
  fi
  exit 1
}

function die() {
  print_usage
  [[ -z $1 ]] && local message="unknown error" || local message="$1"
  echo "error: $message"
  exit 1
}

PARSED=$(getopt -n $0 -o $optstring --long $loptstring -- "$@")
[[ $? -ne 0 ]] && echo && die "failed to parse arguments"
eval set -- "$PARSED"

# ========== Argument Parsing ==========

# Argument Loop
while true; do
  case "$1" in
  -h | --help)
    #--: @opt -h/--help
    #--: @optdesc Print help and exit
    print_help
    ;;
  -i | --infile)
    #--: @opt -i/--infile FILE
    #--: @optdesc Path for systematics file (default: HistFiles/SystHists-ZZ4l$year.root)
    infile="$2"
    [[ ! -f $infile ]] && die "invalid file: $infile"
    shift 2
    ;;
  -o | --outdir)
    #--: @opt -o/--outdir DIR
    #--: @optdesc Path to output directory for generated cards (default: CombineCards/)
    outdir="$2"
    [[ ! -d $outdir ]] && die "invalid dir: $outdir"
    shift 2
    ;;
  --extra-args)
    #--: @opt --extra-args EXTRA
    #--: @optdesc Extra arguments to pass directly to setupZZCombineRun3.py
    extra_args="$2"
    shift 2
    ;;
  --)
    shift
    break
    ;;
  *)
    echo "encountered $1"
    break
    ;;
  esac
done

# Positional Arguments Check
[[ $# -lt 1 ]] && print_help

# Positional Arguments
#--: @arg year [year ...]
#--: @argdesc The years for analysis or 'all' to run all of Run 3
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
