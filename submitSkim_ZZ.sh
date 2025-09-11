if [[ $# -lt 1 ]]; then
  echo usage: $0 YEAR [EXTRA]
  echo
  echo "YEAR: any year in Run 3 for analysis"
  echo "[EXTRA]: optional argument(s) passed directly to script"
  exit 1
fi

year=$1
shift 1

#./farmoutNtupleSkim.py -a ZZ4l$year -s loosePreselection,Zselection,Overlap,QCDVeto,smartCut,4lmass -f ZZ4l$year -e-gen 

./farmoutNtupleSkim.py -a ZZ4l$year -s loosePreselection,Zselection,Overlap,QCDVeto,smartCut,4lmass -f ZZ4l$year $@
