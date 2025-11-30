if [[ $# -ne 1 ]]; then
  echo usage: $0 YEAR/ALL
  echo
  echo "YEAR/ALL: year for analysis or 'all' to run all Run 3"
  exit 1
fi

years=$1
[[ $years = all ]] && years="2022 2023 2024"

for year in $years; do
  ./Utilities/scripts/makeFakeRates.py -a ZZ4l$year -f ZZ4l$year --year $year -s ZplusLSkim --uwvv --noHistConfig --output_file fakeRates-ZZ4l$year.root
  echo "$year done!!==================================="
done
