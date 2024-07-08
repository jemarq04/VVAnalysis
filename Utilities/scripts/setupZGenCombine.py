from python import CombineCardTools
from python import ConfigureJobs
import sys
import ROOT
import logging
import array

ROOT.gROOT.SetBatch(True)
logging.basicConfig(level=logging.DEBUG)

cardtool = CombineCardTools.CombineCardTools()

manager_path = ConfigureJobs.getManagerPath() 
sys.path.append("/".join([manager_path, "AnalysisDatasetManager",
    "Utilities/python"]))

from ConfigHistFactory import ConfigHistFactory
config_factory = ConfigHistFactory(
    "%s/AnalysisDatasetManager" % manager_path,
    "ZGen/NanoAOD",
)

#plot_groups = ["nonprompt", "dy_lo", "dy_htbinned", "dy_htbinned_cp5", "dy_lo_2018"]
plot_groups = ["nonprompt", "dy_htbinned_cp5", "dy_lo_2018"]
plotGroupsMap = {name : config_factory.getPlotGroupMembers(name) for name in plot_groups}

xsecs  = ConfigureJobs.getListOfFilesWithXSec([f for files in list(plotGroupsMap.values()) for f in files])

channels = ["ee", "mm"]
fitvar = "ptZ"
#rebin = array.array('d', [0.0,50.0,100.0,150.0,200.0,250.0,300.0,350.0,400.0])
cardtool.setFitVariable(fitvar)
#cardtool.setRebin(rebin)
cardtool.setProcesses(plotGroupsMap)
cardtool.setChannels(channels)
cardtool.setCrosSectionMap(xsecs)
cardtool.setVariations([])
cardtool.setOutputFolder("/eos/user/k/kelong/CombineStudies/ZGen/%s" % fitvar)

cardtool.setLumi(35.9)
cardtool.setInputFile("/eos/user/k/kelong/HistFiles/ZGen/combined_withNonprompt.root")
cardtool.setOutputFile("ZGenCombineInput.root")
for process in plot_groups:
    #Turn this back on when the theory uncertainties are added
    if process not in ["nonprompt", "data"]: #and False
        cardtool.addTheoryVar(process, 'scale', list(range(0, 8)), exclude=[5, 7], central=-1)
        cardtool.addTheoryVar(process, 'pdf_hessian', list(range(9, 109)), central=-1)
    cardtool.loadHistsForProcess(process)
    cardtool.writeProcessHistsToOutput(process)

nuissance_map = {"ee" : 3, "mm" : 3 }
for chan in channels: #+ ["all"]:
    cardtool.setTemplateFileName("Templates/CombineCards/VGen/ZGen_template_{channel}.txt")
    logging.info("Writting cards for channel %s" % chan)
    cardtool.writeCards(chan, nuissance_map[chan], 
        #extraArgs={"data_name" : "dy_lo", "dy_sample" : "dy_lo"})
        extraArgs={"data_name" : "dy_lo_2018", "dy_sample" : "dy_lo_2018"})
