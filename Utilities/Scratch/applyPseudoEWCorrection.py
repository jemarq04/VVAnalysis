import ROOT

# Scale EW-WZjj by a pretned EW correction
rtfile = ROOT.TFile(
    "/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Loose_Full-08Oct2018_PrefireStudy_EWCorr.root", "UPDATE"
)

ew_folder = rtfile.Get("EW-WZjj")

scale_facs = {
    500: 0.95,
    1000: 0.9,
    1500: 0.85,
    2000: 0.8,
}

scale_facs = {
    500: 0.8,
    1000: 0.733,
    1500: 0.666,
    2000: 0.6,
}

# Only works for 2D distribution with control region!
ew_folder.cd()
for hist_name in ew_folder.GetListOfKeys():
    hist = rtfile.Get("EW-WZjj/" + hist_name.GetName() + ";1")
    for i in range(2, hist.GetNbinsX() + 1):
        corr = scale_facs[(((i + 2) % 4) + 1) * 500]
        hist.SetBinContent(i, hist.GetBinContent(i) * corr)
        hist.SetBinError(i, hist.GetBinError(i) * corr)
    hist.Write()
