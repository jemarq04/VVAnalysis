# coding: utf-8
import ROOT
file = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/HistFiles/Wselection-06Dec2017-TightFrom3LooseLeptons.root")
dir = file.Get("wlljj-ewk")
#dir = file.Get("wz3lnu-powheg")
hist_mjj_mtwz = dir.Get("mjj_mtwz_2D_mmm")

for i in ["eee", "eem", "emm"]:
    temp_hist = dir.Get("mjj_mtwz_2D_"+i)
    hist_mjj_mtwz.Add(temp_hist)
    
hist_mjj_mtwz.GetXaxis().SetTitle("m_{jj} (GeV)")
hist_mjj_mtwz.GetYaxis().SetTitle("M_{T}(3\\ell, p_{T}^{\\mathrm{miss}})")
print("Correlation factor is", hist_mjj_mtwz.GetCorrelationFactor())
#hist_mjj_mtwz.GetYaxis().SetTitleOffset(0.7)
ROOT.gStyle.SetPalette(ROOT.kCMYK)
hist_mjj_mtwz.Draw("colz")
canvas = ROOT.gROOT.FindObject("c1")
canvas.Print("~/www/DibosonAnalysisData/PlottingResults/WZxsec2016/VBSselection/TightLeptonsFromLoose/2017Dec-Nonprompt/mjj_mtwz_2D.pdf")
canvas.Print("~/www/DibosonAnalysisData/PlottingResults/WZxsec2016/VBSselection/TightLeptonsFromLoose/2017Dec-Nonprompt/mjj_mtwz_2D.png")
