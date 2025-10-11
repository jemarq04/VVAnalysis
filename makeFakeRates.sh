if [[ $# -ne 1 ]]; then
  echo usage: $0 YEAR
  exit 1
elif [[ ! $1 =~ ^202[2-3]$ && ! $1 = Run3Combined ]]; then
  echo invalid year: $1
  exit 1
fi

if [[ $1 = 2022 ]]; then lumi=34.652;
elif [[ $1 = 2023 ]]; then lumi=27.76;
elif [[ $1 = Run3Combined ]]; then lumi=62.412;
fi

./Utilities/scripts/makeFakeRates.py -a ZZ4l$1 -f ZZ4l$1 --year $1 -s ZplusLSkim -l $lumi --uwvv --noHistConfig --output_file fakeRates-ZZ4l$1.root && ./ScaleFactors/wrapFakeRates.py -o data/fakeScaleFactorsRun3-ZZ4l$1.root fakeRates-ZZ4l$1.root
echo Done.
