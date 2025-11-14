if [[ $# -ne 1 ]]; then
  echo usage: $0 YEAR
  exit 1
elif [[ ! $1 =~ ^202[2-3]$ && ! $1 = Run3Combined ]]; then
  echo invalid year: $1
  exit 1
fi

./Utilities/scripts/makeFakeRates.py -a ZZ4l$1 -f ZZ4l$1 --year $1 -s ZplusLSkim --uwvv --noHistConfig --output_file fakeRates-ZZ4l$1.root && ./ScaleFactors/wrapFakeRates.py -o data/fakeScaleFactorsRun3-ZZ4l$1.root fakeRates-ZZ4l$1.root
echo Done.
