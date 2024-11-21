#NOTE: Eventually the scale factor file listed below will exist with fake rates.
#   For now, use this in the call so that the appropriate scale factors are retrieved with correctionlib
./Utilities/scripts/makeHistFile.py -f ZZ4l2022 -a ZZ4l2022 -s LooseLeptons --output_file test2022 --year 2022 --uwvv -c eemm -j 12 --with_background -sf data/latestSFs/scaleFactorsZZ4l2022.root #--with_Gen

echo "Job done!!==================================="
