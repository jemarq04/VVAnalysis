import json

outputname = "listFile.json"

dict = {}

dict["nomname"] = "qqZZSpec"  # "zz4l-powheg"
dict["altname"] = "zz4l-amcatnlo"
dict["sigLabel"] = "New MG5+MCFM+Pythia8"  # "POWHEG+MCFM+Pythia8"
dict["sigLabelAlt"] = "Old MG5+MCFM+Pythia8"
dict["f18"] = "UnfHistsFinal-2018NewqqZZMC-14Jul2021-ZZ4l2018.root"
dict["reg"] = True
dict["EWK"] = [
    dict["nomname"],
    "ggZZ4e",
    "ggZZ4m",
    "ggZZ4t",
    "ggZZ2e2mu",
    "ggZZ2e2tau",
    # "ggZZ2mu2tau",
]

dict["altEWK"] = [
    dict["altname"],
    "ggZZ4e",
    "ggZZ4m",
    "ggZZ4t",
    "ggZZ2e2mu",
    "ggZZ2e2tau",
    # "ggZZ2mu2tau",
]

with open(outputname, "w") as output_file:
    json.dump(dict, output_file, indent=4)
