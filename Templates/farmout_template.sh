#!/bin/bash
# This script was created at ${time} with the command: 
#     ${command}
#
# To resubmit failed jobs: ./farmout.sh --resubmit-failed-jobs
DATE=`date +%Y-%m-%d`
#DATE=2019-09-11
pushd ${base_dir}
if [ ! -f ${job_dir}/analysis_code.tar.gz ]; then
    tar \
        -zcvhf ${job_dir}/analysis_code.tar.gz \
        Cuts/ \
        Utilities/ \
        skimNtuples.py
fi
if [ ! -f ${job_dir}/input_file_list.txt ]; then
./Utilities/scripts/makeInputFilesList.py \
    -o ${job_dir}/input_file_list.txt \
    -p "${input_files_path}" \
    --only_root_files
fi
popd
#--output-dir=gsiftp://cms-lvs-gridftp.hep.wisc.edu:2811//hdfs/store/user/$$USER/ZZ4l2016AnalysisJobs_$$DATE/${job_name} \
chmod +x ${job_dir}/skim.sh
#NOTE: Changed $$USER to marquez below
farmoutAnalysisJobs \
    --fwklite \
    --output-dir=/store/user/marquez/${Analysis}AnalysisJobs_$$DATE/${job_name} \
    --input-file-list=${job_dir}/input_file_list.txt \
    --submit-dir=${job_dir}/submit \
    --input-files-per-job=1 \
    --input-dir=root://cmsxrootd.hep.wisc.edu/ \
    --assume-input-files-exist \
    --extra-inputs=${job_dir}/analysis_code.tar.gz \
    --input-basenames-not-unique \
    --opsys=AlmaLinux9 \
    $$1 \
    ${job_name} \
    $$CMSSW_BASE \
    ${job_dir}/skim.sh
