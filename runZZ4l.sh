#!/bin/bash

# Parsing Strings
optstring="hgs"
loptstring="help,gen,syst,frfile:"

# Variables
extra_args="--with_background"
all_years="2022 2023 2024 2025"

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
  -g | --gen)
    #--: @opt -g/--gen
    #--: @optdesc Enable ZZGenSelector
    extra_args="$extra_args --with_Gen"
    shift
    ;;
  -s | --syst)
    #--: @opt -s/--syst
    #--: @optdesc Enable systematic variations
    extra_args="$extra_args --doSystematics"
    shift
    ;;
  --frfile)
    #--: @opt --frfile FILE
    #--: @optdesc Path for fake rate scale factors file (default: data/fakeScaleFactorsRun3-ZZ4l$year.root)
    frfile="$2"
    [[ ! -f $frfile ]] && die "invalid file: $frfile"
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

  echo ./Utilities/scripts/makeHistFile.py -f ZZ4l$year -a ZZ4l$year -s LooseLeptons --year $year -c eeee,eemm,mmee,mmmm -j 12 -sf -F $frtmpfile $extra_args

  echo "$year done!!==================================="
done
