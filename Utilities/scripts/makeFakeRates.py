#!/usr/bin/env python3
import ROOT
import datetime
from python import UserInput,OutputTools
from python import ConfigureJobs
from python import SelectorTools,HistTools
import logging

ROOT.gROOT.SetBatch(True)

def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float,
        default=None, help="luminosity value (in fb-1)")
    parser.add_argument("--uwvv", action='store_true',
        help="Use UWVV format ntuples in stead of NanoAOD")
    parser.add_argument("--noHistConfig", action='store_true',
        help="Don't rely on config file to specify hist info")
    parser.add_argument("--input_tier", type=str,
        help="Selection stage of input files")
    parser.add_argument("--year", type=str,
        default="default", help="Year of Analysis")
    parser.add_argument("-j", "--numCores", type=int, default=1,
        help="Number of cores to use (parallelize by dataset)")
    parser.add_argument("--output_file", "-o", type=str,
        help="Output file name")
    parser.add_argument("-c", "--channels",
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["eee","eem","emm","mmm"], help="List of channels"
                        "separated by commas. NOTE: set to Inclusive for NanoAOD")
    parser.add_argument("-b", "--hist_names",
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["all"], help="List of histograms, "
                        "as defined in %s, separated "
                        "by commas" % ConfigureJobs.getManagerName())
    parser.add_argument("--steps", type=str, choices=["merge", "ewk", "all"],
                        default="all", help="step for fake rate calculation")
    return vars(parser.parse_args())

def main():
    args = getComLineArgs()

    if args['lumi'] is None:
        args['lumi'] = ConfigureJobs.getLuminosity(args['year'])

    today = datetime.date.today().strftime("%d%b%Y")
    fileName = "fakeRate%s-%s.root" % (today, args["analysis"]) \
            if args["output_file"] is None else args["output_file"]

    if args["steps"] in ["merge", "all"]:
        print("Merging input files")
        fOut = ROOT.TFile.Open(fileName, "recreate")
        sf_inputs = [ROOT.TParameter(bool)("applyScaleFacs", False)]

        if args['input_tier'] is None:
            args['input_tier'] = args['selection']

        selection = args['selection'].split("_")[0]
        if selection == "Inclusive2Jet":
            selection = "Wselection"
            print("INFO: Using Wselection for hist defintions")

        analysis = "/".join([args['analysis'], selection])
        hists, hist_inputs = UserInput.getHistInfo(analysis, args['hist_names'], args['noHistConfig'])
        print("hists:", hists)
        print("hist_inputs:", hist_inputs)

        selector = SelectorTools.SelectorDriver(args['analysis'], args['selection'], args['input_tier'], args['year'])
        selector.setOutputfile(fileName)
        selector.setInputs(sf_inputs+hist_inputs)
        selector.isFake()
        selector.setNumCores(args['numCores'])

        if args['uwvv']:
            selector.setNtupleType("UWVV")
            logging.debug("Processing channels %s" % args['channels'])
            selector.setChannels(args['channels'])
        else:
            selector.setNtupleType("NanoAOD")

        if args['filenames']:
            selector.setDatasets(args['filenames'])
        else:
            selector.setFileList(*args['inputs_from_file'])

        selector.applySelector()
        fOut.Close()

    if args["steps"] in ["ewk", "all"]:
        # EWK Correction
        print("Applying EWK corrections")
        fOut = ROOT.TFile.Open(fileName, "update")

        alldata = HistTools.makeFakeRateCompositeHists(fOut,"AllData", ConfigureJobs.getListOfFilesWithXSec([args['analysis']+"data"]))
        OutputTools.writeOutputListItem(alldata, fOut)
        alldata.Delete()

        allewk = HistTools.makeFakeRateCompositeHists(fOut,"AllEWK", ConfigureJobs.getListOfFilesWithXSec(
            ConfigureJobs.getListOfEWKFilenames("ZplusL%s" % args["year"])), True, lumi=args["lumi"])
        OutputTools.writeOutputListItem(allewk, fOut)
        allewk.Delete()

        allDYJets = HistTools.makeFakeRateCompositeHists(fOut,"DYMC", ConfigureJobs.getListOfFilesWithXSec(
            ConfigureJobs.getListOfDYFilenames("ZplusL%s" % args["year"])),True, lumi=args["lumi"])
        OutputTools.writeOutputListItem(allDYJets, fOut)
        allDYJets.Delete()

        #allnonprompt = HistTools.makeFakeRateCompositeHists("NonpromptMC", ConfigureJobs.getListOfFilesWithXSec(
        #    ConfigureJobs.getListOfNonpromptFilenames()))
        #OutputTools.writeOutputListItem(allnonprompt, fOut)
        #allnonprompt.Delete()

        final = HistTools.getDifference(fOut, "DataEWKCorrected", "AllData", "AllEWK", HistTools.getFakeRateRatios)
        OutputTools.writeOutputListItem(final, fOut)
        final.Delete()

        fOut.Close()

    print("Done:", fileName, "(steps: %s)" % args["steps"])

if __name__ == "__main__":
    main()
