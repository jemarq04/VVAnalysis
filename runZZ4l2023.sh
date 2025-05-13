#NOTE: Eventually the scale factor file listed below will exist with fake rates.
#   For now, use this in the call so that the appropriate scale factors are retrieved with correctionlib
#./Utilities/scripts/makeHistFile.py -f ZZ4l2023 -l 27.76 -a ZZ4l2023 -s LooseLeptons --output_file test2023 --year 2023 --uwvv -c eeee,eemm,mmee,mmmm -j 12 --with_background -sf -F data/latestSFs/scalefactorsZZ4l2023.root #--with_Gen
./Utilities/scripts/makeHistFile.py -f ZZ4l2023 -l 27.76 -a ZZ4l2023 -s LooseLeptons --output_file test2023 --year 2023 --uwvv -c eeee,eemm,mmee,mmmm -j 12 -sf #--with_Gen

echo "Job done!!==================================="
