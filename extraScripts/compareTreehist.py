import ROOT 
import pdb 
import json
import array
import math

with open('varsFile.json') as var_json_file:
    myvar_dict = json.load(var_json_file)

_binning = {}
for key in list(myvar_dict.keys()): #key is the variable
    _binning[key] = myvar_dict[key]["_binning"]

def rebin(hist,varName):
    ROOT.SetOwnership(hist, False)
    #No need to rebin certain variables but still might need overflow check
    if varName not in ['eta']:
        bins=array.array('d',_binning[varName])
        Nbins=len(bins)-1 
        hist=hist.Rebin(Nbins,hist.GetName()+"NoConfusion",bins)
    else:
        Nbins = hist.GetSize() - 2
    add_overflow = hist.GetBinContent(Nbins) + hist.GetBinContent(Nbins + 1)
    lastbin_error = math.sqrt(math.pow(hist.GetBinError(Nbins),2)+math.pow(hist.GetBinError(Nbins+1),2))
    hist.SetBinContent(Nbins, add_overflow)
    hist.SetBinError(Nbins, lastbin_error)
    hist.SetBinContent(Nbins+1,0)
    hist.SetBinError(Nbins+1,0)
    if not hist.GetSumw2(): hist.Sumw2()
    return hist

def listh(h): #return list
    
    list = [h.GetBinContent(i) for i in range(1,h.GetNbinsX()+1)]
    return list

def Ratiol(list1,list2):
    ratios = []
    for x,y in zip(list1,list2):
        if y!= 0.:
            ratio = x/y
        else:
            ratio = float(x==y)
        ratios.append(ratio)
    return ratios
    #return [x/y for x,y in zip (list1,list2)]

def printr(l,ro):
    print([round(x,ro) for x in l])

#main, nonprompt background, gen
fm = ROOT.TFile("TreeFile_ZZSelector_Hists27Apr2023-ZZ4l2016_Moriondsel_Inclusive.root")
fb = ROOT.TFile("TreeFile_ZZBackgroundSelector_Hists27Apr2023-ZZ4l2016_Moriondbkgd_Inclusive.root")
fg = ROOT.TFile("TreeFile_ZZGenSelector_Hists27Apr2023-ZZ4l2016_Moriondgen_Inclusive.root")
fh = ROOT.TFile("Hists27Apr2023-ZZ4l2016_Moriond.root")
ftags = ["main","nonmpormpt","Gen"]
datasets = ["data_DoubleEG_Run2016C-17Jul2018-v1", "zz4l-powheg"]
treetag = "_fTreeNtuple_"
channels = ["eeee","eemm","mmee","mmmm"]
var = "Mass"


for i,fin in enumerate([fm,fb,fg]):
    for chan in channels:
        if i == 2:
            chan += "Gen"
        for ds in datasets:
            #Skip gen for data
            if i == 2 and "data" in ds:
                continue
            treename = ds+treetag+chan
            tree = fin.Get(treename)
            histname = ds+chan+"_MassHist_"+ftags[i]
            
            #Following lines didn't work, gets null
            #hist = tree.Draw(prefix+"Mass>>%s(1215,70,2500)"%histname,prefix+"weight")
            #hist = ROOT.gDirectory.Get(histname)
            pdb.set_trace()
            hist = ROOT.TH1D(histname,histname,1215,70,2500)
            if i==0:
                hist2 = fh.Get(ds+"/Mass_"+chan)
            elif i == 1:
                hist2 = fh.Get(ds+"/Mass_Fakes_"+chan)
            else:
                hist2 = fh.Get(ds+"/GenMass_"+chan)

            hist2 = rebin(hist2,"MassAllj")
            for evt in tree:
                #pdb.set_trace()
                if i !=2:
                    exec("hist.Fill(evt.Mass_%s,evt.weight_%s)"%(chan,chan))
                else:
                    exec("hist.Fill(evt.GenMass_%s,evt.Genweight_%s)"%(chan,chan))
            
            hist = rebin(hist,"MassAllj")
            l1 = listh(hist)
            l2 = listh(hist2)
            print(ftags[i])
            print(treename)
            #printr(l1,7)
            #rintr(l2,7)
            printr(Ratiol(l1,l2),7)
            print("")
                    
                
            