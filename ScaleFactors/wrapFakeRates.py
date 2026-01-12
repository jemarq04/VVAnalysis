#!/usr/bin/env python3
import os
import argparse
import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", default="scaleFactors.root", help="output file name")
    parser.add_argument("infile", help="input fakeRates.root file")
    args = parser.parse_args()

    if not os.path.isfile(args.infile):
        parser.error("invalid input file: %s" % args.infile)

    print("INFO: Adding tight fake rates to %s" % args.outfile)

    fScales = ROOT.TFile(args.outfile, "recreate")
    fakeRateFile = ROOT.TFile.Open(args.infile)

    eZZTightFakeRate = ROOT.ScaleFactor("eZZTightFakeRate", "Fake rate from Z+jet")
    mZZTightFakeRate = ROOT.ScaleFactor("mZZTightFakeRate", "Fake rate from Z+jet")
    eZZTightFakeRate.Set2DHist(fakeRateFile.Get("DataEWKCorrected/ratioE2D_allE"), 0, 0, ROOT.ScaleFactor.AsInHist)
    mZZTightFakeRate.Set2DHist(fakeRateFile.Get("DataEWKCorrected/ratioMu2D_allMu"), 0, 0, ROOT.ScaleFactor.AsInHist)

    fScales.cd()
    mZZTightFakeRate.Write()
    eZZTightFakeRate.Write()

    fakeRateFile.Close()
    fScales.Close()


if __name__ == "__main__":
    main()
