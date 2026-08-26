#!/usr/bin/env python
import array
import datetime
import math
import os
import subprocess

from . import makeSimpleHtml
import ROOT
from .python import ConfigureJobs, UserInput
from ROOT import vector as Vec

VFloat = Vec("float")
from PlotTools import PlotStyle as Style

style = Style()
# ROOT.gStyle.SetLineScalePS(1.8)
ROOT.gStyle.SetOptDate(False)
channels = ["eeee", "eemm", "mmmm"]


# channels = []
def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float, default=41.5, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str, default="", help="Output file name")
    parser.add_argument("--test", action="store_true", help="Run test job (no background estimate)")
    parser.add_argument("--variable", "-vr", type=str, default="all", help="variableName")
    parser.add_argument(
        "--noNorm",
        action="store_true",
        help="Leave differential cross sections in abolute normalization rather than normalizing to unity area.",
    )
    parser.add_argument("--NormFb", action="store_true", help="Normalize differential cross sections to the luminosity")
    parser.add_argument("--logy", "--logY", "--log", action="store_true", help="Put vertical axis on a log scale.")
    parser.add_argument("--makeTotals", action="store_true", help="plot total unfolded with uncertainities.")
    parser.add_argument(
        "--unfoldDir",
        type=str,
        nargs="?",
        default="/afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/MGMatrix_MGUnfolded_Uncert_11Feb2020/",
        help="Directory to put response and covariance plots in",
    )
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
for var, prettyVar in prettyVars.items():
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

legParamsLogy = {v: p.copy() for v, p in legParams.items()}
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


def normalizeBins(h):
    binUnit = 1  # min(h.GetBinWidth(b) for b in range(1,len(h)+1))
    for ib in range(1, h.GetNbinsX() + 1):
        w = h.GetBinWidth(ib)
        h.SetBinContent(ib, h.GetBinContent(ib) * binUnit / w)
        h.SetBinError(ib, h.GetBinError(ib) * binUnit / w)
        if h.GetBinError(ib) > h.GetBinContent(ib):
            h.SetBinError(ib, h.GetBinContent(ib))
    h.Sumw2()


def unnormalizeBins(h):
    binUnit = 1  # min(h.GetBinWidth(b) for b in range(1,len(h)+1))
    for ib in range(1, h.GetNbinsX() + 1):
        w = h.GetBinWidth(ib)
        h.SetBinContent(ib, h.GetBinContent(ib) * w / binUnit)
        h.SetBinError(ib, h.GetBinError(ib) * w / binUnit)
        if h.GetBinError(ib) > h.GetBinContent(ib):
            h.SetBinError(ib, h.GetBinContent(ib))
    h.Sumw2()


def createRatio(h1, h2):
    Nbins = h1.GetNbinsX()
    Ratio = h1.Clone("Ratio")
    hStackLast = h2.Clone("hStackLast")
    try:
        Ratio.Sumw2()
    except AttributeError:
        pass
    try:
        hStackLast.Sumw2()
    except AttributeError:
        pass
    for i in range(1, Nbins + 1):
        stackcontent = hStackLast.GetBinContent(i)
        stackerror = hStackLast.GetBinError(i)
        datacontent = h1.GetBinContent(i)
        dataerror = h1.GetBinError(i)
        print("stackcontent: ", stackcontent, " and data content: ", datacontent)
        ratiocontent = 0
        if datacontent != 0:
            ratiocontent = datacontent / stackcontent
        if datacontent != 0:
            error = ratiocontent * (
                math.sqrt(math.pow((dataerror / datacontent), 2) + math.pow((stackerror / stackcontent), 2))
            )
        else:
            error = 2.07
        print("ratio content: ", ratiocontent)
        print("stat error: ", error)
        Ratio.SetBinContent(i, ratiocontent)
        Ratio.SetBinError(i, error)

    Ratio.GetYaxis().SetRangeUser(0.4, 1.8)
    Ratio.SetStats(0)
    Ratio.GetYaxis().CenterTitle()
    Ratio.SetMarkerStyle(20)
    Ratio.SetMarkerSize(0.7)

    line = ROOT.TLine(h1.GetXaxis().GetXmin(), 1.0, h1.GetXaxis().GetXmax(), 1.0)
    line.SetLineStyle(7)

    Ratio.GetYaxis().SetLabelSize(0.14)
    Ratio.GetYaxis().SetTitleSize(0.12)
    Ratio.GetYaxis().SetLabelFont(42)
    Ratio.GetYaxis().SetTitleFont(42)
    Ratio.GetYaxis().SetTitleOffset(0.25)
    Ratio.GetYaxis().SetNdivisions(100)
    Ratio.GetYaxis().SetTickLength(0.05)

    Ratio.GetXaxis().SetLabelSize(0)
    Ratio.GetXaxis().SetTitleSize(0)

    return Ratio, line


def createCanvasPads(varName):
    c = ROOT.TCanvas("c", "canvas")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLegendBorderSize(0)
    # Upper histogram plot is pad1
    pad1 = ROOT.TPad("pad1", "pad1", 0.01, 0.33, 0.99, 0.99)
    pad1.Draw()
    pad1.cd()
    if varName != "drz1z2":
        pad1.SetLogy()
    pad1.SetFillColor(0)
    pad1.SetFrameBorderMode(0)
    pad1.SetBorderMode(0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    # pad1.SetGridx()
    # pad1.Draw()
    return c, pad1


def createPad2(canvas):
    # Lower ratio plot is pad2
    canvas.cd()  # returns to main canvas before defining pad2
    pad2 = ROOT.TPad("pad2", "pad2", 0.01, 0.20, 0.99, 0.33)
    pad2.Draw()
    pad2.cd()
    pad2.SetFillColor(0)
    pad2.SetFrameBorderMode(0)
    pad2.SetBorderMode(1)  # bordermode = -1 box looks as it is behind the screen
    # bordermode = 0 no special effects
    # bordermode = 1 box looks as it is in front of the screen
    pad2.SetTopMargin(0)  # joins upper and lower plot
    pad2.SetBottomMargin(0)
    # pad2.SetGridx()
    # pad2.Draw()
    return pad2


def createPad3(canvas):
    # Lower ratio plot is pad3
    canvas.cd()  # returns to main canvas before defining pad3
    pad3 = ROOT.TPad("pad3", "pad3", 0.01, 0.03, 0.99, 0.20)
    pad3.Draw()
    pad3.cd()
    pad3.SetFillColor(0)
    pad3.SetFrameBorderMode(0)
    # pad3.SetFrameFillStyle(4000)
    pad3.SetBorderMode(0)
    pad3.SetTopMargin(0)  # joins upper and lower plot
    pad3.SetBottomMargin(0.35)
    # pad3.SetGridx()
    # pad3.Draw()
    return pad3


# rebin histos and take care of overflow bins
def rebin(hist, varName):
    ROOT.SetOwnership(hist, False)
    # No need to rebin certain variables but still might need overflow check
    if varName not in ["eta"]:
        bins = array.array("d", _binning[varName])
        Nbins = len(bins) - 1
        hist = hist.Rebin(Nbins, "", bins)
    else:
        Nbins = hist.GetSize() - 2
    add_overflow = hist.GetBinContent(Nbins) + hist.GetBinContent(Nbins + 1)
    hist.SetBinContent(Nbins, add_overflow)
    return hist


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


def getSigTextBox(x, y, sigLabel, size):
    texS = ROOT.TLatex(x, y, str(sigLabel))
    texS.SetNDC()
    texS.SetTextFont(42)
    texS.SetTextSize(size)
    texS.Draw()


def RatioErrorBand(Ratio, hUncUp, hUncDn, hTrueNoErrs, varName):
    ratioGraph = ROOT.TGraphAsymmErrors(Ratio)
    ROOT.SetOwnership(ratioGraph, False)
    tmpData = Ratio.Clone("tmp")
    for i in range(1, tmpData.GetNbinsX() + 1):
        if hTrueNoErrs.GetBinContent(i) == 0:
            continue
        eUp = hUncUp.GetBinContent(i)
        eDn = hUncDn.GetBinContent(i)
        tru = hTrueNoErrs.GetBinContent(i)
        # print "eUp: ",eUp, "","eDn: ",eDn
        errorUp = tmpData.GetBinContent(i) + math.sqrt(math.pow(tmpData.GetBinError(i), 2) + math.pow((eUp / tru), 2))
        errorUp -= Ratio.GetBinContent(i)
        errorDn = max(
            tmpData.GetBinContent(i) - math.sqrt(math.pow(tmpData.GetBinError(i), 2) + math.pow((eDn / tru), 2)), 0
        )
        errorDn = Ratio.GetBinContent(i) - errorDn
        print("stat. error: ", tmpData.GetBinError(i))
        print("eUp/tru: ", eUp / tru)
        print("eDn/tru: ", eDn / tru)
        print("errorUp: ", errorUp, "", "errorDn: ", errorDn)
        ratioGraph.SetPointEYhigh(i - 1, errorUp)
        ratioGraph.SetPointEYlow(i - 1, errorDn)
    ratioGraph.SetFillColorAlpha(1, 0.5)
    ratioGraph.SetFillStyle(3001)
    ratioGraph.GetXaxis().SetLabelSize(0)
    ratioGraph.GetXaxis().SetTitleSize(0)
    # ratioGraph.GetYaxis().SetLabelSize(0)
    # ratioGraph.GetYaxis().SetTitleSize(0)
    ratioGraph.GetXaxis().SetLimits(Ratio.GetXaxis().GetXmin(), Ratio.GetXaxis().GetXmax())
    if varName == "drz1z2":
        ratioGraph.SetMaximum(1.8)
        ratioGraph.SetMinimum(0.4)
    else:
        ratioGraph.SetMaximum(1.8)
        ratioGraph.SetMinimum(0.4)
    return ratioGraph


def MainErrorBand(hMain, hUncUp, hUncDn, varName, norm, normFb):
    MainGraph = ROOT.TGraphAsymmErrors(hMain)
    ROOT.SetOwnership(MainGraph, False)
    tmpData = hMain.Clone("tmp")
    for i in range(1, tmpData.GetNbinsX() + 1):
        if hMain.GetBinContent(i) == 0:
            continue
        eUp = hUncUp.GetBinContent(i)
        eDn = hUncDn.GetBinContent(i)
        # print "eUp: ",eUp, "","eDn: ",eDn
        errorUp = tmpData.GetBinContent(i) + math.sqrt(math.pow(tmpData.GetBinError(i), 2) + math.pow(eUp, 2))
        errorUp -= hMain.GetBinContent(i)
        errorDn = max(tmpData.GetBinContent(i) - math.sqrt(math.pow(tmpData.GetBinError(i), 2) + math.pow(eDn, 2)), 0)
        errorDn = hMain.GetBinContent(i) - errorDn
        print("errorUp: ", errorUp, "", "errorDn: ", errorDn)
        MainGraph.SetPointEYhigh(i - 1, errorUp)
        MainGraph.SetPointEYlow(i - 1, errorDn)
    MainGraph.SetFillColorAlpha(1, 0.7)
    MainGraph.SetFillStyle(3001)
    if norm:
        drawyTitle = _yTitle[varName]
    elif normFb:
        drawyTitle = _yTitleNoNorm[varName]
    else:
        drawyTitle = "Events"
    MainGraph.GetYaxis().SetTitle(drawyTitle)

    # MainGraph.GetYaxis().SetTitleSize(*hMain.GetYaxis().GetTitleSize())
    MainGraph.GetYaxis().SetLabelSize(0.8 * hMain.GetYaxis().GetLabelSize())
    if varName == "drz1z2":
        MainGraph.GetYaxis().SetTitleOffset(1.0)
    else:
        MainGraph.GetYaxis().SetLabelOffset(0.0)
        MainGraph.GetYaxis().SetTitleOffset(1.0)
    # MainGraph.GetXaxis().SetLabelSize(0)
    # MainGraph.GetXaxis().SetTitleSize(0)
    # MainGraph.GetYaxis().SetLabelSize(0)
    # MainGraph.GetYaxis().SetTitleSize(0)
    MainGraph.GetXaxis().SetLimits(hMain.GetXaxis().GetXmin(), hMain.GetXaxis().GetXmax())
    # MainGraph.SetMaximum(1.5)

    MainGraph.SetMaximum(1.2 * (hMain.GetMaximum()))
    MainGraph.SetMinimum(0.5 * (hMain.GetMinimum()))
    # if varName=="drz1z2":
    #    MainGraph.SetMinimum(0.0)
    # else:
    # MainGraph.SetMinimum(0.5*(hMain.GetMinimum()))
    return MainGraph


def generatePlots(hUnfolded, hUncUp, hUncDn, hTruth, hTruthAlt, varName, norm, normFb, lumi, unfoldDir):
    _UnfHists = []
    _TrueHists = []
    # for normalization if needed
    _nomArea = hUnfolded.Integral(0, hUnfolded.GetNbinsX() + 1)
    # Make uncertainties out of the unfolded histos
    ### plot
    hUnf = hUnfolded.Clone()
    hTrue = hTruth.Clone()
    # Alt Signal
    hTrueAlt = hTruthAlt.Clone()
    hTrueLeg = hTruthAlt.Clone()
    # lumi provided already in fb-1
    lumifb = lumi

    if norm:
        hUnf.Scale(1.0 / (hUnf.Integral(0, hUnf.GetNbinsX() + 1)))
    elif normFb:
        hUnf.Scale(1.0 / lumifb)
    else:
        print("no special normalization")

    print("hTrue histo here: ", hTrue)
    print("unfoldDir: ", unfoldDir)
    _xaxisSize = hUnf.GetXaxis().GetTitleSize()
    _yaxisSize = hTrue.GetXaxis().GetTitleSize()
    if unfoldDir:
        # Create a ratio plot
        c, pad1 = createCanvasPads(varName)
        Unfmaximum = hUnf.GetMaximum()
        hTrue.SetFillColor(ROOT.TColor.GetColor("#99ccff"))
        hTrue.SetLineColor(ROOT.TColor.GetColor("#000099"))
        hTrue.SetFillStyle(3010)
        # AltSignal
        hTrueAlt.SetFillColor(2)
        hTrueAlt.SetLineStyle(10)  # dashes
        hTrueAlt.SetFillStyle(0)  # hollow
        hTrueAlt.SetLineColor(ROOT.kRed)
        print("Total Truth Integral", hTrue.Integral())
        print("Total Alt Truth Integral", hTrueAlt.Integral())
        print("Total Unf Data Integral", hUnf.Integral())
        Truthmaximum = hTrue.GetMaximum()
        hTrue.SetLineWidth(2 * hTrue.GetLineWidth())
        hTrueAlt.SetLineWidth(2 * hTrueAlt.GetLineWidth())

        if not norm and normFb:
            print(f"Inclusive fiducial cross section = {hUnf.Integral(0, hUnf.GetNbinsX() + 1)} fb")
        if norm or normFb:
            normalizeBins(hUnf)

        if norm:
            hUncUp.Scale(1.0 / hUnfolded.Integral(0, hUnfolded.GetNbinsX() + 1))
            hUncDn.Scale(1.0 / hUnfolded.Integral(0, hUnfolded.GetNbinsX() + 1))
        elif normFb:
            hUncUp.Scale(1.0 / lumifb)
            hUncDn.Scale(1.0 / lumifb)
        else:
            print("no special normalization")

        if norm or normFb:
            normalizeBins(hUncUp)
            normalizeBins(hUncDn)

        if norm:
            trueInt = hTrue.Integral(0, hTrue.GetNbinsX() + 1)
            hTrue.Scale(1.0 / trueInt)
            # hTrueUncUp /= trueInt # (trueInt + hTrueUncUp.Integral(0,hTrueUncUp.GetNbinsX()+1))
            # hTrueUncDn /= trueInt # (trueInt - hTrueUncDn.Integral(0,hTrueUncDn.GetNbinsX()+1))
            # Alt Signal
            AltTrueInt = hTrueAlt.Integral(0, hTrueAlt.GetNbinsX() + 1)
            hTrueAlt.Scale(1.0 / AltTrueInt)
        elif normFb:
            hTrue.Scale(1.0 / lumifb)
            # hTrueUncUp /= lumifb
            # hTrueUncDn /= lumifb
            hTrueAlt.Scale(1.0 / lumifb)
        else:
            print("no special normalization")

        if norm or normFb:
            normalizeBins(hTrue)
            # normalizeBins(hTrueUncUp)
            # normalizeBins(hTrueUncDn)
            normalizeBins(hTrueAlt)

        hTrue.Draw("HIST")
        hTrueAlt.Draw("HIST")

        if Unfmaximum > Truthmaximum:
            hTrue.SetMaximum(Unfmaximum * 1.2)
        else:
            hTrue.SetMaximum(Truthmaximum * 1.2)

        hTrue.GetXaxis().SetTitle("")

        UnfErrBand = MainErrorBand(hUnf, hUncUp, hUncDn, varName, norm, normFb)
        UnfErrBand.Draw("a2")
        hTrue.GetXaxis().SetLabelSize(0)
        hTrue.GetXaxis().SetTitleSize(0)
        # hTrue.GetYaxis().SetTitle("Events")
        # hTrue.GetYaxis().SetTitleOffset(1.0)
        hTrueAlt.GetXaxis().SetLabelSize(0)
        hTrueAlt.GetXaxis().SetTitleSize(0)
        hTrueAlt.Draw("HISTSAME")
        hTrue.Draw("HISTSAME")
        # hUnf.Sumw2(False)
        # hUnf.SetBinErrorOption(ROOT.TH1.kPoisson)
        hUnf.SetLineColor(ROOT.kBlack)
        hUnf.SetMarkerStyle(20)
        hUnf.SetMarkerSize(0.7)
        hUnf.GetXaxis().SetTitle("")
        hUnf.GetXaxis().SetLabelSize(0)
        hUnf.GetXaxis().SetTitleSize(0)
        hUnf.Draw("PE1SAME")

        texS, texS1 = getLumiTextBox()
        # sigLabel = "POWHEG+MCFM+Pythia8"
        sigLabel = "POWHEG+Pythia8"

        # sigLabelAlt = "MG5_aMC@NLO+MCFM+Pythia8"
        sigLabelAlt = "MG5_aMC@NLO+Pythia8"

        if varName == "dphiz1z2" or varName == "drz1z2":
            leg = ROOT.TLegend(0.15, 0.60, 0.15 + 0.015 * len(sigLabelAlt), 0.90, "")
        elif varName == "leppt":
            leg = ROOT.TLegend(0.20, 0.18, 0.20 + 0.015 * len(sigLabelAlt), 0.48, "")
        else:
            leg = ROOT.TLegend(0.55, 0.60, 0.55 + 0.015 * len(sigLabelAlt), 0.90, "")
        # leg.AddEntry(hUnf,"Data + stat. unc.","lep")
        leg.AddEntry(hUnf, "MadGraph + stat. unc.", "lep")
        leg.AddEntry(UnfErrBand, "Stat. #oplus syst. unc.", "f")
        leg.AddEntry(hTrue, sigLabel, "lf")

        hTrueLeg.SetFillColor(2)
        hTrueLeg.SetLineStyle(10)  # dashes
        hTrueLeg.SetFillColorAlpha(2, 0.4)
        hTrueLeg.SetFillStyle(3001)  # solid
        hTrueLeg.SetLineColor(ROOT.kRed)
        hTrueLeg.SetLineWidth(4 * hTrueLeg.GetLineWidth())
        leg.AddEntry(hTrueLeg, sigLabelAlt, "l")
        leg.SetFillColor(ROOT.kWhite)
        leg.SetBorderSize(1)
        leg.SetFillStyle(1001)
        leg.SetTextSize(0.025)
        leg.Draw()

        # SecondPad
        _pad2 = createPad2(c)

        hTrueNoErrs = hTrue.Clone()  # need central value only to keep ratio uncertainties consistent
        nbins = hTrueNoErrs.GetNbinsX()
        print("trueNbins: ", nbins)

        Unfbins = hUnf.GetNbinsX()
        print("UnfNbins: ", Unfbins)
        # hTrueNoErrs.SetError(array.array('d',[0.]*nbins))
        # Starting the ratio proceedure
        Ratio, line = createRatio(hUnf, hTrueNoErrs)
        ratioErrorBand = RatioErrorBand(Ratio, hUncUp, hUncDn, hTrueNoErrs, varName)
        ratioErrorBand.GetYaxis().SetLabelSize(0)
        ratioErrorBand.GetYaxis().SetTitleSize(0)
        ratioErrorBand.Draw("a2")

        _sigTex = getSigTextBox(0.15, 0.8, sigLabel, 0.12)
        Ratio.Draw("PE1SAME")
        line.SetLineColor(ROOT.kBlack)
        line.Draw("same")

        Altyaxis = ROOT.TGaxis(
            hUnf.GetXaxis().GetXmin(),
            ratioErrorBand.GetMinimum(),
            hUnf.GetXaxis().GetXmin(),
            ratioErrorBand.GetMaximum(),
            ratioErrorBand.GetMinimum(),
            ratioErrorBand.GetMaximum(),
        )
        Altyaxis.SetNdivisions(3)
        Altyaxis.SetTitle("Data/Theo")
        Altyaxis.SetLabelFont(42)
        Altyaxis.SetLabelOffset(0.01)
        Altyaxis.SetLabelSize(0.14)
        Altyaxis.SetTitleFont(42)
        Altyaxis.SetTitleSize(0.14)
        Altyaxis.SetTitleOffset(0.30)
        Altyaxis.Draw("SAME")

        # ThirdPad
        _pad3 = createPad3(c)

        hTrueAltNoErrs = hTrueAlt.Clone()  # need central value only to keep ratio uncertainties consistent
        # nbins=hTrueNoErrs.GetNbinsX()
        # print("trueNbins: ",nbins)

        # Unfbins=hUnf.GetNbinsX()
        # print("UnfNbins: ",Unfbins)

        # hTrueNoErrs.SetError(array.array('d',[0.]*nbins))
        # Starting the ratio proceedure
        AltRatio, Altline = createRatio(hUnf, hTrueAltNoErrs)
        AltRatioErrorBand = RatioErrorBand(AltRatio, hUncUp, hUncDn, hTrueAltNoErrs, varName)
        AltRatioErrorBand.GetYaxis().SetLabelSize(0)
        AltRatioErrorBand.GetYaxis().SetTitleSize(0)
        AltRatioErrorBand.Draw("a2")
        AltRatio.Draw("PE1SAME")
        # ratioErrorBand.Draw("p")
        Altline.SetLineColor(ROOT.kRed)
        Altline.Draw("same")

        _AltTex = getSigTextBox(0.15, 0.8, sigLabelAlt, 0.10)
        # redraw axis
        xaxis = ROOT.TGaxis(
            hUnf.GetXaxis().GetXmin(),
            ratioErrorBand.GetMinimum(),
            hUnf.GetXaxis().GetXmax(),
            ratioErrorBand.GetMinimum(),
            hUnf.GetXaxis().GetXmin(),
            hUnf.GetXaxis().GetXmax(),
            510,
        )
        xaxis.SetTitle(prettyVars[varName] + "" + units[varName])
        # labelTex = getSigTextBox(0.9,0.8,prettyVars[varName]+''+units[varName])
        xaxis.SetLabelFont(42)
        xaxis.SetLabelOffset(0.03)
        xaxis.SetLabelSize(0.12)
        xaxis.SetTitleFont(42)
        xaxis.SetTitleSize(0.18)
        xaxis.SetTitleOffset(0.80)
        xaxis.Draw("SAME")

        yaxis = ROOT.TGaxis(
            hUnf.GetXaxis().GetXmin(),
            ratioErrorBand.GetMinimum(),
            hUnf.GetXaxis().GetXmin(),
            ratioErrorBand.GetMaximum(),
            ratioErrorBand.GetMinimum(),
            ratioErrorBand.GetMaximum(),
        )
        yaxis.SetNdivisions(3)
        yaxis.SetTitle("Data/Theo")
        yaxis.SetLabelFont(42)
        yaxis.SetLabelOffset(0.01)
        yaxis.SetLabelSize(0.11)
        yaxis.SetTitleFont(42)
        yaxis.SetTitleSize(0.11)
        yaxis.SetTitleOffset(0.35)
        yaxis.Draw("SAME")
        c.Update()
        plotName = "Ratio_%s" % (varName)
        output_name = "/".join([unfoldDir, plotName])
        # c.Print("%s/Ratio_%s.png" % (unfoldDir,varName))
        # c.Print("%s/Ratio_%s.eps" % (unfoldDir,varName))
        c.Print(output_name + ".eps")
        c.Print(output_name + ".png")
        subprocess.call(["epstopdf", "--outfile=%s" % output_name + ".pdf", output_name + ".eps"], env={})
        os.remove(output_name + ".eps")
        del c


def mkdir(plotDir):
    for outdir in [plotDir]:
        try:
            os.makedirs(os.path.expanduser(outdir))
        except OSError as e:
            print(e)


varNames = {"mass": "Mass", "pt": "ZZPt", "zpt": "ZPt", "leppt": "LepPt", "dphiz1z2": "dPhiZ1Z2", "drz1z2": "dRZ1Z2"}
UnfoldDir = args["unfoldDir"]
UnfoldOutDirs = {}
# Make differential cross sections normalizing to unity area.')
norm = not args["noNorm"]
# normalize with the luminosity instead of area under the curve
normFb = args["NormFb"]
# def main():
runVariables = []
runVariables.append(args["variable"])
print("runVariables: ", runVariables)
# Save histograms from saveUnfolded.py in this root file
fUse = ROOT.TFile.Open("PowMatrix_MGUnfHists-11Feb2020-ZZ4l2018.root", "read")
for varName in runVariables:
    print("varName:", varNames[varName])
    # save unfolded distributions by channel, then systematic
    hUnfolded = {}
    hTrue = {}
    hTrueAlt = {}
    hErr = {}
    hErrTrue = {}
    for chan in channels:
        print("channel: ", chan)
        print("hUnfolded: ", hUnfolded)
        print("hTrue: ", hTrue)
        UnfoldOutDir = UnfoldDir + "/" + chan + "/plots"
        if chan not in UnfoldOutDirs:
            UnfoldOutDirs[chan] = UnfoldOutDir
        if not os.path.exists(UnfoldOutDir):
            mkdir(UnfoldOutDir)
        hUnfolded[chan] = fUse.Get(chan + "_" + varName + "_unf")
        hTrue[chan] = fUse.Get(chan + "_" + varName + "_true")
        hTrueAlt[chan] = fUse.Get(chan + "_" + varName + "_trueAlt")
        print("returning unfolded? ", hUnfolded[chan])
        print("returning truth? ", hTrue[chan])
        print("returning Alt truth? ", hTrueAlt[chan])
        # Get the total UncUp and total UncDown histograms from the file as well
        hUncUp = fUse.Get(chan + "_" + varName + "_totUncUp")
        hUncDn = fUse.Get(chan + "_" + varName + "_totUncDown")
        print("UnfoldOutDir:", UnfoldOutDir)
        generatePlots(
            hUnfolded[chan],
            hUncUp,
            hUncDn,
            hTrue[chan],
            hTrueAlt[chan],
            varName,
            norm,
            normFb,
            args["lumi"],
            UnfoldOutDir,
        )

    if args["makeTotals"]:
        # Now access the histograms for all channels combined together
        # While saving in makeResponseMatrix.py, make a "total" category as wel
        hUnfTot = fUse.Get("tot_" + varName + "_unf")
        hTrueTot = fUse.Get("tot_" + varName + "_true")
        hTrueAltTot = fUse.Get("tot_" + varName + "_trueAlt")
        hTotUncUp = fUse.Get("tot_" + varName + "_totUncUp")
        hTotUncDn = fUse.Get("tot_" + varName + "_totUncDown")
        UnfoldOutDir = UnfoldDir + "/" + "tot" + "/plots"
        if "tot" not in UnfoldOutDirs:
            UnfoldOutDirs["tot"] = UnfoldOutDir
        if not os.path.exists(UnfoldOutDir):
            mkdir(UnfoldOutDir)
        generatePlots(
            hUnfTot, hTotUncUp, hTotUncDn, hTrueTot, hTrueAltTot, varName, norm, normFb, args["lumi"], UnfoldOutDir
        )
# Show plots nicely on my webpages
# for cat in ["tot"]:
for cat in ["eeee", "eemm", "mmmm", "tot"]:
    # This is where we put all the plots in html format for quick access/debugging
    makeSimpleHtml.writeHTML(
        os.path.expanduser(UnfoldOutDirs[cat].replace("/plots", "")), "Unfolded Distributions (from MC)"
    )
fUse.Close()
# exit(0)

# if __name__ == "__main__":
#    main()
