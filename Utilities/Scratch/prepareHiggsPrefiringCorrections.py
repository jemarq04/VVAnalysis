# coding: utf-8
import ROOT
import math
import array

ROOT.gROOT.SetBatch(True)
nocorr_file = ROOT.TFile("/afs/cern.ch/user/k/kelong/public/SMP-18-001/Higgs/NoCorrection/VBSselection_Loose_Full-04Oct2018_Higgs_NoPrefireCorrection_wCR.root")
corr_file = ROOT.TFile("/afs/cern.ch/user/k/kelong/public/SMP-18-001/Higgs/WithPrefiringCorrection/VBSselection_Loose_Full-04Oct2018_Higgs_WithPrefireCorrection_wCR.root")
jakobs_file = ROOT.TFile("Jakob/higgs30/wz3l3lHig_input_13TeV2016.root")

corrections_file = ROOT.TFile("VBSselection_LooseSelection_Higgs_prefiringCorrections.root", "RECREATE") 
output_file = ROOT.TFile("VBSselection_Higgs_fromJakob_withCorrections.root", "Recreate")
var = "MTWZ_wCR"

names = {"EWWZ" : "EW-WZjj", 
        "WZ" :"QCD-WZjj", 
        "VVV" : "top-ewk", 
        "ZZ" : "vv", 
        "Fake" : "DataEWKCorrected", 
        "Zg" : "zg"
}

names.update({ "Higgs_M%i" % m : "chargedHiggsWZ-m%i" % m for m in [300,400,500,600,700,800,900,1000,1500,2000]})
flatScaleFac=True

corrections_file.cd()
for folder in list(names.values()):
    nonprompt = "DataEWKCorrected" in folder
    hist_name = var if not nonprompt else var + "_Fakes"
    corr_hist = corr_file.Get("/".join([folder, hist_name]))
    uncorr_hist = nocorr_file.Get("/".join([folder, hist_name]))

    nbins = corr_hist.GetNbinsX()
    err1 = array.array('d', [0])
    err2 = array.array('d', [0])
    int1 = corr_hist.IntegralAndError(2, nbins+1, err1)
    int2 = uncorr_hist.IntegralAndError(2, nbins+1, err2)
    int_ratio = int1/int2
    int_error = int_ratio*math.sqrt((err1[0]/int1)**2 + (err2[0]/int2)**2)

    cr_ratio = corr_hist.GetBinContent(1)/uncorr_hist.GetBinContent(1)
    cr_err = cr_ratio*math.sqrt((corr_hist.GetBinError(1)/corr_hist.GetBinContent(1))**2 + (uncorr_hist.GetBinError(1)/uncorr_hist.GetBinContent(1))**2)
    print("Overall correction to yield for sample %s is %0.3f in CR and %0.3f in signal" % (folder, cr_ratio, int_ratio))
    ratio = corr_hist.Clone(folder +"_ratio")
    ROOT.SetOwnership(ratio, False)
    # These seem too unstable to take bin-by-bin corrections
    if nonprompt or flatScaleFac:
        ratio.SetBinContent(1, cr_ratio)
        ratio.SetBinError(1, cr_err)
        for i in range(2, ratio.GetNbinsX()+1):
            ratio.SetBinContent(i, int_ratio)
            ratio.SetBinError(i, int_error)
    else:
        ratio.Divide(uncorr_hist)
        for i in range(ratio.GetNbinsX()+1):
            #if abs(1-ratio.GetBinContent(i)/int_ratio) > 0.2:
            if ratio.GetBinError(i)/ratio.GetBinContent(i) > 0.5:
                ratio.SetBinContent(i, int_ratio)
                ratio.SetBinError(i, int_error)
                print("WARNING! Setting bin %i of hist %s to total ratio" % (i, folder))
    ratio.Write()
    canvas_name = folder+"_canvas"
    canvas = ROOT.TCanvas(canvas_name, canvas_name)
    ratio.Draw("hist e1")
    ratio.GetXaxis().SetTitle("m_{T}(WZ) [GeV]")
    ratio.GetYaxis().SetTitle("Prefire corr. / uncorr.")
    filename = "/afs/cern.ch/user/k/kelong/www/ChargedHiggs/Kenneth/PrefireCorrRatios/%s.pdf" % folder 
    if flatScaleFac:
        filename = filename.replace(".pdf", "_flat.pdf")
    canvas.Print(filename)

for hist_key in jakobs_file.GetListOfKeys():
    hist_name = hist_key.GetName()
    hist = jakobs_file.Get(hist_name)
    output_file.cd()
    if "Data" in hist_name:
        hist.Write()
        continue
    corrected_hist = hist.Clone()
    isHiggs = "Higgs" in corrected_hist.GetName()
    name = "_".join(corrected_hist.GetName().split("_")[1:2+isHiggs])
    if name in list(names.keys()):
        correction_hist = corrections_file.Get(names[name]+"_ratio")
    elif name in list(names.values()):
        correction_hist = corrections_file.Get(name+"_ratio")
    else:
        print("WARNING: Found no correction for process %s" % name)
        continue
    if not correction_hist.GetNbinsX() == hist.GetNbinsX():
        raise RuntimeError("Unequal number of bins for correction and central hist" \
                "found %i for correction, %i for central" % (correction_hist.GetNbinsX(), hist.GetNbinsX()))
    for i in range(hist.GetNbinsX()+1):
        corrected_hist.SetBinError(i, hist.GetBinError(i)*correction_hist.GetBinContent(i))
        corrected_hist.SetBinContent(i, hist.GetBinContent(i)*correction_hist.GetBinContent(i))
    corrected_hist.Write()
