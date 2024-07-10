#!/usr/bin/env python3
import ROOT
from python import SelectorTools
from python import UserInput
from python import ConfigureJobs
import os
import sys

def writeOutputListItem(item, directory):
    if item.ClassName() == "TList":
        d = directory.Get(item.GetName())
        if not d:
            d = directory.mkdir(item.GetName())
            ROOT.SetOwnership(d, False)
        for subItem in item:
            writeOutputListItem(subItem, d)
    elif hasattr(item, 'Write'):
        directory.cd()
        item.Write()
    else:
        print("Couldn't write output item:")
        print(repr(item))
    directory.cd()

def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--proof", "-p", 
        action='store_true', help="Don't use proof")
    parser.add_argument("--lumi", "-l", type=float,
        default=35.87, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str,
        default="test.root", help="Output file name")
    parser.add_argument("--output_selection", type=str,
        default="", help="Selection stage of output file "
        "(Same as input if not give)")
    parser.add_argument("-b", "--hist_names", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["all"], help="List of histograms, "
                        "as defined in AnalysisDatasetManager, separated "
                        "by commas")
    return vars(parser.parse_args())

def getDifference(name, dir1, dir2, addRatios=True):
    differences = ROOT.TList()
    differences.SetName(name)
    channels = ["eee", "eem", "emm", "mmm"]
    for histname in [i.GetName() for i in fOut.Get(dir1).GetListOfKeys()]:
        if histname == "sumweights": continue
        hist1 = fOut.Get("/".join([dir1, histname]))
        hist2 = fOut.Get("/".join([dir2, histname]))
        if hist1 and hist2:
            diff = hist1.Clone()
            diff.Add(hist2, -1)
        elif not hist1:
            print("WARNING: Hist %s was not produced for " \
                "dataset(s) %s" % (histname, dir1))
        elif not hist2:
            print("WARNING: Hist %s was not produced for " \
                "dataset(s) %s" % (histname, dir2))
        differences.Add(diff)
    if addRatios:
        ratios = getRatios(differences)
        for ratio in ratios:
            differences.Add(ratio) 
    return differences

def makeCompositeHists(name, members, lumi):
    composite = ROOT.TList()
    composite.SetName(name)
    for directory in [str(i) for i in list(members.keys())]:
        if not fOut.Get(directory):
            print("Skipping invalid filename %s" % directory)
            continue
        for histname in [i.GetName() for i in fOut.Get(directory).GetListOfKeys()]:
            if histname == "sumweights": continue
            hist = fOut.Get("/".join([directory, histname]))
            if hist:
                sumhist = composite.FindObject(hist.GetName())
                if "data" not in directory and hist.GetEntries() > 0:
                    sumweights_hist = fOut.Get("/".join([directory, "sumweights"]))
                    sumweights = sumweights_hist.Integral()
                    hist.Scale(members[directory]*1000*lumi/sumweights)
            else:
                raise RuntimeError("hist %s was not produced for "
                    "dataset %s!" % (histname, directory))
            if not sumhist:
                sumhist = hist.Clone()
                composite.Add(sumhist)
            else:
                sumhist.Add(hist)
    return composite

def getHistExpr(hist_names, selection):
    info = ROOT.TList()
    info.SetName("histinfo")
    for hist_name in hist_names:
        bin_info = HistTools.getHistBinInfo(manager_path, selection, hist_name)
        bin_expr = "{nbins}, {xmin}, {xmax}".format(**bin_info)
        info.Add(ROOT.TNamed(hist_name, "%s $ %s" % (hist_name, bin_expr))
        )
    return info

ROOT.gROOT.SetBatch(True)

args = getComLineArgs()
manager_path = ConfigureJobs.getManagerPath()
sys.path.append("/".join([manager_path, 
    "AnalysisDatasetManager", "Utilities/python"]))
import HistTools 

tmpFileName = args['output_file']
fOut = ROOT.TFile(tmpFileName, "recreate")

fScales = ROOT.TFile('data/scaleFactors.root')
#mCBMedFakeRate = fScales.Get("mCBMedFakeRate_Svenja")
#eCBTightFakeRate = fScales.Get("eCBTightFakeRate_Svenja")
mCBMedFakeRate = fScales.Get("mCBMedFakeRate")
mCBTightFakeRate = fScales.Get("mCBTightFakeRate")
eCBTightFakeRate = fScales.Get("eCBTightFakeRate")
# For medium muons
#mCBMedFakeRate.SetName("fakeRate_allMu")
mCBTightFakeRate.SetName("fakeRate_allMu")
eCBTightFakeRate.SetName("fakeRate_allE")

muonIsoSF = fScales.Get('muonIsoSF')
muonIdSF = fScales.Get('muonTightIdSF')
electronTightIdSF = fScales.Get('electronTightIdSF')
pileupSF = fScales.Get('pileupSF')

fr_inputs = [eCBTightFakeRate, mCBTightFakeRate,]
sf_inputs = [electronTightIdSF, muonIsoSF, muonIdSF, pileupSF]
selection = args['selection'].replace("LooseLeptons", "") \
    if args['output_selection'] == "" else args['output_selection'].split("_")[0]
analysis = "/".join([args['analysis'], selection])
hists = HistTools.getAllHistNames(manager_path, analysis) \
    if "all" in args['hist_names'] else args['hist_names']
    
hist_inputs = [getHistExpr(hists, analysis)]
tselection = [ROOT.TNamed("selection", args['output_selection'])]

if args['proof']:
    ROOT.TProof.Open('workers=12')
background = SelectorTools.applySelector(["WZxsec2016data"] +
    ConfigureJobs.getListOfEWKFilenames(), 
        "WZBackgroundSelector", args['selection'], fOut, 
        extra_inputs=fr_inputs+hist_inputs+tselection, proof=args['proof'])
mc = SelectorTools.applySelector(["WZxsec2016"], "WZSelector", args['selection'], fOut, 
        extra_inputs=sf_inputs+hist_inputs+tselection, addsumweights=True, proof=args['proof'])

alldata = makeCompositeHists("AllData", 
    ConfigureJobs.getListOfFilesWithXSec(["WZxsec2016data"], manager_path), args['lumi'])
writeOutputListItem(alldata, fOut)
nonpromptmc = makeCompositeHists("NonpromptMC", ConfigureJobs.getListOfFilesWithXSec( 
    ConfigureJobs.getListOfNonpromptFilenames(), manager_path), args['lumi'])
writeOutputListItem(nonpromptmc, fOut)
ewkmc = makeCompositeHists("AllEWK", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfEWKFilenames(), manager_path), args['lumi'])
writeOutputListItem(ewkmc, fOut)
ewkcorr = getDifference("DataEWKCorrected", "AllData", "AllEWK", False)

writeOutputListItem(ewkcorr, fOut)
