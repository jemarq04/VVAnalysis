import datetime
from . import UserInput
import fnmatch
import glob
import subprocess
import os
import json
import string

def getManagerPath():
    path = "/cms/uhussain" if "hep.wisc.edu" in os.environ['HOSTNAME'] else \
            "/afs/cern.ch/user/u/uhussain/work"
    return path
def getListOfEWKFilenames():
    return [
        #"wz3lnu-mg5amcnlo",
        "wz3lnu-powheg"
    # Use jet binned WZ samples for subtraction by default
    #    "wz3lnu-mgmlm-0j",
    #    "wz3lnu-mgmlm-1j",
    #    "wz3lnu-mgmlm-2j",
    #    "wz3lnu-mgmlm-3j",
        "zz4l-powheg",
        "ggZZ4e",
        "ggZZ4m",
        "ggZZ2e2mu",
    ]
def getListOfNonpromptFilenames():
    return ["tt-lep",
        "st-schan",
        "st-tchan-t",
        "st-tchan-tbar",
        "st-tw",
        "st-tbarw",
        "DYm50-0j-nlo",
        "DYm50-1j-nlo",
        "DYm50-2j-nlo",
    ]
def getJobName(sample_name, analysis, selection, version):
    date = '{:%Y-%m-%d}'.format(datetime.date.today())
    selections = selection.split(",")
    selection_name = "To".join([selections[0],selections[-1]]) \
        if len(selections) > 1 else selections[0]
    return '-'.join([date, sample_name, analysis, selection_name, 
        ("v%s" % version) if version.isdigit() else version])
def getNumberAndSizeOfLocalFiles(path_to_files):
    file_list = glob.glob(path_to_files)
    return (len(file_list), sum([os.path.getsize(f)/1000000 for f in file_list]))
def getNumberAndSizeOfHDFSFiles(file_path):
    p = subprocess.Popen(["hdfs", "dfs", "-ls", "-h", file_path.replace("/hdfs", "")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    out,err = p.communicate()
    file_info = []
    for line in out.splitlines():
        split = line.split()
        if len(split) != 9:
            continue
        file_info.append(float(split[4].rstrip("mkg")))
    return (0,0) if len(file_info) == 0 else (len(file_info), sum(file_info))
def getListOfHDFSFiles(file_path):
    try:
        out = subprocess.check_output(["hdfs", "dfs", "-ls", file_path.replace("/hdfs", "")], encoding="utf8")
    except subprocess.CalledProcessError as error:
        logging.warning(error)
        return []
    files = []
    for line in out.splitlines():
        split = line.split(" ", 1)
        if len(split) != 2:
            continue
        elif "root" in split[1]:
            files.append("/"+split[1])
    return files
def getListOfFiles(filelist, manager_path):
    data_path = "%s/ZZ4lDatasetManager/FileInfo" % manager_path
    data_info = UserInput.readAllJson("/".join([data_path, "%s.json" % "data/*"]))
    mc_info = UserInput.readAllJson("/".join([data_path, "%s.json" % "montecarlo/*"]))
    valid_names = list(data_info.keys()) + list(mc_info.keys())
    names = []
    for name in filelist:
        print("name in filelist: ",name)
        zz4l="ZZ4l"
        Zl="ZplusL"
        isTight = "Tight" in name
        name = name.replace("Tight","")
        if (zz4l in name) or (Zl in name):
            dataset_file = "%s/ZZ4lDatasetManager/FileInfo/%s/%s.json" % (manager_path, name, "LooseNtuples" if isTight else "ntuples")
            print(dataset_file)
            if not os.path.isfile(dataset_file):
                raise ValueError("Invalid name in filelist: could not find '%s'. If desired, 'Tight' can also be in the name." % dataset_file)
            allnames = list(json.load(open(dataset_file)).keys())
            print(allnames)
            if "nodata" in name:
                nodata = [x for x in allnames if "Run" not in x]
                names += nodata
            elif "Run" in name:
                names += [x for x in allnames if "Run" in x]
            else:
                names += allnames
        elif "*" in name:
            names += fnmatch.filter(valid_names, name)
        else:
            if name.split("__")[0] not in valid_names:
                print("%s is not a valid name" % name)
                continue
            names += [name]
    return names
def fillTemplatedFile(template_file_name, out_file_name, template_dict):
    with open(template_file_name, "r") as templateFile:
        source = string.Template(templateFile.read())
        result = source.substitute(template_dict)
    with open(out_file_name, "w") as outFile:
        outFile.write(result)
def getListOfFilesWithXSec(filelist, manager_path):
    data_path = "%s/ZZ4lDatasetManager/FileInfo" % manager_path
    files = getListOfFiles(filelist, manager_path)
    mc_info = UserInput.readAllJson("/".join([data_path, "%s.json" % "montecarlo/*"]))
    info = {}
    for file_name in files:
        if "Run" in file_name:
            info.update({file_name : 1})
        else:
            file_info = mc_info[file_name.split("__")[0]]
            kfac = file_info["kfactor"] if "kfactor" in list(file_info.keys()) else 1
            info.update({file_name : file_info["cross_section"]*kfac})
    return info
def getPreviousStep(selection, analysis):
    selection_map = {}
    if "ZZ4l" in analysis:
        selection_map = { "ntuples": "ntuples",
                "loosePreselection" : "ntuples",
                "preselection" : "ntuples",
                "TightZZ" : "LooseNtuples",
                "4lCRBase" : "ntuples"
        }
    elif "ZplusL" in analysis:
        selection_map = { "ntuples": "ntuples",
                "ZplusLBase" : "ntuples"
        }
    first_selection = selection.split(",")[0].strip()
    if first_selection not in list(selection_map.keys()):
        if "preselection" in first_selection:
            first_selection = "preselection"
        else:
            raise ValueError("Invalid selection '%s'. Valid selections are:"
                "%s" % (first_selection, list(selection_map.keys())))
    return selection_map[first_selection]
def getInputFilesPath(sample_name, manager_path,selection, analysis):
    data_path = "%s/ZZ4lDatasetManager/FileInfo" % manager_path
    input_file_name = "/".join([data_path, analysis, "%s.json" %
        selection])
    input_files = UserInput.readJson(input_file_name)
    if sample_name not in list(input_files.keys()):
        raise ValueError("Invalid input file %s. Input file must correspond"
               " to a definition in %s" % (sample_name, input_file_name))
    filename = input_files[sample_name]['file_path']
    #print "filename: ",filename
    return filename
def getCutsJsonName(selection, analysis):
    return "/".join(["Cuts", analysis, selection + ".json"]) 
def getTriggerName(sample_name,analysis, selection):
    trigger_names = ["MuonEG", "DoubleMuon", "DoubleEG","EGamma", "SingleMuon", "SingleElectron"]
    if "Run" in sample_name and (getPreviousStep(selection, analysis) == "ntuples" or getPreviousStep(selection, analysis) == "LooseNtuples"):
        for name in trigger_names:
            if name in sample_name:
                return "-t " + name
    return "-t MonteCarlo"
