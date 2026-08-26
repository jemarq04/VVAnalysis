#!/usr/bin/env python
import array
import datetime
import math

import ROOT
from python import ConfigureJobs, UserInput
from ROOT import vector as Vec

VFloat = Vec("float")
from PlotTools import PlotStyle as Style

style = Style()
# ROOT.gStyle.SetLineScalePS(1.8)
ROOT.gStyle.SetOptDate(False)
channels = ["eeee", "eemm", "mmmm"]


def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float, default=41.5, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str, default="", help="Output file name")
    parser.add_argument("--variable", "-vr", type=str, default="all", help="variableName")
    parser.add_argument("--logy", "--logY", "--log", action="store_true", help="Put vertical axis on a log scale.")
    return vars(parser.parse_args())


args = getComLineArgs()

today = datetime.date.today().strftime("%d%b%Y")

manager_path = ConfigureJobs.getManagerPath()

analysis = args["analysis"]
_binning = {
    "pt": [25.0 * i for i in range(4)] + [100.0, 150.0, 200.0, 300.0],
    #'mass' : [100.+100.*i for i in range(12)],
    "mass": [100.0] + [200.0 + 50.0 * i for i in range(5)] + [500.0, 600.0, 800.0],
    "massFull": [80.0, 100.0, 120.0, 130.0, 150.0, 180.0, 200.0, 240.0, 300.0, 400.0, 1000],
    "eta": [6, 0.0, 6.0],
    "zmass": [60.0, 80.0, 84.0, 86.0] + [87.0 + i for i in range(10)] + [98.0, 102.0, 120.0],  # [12, 60., 120.],
    "z1mass": [60.0, 80.0, 84.0, 86.0] + [87.0 + i for i in range(10)] + [98.0, 102.0, 120.0],  # [12, 60., 120.],
    "z2mass": [60.0, 75.0, 83.0] + [84.0 + i for i in range(14)] + [105.0, 120.0],  # [12, 60., 120.],
    "z1pt": [i * 25.0 for i in range(7)] + [200.0, 300.0],
    "z2pt": [i * 25.0 for i in range(7)] + [200.0, 300.0],
    "zpt": [i * 25.0 for i in range(7)] + [200.0, 300.0],
    "zHigherPt": [i * 25.0 for i in range(7)] + [200.0, 300.0],
    "zLowerPt": [i * 25.0 for i in range(7)] + [200.0, 300.0],
    "leppt": [i * 15.0 for i in range(11)],
    "l1Pt": [0.0, 15.0, 30.0, 40.0, 50.0]
    + [60.0 + 15.0 * i for i in range(9)]
    + [195.0, 225.0],  # [14,0.,210.],#[15, 0., 150.],
    "dphiz1z2": [0.0, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25],
    "drz1z2": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
}
units = {
    "pt": "[GeV]",
    "mass": "[GeV]",
    "massFull": "[GeV]",
    "eta": "",
    "zmass": "[GeV]",
    "z1mass": "[GeV]",
    "z2mass": "[GeV]",
    "zpt": "[GeV]",
    "z1pt": "[GeV]",
    "z2pt": "[GeV]",
    "zHigherPt": "[GeV]",
    "zLowerPt": "[GeV]",
    "leppt": "[GeV]",
    "l1Pt": "[GeV]",
    "dphiz1z2": "",
    "drz1z2": "",
}

yaxisunits = {
    "pt": "GeV",
    "mass": "GeV",
    "massFull": "GeV",
    "eta": "",
    "zmass": "GeV",
    "z1mass": "GeV",
    "z2mass": "GeV",
    "zpt": "GeV",
    "z1pt": "GeV",
    "z2pt": "GeV",
    "zHigherPt": "GeV",
    "zLowerPt": "GeV",
    "leppt": "GeV",
    "l1Pt": "GeV",
    "dphiz1z2": "",
    "drz1z2": "",
}

prettyVars = {
    "pt": "p_{T}^{4\\ell}",
    "mass": "m_{4\\ell}",
    "massFull": "m_{4\\ell}",
    "eta": "\\eta_{4\\ell}",
    "zmass": "m_{Z}",
    "z1mass": "m_{Z_{1}}",
    "z2mass": "m_{Z_{2}}",
    "z1pt": "p_{T}^{Z_{1}}",
    "z2pt": "p_{T}^{Z_{2}}",
    "zpt": "p_{T}^{Z}",
    "zHigherPt": "p_\\text{T}^{\\text{Z}_{\\text{lead}}}",
    "zLowerPt": "p_\\text{T}^{\\text{Z}_{\\text{sublead}}}",
    "leppt": "p_{T}^{\\ell}",
    "l1Pt": "p_\\text{T}^{\\ell_1}",
    "dphiz1z2": "\\Delta\\phi_{Z_{1},Z_{2}}",
    "drz1z2": "\\Delta\\text{R}_{Z_{1},Z_{2}}}",
}

_xTitle = {}
_yTitle = {}
_yTitleNoNorm = {}

_yTitleTemp = "{prefix} \\frac{{d\\sigma_{{\\text{{fid}}}}}}{{d{xvar}}} {units}"
for var, prettyVar in prettyVars.iteritems():
    xt = prettyVar
    if yaxisunits[var]:
        xt += f" \\, \\left(\\text{{{yaxisunits[var]}}}\\right)"
        yt = _yTitleTemp.format(
            xvar=prettyVar,
            prefix="\\frac{1}{\\sigma_{\\text{fid}}}",
            units=f"\\, \\left( \\frac{{1}}{{\\text{{{yaxisunits[var]}}}}} \\right)",
        )
        ytnn = _yTitleTemp.format(
            xvar=prettyVar,
            prefix="",
            units=f"\\, \\left( \\frac{{\\text{{fb}}}}{{\\text{{{yaxisunits[var]}}}}} \\right)",
        )
    else:
        yt = _yTitleTemp.format(prefix="\\frac{1}{\\sigma_{\\text{fid}}}", xvar=prettyVar, units="")
        ytnn = _yTitleTemp.format(prefix="", xvar=prettyVar, units="\\left( \\text{fb} \\right)")

    _xTitle[var] = xt
    _yTitle[var] = yt
    _yTitleNoNorm[var] = ytnn

# list of variables not counting systematic shifts
varList = ["Mass", "ZZPt", "ZPt", "LepPt", "dPhiZ1Z2", "dRZ1Z2"]

# Sometimes need to more or resize legend
legDefaults = {
    "textsize": 0.034,  # .027,#2,
    "leftmargin": 0.35,
    "entryheight": 0.037,
    "rightmargin": 0.03,
}
legParams = {v.lower(): legDefaults.copy() for v in varList}
legParams["z1mass"] = {
    "textsize": 0.026,
    "leftmargin": 0.03,
    "rightmargin": 0.46,
    "entryheight": 0.034,  # 23
    "entrysep": 0.007,
}
legParams["pt"] = legParams["zzpt"].copy()
legParams["zmass"] = legParams["z1mass"].copy()
legParams["z2mass"] = legParams["z1mass"].copy()
legParams["deltaEtajj"] = legParams["z1mass"].copy()
legParams["deltaEtajj"]["leftmargin"] = 0.5
legParams["deltaEtajj"]["rightmargin"] = 0.03
legParams["deltaEtajj"]["topmargin"] = 0.05
legParams["eta"] = legParams["deltaEtajj"].copy()
# legParams['massFull']['leftmargin'] = 0.25

legParamsLogy = {v: p.copy() for v, p in legParams.iteritems()}
# legParamsLogy['l1Pt']['topmargin'] = 0.65
# legParamsLogy['l1Pt']['leftmargin'] = 0.2
# legParamsLogy['l1Pt']['rightmargin'] = 0.18
legParamsLogy["mass"]["topmargin"] = 0.075
legParamsLogy["mass"]["leftmargin"] = 0.35
legParamsLogy["mass"]["rightmargin"] = 0.025
legParamsLogy["mass"]["textsize"] = 0.033
legParamsLogy["leppt"]["topmargin"] = 0.05
# legParamsLogy['zHigherPt']['topmargin'] = 0.045
# legParamsLogy['massFull']['topmargin'] = 0.035


def createCanvasPads(varName):
    c = ROOT.TCanvas("c", "canvas")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLegendBorderSize(0)
    # Upper histogram plot is pad1
    pad1 = ROOT.TPad("pad1", "pad1", 0.01, 0.01, 0.99, 0.99)
    pad1.Draw()
    pad1.cd()
    # if varName!="drz1z2":
    #    pad1.SetLogy()
    pad1.SetFillColor(0)
    pad1.SetFrameBorderMode(0)
    pad1.SetBorderMode(0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    # pad1.SetGridx()
    # pad1.Draw()
    return c, pad1


def getLumiTextBox():
    texS = ROOT.TLatex(0.77, 0.955, str(args["lumi"]) + " fb^{-1} (13 TeV)")
    texS.SetNDC()
    texS.SetTextFont(42)
    texS.SetTextSize(0.040)
    texS.Draw()
    texS1 = ROOT.TLatex(0.15, 0.955, "#bf{CMS} #it{Preliminary}")
    texS1.SetNDC()
    texS1.SetTextFont(42)
    texS1.SetTextSize(0.040)
    texS1.Draw()
    return texS, texS1


varNames = {"mass": "Mass", "pt": "ZZPt", "zpt": "ZPt", "leppt": "LepPt", "dphiz1z2": "dPhiZ1Z2", "drz1z2": "dRZ1Z2"}
runVariables = []
runVariables.append(args["variable"])
print("runVariables: ", runVariables)
# Save histograms from saveUnfolded.py in this root file
savePullHists = []
for varName in runVariables:
    print("varName:", varNames[varName])
    # save unfolded and Gen MadGraph histograms as key-value pairs in the histogram dictionary
    histosMG = {}
    for year in ["2016", "2017", "2018"]:
        fileName = "PowMatrix_MGUnfHistsExtraBins-12Mar2020-ZZ4l%s.root" % (year)
        fUse = ROOT.TFile.Open(fileName, "read")
        hMGUnfolded = {}
        hMGTrue = {}
        hMGUnc = {}
        for chan in channels:
            hMGUnfolded[chan] = fUse.Get(chan + "_" + varName + "_unf")
            hMGTrue[chan] = fUse.Get(chan + "_" + varName + "_trueAlt")
            hMGUnc[chan] = fUse.Get(chan + "_" + varName + "_totUncUp")
            hMGUnf = hMGUnfolded[chan].Clone()
            hMGUnf.SetName(chan + "_" + varName + "_unf_" + year)
            hMGUnf.SetDirectory(0)
            # print("hMGUnf:",hMGUnf)
            hMGTruth = hMGTrue[chan].Clone()
            hMGTruth.SetName(chan + "_" + varName + "_trueAlt_" + year)
            hMGTruth.SetDirectory(0)
            # print("hMGTruth: ",hMGTruth)
            hTotMGUnc = hMGUnc[chan].Clone()
            hTotMGUnc.SetName(chan + "_" + varName + "_totUnc_" + year)
            hTotMGUnc.SetDirectory(0)
            histosMG[hMGUnf] = (hMGTruth, hTotMGUnc)
            # print("9 sets of histos: ",histosMG)
        fUse.Close()
        # print the dictionary containing 9 pairs of MG unfolded and true histograms
    # print("9 sets of histos: ",histosMG)

    # save unfolded and Gen Powheg histograms as key-value pairs in the histogram dictionary
    histosPow = {}
    for year in ["2016", "2017", "2018"]:
        PowfileName = "MGMatrix_PowUnfHists_ExtraBins-12Mar2020-ZZ4l%s.root" % (year)
        fPowUse = ROOT.TFile.Open(PowfileName, "read")
        hPowUnfolded = {}
        hPowTrue = {}
        hPowUnc = {}
        for chan in channels:
            hPowUnfolded[chan] = fPowUse.Get(chan + "_" + varName + "_unf")
            hPowTrue[chan] = fPowUse.Get(chan + "_" + varName + "_true")
            hPowUnc[chan] = fPowUse.Get(chan + "_" + varName + "_totUncUp")
            hPowUnf = hPowUnfolded[chan].Clone()
            hPowUnf.SetName(chan + "_" + varName + "_PowUnf_" + year)
            hPowUnf.SetDirectory(0)
            # print("hPowUnf:",hPowUnf)
            hPowTruth = hPowTrue[chan].Clone()
            hPowTruth.SetName(chan + "_" + varName + "_true_" + year)
            hPowTruth.SetDirectory(0)
            # print("hPowTruth: ",hPowTruth)
            hTotPowUnc = hPowUnc[chan].Clone()
            hTotPowUnc.SetName(chan + "_" + varName + "_PowTotUnc_" + year)
            hTotPowUnc.SetDirectory(0)
            histosPow[hPowUnf] = (hPowTruth, hTotPowUnc)
            # print("9 sets of histos: ",histosPow)
        fPowUse.Close()
        # print the dictionary containing 9 pairs of MG unfolded and true histograms
    # print("9 sets of histos: ",histosPow)
    # Now its time to set up the TH2F Pull histograms
    if varName == "eta":
        histbins = array.array("d", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    else:
        histbins = array.array("d", _binning[varName])
    # print "histbins: ",histbins
    pullName = "pull_%s" % (varNames[varName])
    title = "pull;%s;pull" % (varNames[varName])
    hPull = ROOT.TH2F(pullName, title, len(histbins) - 1, histbins, 50, -5, 5)

    # We want to add the 9th bin content to 8th bin along with stat error, syst error = 0 in last bin (800-2000) anyways
    if varName == "pt" or varName == "mass" or varName == "leppt" or varName == "zpt" or varName == "drz1z2":
        for i in range(1, hMGUnf.GetNbinsX()):
            for hUnf, histTuple in histosMG.items():
                hGen = histTuple[0]
                hSystUnc = histTuple[1]
                if i == hMGUnf.GetNbinsX() - 1:
                    TotalStat = (hUnf.GetBinError(i)) ** 2
                    TotalStat += (hUnf.GetBinError(i + 1)) ** 2
                    TotUnfContent = hUnf.GetBinContent(i) + hUnf.GetBinContent(i + 1)
                    TotGenContent = hGen.GetBinContent(i) + hGen.GetBinContent(i + 1)
                    pull = (TotUnfContent - TotGenContent) / (math.sqrt(TotalStat))
                    binCenter = hUnf.GetXaxis().GetBinCenter(i)
                    print(
                        "binCenter: ",
                        binCenter,
                        "-",
                        "MGUnfContent: ",
                        TotUnfContent,
                        "-",
                        "MGGen: ",
                        TotGenContent,
                        "-",
                        "statError: ",
                        math.sqrt(TotalStat),
                        "-",
                        "syst: ",
                        hSystUnc.GetBinContent(i),
                    )
                else:
                    # pull = (hUnf.GetBinContent(i) - hGen.GetBinContent(i))/(hSystUnc.GetBinContent(i))
                    pull = (hUnf.GetBinContent(i) - hGen.GetBinContent(i)) / (hUnf.GetBinError(i))
                    binCenter = hUnf.GetXaxis().GetBinCenter(i)
                    print(
                        "binCenter: ",
                        binCenter,
                        "-",
                        "MGUnfContent: ",
                        hUnf.GetBinContent(i),
                        "-",
                        "MGGen: ",
                        hGen.GetBinContent(i),
                        "-",
                        "statError: ",
                        hUnf.GetBinError(i),
                        "-",
                        "syst: ",
                        hSystUnc.GetBinContent(i),
                    )
                print("pull: ", round(pull, 4))
                hPull.Fill(binCenter, round(pull, 4))

            for hPoUnf, histTuplePow in histosPow.items():
                hPowGen = histTuplePow[0]
                hSystUncPow = histTuplePow[1]
                if i == hMGUnf.GetNbinsX() - 1:
                    TotalPowStat = (hPoUnf.GetBinError(i)) ** 2
                    TotalPowStat += (hPoUnf.GetBinError(i + 1)) ** 2
                    TotPowUnfContent = hPoUnf.GetBinContent(i) + hPoUnf.GetBinContent(i + 1)
                    TotPowGenContent = hPowGen.GetBinContent(i) + hPowGen.GetBinContent(i + 1)
                    pullPow = (TotPowUnfContent - TotPowGenContent) / (math.sqrt(TotalPowStat))
                    PowbinCenter = hPoUnf.GetXaxis().GetBinCenter(i)
                    print(
                        "PowbinCenter: ",
                        PowbinCenter,
                        "-",
                        "PowUnfContent: ",
                        TotPowUnfContent,
                        "-",
                        "PowGen: ",
                        TotPowGenContent,
                        "-",
                        "statError: ",
                        math.sqrt(TotalPowStat),
                        "-",
                        "syst: ",
                        hSystUncPow.GetBinContent(i),
                    )
                else:
                    # pull = (hPoUnf.GetBinContent(i) - hPowGen.GetBinContent(i))/(hSystUncPow.GetBinContent(i))
                    pullPow = (hPoUnf.GetBinContent(i) - hPowGen.GetBinContent(i)) / (hPoUnf.GetBinError(i))
                    PowbinCenter = hPoUnf.GetXaxis().GetBinCenter(i)
                    print(
                        "binCenter: ",
                        PowbinCenter,
                        "-",
                        "PowUnfContent: ",
                        hPoUnf.GetBinContent(i),
                        "-",
                        "statError: ",
                        hPoUnf.GetBinError(i),
                        "-",
                        "syst: ",
                        hSystUncPow.GetBinContent(i),
                    )
                print("pullPow: ", round(pullPow, 4))
                hPull.Fill(PowbinCenter, round(pullPow, 4))

    else:
        for i in range(1, hMGUnf.GetNbinsX() + 1):
            for hUnf, histTuple in histosMG.items():
                hGen = histTuple[0]
                hSystUnc = histTuple[1]
                # pull = (hUnf.GetBinContent(i) - hGen.GetBinContent(i))/(hSystUnc.GetBinContent(i))
                pull = (hUnf.GetBinContent(i) - hGen.GetBinContent(i)) / (hUnf.GetBinError(i))
                binCenter = hUnf.GetXaxis().GetBinCenter(i)
                print(
                    "binCenter: ",
                    binCenter,
                    "-",
                    "MGUnfContent: ",
                    hUnf.GetBinContent(i),
                    "-",
                    "statError: ",
                    hUnf.GetBinError(i),
                    "-",
                    "syst: ",
                    hSystUnc.GetBinContent(i),
                )
                print("pull: ", round(pull, 4))
                hPull.Fill(binCenter, round(pull, 4))

            for hPoUnf, histTuplePow in histosPow.items():
                hPowGen = histTuplePow[0]
                hSystUncPow = histTuplePow[1]
                # pull = (hPoUnf.GetBinContent(i) - hPowGen.GetBinContent(i))/(hSystUncPow.GetBinContent(i))
                pullPow = (hPoUnf.GetBinContent(i) - hPowGen.GetBinContent(i)) / (hPoUnf.GetBinError(i))
                PowbinCenter = hPoUnf.GetXaxis().GetBinCenter(i)
                print(
                    "binCenter: ",
                    PowbinCenter,
                    "-",
                    "PowUnfContent: ",
                    hPoUnf.GetBinContent(i),
                    "-",
                    "statError: ",
                    hPoUnf.GetBinError(i),
                    "-",
                    "syst: ",
                    hSystUncPow.GetBinContent(i),
                )
                print("pullPow: ", round(pullPow, 4))
                hPull.Fill(PowbinCenter, round(pullPow, 4))

    savePullHists.append(hPull)


today = datetime.date.today().strftime("%d%b%Y")
tmpFileName = "MGPowMatrix_PowMGUnfGenPullsExtrabins-%s.root" % (today)
# fHistOut = ROOT.TFile.Open(tmpFileName, "update")
# fHistOut.cd()
for newhists in savePullHists:
    output = ROOT.TCanvas("output", "output")
    # ROOT.gStyle.SetOptStat(1110)
    ROOT.gStyle.SetOptFit(1111)
    ROOT.gStyle.SetLegendBorderSize(0)
    output.cd()
    print("Pull:", newhists)
    name = newhists.GetName()
    print("PullName: ", name)
    newhists.FitSlicesY(0, 1, 6)
    pull_1 = ROOT.gDirectory.Get(name + "_1")
    print("pull_1:", pull_1)
    pull_1.GetYaxis().SetRangeUser(-1.0, 1.0)
    pull_1.Fit("pol0")
    name = newhists.GetName()
    print("PullName: ", name)
    output.SaveAs("Pulls/" + name + "_mean.png")
    output.SaveAs("Pulls/" + name + "_mean.pdf")
    # output.SaveAs("Pulls/"+name+"_mean.root")

    pull_2 = ROOT.gDirectory.Get(name + "_2")
    pull_2.GetYaxis().SetRangeUser(0.0, 2.0)
    pull_2.Fit("pol2")
    output.SaveAs("Pulls/" + name + "_width.png")
    output.SaveAs("Pulls/" + name + "_width.pdf")
    # output.SaveAs("Pulls/"+name+"_width.root")
    print("pull_1bins: ", pull_1.GetNbinsX())
    print("pull_2bins: ", pull_2.GetNbinsX())
    for i in range(1, pull_1.GetNbinsX() + 1):
        print("i:", i, " pull_1: ", pull_1.GetBinContent(i))
        print("i:", i, " pull_2: ", pull_2.GetBinContent(i))
        pull_1.SetBinError(i, pull_2.GetBinContent(i))
    newhists.Draw("colz")
    pull_1.SetLineColor(ROOT.kBlack)
    pull_1.SetMarkerColor(ROOT.kBlack)
    pull_1.SetLineWidth(2)
    pull_1.Draw("e1 same")
    output.SaveAs("Pulls/" + name + "_pull.png")
    output.SaveAs("Pulls/" + name + "_pull.pdf")
    # output.SaveAs("Pulls/"+name+"_pull.root")
    # newhists.Write()
# fHistOut.Close()
