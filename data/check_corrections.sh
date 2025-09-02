#!/bin/bash

for pog in POG/*/; do
  [[ ! -d $pog ]] && break
  for era in ${pog}*/; do
    [[ ! -d $era ]] && break
    for f in ${era}*.json.gz; do
      [[ ! -f $f || -L $f ]] && continue

      centralfile="/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/$f"
      if ! diff $f $centralfile >& /dev/null; then
        echo
        echo $f is out-of-date.
        read -p "Update the file? (y/n): " choice
        [[ $choice == [yY] ]] && cp -v $centralfile $f
      fi  
    done
  done
done
