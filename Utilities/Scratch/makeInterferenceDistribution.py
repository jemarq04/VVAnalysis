# coding: utf-8
import ROOT
rtfile = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Tight_Full-31May2018.root", "update")
wzdir = rtfile.Get("EW-WZjj")
wzdir.cd()
for chan in ["eee", "eem", "emm", "mmm",]:
    for var in ["Up", "Down"]:
        hist = wzdir.Get("mjj_etajj_unrolled_wCR_%s" % chan)
        int_hist = hist.Clone("mjj_etajj_unrolled_wCR_InterferenceEW-QCD%s_%s" % (var, chan))
        int_hist.SetBinContent(1, hist.GetBinContent(1)*(1.0 + 0.12*(-1 if var == "Down" else 1)))
        for i in range(2, int_hist.GetNbinsX()+1):
            int_hist.SetBinContent(i, hist.GetBinContent(i)*(1.0 + 0.04*(-1 if var == "Down" else 1)))
        print(int_hist.Write())
        
