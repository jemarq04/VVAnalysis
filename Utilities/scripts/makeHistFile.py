#!/usr/bin/env python3
import ROOT
from python import SelectorTools
from python import UserInput
from python import OutputTools
from python import ConfigureJobs
from python import HistTools
import os
import logging
import sys
import datetime
import subprocess

# logging.basicConfig(level=logging.DEBUG)


def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float, default=None, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str, default="test.root", help="Output file name")
    parser.add_argument("--test", action="store_true", help="Run test job (no background estimate)")
    parser.add_argument("--uwvv", action="store_true", help="Use UWVV format ntuples in stead of NanoAOD")
    parser.add_argument("--with_background", action="store_true", help="Don't run background selector")
    parser.add_argument("--with_Gen", action="store_true", help="Don't run ZZGen selector")
    parser.add_argument("--noHistConfig", action="store_true", help="Don't rely on config file to specify hist info")
    parser.add_argument("-j", "--numCores", type=int, default=1, help="Number of cores to use (parallelize by dataset)")
    parser.add_argument("--input_tier", type=str, default="", help="Selection stage of input files")
    parser.add_argument("--year", type=str, default="default", help="Year of Analysis")
    parser.add_argument("-sf", "--apply_scalefactors", action="store_true", help="apply scale factors")
    parser.add_argument("--fakerates_file", "-F", type=str, default="", help="fake rates file name")
    parser.add_argument(
        "-c",
        "--channels",
        type=lambda x: [i.strip() for i in x.split(",")],
        default=["eee", "eem", "emm", "mmm"],
        help="List of channelsseparated by commas. NOTE: set to Inclusive for NanoAOD",
    )
    parser.add_argument(
        "-b",
        "--hist_names",
        type=lambda x: [i.strip() for i in x.split(",")],
        default=["all"],
        help="List of histograms, as defined in %s, separated by commas" % ConfigureJobs.getManagerName(),
    )
    return vars(parser.parse_args())


def makeHistFile(args):
    ROOT.gROOT.SetBatch(True)

    manager_path = ConfigureJobs.getManagerPath()
    if manager_path not in sys.path:
        sys.path.insert(0, "/".join([manager_path, ConfigureJobs.getManagerName(), "Utilities/python"]))

    if args["lumi"] is None:
        args["lumi"] = ConfigureJobs.getLuminosity(args["year"], "", manager_path)

    today = datetime.date.today().strftime("%d%b%Y")

    tmpFileName = "Hists%s-%s.root" % (
        today,
        args["output_file"] if args["selection"] == "SignalSync" or args["test"] else args["analysis"],
    )
    toCombine = args["with_background"] or args["with_Gen"]
    fOut = ROOT.TFile(tmpFileName if not toCombine else tmpFileName.replace(".root", "sel.root"), "recreate")
    combinedNames = [fOut.GetName()]

    if args["fakerates_file"] and not os.path.isfile(args["fakerates_file"]):
        print("WARNING: file:%s not found -> no fake rates added" % args["fakerates_file"])
        args["fakerates_file"] = ""

    fr_inputs = []
    if args["fakerates_file"] or args["apply_scalefactors"]:
        if "ZZ4l" in args["analysis"]:
            if args["fakerates_file"]:
                fScales = ROOT.TFile(args["fakerates_file"])
                mZZTightFakeRate = fScales.Get("mZZTightFakeRate")
                eZZTightFakeRate = fScales.Get("eZZTightFakeRate")
                if mZZTightFakeRate:
                    mZZTightFakeRate.SetName("fakeRate_allMu")
                if eZZTightFakeRate:
                    eZZTightFakeRate.SetName("fakeRate_allE")
                fr_inputs = [eZZTightFakeRate, mZZTightFakeRate]

            sf_inputs = [
                ROOT.TNamed("basename", "%s/src/Analysis/VVAnalysis/data/XPOG" % os.environ["CMSSW_BASE"]),
                # ROOT.TNamed("qqZZ_kfac", "data/qqZZ_kfacs.json"),
                ROOT.TNamed("eIdSF", "data/ElectronSF_HZZ.json"),
                ROOT.TNamed("mIdSF", "data/MuonSF_HZZ.json"),
            ]
        else:
            # This block below has not been updated since Run 2
            fScales = ROOT.TFile("data/scaleFactors.root")
            mCBTightFakeRate = fScales.Get("mCBTightFakeRate")
            eCBTightFakeRate = fScales.Get("eCBTightFakeRate")
            useSvenjasFRs = False
            useJakobsFRs = False
            if useSvenjasFRs:
                mCBTightFakeRate = fScales.Get("mCBTightFakeRate_Svenja")
                eCBTightFakeRate = fScales.Get("eCBTightFakeRate_Svenja")
            elif useJakobsFRs:
                mCBTightFakeRate = fScales.Get("mCBTightFakeRate_Jakob")
                eCBTightFakeRate = fScales.Get("eCBTightFakeRate_Jakob")
            # For medium muons
            # mCBMedFakeRate.SetName("fakeRate_allMu")
            if mCBTightFakeRate:
                mCBTightFakeRate.SetName("fakeRate_allMu")
            if eCBTightFakeRate:
                eCBTightFakeRate.SetName("fakeRate_allE")

            muonIsoSF = fScales.Get("muonIsoSF")
            muonIdSF = fScales.Get("muonTightIdSF")
            electronTightIdSF = fScales.Get("electronTightIdSF")
            electronGsfSF = fScales.Get("electronGsfSF")
            pileupSF = fScales.Get("pileupSF")

            # fPrefireEfficiency = ROOT.TFile('data/Map_Jet_L1FinOReff_bxm1_looseJet_JetHT_Run2016B-H.root')
            fPrefireEfficiency = ROOT.TFile("data/Map_Jet_L1FinOReff_bxm1_looseJet_SingleMuon_Run2016B-H.root")
            prefireEff = fPrefireEfficiency.Get("prefireEfficiencyMap")

            fr_inputs = [
                eCBTightFakeRate,
                mCBTightFakeRate,
            ]
            sf_inputs = [electronTightIdSF, electronGsfSF, muonIsoSF, muonIdSF, pileupSF, prefireEff]

        sf_inputs.append(ROOT.TParameter(bool)("applyScaleFacs", args["apply_scalefactors"]))

    if args["input_tier"] == "":
        args["input_tier"] = args["selection"]
    selection = args["selection"].split("_")[0]

    if selection == "Inclusive2Jet":
        selection = "Wselection"
        print("Info: Using Wselection for hist defintions")
    analysis = "/".join([args["analysis"], selection])
    hists, hist_inputs = UserInput.getHistInfo(analysis, args["hist_names"], args["noHistConfig"])

    selector = SelectorTools.SelectorDriver(args["analysis"], args["selection"], args["input_tier"], args["year"])
    selector.setOutputfile(fOut.GetName())
    selector.setInputs(sf_inputs + hist_inputs)

    selector.setNtupleType("UWVV" if args["uwvv"] else "NanoAOD")
    if args["uwvv"]:
        logging.debug("Processing channels " % args["channels"])
        selector.setChannels(args["channels"])
    selector.setNumCores(args["numCores"])

    if args["filenames"]:
        selector.setDatasets(args["filenames"])
    else:
        selector.setFileList(*args["inputs_from_file"])
    selector.applySelector()

    print("Pause here")
    # sys.exit()

    if args["with_background"]:
        selector.isBackground()
        selector.setInputs(sf_inputs + hist_inputs + fr_inputs)
        output_name = tmpFileName.replace(".root", "bkgd.root")
        selector.setOutputfile(output_name)
        selector.applySelector()
        combinedNames.append(output_name)
    # pdb.set_trace()
    if args["with_Gen"]:
        selector.isGen()
        selector.setChannels([c + "Gen" for c in args["channels"]])
        # Make sure to remove data from the dataset lists
        selector.setInputs(hist_inputs)
        output_name = tmpFileName.replace(".root", "gen.root")
        selector.setOutputfile(output_name)
        combinedNames.append(output_name)
        if args["filenames"]:
            # selector.setDatasets(args['filenames'])
            selector.setDatasets(ConfigureJobs.getListOfGenFilenames(args["analysis"]))
        else:
            selector.setFileList(*args["inputs_from_file"])
        selector.applySelector()
        selector.setChannels(args["channels"])
        selector.outputFile().Close()

    if len(combinedNames) > 1:
        rval = subprocess.call(["hadd", "-f", tmpFileName] + combinedNames)
        if rval == 0:
            list(map(os.remove, combinedNames))

    fOut.Close()
    if args["test"]:
        sys.exit(0)

    fOut = ROOT.TFile.Open(tmpFileName, "update")
    alldata = HistTools.makeCompositeHists(
        fOut,
        "AllData",
        ConfigureJobs.getListOfFilesWithXSec([args["analysis"] + "data"], manager_path),
        args["lumi"],
        underflow=False,
        overflow=False,
    )
    OutputTools.writeOutputListItem(alldata, fOut)
    alldata.Delete()

    if "ZZ4l" not in args["analysis"]:
        nonpromptmc = HistTools.makeCompositeHists(
            fOut,
            "NonpromptMC",
            ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfNonpromptFilenames(), manager_path),
            args["lumi"],
            underflow=False,
            overflow=False,
        )
        nonpromptmc.Delete()

        OutputTools.writeOutputListItem(nonpromptmc, fOut)

    ewkmc = HistTools.makeCompositeHists(
        fOut,
        "AllEWK",
        ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfEWKFilenames(args["analysis"]), manager_path),
        args["lumi"],
        underflow=False,
        overflow=False,
    )
    OutputTools.writeOutputListItem(ewkmc, fOut)
    ewkmc.Delete()

    ewkcorr = HistTools.getDifference(fOut, "DataEWKCorrected", "AllData", "AllEWK")
    OutputTools.writeOutputListItem(ewkcorr, fOut)
    ewkcorr.Delete()


def main():
    makeHistFile(getComLineArgs())
    exit(0)


if __name__ == "__main__":
    main()
