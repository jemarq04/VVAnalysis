#!/usr/bin/env python3

import os
import ROOT
import argparse
from python import OutputTools
from python import ConfigureJobs
from python import HistTools
import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", help="overwrite output file if it exists")
    parser.add_argument("-o", "--outfile", help="output file (default: Hists<DATE>-<ANALYSIS>.root or fakeRates-<ANALYSIS>.root)")
    parser.add_argument("-a", "--analysis", default="ZZ4lRun3Combined", help="name of combined analysis in dataset manager")
    parser.add_argument("-y", "--years", default=[],
        type=lambda x: [i.strip() for i in x.split(",")], 
        help="comma-separated list of years")
    parser.add_argument("infiles", nargs="+", help="list of infiles to combine")
    args = parser.parse_args()

    #initial error checking
    if not any(args.analysis.startswith(x) for x in ["ZZ4l", "ZplusL"]):
        parser.error(f"invalid analysis, must be type ZZ4l or ZplusL: {args.analysis}")

    #set variables
    manager_path = ConfigureJobs.getManagerPath()
    manager_name = ConfigureJobs.getManagerName()
    if args.analysis.startswith("ZZ4l"):
        zz_analysis = args.analysis
    else:
        zz_analysis = "ZZ4l" + args.analysis.split("ZplusL")[1]
    if args.outfile is None:
        today = datetime.date.today().strftime("%d%b%Y")
        if args.analysis.startswith("ZZ4l"):
            args.outfile = f"Hists{today}-{zz_analysis}.root"
        else:
            args.outfile = f"fakeRates-{zz_analysis}.root"

    #error checking
    if not args.force and os.path.isfile(args.outfile):
        parser.error(f"file already exists: {args.outfile}")
    if args.years:
        if len(args.years) != len(args.infiles):
            parser.error("number of years provided must match number of input files")
    else:
        for f in args.infiles:
            if not os.path.isfile(f):
                parser.error(f"invalid file: {f}")
            analysis = f.split("-")[1].split(".root")[0]
            path = os.path.join(manager_path, manager_name, "FileInfo", analysis)
            args.years.append(analysis[-4:])
            if not os.path.isdir(path) or not args.years[-1].isdigit():
                parser.error(f"could not parse year from filename: {f}, consider using -y/--years")

    lumis = [float("%.2f" % ConfigureJobs.getLuminosity(year, "", manager_path)) for year in args.years]
    lumi = sum(lumis)
    print(f"Luminosity: {lumi:.2f}")

    skip_dirs = ["AllData", "AllEWK", "DataEWKCorrected", "DYMC"]
    with ROOT.TFile.Open(args.outfile, "recreate") as outfile:
        print(f"Writing output file {args.outfile}...")
        for i in range(len(args.infiles)):
            file_path = args.infiles[i]
            year = args.years[i]
            eras = ConfigureJobs.getLuminosityEras(year, manager_path)

            with ROOT.TFile.Open(file_path) as infile:
                print(f" Copying from {file_path}...")
                for key in infile.GetListOfKeys():
                    sample = infile.Get(key.GetName())
                    if not sample.InheritsFrom("TDirectory") or key.GetName() in skip_dirs:
                        continue
                    
                    new_key = key.GetName()
                    if not new_key.startswith("data"):
                        if not eras:
                            new_key += f"_{year}"
                        else:
                            for suffix in eras:
                                if new_key.endswith(suffix):
                                    new_key = new_key.replace(suffix, f"{year}_{suffix}")
                                    break

                    new_sample = outfile.mkdir(new_key)
                    for hkey in sample.GetListOfKeys():
                        new_sample.WriteObject(sample.Get(hkey.GetName()))

    with ROOT.TFile.Open(args.outfile, "update") as outfile:
        is_ZZ = args.analysis.startswith("ZZ4l")
        key_ZZ = args.analysis if is_ZZ else "ZZ4l" + args.analysis.split("ZplusL")[1]

        if is_ZZ:
            alldata = HistTools.makeCompositeHists(outfile,"AllData", 
                ConfigureJobs.getListOfFilesWithXSec([f"{key_ZZ}data"], manager_path), lumi,
                underflow=False, overflow=False)
        else:
            alldata = HistTools.makeFakeRateCompositeHists(outfile,"AllData",
                ConfigureJobs.getListOfFilesWithXSec([f"{key_ZZ}data"]))
        OutputTools.writeOutputListItem(alldata, outfile)
        alldata.Delete()

        print(" Saving AllEWK...")
        if is_ZZ:
            ewkmc = HistTools.makeCompositeHists(outfile,"AllEWK", ConfigureJobs.getListOfFilesWithXSec(
                ConfigureJobs.getListOfEWKFilenames(args.analysis), manager_path), lumi,
                underflow=False, overflow=False)
        else:
            ewkmc = HistTools.makeFakeRateCompositeHists(outfile,"AllEWK", ConfigureJobs.getListOfFilesWithXSec(
                ConfigureJobs.getListOfEWKFilenames(args.analysis)), True, lumi=lumi)
        OutputTools.writeOutputListItem(ewkmc, outfile)
        ewkmc.Delete()

        if not is_ZZ:
            allDYJets = HistTools.makeFakeRateCompositeHists(outfile,"DYMC", ConfigureJobs.getListOfFilesWithXSec(
                ConfigureJobs.getListOfDYFilenames(args.analysis)),True, lumi=lumi)
            OutputTools.writeOutputListItem(allDYJets, outfile)
            allDYJets.Delete()

        print(" Saving DataEWKCorrected...")
        ewkcorr = HistTools.getDifference(outfile, "DataEWKCorrected", "AllData", "AllEWK", None if is_ZZ else HistTools.getFakeRateRatios)
        OutputTools.writeOutputListItem(ewkcorr, outfile)
        ewkcorr.Delete()
    print("Done.")

if __name__ == "__main__":
    main()
