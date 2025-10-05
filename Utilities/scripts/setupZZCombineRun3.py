#!/usr/bin/env python3
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", help="name of input histogram file")
    parser.add_argument("-o", "--outdir", default="combine",
        help="name of output directory for the datacard(s)")
    parser.add_argument("-f", "--fit-var", default="Mass", 
        help="fit variable (default: Mass)")
    parser.add_argument("-l", "--lumi", help="luminosity")
    parser.add_argument("-c", "--channels",
        type=lambda x : [i.strip() for i in x.split(',')],
        default=["eeee", "eemm", "mmee", "mmmm"],
        help="comma-separated list of channels")
    parser.add_argument("--autoMCStats", action="store_true",
        help="use Combine's autoMCStats feature")
    parser.add_argument("year", choices=[2022,2023], type=int,
        help="year for analysis (e.g. 2022 for ZZ4l2022")
    args = parser.parse_args()

    from python import CombineCardGenerator

    # Configuration of analysis
    analysis = f"ZZ4l{args.year}"
    fileMap = {
        2022: "HistFiles/Hists-ZZ4l2022.root",
        2023: "HistFiles/Hists-ZZ4l2023.root",
        2024: "HistFiles/Hists-ZZ4l2024.root",
    }
    lumiMap = {
        2022: 34.652,
        2023: 27.76,
        2024: 109.33,
    }
    lumiUncMap = {
        2022: 1.014,
        2023: 1.013,
        2024: 0.0, #TODO, unavailable at the moment
    }
    sig_procs = ["qqZZ-powheg"]
    bkg_procs = ["ggZZ", "VVV", "nonprompt"]
    all_procs = sig_procs + bkg_procs[:-1]

    if args.infile is None:
        args.infile = fileMap[args.year]
    if args.lumi is None:
        args.lumi = lumiMap[args.year]

    # Error checking
    if not os.path.isfile(args.infile):
        parser.error(f'file {args.infile} does not exist')
    elif not args.infile.endswith(".root"):
        parser.error(f'file {args.infile} is not a valid ROOT file')

    if not os.path.isdir(args.outdir):
        try:
            os.mkdir(args.outdir)
        except:
            parser.error(f'error creating directory {args.outdir}')

    # Create the generator by supplying 
    #  - the analysis (e.g. ZZ4l2022)
    #  - the fit variable (right now it only accepts one)
    #  - the file to read from
    #  - the signal processes (e.g. qqZZ-powheg)
    #  - the background processes (e.g. ggZZ, VVV)
    #  - the list of desired channels
    #  - the luminosity for the given analysis
    #  - whether or not to use combine's 'auto stats'
    generator = CombineCardGenerator.CombineCardGenerator(
        analysis, args.fit_var, args.infile, sig_procs, bkg_procs,
        channels=args.channels, lumi=args.lumi, auto_stats=args.autoMCStats
    )

    systematics_lnN = {
        "bkgStat": {"nonprompt": "1.4"},
        "trigger": {proc: "1.020" for proc in all_procs},
        "CMS_lumi": {proc: str(lumiUncMap[args.year]) for proc in all_procs},
    }
    systematics_shape = {
        "CMS_pileup": {proc: "1" for proc in all_procs},
    }

    # Add systematics by supplying 
    #  - the name of the systematic (e.g. CMS_eff_e)
    #  - a dictionary of values for each signal and background process
    #  - whether or not it is a 'shape' uncertainty
    # By default, AddSystematics() will apply to ALL channels. To specify a channel,
    # use the 'channel' keyword for the function call.
    for syst,values in systematics_lnN.items():
        generator.AddSystematics(
            syst,
            values,
            shape=False
        )
    for syst,values in systematics_shape.items():
        generator.AddSystematics(
            syst,
            values,
            shape=True
        )
    for channel in args.channels:
        if "e" in channel:
            for syst in ["CMS_eff_e", "CMS_RecoEff_e"]:
                generator.AddSystematics(
                    syst,
                    {proc: "1" for proc in all_procs},
                    channel=channel,
                    shape=True
                )
        if "m" in channel:
            generator.AddSystematics(
                "CMS_eff_m",
                {proc: "1" for proc in all_procs},
                channel=channel,
                shape=True
            )

    # Finally, you can create the cards by specifying the 
    # output directory for them.
    generator.GenerateCards(args.outdir)

if __name__ == "__main__":
    main()

