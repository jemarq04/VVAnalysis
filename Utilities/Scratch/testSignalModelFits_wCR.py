# coding: utf-8
import ROOT
import random
import numpy
combine_file = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Tight-11Mar2018-TightFrom3MediumLeptons_JakobsControlPt30.root", "update")
plot_file = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/HistFiles/VBSselection_Tight-11Mar2018-TightFrom3MediumLeptons_JakobsControlPt30.root", "update")

plot_file.cd()
new_dir = plot_file.Get("AllData")
if not new_dir:
    new_dir = ROOT.TDirectoryFile("AllData", "AllData")
new_dir.cd()
smearSig=False
smearBkgd=False
forcePoisson=False
noWrite = False
hist_name ="mjj_etajj_unrolled_wCR_"
chans = ["eee", "eem", "emm", "mmm"]
for chan in chans:
    hist = combine_file.Get("AllData/" + hist_name + chan +";1").Clone()
    ROOT.SetOwnership(hist, False)
    #hist = combine_file.Get("wzjj-vbfnlo/mjj_etajj_unrolled_%s" % chan).Clone()
    sig_hist = combine_file.Get("wzjj-ewk/" +hist_name + chan)
    sig_hist.SetBinContent(1, 0)
    sig_hist.SetBinError(1,0) 
    hist.Add(sig_hist)
    if smearSig:
        for i in range(2, hist.GetNbinsX()+1):
            val = hist.GetBinContent(i)
            hist.SetBinContent(i, random.gauss(val, val*0.1))
    for bkgd in ["zg", "vv", "wz-mgmlm", "top-ewk",]:
        bkhist = combine_file.Get(bkgd + "/" + hist_name +  chan)
        if smearBkgd:
            for i in range(1, hist.GetNbinsX()+1):
                orig_content = bkhist.GetBinContent(i)
                val = bkhist.GetBinContent(i)
                bkhist.SetBinContent(i, random.gauss(val, val*random.uniform(0.1, 0.4)))
        bkhist.SetBinContent(1, 0)
        bkhist.SetBinError(1,0) 
        hist.Add(bkhist)
    
    nphist = combine_file.Get("DataEWKCorrected/" +hist_name +"Fakes_"+ chan)
    if smearBkgd:
        for i in range(1, hist.GetNbinsX()+1):
            val = nphist.GetBinContent(i)
            nphist.SetBinContent(i, random.gauss(val, val*0.3))
    nphist.SetBinContent(1,0) 
    nphist.SetBinError(1,0) 
    hist.Add(nphist)
    if forcePoisson:
        for i in range(1, hist.GetNbinsX()+1):
            val = hist.GetBinContent(i)
            hist.SetBinContent(i, numpy.random.poisson(val))
    hist.Sumw2(False)
    ROOT.SetOwnership(hist, False)
if not noWrite:
    plot_file.cd()
    print(new_dir.Write())
    combine_file.cd()
    combine_dir = combine_file.Get("AllData")
    if not combine_dir:
        combine_dir = ROOT.TDirectoryFile("AllData", "AllData")
    combine_dir.cd() 
    for chan in chans:
        hist = new_dir.Get(hist_name+chan).Clone()
        ROOT.SetOwnership(hist, False)
    print(combine_dir.Write())
else:
    print(new_dir.ls())
    print("Dir is", new_dir)
    for chan in chans:
        hist = new_dir.Get(hist_name+chan).Clone()
        print("Hist is", hist.GetName(), "Integral is", hist.Integral())
