# coding: utf-8
import ROOT
import random
import numpy
combine_file = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Tight-28Feb2018-TightFrom3MediumLeptons.root", "update")
plot_file = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/HistFiles/VBSselection_Tight-28Feb2018-TightFrom3MediumLeptons.root", "update")

new_dir = plot_file.Get("AllData")
if not new_dir:
    new_dir = ROOT.TDirectoryFile("AllData", "AllData")
new_dir.cd()
smearSig=True
smearBkgd=True
forcePoisson=True
for chan in ["eee", "eem", "emm", "mmm"]:
    hist = combine_file.Get("wzjj-vbfnlo/mjj_etajj_unrolled_%s" % chan).Clone()
    #hist = combine_file.Get("wzjj-ewk/mjj_etajj_unrolled_%s" % chan).Clone()
    if smearSig:
        for i in range(1, hist.GetNbinsX()+1):
            val = hist.GetBinContent(i)
            hist.SetBinContent(i, random.gauss(val, val*0.1))
    for bkgd in ["zg", "vv", "wz-mgmlm", "top-ewk",]:
        bkhist = combine_file.Get("%s/mjj_etajj_unrolled_%s" % (bkgd, chan))
        if smearBkgd:
            for i in range(1, hist.GetNbinsX()+1):
                orig_content = bkhist.GetBinContent(i)
                val = bkhist.GetBinContent(i)
                bkhist.SetBinContent(i, random.gauss(val, val*random.uniform(0.1, 0.4)))
        hist.Add(bkhist)
    
    nphist = combine_file.Get("DataEWKCorrected/mjj_etajj_unrolled_Fakes_%s" % chan)
    if smearBkgd:
        for i in range(1, hist.GetNbinsX()+1):
            val = nphist.GetBinContent(i)
            nphist.SetBinContent(i, random.gauss(val, val*0.3))
    hist.Add(nphist)
    if forcePoisson:
        for i in range(1, hist.GetNbinsX()+1):
            val = hist.GetBinContent(i)
            hist.SetBinContent(i, numpy.random.poisson(val))
    hist.Sumw2(False)
    ROOT.SetOwnership(hist, False)
print(new_dir.Write())
combine_file.cd()
combine_dir = combine_file.Get("AllData")
combine_dir.cd() 
if not combine_dir:
    combine_dir = ROOT.TDirectoryFile("AllData", "AllData")
for i in new_dir.GetListOfKeys():
    hist = new_dir.Get(i.GetName()).Clone()
    ROOT.SetOwnership(hist, False)
print(combine_dir.Write())
