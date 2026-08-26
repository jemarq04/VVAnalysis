import json

outputname = "listFile.json"

dict = {}

dict["nomname"] = "zz4l-amcatnlo"  # "zz4l-powheg"
dict["altname"] = "zz4l-powheg"  # "zz4l-amcatnlo"
dict["sigLabel"] = "MG5_aMC@NLO+MCFM+Pythia8"  # "POWHEG+MCFM+Pythia8"
dict["sigLabelAlt"] = "POWHEG+MCFM+Pythia8"  # "MG5_aMC@NLO+MCFM+Pythia8"
dict["f16"] = "2016Full_MassFull.root"
dict["f17"] = "2017Full.root"
dict["f18"] = "2018Full.root"
dict["fFull"] = "allFull.root"
dict["reg"] = True
dict["EWK"] = [
    dict["nomname"],
    "ggZZ4e",
    "ggZZ4m",
    "ggZZ4t",
    "ggZZ2e2mu",
    "ggZZ2e2tau",
    "ggZZ2mu2tau",
    "ggHZZ",
    "vbfHZZ",
    "WplusHToZZ",
    "WminusHToZZ",
    "ZHToZZ_4L",
    "ttH_HToZZ_4L",
]

dict["altEWK"] = [
    dict["altname"],
    "ggZZ4e",
    "ggZZ4m",
    "ggZZ4t",
    "ggZZ2e2mu",
    "ggZZ2e2tau",
    "ggZZ2mu2tau",
    "ggHZZ",
    "vbfHZZ",
    "WplusHToZZ",
    "WminusHToZZ",
    "ZHToZZ_4L",
    "ttH_HToZZ_4L",
]

with open(outputname, "w") as output_file:
    json.dump(dict, output_file, indent=4)
