if [[ $# -ne 1 ]]; then
  echo usage: $0 YEAR/ALL
  echo
  echo "YEAR/ALL: year for analysis or 'all' to run all Run 3"
  exit 1
elif [[ ! $1 =~ ^202[2-3]$ ]]; then
  echo invalid year: $1
  exit 1
fi

year=$1
[[ $year = all ]] && year="2022 2023"

for yr in $year; do
  if [[ $yr = 2022 ]]; then lumi=34.652;
  elif [[ $yr = 2023 ]]; then lumi=27.76;
  fi
  frfile=data/fakeScaleFactorsRun3-ZZ4l$yr.root

  #NOTE: Eventually the scale factor file listed below will exist with fake rates.
  #   For now, use this in the call so that the appropriate scale factors are retrieved with correctionlib
  #./Utilities/scripts/makeHistFile.py -f ZZ4l$yr -l $lumi -a ZZ4l$yr -s LooseLeptons --output_file "test$yr" --year $yr --uwvv -c eeee,eemm,mmee,mmmm -j 12 -sf #--with_Gen
  ./Utilities/scripts/makeHistFile.py -f ZZ4l$yr -l $lumi -a ZZ4l$yr -s LooseLeptons --output_file "test$yr" --year $yr --uwvv -c eeee,eemm,mmee,mmmm -j 12 -sf --with_background -F $frfile

  echo "$yr done!!==================================="
done
