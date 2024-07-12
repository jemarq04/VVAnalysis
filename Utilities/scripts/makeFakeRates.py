#!/usr/bin/env python3
import ROOT
import glob
import datetime
from python import UserInput,OutputTools
from python import ConfigureJobs
from python import SelectorTools,HistTools
import logging
import sys

ROOT.gROOT.SetBatch(True)

def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float,
        default=41.5, help="luminosity value (in fb-1)")
    parser.add_argument("--test", action='store_true',
        help="Run test job (no background estimate)")
    parser.add_argument("--uwvv", action='store_true',
        help="Use UWVV format ntuples in stead of NanoAOD")
    parser.add_argument("--noHistConfig", action='store_true',
        help="Don't rely on config file to specify hist info")
    parser.add_argument("--input_tier", type=str,
        default="", help="Selection stage of input files")
    parser.add_argument("--year", type=str,
        default="default", help="Year of Analysis")
    parser.add_argument("-j", "--numCores", type=int, default=1,
        help="Number of cores to use (parallelize by dataset)")
    parser.add_argument("--scalefactors_file", "-sf", type=str,
        default="", help="ScaleFactors file name")
    parser.add_argument("--output_file", "-o", type=str,
        default="", help="Output file name")
    parser.add_argument("-c", "--channels", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["eee","eem","emm","mmm"], help="List of channels"
                        "separated by commas. NOTE: set to Inclusive for NanoAOD")
    parser.add_argument("-b", "--hist_names", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["all"], help="List of histograms, "
                        "as defined in ZZ4lRun2DatasetManager, separated "
                        "by commas")
    return vars(parser.parse_args())

def getHistNames(channels):
    base_hists = [x+y for x in ["passingLooseE", "passingTightE","passingLooseMu", "passingTightMu"] \
            for y in "1DEta", "1DPt_barrel","1DPt_endcap", "2D"]
    if len(channels) == 0:
        return base_hists
    return [x+"_"+y for x in base_hists for y in channels]

# Turn off overflow for FR hists (> 50 is pretty much all EWK anyway)
def makeCompositeHists(hist_file,name, members, addRatios=True, overflow=False):
    composite = ROOT.TList()
    composite.SetName(name)
    if name=="AllEWK":
        print("EWK members: ",members)
    for directory in [str(i) for i in list(members.keys())]:
        for histname in getHistNames(["eee", "eem", "emm", "mmm"]):
            print("histname:", histname)
            print("hist_file:", hist_file)
            print("directory:",directory)
            hist = hist_file.Get("/".join([directory, str(histname)]))
            print("hist:", hist)
            if hist:
                sumhist = composite.FindObject(hist.GetName())
                if "data" not in directory and hist.GetEntries() > 0:
                    sumweights_hist = hist_file.Get("/".join([directory, "sumweights"]))
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

today = datetime.date.today().strftime("%d%b%Y")
#fileName = "data/fakeRate%s-%s.root" % (today,args['analysis']) if args['output_file'] == "" \
#        else args['output_file']
fileName="data/fakeRate15Sep2019-ZZ4l2016.root"
if not args['test']:
    fOut = ROOT.TFile(fileName, "recreate")
    
    
    addScaleFacs = False
    if args['analysis'] == "WZxsec2016" or args['analysis'] == 'Zstudy_2016' or args['scalefactors_file']:
        addScaleFacs = True
    sf_inputs = [ROOT.TParameter(bool)("applyScaleFacs", False)]
    
    if args['input_tier'] == '':
        args['input_tier'] = args['selection']
    selection = args['selection'].split("_")[0]
    
    if selection == "Inclusive2Jet":
        selection = "Wselection"
        print("Info: Using Wselection for hist defintions")
    analysis = "/".join([args['analysis'], selection])
    hists, hist_inputs = UserInput.getHistInfo(analysis, args['hist_names'], args['noHistConfig'])
    print("hists: ",hists)
    print("hist_inputs: ", hist_inputs)
    selector = SelectorTools.SelectorDriver(args['analysis'], args['selection'], args['input_tier'], args['year'])
    selector.setOutputfile(fOut.GetName())
    selector.setInputs(sf_inputs+hist_inputs)
    selector.isFake()
    
    selector.setNtupeType("UWVV" if args['uwvv'] else "NanoAOD")
    if args['uwvv']:
        logging.debug("Processing channels " % args['channels'])
        selector.setChannels(args['channels'])
    
    selector.setNumCores(args['numCores'])
    
    if args['filenames']:
        selector.setDatasets(args['filenames'])
    else:
        selector.setFileList(*args['inputs_from_file'])
    mc = selector.applySelector()
    
    #if args['test']:
    #    sys.exit(0)
    
    #fOut.Close()
if args['test']:
    fOut = ROOT.TFile.Open(fileName, "update")
    alldata = makeCompositeHists(fOut,"AllData", ConfigureJobs.getListOfFilesWithXSec([args['analysis']+"data"]))
    OutputTools.writeOutputListItem(alldata, fOut)
    alldata.Delete()
    allewk = makeCompositeHists(fOut,"AllEWK", ConfigureJobs.getListOfFilesWithXSec(
        ConfigureJobs.getListOfEWKFilenames()), True)
    OutputTools.writeOutputListItem(allewk, fOut)
    allewk.Delete()
    allDYJets = makeCompositeHists(fOut,"DYMC", ConfigureJobs.getListOfFilesWithXSec(
        ConfigureJobs.getListOfDYFilenames()),True)
    OutputTools.writeOutputListItem(allDYJets, fOut)
    allDYJets.Delete()
    #allnonprompt = makeCompositeHists("NonpromptMC", ConfigureJobs.getListOfFilesWithXSec(
    #    ConfigureJobs.getListOfNonpromptFilenames()))
    #OutputTools.writeOutputListItem(allnonprompt, fOut)
    final = HistTools.getDifference(fOut, "DataEWKCorrected", "AllData", "AllEWK", getRatios)
    OutputTools.writeOutputListItem(final, fOut)
    final.Delete()
