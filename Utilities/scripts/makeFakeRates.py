#!/usr/bin/env python
import ROOT
import glob
import datetime
from python import UserInput
from python import ConfigureJobs

channels = ["eee", "eem", "emm", "mmm"]
def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--proof", "-p", 
        action='store_true', help="Don't use proof")
    parser.add_argument("--lumi", "-l", type=float,
        default=35.87, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str,
        default="", help="Output file name")
    return vars(parser.parse_args())

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

def getHistNames(channels):
    base_hists = [x+y for x in ["passingLoose", "passingTight"] \
            for y in "1DEta", "1DPt", "2D"]
    if len(channels) == 0:
        return base_hists
    return [x+"_"+y for x in base_hists for y in channels]

def makeCompositeHists(name, members, addRatios=True, overflow=True):
    composite = ROOT.TList()
    composite.SetName(name)
    for directory in [str(i) for i in list(members.keys())]:
        for histname in getHistNames(["eee", "eem", "emm", "mmm"]):
            hist = fOut.Get("/".join([directory, histname]))
            if hist:
                sumhist = composite.FindObject(hist.GetName())
                if "data" not in directory and hist.GetEntries() > 0:
                    sumweights_hist = fOut.Get("/".join([directory, "sumweights"]))
                    sumweights = sumweights_hist.Integral()
                    hist.Scale(members[directory]*1000*args['lumi']/sumweights)
                if overflow and isinstance(hist, ROOT.TH1):
                    xbins = hist.GetNbinsX()
                    ybins = hist.GetNbinsY()
                    for i in range(1,xbins):
                        setbin = hist.GetBin(i, ybins)
                        obin = hist.GetBin(i, ybins+1)
                        hist.SetBinContent(setbin, 
                            hist.GetBinContent(obin)+hist.GetBinContent(setbin))
                    for i in range(1, ybins):
                        setbin = hist.GetBin(xbins, i)
                        obin = hist.GetBin(xbins+1, i)
                        hist.SetBinContent(setbin, 
                            hist.GetBinContent(obin)+hist.GetBinContent(setbin))
                    setbin = hist.GetBin(xbins, ybins)
                    obin = hist.GetBin(xbins+1, ybins+1)
                    hist.SetBinContent(setbin, 
                        hist.GetBinContent(obin)+hist.GetBinContent(setbin))
            else:
                raise RuntimeError("hist %s was not produced for "
                    "dataset %s!" % (histname, directory))
            if not sumhist:
                sumhist = hist.Clone()
                composite.Add(sumhist)
            else:
                sumhist.Add(hist)
    for hist_name in getHistNames([]):
        etot = composite.FindObject(hist_name+"_eee").Clone()
        etot.SetName(hist_name+"_allE")
        etot.Add(composite.FindObject(hist_name+"_emm"))
        composite.Add(etot)
        mtot = composite.FindObject(hist_name+"_mmm").Clone()
        mtot.SetName(hist_name+"_allMu")
        mtot.Add(composite.FindObject(hist_name+"_eem"))
        composite.Add(mtot)
    if addRatios:
        ratios = getRatios(composite)
        for ratio in ratios:
            composite.Add(ratio) 
    return composite

def getDifference(name, dir1, dir2, addRatios=True, composite=True):
    differences = ROOT.TList()
    differences.SetName(name)
    if composite:
        channels.extend(["allE", "allMu"])
    for histname in getHistNames(channels):
        hist1 = fOut.Get("/".join([dir1, histname]))
        hist2 = fOut.Get("/".join([dir2, histname]))
        if hist1 and hist2:
            diff = hist1.Clone()
            diff.Add(hist2, -1)
        else:
            raise RuntimeError("hist %s was not produced for "
                "dataset(s) %s and/or %s!" % (histname, dir1, dir2))
        differences.Add(diff)
    if addRatios:
        ratios = getRatios(differences)
        for ratio in ratios:
            differences.Add(ratio) 
    return differences

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
if args['proof']:
    ROOT.TProof.Open("workers=12")
    proof = ROOT.gProof
today = datetime.date.today().strftime("%d%b%Y")
fileName = "data/fakeRate%s-%s.root" % (today, args['selection']) if args['output_file'] == "" \
        else args['output_file']
fOut = ROOT.TFile(fileName, "recreate")
selector_name = "FakeRateSelector"
path = ConfigureJobs.getManagerPath()
for dataset in ConfigureJobs.getListOfFiles(args['filenames'], path, args['selection']):
    for chan in channels: 
        select = getattr(ROOT, selector_name)()
        inputs = ROOT.TList()
        select.SetInputList(inputs)
        tchan = ROOT.TNamed("channel", chan)
        tname = ROOT.TNamed("name", dataset)
        inputs.Add(tname)
        inputs.Add(tchan)
        ROOT.gROOT.cd()
        sumweights_hist = ROOT.TH1D("sumweights", "sumweights", 1,0,100)
        if proof:
            proof_path = "_".join([dataset, args['analysis'], 
                args['selection']+("#/%s/ntuple" % chan)])
            proof.Process(proof_path, select, "")
            proof_meta_path = "_".join([dataset, args['analysis'], 
                args['selection']+"#/metaInfo/metaInfo"])
            ## TODO proof draw command for meta tree
            #proof.DrawSelect(proof_path, "1>>sumweights", "")
        else: 
            chain = ROOT.TChain("%s/ntuple" % chan)
            meta_chain = ROOT.TChain("metaInfo/metaInfo")
            try:
                file_path = ConfigureJobs.getInputFilesPath(dataset, 
                    path, args['selection'], args['analysis'])
                print(file_path)
                chain.Add(file_path)
                chain.Process(select, "")
                if "data" not in dataset and chan == "eee":
                    meta_chain.Add(file_path)
                    meta_chain.Draw("1>>sumweights", "summedWeights")
                    sumweights_hist.SetDirectory(0)
            except ValueError as e:
                print(e)
                sumweights_hist.Delete()
                continue
        output = select.GetOutputList()
        if chan == "eee":
            outputlist = output.FindObject(dataset)
            outputlist.Add(sumweights_hist)
            ROOT.SetOwnership(sumweights_hist, False)
            outputlist.SetOwner()
        for item in output:
            if "PROOF" in item.GetName() or item.GetName() == "MissingFiles":
                continue
            writeOutputListItem(item, fOut)
            ROOT.SetOwnership(item, False)
            item.Delete()
        if hasattr(sumweights_hist, "Delete"):
            sumweights_hist.Delete()
alldata = makeCompositeHists("AllData", ConfigureJobs.getListOfFilesWithXSec(["WZxsec2016data"], path))
writeOutputListItem(alldata, fOut)
allewk = makeCompositeHists("AllEWK", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfEWKFilenames(), path), False)
writeOutputListItem(allewk, fOut)
final = getDifference("DataEWKCorrected", "AllData", "AllEWK")
writeOutputListItem(final, fOut)
