from python import CombineCardGenerator

#TODO: use argparse

# Configuration of analysis
year = "2022"
analysis = f"ZZ4l{year}"
fit_variable = "Mass"
fileMap = {
        "2022": "HistFiles/Hists19Jun2025-ZZ4l2022.root",
        "2023": "",
        "2024": "",
        "2025": "",
}
sig_procs = ["qqZZ-powheg"]
bkg_procs = ["ggZZ", "VVV"]
all_procs = sig_procs + bkg_procs
channels = ["eeee", "eemm", "mmee", "mmmm"]
lumiMap = {
        "2022": (34.652, 1.014),
        "2023": (27.76, 1.013),
        "2024": 1,
        "2025": 1,
}

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
    analysis, fit_variable, fileMap[year], sig_procs, bkg_procs,
    channels=channels, lumi=lumiMap[year][0], auto_stats=False
)

systematics_lnN = {
    "bkgStat": {"nonprompt": 1.4},
    "trigger": {proc: "1.020" for proc in all_procs},
    "CMS_lumi": {proc: str(lumiMap[year][1]) for proc in all_procs},
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
for channel in channels:
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
generator.GenerateCards("temp")
