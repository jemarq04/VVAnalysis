from python import CombineCardTools
from python import ConfigureJobs
import sys
import ROOT
import logging
import array
import os
import shutil

#logging.basicConfig(level=logging.DEBUG)

cardtool = CombineCardTools.CombineCardTools()


manager_path = ConfigureJobs.getManagerPath() 
manager_name = ConfigureJobs.getManagerName()
#print("manager_path: ", manager_path)
#print("manager_name: ", manager_name)
sys.path.append("/".join([manager_path, manager_name,
    "Utilities/python"]))
#print(sys.path)
from ConfigHistFactory import ConfigHistFactory
config_factory = ConfigHistFactory(
    "%s/%s" % (manager_path, manager_name),
    "ZZ4l2016/LooseLeptons",
)
#manager_path = ConfigureJobs.getManagerPath() 
#manager_name = ConfigureJobs.getManagerName()
##print("manager_path: ", manager_path)
#if manager_path not in sys.path:
#        sys.path.insert(0, "/".join([manager_path,"ZZ4lRun2DatasetManager", "Utilities/python"]))
#dataset_file = "%s/ZZ4lRun2DatasetManager/FileInfo/ZZ4l2016/%s.json" % (manager_path, "LooseLeptons")
#allnames = json.load(open(dataset_file))
#atgcSamples={}
#for name in allnames.keys():
#    if "atgc" in name or "sherpa" in name:
#        atgcSamples[str(name)]= str(allnames[name]['plot_group'])
#print(atgcSamples)

plot_groups = ["HZZ_signal","qqZZ_powheg","zzjj4l_ewk","ggZZ", "VVV", "data", "nonprompt",] 
plotGroupsMap = {name : config_factory.getPlotGroupMembers(name) for name in plot_groups}
xsecs  = ConfigureJobs.getListOfFilesWithXSec([f for files in list(plotGroupsMap.values()) for f in files])


lumiMap = {"2016" : 35.9, "2017" : 41.5, "2018" : 59.67,"FullRun2":137.1}
fileMap = { "2016" : "/afs/cern.ch/user/u/uhussain/ZZ4lRun2HistFiles/Hists17Oct2019-ZZ4l2016_Moriond.root",
    "2017" : "/afs/cern.ch/user/u/uhussain/ZZ4lRun2HistFiles/Hists14Oct2019-ZZ4l2017_Moriond.root",
    "2018" : "/afs/cern.ch/user/u/uhussain/ZZ4lRun2HistFiles/Hists15Oct2019-ZZ4l2018_MVA.root",
    "FullRun2":"/afs/cern.ch/user/u/uhussain/ZZ4lRun2HistFiles/Hists17Oct2019-ZZFullRun2.root",
    }
channels = ["eeee", "eemm", "mmee", "mmmm"]
nuissance_map = {"eeee" : 16, "eemm" : 17, "mmee" : 17, "mmmm" : 15, "all" : 13}
#fitvar = "ZZPt"
#rebin = array.array('d', [0.0,50.0,100.0,150.0,200.0,250.0,300.0,350.0,400.0])
fitvar = "Mass"
rebin = array.array('d', [100.0,200.0,250.0,300.0,350.0,400.0,500.0,600.0,800.0,1000.0,1200.0])
#fitvar = "yield"
#cardtool.setRebin(rebin)
cardtool.setFitVariable(fitvar)
cardtool.setFitVariableAppend("nonprompt", "Fakes")
cardtool.setProcesses(plotGroupsMap)
cardtool.setChannels(channels)
cardtool.setCrosSectionMap(xsecs)
cardtool.setVariations(["CMS_eff_e", "CMS_RecoEff_e", "CMS_eff_m","CMS_pileup"],
                        exclude=["nonprompt", "data"])
#cardtool.setOutputFolder("/eos/user/k/kelong/CombineStudies/ZZ/%s2016Fit" % fitvar)

combine_dir = ConfigureJobs.getCombinePath()
folder_name="%sFitFullRunII" % fitvar

output_dir = '/'.join([combine_dir,"ZZ", folder_name])

try:
    os.makedirs(output_dir)
except OSError as e:
    logging.warning(e)
    pass
output_folder = "CombineStudies/ZZ/%sFitFullRunII_Oct29" % fitvar 
cardtool.setOutputFolder(output_folder)

for year in ["2016","2017","2018"]:
#One has to make templates for full Run 2 which i haven't done yet.
#for year in ["FullRun2"]:
    cardtool.setLumi(lumiMap[year])
    cardtool.setInputFile(fileMap[year])
    print(fileMap[year], lumiMap[year] )
    cardtool.setOutputFile("ZZCombineInput_{year}.root".format(year=year))
    #cardtool.setOutputFolder("/eos/user/k/kelong/CombineStudies/ZZ/%s%sFit" % (fitvar, year))
    for process in plot_groups:
        #Turn this back on when the theory uncertainties are added
        if process not in ["zzjj4l_ewk","qqZZ_sherpa","zzqjj4l_ewk","nonprompt", "data"]: #and False
            cardtool.addTheoryVar(process, 'scale', list(range(1, 10)), exclude=[7, 9], central=0)
            cardtool.addTheoryVar(process, 'pdf_hessian' if year != "2016" else 'pdf_mc', [1]+[i for i in range(10, 111)], central=0)
        cardtool.loadHistsForProcess(process)
        cardtool.writeProcessHistsToOutput(process)

    for chan in channels + ["all"]:
        cardtool.setTemplateFileName("Templates/CombineCards/ZZSelection/ZZ_template{year}_{channel}.txt")
        logging.info("Writting cards for channel %s" % chan)
        cardtool.writeCards(chan, nuissance_map[chan], year=year)


copyFiles=os.listdir(output_folder)
for f in copyFiles:
    full_file_name=os.path.join(output_folder,f)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name,output_dir)
