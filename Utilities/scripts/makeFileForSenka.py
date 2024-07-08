import sys
import ROOT
import os
import logging
#Putting qqZZ_sherpa in the atgc files
#plot_groups = ["HZZ_signal","qqZZ_powheg","qqZZ_sherpa","zzjj4l_ewk","ggZZ", "VVV", "data", "nonprompt",]
plot_groups = ["HZZ_signal","qqZZ_powheg","zzjj4l_ewk","ggZZ", "VVV", "data", "nonprompt",]
#plot_groups = ["HZZ_signal"]
fileMap = { "2016" : "/data/uhussain/ZZTo4l/FullRun2/VVAnalyzer/CMSSW_10_3_1/src/Analysis/VVAnalysis/ZZCombineInput_2016.root",
    "2017" : "/data/uhussain/ZZTo4l/FullRun2/VVAnalyzer/CMSSW_10_3_1/src/Analysis/VVAnalysis/ZZCombineInput_2017.root",
    "2018" : "/data/uhussain/ZZTo4l/FullRun2/VVAnalyzer/CMSSW_10_3_1/src/Analysis/VVAnalysis/ZZCombineInput_2018.root",
    }
channels = ["eeee", "eemm", "mmmm"]
#channels = ["eemm"]
eVariations = ["CMS_eff_eUp", "CMS_eff_eDown","CMS_RecoEff_eUp", "CMS_RecoEff_eDown"]
mVariations = ["CMS_eff_mUp","CMS_eff_mDown"]
#systVariations=[]
#"CMS_pileup"],
#theorVariations=[]
theorVariations = ["pdf","QCDscale"]
fitvar = "Mass"

outputFolder = "ForSenka/%sFullRunII" % fitvar
if not os.path.isdir(outputFolder):
    os.makedirs(outputFolder)

for year in list(fileMap.keys()):
#for year in ["2016"]:
    fileName=fileMap[year]
    if type(fileName) == str: hist_file = ROOT.TFile.Open(fileName)
    for chan in channels:
        savehists=[]
        outputFile = "ZZSMInput_%s_%s.root" % (chan,year)
        for process in plot_groups:
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
            if process in ["qqZZ_powheg","HZZ_signal","ggZZ","VVV"]:
                for var in theorVariations:
                    histNames.append("Mass_%s_%sUp_%s" % (var,process,chan))
                    histNames.append("Mass_%s_%sDown_%s" % (var,process,chan))
            print("plot_group: ",process)
            print("histNames: ",histNames)
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
                tmphist.Delete()
                newName = name.replace("Mass",process)
                newName = newName.replace("_"+chan,"")
                if "pdf" or "QCD" in newName:
                    newName = newName.replace("_"+process,"")
                if "Fakes" in newName:
                    newName = newName.replace("_Fakes","")
                if "data" in newName:
                    newName = newName.replace("data","data_obs")
                hist.SetName(newName)
                savehists.append(hist)

        fOut = ROOT.TFile.Open("/".join([outputFolder, outputFile]), "RECREATE")
        fOut.cd()
        for newhists in savehists:
            newhists.Write()
        fOut.Close()
    hist_file.Close()




