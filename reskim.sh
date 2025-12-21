if [[ $# -lt 1 ]]; then
  echo usage: $0 JOBS_DIR OUT_DIR INCLUDE_MC
  echo
  echo "JOBS_DIR: directory in /nfs_scratch for relevant jobs"
  echo "OUT_DIR: directory in /hdfs/store for output files"
  echo "INCLUDE_MC: 0=no, 1=yes. (default: 0)"
  exit 1
fi

jobsdir=$1
outdir=$2
if [[ ! -z $3 ]]; then
  [[ $3 -eq 0 ]] && include_mc=0 || include_mc=1
else
  include_mc=0
fi

if [[ ! -d $jobsdir ]]; then
  echo invalid directory: $jobsdir
  exit 1
elif [[ ! -d $outdir ]]; then
  echo invalid directory: $outdir
  exit 1
fi

if [[ $(basename $outdir) =~ ^ZZ4l ]]; then
  jobtype=ZZ4l
  selections="loosePreselection,Zselection,Overlap,QCDVeto,smartCut,4lmass"
elif [[ $(basename $outdir) =~ ^ZplusL ]]; then
  jobtype=ZplusL
  selections="ZplusLBase,Zselection,LepPt,LepOverlap,4lVeto"
else
  echo "couldn't determine job type (ZZ4l or ZplusL) from outdir: $outdir"
  exit 1
fi
[[ $jobsdir =~ $jobtype([0-9]+)AnalysisJobs ]] && year="${BASH_REMATCH[1]}"

if [[ -z $year ]]; then
  echo "couldn't determine year from input directory: $jobsdir"
  exit 1
fi

for group in $jobsdir/*/; do
  [[ ! -d $group ]] && continue
  if [[ $group = *data_*Run$year* ]]; then
    if [[ $group =~ data_(.*)_Run$year ]]; then
      trigger="${BASH_REMATCH[1]}"
    else
      echo "Error determining trigger for $group. Skipping..."
      continue
    fi
  else
    [[ $include_mc -eq 0 ]] && continue
    trigger="MonteCarlo"
  fi
  [[ $include_mc -eq 0 && ! $group = *data_*Run$year* ]] && continue
  groupname=$(basename $group)
  if [[ ! -d $outdir/$groupname ]]; then
    echo "couldn't find output directory for $groupname in $outdir"
    echo Skipping...
    continue
  fi
  echo Checking ${groupname%%-$jobtype$year*}...

  for dir in $group/submit/*/; do
    name=$(basename $dir)
    if [[ ! -e $outdir/$groupname/$name.root ]]; then
      valid_inputs=true
      while read line; do
        if [[ $line = root* ]]; then
          if [[ ! -e ${line/*store/\/hdfs\/store} ]]; then
            valid_inputs=false
            break
          fi
        elif [[ ! -e $line ]]; then
          echo does not start with root? $line
          [[ $line = root* ]] && echo but it does...
          valid_inputs=false
          break
        fi
      done < $dir/$name.inputs
      if ! $valid_inputs; then
        echo "Inputs for $dir cannot be found:"
        cat $dir/$name.inputs
        echo "Skipping..."
        continue
      fi

      echo Skimming $(cat $dir/$name.inputs)...
      ./skimNtuples.py -s $selections -a $jobtype$year -t $trigger -f $dir/$name.inputs -o temp_reskim.root && mv -v temp_reskim.root $outdir/$groupname/$name.root
      echo
    fi
  done
done
echo Done.
