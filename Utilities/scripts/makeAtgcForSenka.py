import sys
import ROOT
import os
import logging
import json
import array
from python import ConfigureJobs

def addOverflow(hist):
    addOverflowAndUnderflow(hist, underflow=False, overflow=True)

def addOverflowAndUnderflow(hist, underflow=True, overflow=True):
    if not "TH1" in hist.ClassName():
        return
    if overflow:
        # Returns num bins + overflow + underflow
        num_bins = hist.GetNbinsX()
        add_overflow = hist.GetBinContent(num_bins) + hist.GetBinContent(num_bins + 1)
        hist.SetBinContent(num_bins, add_overflow)
    if underflow:
        add_underflow = hist.GetBinContent(0) + hist.GetBinContent(1)
        hist.SetBinContent(1, add_underflow)

manager_path = ConfigureJobs.getManagerPath() 
manager_name = ConfigureJobs.getManagerName()
#print("manager_path: ", manager_path)
if manager_path not in sys.path:
        sys.path.insert(0, "/".join([manager_path,"ZZ4lRun2DatasetManager", "Utilities/python"]))

fileMap = { "2016" : "/afs/cern.ch/user/u/uhussain/ZZ4lRun2HistFiles/Hists17Oct2019-ZZ4l2016_Moriond.root",
    "2017" : "",
    "2018" : "/afs/cern.ch/user/u/uhussain/ZZ4lRun2HistFiles/Hists29Oct2019-ZZ4l2018_MVA.root",
    }
channels = ["eeee", "eemm", "mmmm"]
#channels = ["eemm"]
eVariations = ["CMS_eff_eUp", "CMS_eff_eDown","CMS_RecoEff_eUp", "CMS_RecoEff_eDown"]
mVariations = ["CMS_eff_mUp","CMS_eff_mDown"]
#systVariations=[]
fitvar = "Mass"
rebin = array.array('d', [100.0,200.0,250.0,300.0,350.0,400.0,500.0,600.0,800.0,1000.0,1200.0])
outputFolder = "ForSenka/%sFullRunII" % fitvar
if not os.path.isdir(outputFolder):
    os.makedirs(outputFolder)

#for year in fileMap.keys():
for year in ["2018"]:
    dataset_file = "%s/ZZ4lRun2DatasetManager/FileInfo/ZZ4l%s/%s.json" % (manager_path,year, "LooseLeptons")
    allnames = json.load(open(dataset_file))
    atgcSamples={}
    for name in list(allnames.keys()):
        if "atgc" in name or "sherpa" in name:
            atgcSamples[str(name)]= str(allnames[name]['plot_group'])
    print(atgcSamples)
    fileName=fileMap[year]
    print("fileName: ",fileName)
    if type(fileName) == str: hist_file = ROOT.TFile.Open(fileName)
    for chan in channels:
        savehists=[]
        outputFile = "ZZatgcInput_%s_%s.root" % (chan,year)
        for process in [str(i) for i in list(atgcSamples.keys())]:
            histNames=[]
            if process=="nonprompt":
                histNames.append("Mass_Fakes_{channel}".format(channel=chan))
            else:
                histNames.append("Mass_{channel}".format(channel=chan))
            if not hist_file.Get(process):
                logging.warning("Skipping invalid filename %s" % process)
                continue
            if process not in ["data","nonprompt"]:
                if chan=="eeee":
                    for var in eVariations:
                        histNames.append("Mass_%s_%s" % (var,chan))
                elif chan=="mmmm":
                    for var in mVariations:
                        histNames.append("Mass_%s_%s" % (var,chan))
                elif chan=="eemm":
                    for var in eVariations+mVariations:
                        histNames.append("Mass_%s_%s" % (var,chan))
            #print("plot_group: ",process)
            #print("histNames: ",histNames)
            for name in histNames:
                tmphist = hist_file.Get("/".join([process, name]))
                if not tmphist: 
                    raise RuntimeError("Failed to produce histogram %s" % "/".join([process, name]))
                if "eemm" in name:
                    ##combine eemm and mmee channels
                    secname = name.replace("eemm","mmee")
                    tmphist2 = hist_file.Get("/".join([process, secname]))
                    #print(tmphist.GetName(),": ",tmphist.Integral())
                    #print(tmphist2.GetName(),": ",tmphist2.Integral())
                    tmphist.Add(tmphist2)
                hist = tmphist.Clone()
                #print("total: ",hist.Integral())
                histnew = hist.Rebin(len(rebin)-1,"histnew",rebin)
                addOverflow(histnew)
                tmphist.Delete()
                if process=="zz4l-sherpa":
                    print("this process happens in 2016")
                    histnew.Scale(0.455985*1000*35.9*1.239/histnew.Integral())
                if process=="zz4l-atgc_1" and year=="2018":
                    print("this process happens in 2018")
                    histnew.Scale(0.455985*1000*41.5*1.239/histnew.Integral())
                newName = name.replace("Mass",str(atgcSamples[process]))
                newName = newName.replace("_"+chan,"")
                hist.Delete()
                histnew.SetName(newName)
                savehists.append(histnew)

        fOut = ROOT.TFile.Open("/".join([outputFolder, outputFile]), "RECREATE")
        fOut.cd()
        for newhists in savehists:
            newhists.Write()
        fOut.Close()
    hist_file.Close()




