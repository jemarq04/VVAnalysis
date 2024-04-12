#./Utilities/scripts/makeHistFile.py -a ZZ4l2018 -s LooseLeptons --output_file test2018 --muIDType MVA --year 2018 --uwvv -c eeee,eemm,mmee,mmmm -f ZZ4l2018 -j 12 --with_background -sf data/latestSFs/scaleFactorsZZ4l2018.root #--with_Gen
./Utilities/scripts/makeHistFile.py -a ZZ4l2018 -s LooseLeptons --output_file test2018 --muIDType MVA --year 2018 --uwvv -c eemm -f ZZ4l2018 -j 12 --with_background -sf data/latestSFs/scaleFactorsZZ4l2018.root #--with_Gen

echo "Job done!!==================================="
