#!/usr/bin/env python3
import argparse
import json
import os
import sys
import datetime
import subprocess
import glob
from Utilities.python import UserInput
from Utilities.python import ConfigureJobs
import math
import logging
import pdb

def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--scaleFacs", action='store_true',
                        help="Add lepton and pilup scale factors to "
                        "ntuple (by default they are not added)")
    parser.add_argument("--deduplicateAcrossChannels", action='store_true',
                        help="Add a flag deduplicated==1 to ntuple for an event" 
                        "in a channel (eeee/eemm/mmmm) that does not belong to that"
                        "channel. This deduplication across channels only needs to happen"
                        "in MC samples")
    parser.add_argument("-e", "--extraArgs", type=str, default='',
                        help="Extra arguments to pass to skimNtuples script")
    parser.add_argument("--noSubmit", action='store_true',
                        help="Create submit scripts but don't call farmout")
    return vars(parser.parse_args())

def getFilesPerJob(path_to_files):
    file_type = "Local" if "store" not in path_to_files else "HDFS"
    if file_type=="Local":
        num, tot_size = getattr(ConfigureJobs, "getNumberAndSizeOf%sFiles" % file_type)(path_to_files)
        if num == 0:
            raise ValueError("Size of file list is zero for path: %s" % path_to_files)
        print("Number: ",num)
        print("TotSize: ",tot_size)
        return 1
    else:
        num, tot_size = getattr(ConfigureJobs, "getNumberAndSizeOf%sFiles" % file_type)(path_to_files)
        if num == 0:
            raise ValueError("Size of file list is zero for path: %s" % path_to_files)
        average_size = tot_size/num
        return int(math.ceil(200./average_size))
# The intention here was to make sure the output order isn't jumbled together,
# as it is when subprocess outputs are written together. This is an admittedly
# sloppy solution, however
def callFarmout(output_dir, script_name, noSubmit):
    log_file_name = '/'.join([output_dir, 'log.txt'])
    with open(log_file_name, 'w') as log:
        log.write('Condor submit info created with the command:'
            '\n    %s\n' % ' '.join(sys.argv))
        log.write('Using VVAnalysis code by Kenneth Long (U. Wisconsin):\n')
        log.write('https://github.com/uhussain/VVAnalysis\n\n')
        log.write('The git hash of the commit used and the output of git diff is below\n') 
        log.write('-'*80 + '\n')
        log.write('-'*80 + '\n')
    with open(log_file_name, 'a') as log:
        subprocess.call(['git', 'log', '-1', '--format="%H"'], stdout=log)
        subprocess.call(['git', 'diff'], stdout=log)
    with open(log_file_name, 'a') as log:
        log.write('\n' +'-'*80 + '\n')
        log.write('-'*80 + '\n\n')
        log.write('The output of the generated farmout.sh script is below\n')
    status = 2
    farmout_command = ['bash', script_name]
    if noSubmit:
        farmout_command.append("--no-submit")
    with open(log_file_name, 'a') as log:
        status = subprocess.call(farmout_command, stdout=log, stderr=log)
    if status != 0:
        print("Error in submitting files to condor. Check the log file: %s" % log_file_name)
    if noSubmit: status = -1
    return status
def farmoutNtupleSkim(sample_name, path, selection, analysis, version, scaleFacs, deduplicateAcrossChannels, noSubmit, extraArgs):
    farmout_dict = {}
    farmout_dict['input_files_path'] = ConfigureJobs.getInputFilesPath(
        sample_name, 
        path,
        ConfigureJobs.getPreviousStep(selection, analysis), 
        analysis
    )
    job_name = ConfigureJobs.getJobName(sample_name, analysis, selection, version) 
    farmout_dict['base_dir'] = os.path.dirname(os.path.realpath(sys.argv[0]))
    first_selection = selection.split(",")[0].strip()
    #pdb.set_trace()
    if first_selection=="4lCRBase":
        submission_dir = ("/nfs_scratch/marquez5/%s") \
            % '{:%Y-%m-%d}_%sAnalysisJobs'.format(datetime.date.today()) %analysis
    elif first_selection=="ZplusLBase":
        #submission_dir = ("/nfs_scratch/marquez5/%s") \
        #    % '{:%Y-%m-%d}_%sAnalysisJobs'.format(datetime.date.today()) %analysis
        submission_dir = ("/nfs_scratch/marquez5/%s") \
            % '2019-09-12_%sAnalysisJobs' %analysis

    else:
        submission_dir = ("/nfs_scratch/marquez5/%s") \
            % '{:%Y-%m-%d}_%sAnalysisJobs'.format(datetime.date.today()) %analysis
        #submission_dir = ("/nfs_scratch/marquez5/%s") \
        #    % '2019-09-12_%sAnalysisJobs' %analysis
    try:
        os.mkdir(submission_dir)
    except:
        pass
    farmout_dict['job_dir'] = submission_dir + "/" + job_name
    #This is to make sure the copyTree function does not fail with memory allocation due to big trees especiall in ZZ4l samples!
    if ("Run" not in sample_name):
        farmout_dict['files_per_job'] = 1
    else:
        farmout_dict['files_per_job'] = getFilesPerJob(farmout_dict['input_files_path'])
    farmout_dict['job_name'] = job_name
    farmout_dict['Analysis'] = analysis
    farmout_dict['time'] = datetime.datetime.now()
    farmout_dict['command'] = ' '.join(sys.argv)
    script_name = '/'.join([farmout_dict['job_dir'], 'farmout.sh'])
    os.mkdir(farmout_dict['job_dir'])
    ConfigureJobs.fillTemplatedFile('/'.join([farmout_dict['base_dir'], 
        'Templates/farmout_template.sh']),
        script_name, 
        farmout_dict
    )
    createRunJob(farmout_dict['base_dir'], 
        farmout_dict['job_dir'],
        selection,
        analysis,
        ConfigureJobs.getTriggerName(sample_name,analysis, selection),
        scaleFacs and ("Run" not in sample_name),
        deduplicateAcrossChannels and ("Run" not in sample_name), 
        extraArgs
    )
    status = callFarmout(farmout_dict['job_dir'], script_name, noSubmit)
    if status == 0:
        print("Submitted jobs for %s file set to condor." % sample_name)
    elif status == -1: 
        print("Test run: submit directory created but not submitted")
    else:
        print("Jobs not submitted")
def createRunJob(base_dir, job_dir, selection, analysis, trigger_name, addScaleFacs, addDuplicatedFlag, extraArgs):
    fill_dict = {'selection' : selection,
        'analysis' : analysis,
        'time' : datetime.datetime.now(),
        'trigger' : trigger_name,
        'command' : ' '.join(sys.argv),
        'extraArgs' : extraArgs,
        'addScaleFacs' : addScaleFacs,
        'addDuplicatedFlag': addDuplicatedFlag,
    }
    ConfigureJobs.fillTemplatedFile('/'.join([base_dir, 'Templates/skim_template.sh']),
        '/'.join([job_dir, 'skim.sh']), fill_dict)
def main():
    #for selection in selection_map.iteritems():
    args = getComLineArgs()
    if not "CMSSW_BASE" in os.environ:
        print("cmsenv not found")
        return
    path = "%s/src/Data_manager" % os.environ["CMSSW_BASE"]
    #path = "/afs/hep.wisc.edu/home/hhe62/vvanalysis_skim/CMSSW_10_3_1/src/Data_manager" if "hep.wisc.edu" in os.environ['HOSTNAME'] else \
    #        "/afs/cern.ch/user/h/hehe/work"
    print(os.environ['HOSTNAME'])
    print(path)
   # pdb.set_trace()
    print(ConfigureJobs.getListOfFiles(args['filenames'], path))
    
    for file_name in ConfigureJobs.getListOfFiles(args['filenames'], path):
        try:
            farmoutNtupleSkim(file_name, path, args['selection'], 
                args['analysis'], args['version'], args['scaleFacs'], args['deduplicateAcrossChannels'], 
                args['noSubmit'], args['extraArgs'])
        except (ValueError, OSError) as error:
            logging.warning(error)
            logging.warning("Skipping submission for %s" % file_name)

if __name__ == "__main__":
    main()
