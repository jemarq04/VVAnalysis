import datetime
from . import UserInput
import fnmatch
import glob
import subprocess
import os
import json
import array
import string
import socket
import logging
#try:
import configparser
#except:
    #import ConfigParser as configparser
    #from six.moves import configparser

def get2DBinning(xvar="mjj", yvar="etajj", analysis='WZ'):
    #return (array.array('d', [500, 1000,1500, 2000, 2500]),
    # [0, 150, 300, 450] # for MT(WZ)
#    return (array.array('d', [500, 1000, 1350, 1750, 2000, 2500]),
    xbinning = []
    ybinning = []
    if xvar == "mjj":
        xbinning = array.array('d', [500, 1000,1500, 2000, 2500])
        #xbinning = array.array('d', [500, 1000, 1350, 1750, 2500])

    if yvar == 'etajj':
        ybinning = [2.5, 4, 5, 20]
    #if yvar == 'etajj':
    #    ybinning = [2.5, 4, 5.5, 20]
    elif yvar == 'dRjj':
        ybinning = [0, 5, 6, 20]
    return (xbinning, ybinning)

def getBinning(variable='MTWZ', isVBS=True, isHiggs=False):
    if variable == 'MTWZ':
        if isVBS:
            if isHiggs:
                return [0,50,100,150,200,250,300,400,500,700,1000,1500,2000]
            return [0,100,200,300,400,500,700,1000,1500,2000]
        return [0,50,100,200,300,400,500,700,1000,1200]
    return []

def getChannels(analysis='WZ'):
    if analysis == 'WZ':
        return ["eee", "eem", "emm", "mmm"]

def getManagerName():
    config_name = "Templates/config.%s" % os.getlogin()
    default_name = "AnalysisDatasetManager"
    if not os.path.isfile(config_name):
        logging.warning("dataset_manager_name not specified in config file %s" % config_name)
        logging.warning("Using default '%s'" % default_name)
        return default_name
    config = configparser.ConfigParser()
    config.read_file(open(config_name))
    if "dataset_manager_name" not in config['Setup']:
        logging.warning("dataset_manager_name not specified in config file %s" % config_name)
        logging.warning("Using default '%s'" % default_name)
        return default_name
    return config['Setup']['dataset_manager_name']

def getManagerPath():
    config_name = "Templates/config.%s" % os.getlogin()
    if not os.path.isfile(config_name):
        if os.path.isdir(getManagerName()):
            return '.'
        else:
            raise IOError("Failed to find valid config file. Looking for %s"
                    % config_name)
    config = configparser.ConfigParser()
    config.read_file(open(config_name))
    if "dataset_manager_path" not in config['Setup']:
        raise ValueError("dataset_manager_path not specified in config file %s"
                        % config_name)
    return config['Setup']['dataset_manager_path'].replace("$CMSSW_BASE", os.environ["CMSSW_BASE"]) + "/"

def getLumiMap(manager_path = ""):
    if manager_path == "":
        manager_path = getManagerPath()
    lumi_path = "%s/%s/luminosityMap.json" % (manager_path, getManagerName())
    with open(lumi_path) as infile:
        info = json.load(infile)
    return info

def getCombinePath():
    config = configparser.ConfigParser()
    config.read_file(open("Templates/config.%s" % os.environ["USER"]))
    if "combine_path" not in config['Setup']:
        raise ValueError("combine_path not specified in config file Template/config.%s"
                            % os.environ["USER"])
    return config['Setup']['combine_path'] + "/"
def getListOfGenFilenames(analysis='ZZ'):
    if 'ZZ' in analysis:
        return [
            "zz4l-amcatnlo",
            "zz4l-powheg",
            #"qqZZSpec",
            "ZZJJTo4L-EWK",
            "ggZZ4e",
            "ggZZ4m",
            "ggZZ4t",
            "ggZZ2e2mu",
            "ggZZ2e2tau",
            "ggZZ2mu2tau",
            "ggHZZ",
            "ttH_HToZZ_4L",
            "WminusHToZZ",
            "WplusHToZZ",
            "ZHToZZ_4L",
            "vbfHZZ",
        ]
    return []
def getListOfEWKFilenames(analysis=""):
    lumi_info = getLumiMap()

    if "ZZ4l" in analysis:
        outlist = [
            #"zz4l-amcatnlo",
            "zz4l-powheg",
            #"ZZJJTo4L-EWK",
            "ggZZ4e",
            "ggZZ4m",
            "ggZZ4t",
            "ggZZ2e2mu",
            "ggZZ2e2tau",
            "ggZZ2mu2tau",
        ]
        for year in lumi_info.keys():
            if f"ZZ4l{year}" in analysis:
                eras = ["_%s" % x for x in getLuminosityEras(year)]
                if not eras:
                    eras = [""]
                outlist = ["%s%s" % (name, era) for name in outlist for era in eras]
        return outlist
    elif "ZplusL" in analysis:
        outlist = [
            "wz3lnu-powheg",
            #"wz3lnu-mgmlm-0j",
            #"wz3lnu-mgmlm-1j",
            #"wz3lnu-mgmlm-2j",
            #"wz3lnu-mgmlm-3j",
            #"wlljj-ewk",
            "zz4l-powheg",
            "zzjj4l-ewk",
            #"zz2l2vjj-ewk",
            #"tzq",
            "ttZ",
            #"ttw",
            "ZZZ",
            "WWZ",
            "WZZ",
            #"ww",
            #"zg",
            "ggZZ4e",
            "ggZZ4m",
            "ggZZ4t",
            "ggZZ2e2mu",
            "ggZZ2e2tau",
            "ggZZ2mu2tau",
        ]
        for year in lumi_info.keys():
            if f"ZplusL{year}" in analysis:
                eras = ["_%s" % x for x in getLuminosityEras(year)]
                if not eras:
                    eras = [""]
                outlist = ["%s%s" % (name, era) for name in outlist for era in eras]
        return outlist

    return []
def getListOfDYFilenames(analysis=""):
    lumi_info = getLumiMap()
    outlist = [
        "DYm10to50-2j",
        "DYm50-2j",
    ]
    #TODO: Replace with checks to plotgroups json file. Add symlinks for ZplusL
    if any(year in analysis for year in ["2024", "2025"]):
        outlist = [
            "DY2e-m10to50",
            "DY2m-m10to50",
            "DY2t-m10to50",
            "DY2e-m50-2j",
            "DY2m-m50-2j",
            "DY2t-m50-2j",
        ]

    for year in lumi_info.keys():
        if year in analysis:
            eras = ["_%s" % x for x in getLuminosityEras(year)]
            if not eras:
                eras = [""]
            outlist = ["%s%s" % (name, era) for name in outlist for era in eras]
    return outlist

def getListOfNonpromptFilenames():
    return ["tt-lep",
        "st-schan",
        "st-tchan-t",
        "st-tchan-tbar",
        "st-tw",
        "st-tbarw",
        #"DYm50",
        "DYm50-1j",
        "DYm50-2j",
        "DYm50-3j",
        "DYm50-4j",
    ]
def getJobName(sample_name, analysis, selection, version):
    date = '{:%Y-%m-%d}'.format(datetime.date.today())
    selection = selection.replace(";",",")
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
            stderr=subprocess.PIPE
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
        split = line.rsplit(" ", 1)
        if len(split) != 2:
            continue
        elif "root" in split[1]:
            files.append(split[1])
    return files

# TODO: Would be good to switch the order of the last two arguments
# completely deprecate manager_path without breaking things
def getListOfFiles(filelist, selection, manager_path="", analysis=""):
    if manager_path == "":
        manager_path = getManagerPath()
    data_path = "%s/%s/FileInfo" % (manager_path, getManagerName())
    data_info = UserInput.readAllInfo("/".join([data_path, "data/*"]))
    mc_info = UserInput.readAllInfo("/".join([data_path, "montecarlo/montecarlo*"]))
    analysis_info = UserInput.readInfo("/".join([data_path, analysis, selection])) \
        if analysis != "" else []
    lumi_info = getLumiMap(manager_path)
    valid_names = (list(data_info.keys()) + list(mc_info.keys())) if not analysis_info else list(analysis_info.keys())
    names = []
    for name in filelist:
        if ".root" in name:
            names.append(name)
        elif any("ZZ4l%s" % year in name for year in lumi_info.keys()):
            key = ["ZZ4l%s" % year for year in lumi_info.keys() if "ZZ4l%s" % year in name][0]
            dataset_file = manager_path + \
                "%s/FileInfo/%s/%s.json" % (getManagerName(), key, selection)
            allnames = list(json.load(open(dataset_file)).keys())
            if "nodata" in name:
                names += [x for x in allnames if "data" not in x]
            elif "data" in name:
                names += [x for x in allnames if "data" in x]
            else:
                names += allnames
        elif "*" in name:
            names += fnmatch.filter(valid_names, name)
        else:
            if name.split("__")[0] not in valid_names:
                print("%s is not a valid name" % name)
                print("Valid names must be defined in AnalysisDatasetManager/FileInfo/(data/montecarlo)*")
                continue
            names += [name]
    return [str(i) for i in names]

def getXrdRedirector():
    usbased = ["wisc.edu"]
    usredir = 'cmsxrootd.fnal.gov'
    globalredir = 'cms-xrd-global.cern.ch'
    # Cluster machines may not have this env variable
    if any(i in socket.gethostname() for i in usbased):
        return usredir
    return globalredir

def fillTemplatedFile(template_file_name, out_file_name, template_dict):
    with open(template_file_name, "r") as templateFile:
        source = string.Template(templateFile.read())
        result = source.substitute(template_dict)
    with open(out_file_name, "w") as outFile:
        outFile.write(result)

def getListOfFilesWithXSec(filelist, manager_path="", selection="ntuples"):
    if manager_path == "":
        manager_path = getManagerPath()
    data_path = "%s/%s/FileInfo" % (manager_path, getManagerName())
    files = getListOfFiles(filelist, selection, manager_path)
    mc_info = UserInput.readAllInfo("/".join([data_path, "montecarlo/montecarlo*"]))
    info = {}
    for file_name in files:
        if "data" in file_name.lower() or "nonprompt" in file_name.lower():
            info.update({file_name : 1})
        else:
            file_info = mc_info[file_name.split("__")[0]]
            kfac = file_info["kfactor"] if "kfactor" in list(file_info.keys()) else 1
            info.update({file_name : file_info["cross_section"]*kfac})
    return info

def getListOfFilesWithDASPath(filelist, analysis, selection, manager_path=""):
    if manager_path == "":
        manager_path = getManagerPath()
    data_path = "%s/%s/FileInfo" % (manager_path, getManagerName())
    files = getListOfFiles(filelist, selection, manager_path, analysis)
    selection_info = UserInput.readInfo("/".join([data_path, analysis, selection]))
    info = {}
    for file_name in files:
        if "DAS" not in list(selection_info[file_name].keys()):
            print("ERROR: DAS path not defined for file %s in analysis %s/%s" % (file_name, analysis, selection))
            continue
        info.update({file_name : selection_info[file_name]["DAS"]})
    return info

def getConfigFileName(config_file_name):
    for extension in ["json", "py"]:
        if os.path.isfile(".".join([config_file_name, extension])):
            return ".".join([config_file_name, extension])
    raise ValueError("Invalid configuration file. Tried to read %s which does not exist" % \
            config_file_name)

def getInputFilesPath(sample_name, selection, analysis, manager_path=""):
    if manager_path == "":
        manager_path = getManagerPath()
    if ".root" in sample_name:
        print("INFO: using simple file %s" % sample_name)
        return sample_name
    data_path = "%s/%s/FileInfo" % (manager_path, getManagerName())
    input_file_base_name = "/".join([data_path, analysis, selection])
    input_file_name = getConfigFileName(input_file_base_name)
    input_files = UserInput.readInfo(input_file_name)
    if sample_name not in list(input_files.keys()):
        raise ValueError("Invalid input file %s. Input file must correspond"
               " to a definition in %s" % (sample_name, input_file_name))
    filename = input_files[sample_name]['file_path']
    return filename

def getCutsJsonName(selection, analysis):
    return "/".join(["Cuts", analysis, selection])

def getTriggerName(sample_name, analysis, selection):
    trigger_names = ["MuonEG", "DoubleMuon", "DoubleEG", "SingleMuon", "SingleElectron"]
    if "data" in sample_name and getPreviousStep(selection, analysis) == "ntuples":
        for name in trigger_names:
            if name in sample_name:
                return "-t " + name
    return "-t MonteCarlo"

def getLuminosityEras(year, manager_path=""):
    lumi_info = getLumiMap(manager_path)

    if year not in lumi_info:
        raise ValueError("Invalid year: %s. Must be present in lumi map" % year)

    if "eras" not in lumi_info[year]:
        if "years" in lumi_info[year]:
            outlist = []
            for yr in lumi_info[year]["years"]:
                if "eras" in lumi_info[yr]:
                    outlist += [f"{yr}_{era}" for era in lumi_info[yr]["eras"].keys()]
                else:
                    outlist += [yr]
            return outlist
        else:
            return []
    else:
        return list(lumi_info[year]["eras"].keys())

def getLuminosity(year, era="", manager_path=""):
    if manager_path == "":
        manager_path = getManagerPath()
    lumi_info = getLumiMap(manager_path)

    if year not in lumi_info:
        raise ValueError("Invalid year: %s. Must be present in lumi map" % year)
    if "years" in lumi_info[year]:
        return sum(getLuminosity(yr, "", manager_path) for yr in lumi_info[year]["years"])
    elif "lumi" not in lumi_info[year]:
        if era != "" and era not in lumi_info[year]["eras"]:
            raise ValueError("Invalid era (%s) for year: %s" % (era, year))
    elif era != "":
        raise ValueError("No eras present for year: %s. Must be present in lumi map" % year)

    if era == "":
        if "lumi" in lumi_info[year]:
            lumi = lumi_info[year]["lumi"]
        else:
            lumi = sum(lumi_info[year]["eras"].values())
    else:
        lumi = lumi_info[year]["eras"][era]

    return lumi
