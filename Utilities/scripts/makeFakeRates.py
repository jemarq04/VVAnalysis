#!/usr/bin/env python
import datetime

import ROOT
from .python import ConfigureJobs, HistTools, OutputTools, SelectorTools, UserInput

ROOT.gROOT.SetBatch(True)

channels = ["eee", "eem", "emm", "mmm"]


def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--proof", "-p", action="store_true", help="Don't use proof")
    parser.add_argument("--lumi", "-l", type=float, default=35.87, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str, default="", help="Output file name")
    return vars(parser.parse_args())


def getHistNames(channels):
    base_hists = [x + y for x in ["passingLoose", "passingTight"] for y in ["1DEta", "1DPt", "2D"]]
    if len(channels) == 0:
        return base_hists
    return [x + "_" + y for x in base_hists for y in channels]


# Turn off overflow for FR hists (> 50 is pretty much all EWK anyway)
def makeCompositeHists(name, members, addRatios=True, overflow=False):
    composite = ROOT.TList()
    composite.SetName(name)
    for directory in [str(i) for i in members]:
        for histname in getHistNames(["eee", "eem", "emm", "mmm"]):
            hist = fOut.Get("/".join([directory, histname]))
            if hist:
                sumhist = composite.FindObject(hist.GetName())
                if "data" not in directory and hist.GetEntries() > 0:
                    sumweights_hist = fOut.Get("/".join([directory, "sumweights"]))
                    sumweights = sumweights_hist.Integral()
                    hist.Scale(members[directory] * 1000 * args["lumi"] / sumweights)
                if overflow and isinstance(hist, ROOT.TH1):
                    xbins = hist.GetNbinsX()
                    ybins = hist.GetNbinsY()
                    for i in range(1, xbins):
                        setbin = hist.GetBin(i, ybins)
                        obin = hist.GetBin(i, ybins + 1)
                        hist.SetBinContent(setbin, hist.GetBinContent(obin) + hist.GetBinContent(setbin))
                    for i in range(1, ybins):
                        setbin = hist.GetBin(xbins, i)
                        obin = hist.GetBin(xbins + 1, i)
                        hist.SetBinContent(setbin, hist.GetBinContent(obin) + hist.GetBinContent(setbin))
                    setbin = hist.GetBin(xbins, ybins)
                    obin = hist.GetBin(xbins + 1, ybins + 1)
                    hist.SetBinContent(setbin, hist.GetBinContent(obin) + hist.GetBinContent(setbin))
            else:
                raise RuntimeError("hist %s was not produced for dataset %s!" % (histname, directory))
            if not sumhist:
                sumhist = hist.Clone()
                composite.Add(sumhist)
            else:
                sumhist.Add(hist)
    for hist_name in getHistNames([]):
        etot = composite.FindObject(hist_name + "_eee").Clone()
        etot.SetName(hist_name + "_allE")
        etot.Add(composite.FindObject(hist_name + "_emm"))
        composite.Add(etot)
        mtot = composite.FindObject(hist_name + "_mmm").Clone()
        mtot.SetName(hist_name + "_allMu")
        mtot.Add(composite.FindObject(hist_name + "_eem"))
        composite.Add(mtot)
    if addRatios:
        ratios = getRatios(composite)
        for ratio in ratios:
            composite.Add(ratio)
    return composite


def getRatios(hists):
    ratios = []
    for hist in hists:
        if "Tight" not in hist.GetName():
            continue
        ratio = hist.Clone()
        ratio.SetName(hist.GetName().replace("passingTight", "ratio"))
        if not ratio.GetSumw2():
            ratio.Sumw2()
        ratio.Divide(hists.FindObject(hist.GetName().replace("Tight", "Loose")))
        ratios.append(ratio)
    return ratios


args = getComLineArgs()
proof = 0
if args["proof"]:
    ROOT.TProof.Open("workers=12")
    proof = ROOT.gProof
today = datetime.date.today().strftime("%d%b%Y")
fileName = "data/fakeRate%s-%s.root" % (today, args["selection"]) if args["output_file"] == "" else args["output_file"]
fOut = ROOT.TFile(fileName, "recreate")

fScales = ROOT.TFile("data/scaleFactors.root")
muonIsoSF = fScales.Get("muonIsoSF")
muonIdSF = fScales.Get("muonTightIdSF")
electronTightIdSF = fScales.Get("electronTightIdSF")
electronGsfSF = fScales.Get("electronGsfSF")
pileupSF = fScales.Get("pileupSF")
sf_inputs = [electronTightIdSF, electronGsfSF, muonIsoSF, muonIdSF, pileupSF]

SelectorTools.applySelector(
    args["filenames"],
    "FakeRateSelector",
    args["selection"],
    fOut,
    extra_inputs=sf_inputs,
    proof=args["proof"],
    addSumweights=True,
)

alldata = makeCompositeHists("AllData", ConfigureJobs.getListOfFilesWithXSec(["WZxsec2016data"]))
OutputTools.writeOutputListItem(alldata, fOut)
allewk = makeCompositeHists(
    "AllEWK", ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfEWKFilenames()), False
)
OutputTools.writeOutputListItem(allewk, fOut)
allnonprompt = makeCompositeHists(
    "NonpromptMC", ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfNonpromptFilenames())
)
OutputTools.writeOutputListItem(allnonprompt, fOut)
final = HistTools.getDifference(fOut, "DataEWKCorrected", "AllData", "AllEWK", getRatios)
OutputTools.writeOutputListItem(final, fOut)
