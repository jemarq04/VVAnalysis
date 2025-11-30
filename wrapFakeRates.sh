if [[ $# -ne 1 ]]; then
  echo usage: $0 FILE YEAR
  echo
  echo "FILE: input file to wrap"
  echo "YEAR: year for analysis"
  exit 1
elif [[ ! -f $1 ]]; then
  echo invalid file: $1
  exit 1
fi

infile=$1
year=$2

./ScaleFactors/wrapFakeRates.py -o data/fakeScaleFactorsRun3-ZZ4l$year.root $infile
echo "$year done!!==================================="
