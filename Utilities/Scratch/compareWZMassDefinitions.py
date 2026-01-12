# coding: utf-8
import ROOT

chain = ROOT.TChain("analyzeWZ/Ntuple")
# chain.Add("/data/kelong/DibosonAnalysisData/GenAnalysis/WLLJJ_EWK-MGLO_ScalesMaxPtJ_GenNtuples_leptonType-rivet_2017-11-12-wzGen_cfg/*")
chain.Add(
    "/data/kelong/DibosonAnalysisData/GenAnalysis/WLLJJ_WToLNu_aQGC-FM_UPDATE_MGLO_GenNtuples_leptonType-dressed_2018-02-07-wzGen_cfg/*"
)

canvas = ROOT.TCanvas("canvas", "canvas")

ROOT.gStyle.SetPalette(ROOT.kCMYK)

hist_3lmet = ROOT.TH1D("3lmet", "3lmet", 100, 0, 2000)
hist2D = ROOT.TH2D("hist2D", "hist2D", 50, 0, 500, 50, 0, 500)
hist2D_MT = ROOT.TH2D("mt", "mt", 50, 0, 500, 50, 0, 500)
hist2D_MTgenMET = ROOT.TH2D("mtgenmet", "mtgenmet", 50, 0, 500, 50, 0, 500)
hist2D_MTtrue = ROOT.TH2D("mttrue", "mttrue", 50, 0, 500, 50, 0, 500)
hist2D_Svenja_MTgenMET = ROOT.TH2D("mtgenmet_svenja", "mtgenmet_svenja", 50, 0, 500, 50, 0, 500)
hist2D_Svenja_MTtrue = ROOT.TH2D("mttrue_svenja", "mttrue_svenja", 50, 0, 500, 50, 0, 500)

for row in chain:
    nu = ROOT.TLorentzVector()
    nu.SetPtEtaPhiM(row.NuPt, 0, row.NuPhi, 0)
    l1 = ROOT.TLorentzVector()
    l1.SetPtEtaPhiM(row.l1Pt, row.l1Eta, row.l1Phi, 0)
    l2 = ROOT.TLorentzVector()
    l2.SetPtEtaPhiM(row.l2Pt, row.l2Eta, row.l2Phi, 0)
    l3 = ROOT.TLorentzVector()
    l3.SetPtEtaPhiM(row.l3Pt, row.l3Eta, row.l3Phi, 0)
    threelMet = l1 + l2 + l3 + nu
    hist2D.Fill(row.Mass, threelMet.M())
    hist2D_MTtrue.Fill(row.Mass, row.MTtrue)
    hist2D_MTgenMET.Fill(row.Mass, row.MTgenMET)
    hist2D_Svenja_MTgenMET.Fill(threelMet.M(), row.MTgenMET)
    hist2D_Svenja_MTtrue.Fill(threelMet.M(), row.MTtrue)
    hist_3lmet.Fill(threelMet.M(), row.LHEweights[455] / row.LHEweights[0])

# hist2D.Draw("colz")
# hist2D.GetXaxis().SetTitle("M_{WZ} (GeV)")
# hist2D.GetYaxis().SetTitle("M_{3l+MET} (GeV)")
# canvas.Print("~/www/WZMassDefinitionComparison/M_3lmet_vs_Mass.pdf")
#
# hist2D_MTtrue.Draw("colz")
# hist2D_MTtrue.GetXaxis().SetTitle("M_{WZ} (GeV)")
# hist2D_MTtrue.GetYaxis().SetTitle("M_{T}(3l, #nu) (GeV)")
# canvas.Print("~/www/WZMassDefinitionComparison/MTtrueWZ_vs_Mass.pdf")
#
# hist2D_MTgenMET.Draw("colz")
# hist2D_MTgenMET.GetXaxis().SetTitle("M_{WZ} (GeV)")
# hist2D_MTgenMET.GetYaxis().SetTitle("M_{T}(3l, GenMET) (GeV)")
# canvas.Print("~/www/WZMassDefinitionComparison/MTgenMETWZ_vs_Mass.pdf")
#
# hist2D_Svenja_MTtrue.Draw("colz")
# hist2D_Svenja_MTtrue.GetXaxis().SetTitle("M_{3l+MET} (GeV)")
# hist2D_Svenja_MTtrue.GetYaxis().SetTitle("M_{T}(3l, #nu) (GeV)")
# canvas.Print("~/www/WZMassDefinitionComparison/M_3lmet_vs_MTtrueWZ.pdf")
#
# hist2D_Svenja_MTgenMET.Draw("colz")
# hist2D_Svenja_MTgenMET.GetXaxis().SetTitle("M_{3l+MET} (GeV)")
# hist2D_Svenja_MTgenMET.GetYaxis().SetTitle("M_{T}(3l, GenMET) (GeV)")
# canvas.Print("~/www/WZMassDefinitionComparison/M_3lmet_vs_MTgenMETWZ.pdf")
#
hist_mt1D = hist_3lmet.Clone("mttrue1D")
chain.Draw("MTtrue>>mttrue1D", "row.LHEweights[455]/row.LHEweights[0]")
hist_mt1D.Draw("hist")
hist_3lmet.Draw("hist same")
hist_3lmet.SetLineColor(ROOT.kBlue)
# hist_mt1D.SetLineColor(ROOT.kRed)
# canvas.Print("~/www/WZMassDefinitionComparison/M_3lmet_vs_MTWZ_1D.pdf")
