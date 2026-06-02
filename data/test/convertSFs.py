#!/usr/bin/env python3

import correctionlib.convert
import correctionlib.schemav2 as cs
import os
import json
import argparse

VARIATIONS = {
    "up": 1,
    "down": -1,
}

FLOW = "clamp"


def writeSFs(info, fname, redo_systs=False, flatten=False):
    DESC = info["desc"]
    HIST_NAME = info["sfname"]
    HUNC_NAME = info["uncname"]
    CORRS = info["corrections"]
    INPUTS = info["inputs"]
    OUTPUT = info["output"]

    corrections = []
    for name in CORRS:
        if not os.path.isfile(CORRS[name]["file"]):
            print(f" File not found: {CORRS[name]['file']}")
            continue
        print(f" Converting {name}...")

        # Create uncertainty histograms if needed
        if redo_systs:
            import ROOT

            with ROOT.TFile.Open(CORRS[name]["file"], "update") as infile:
                hist = infile.Get(HIST_NAME)
                error_scale = CORRS[name]["err_mult"] if "err_mult" in CORRS[name] else 1.0
                if HUNC_NAME not in infile.GetListOfKeys():
                    hunc = hist.Clone(HUNC_NAME)
                    if hist.InheritsFrom("TH3"):
                        for i in range(1, hist.GetNbinsX() + 1):
                            for j in range(1, hist.GetNbinsY() + 1):
                                for k in range(1, hist.GetNbinsZ() + 1):
                                    hunc.SetBinContent(i, j, k, error_scale * hist.GetBinError(i, j, k))
                    elif hist.InheritsFrom("TH2"):
                        for i in range(1, hist.GetNbinsX() + 1):
                            for j in range(1, hist.GetNbinsY() + 1):
                                hunc.SetBinContent(i, j, error_scale * hist.GetBinError(i, j))
                    else:
                        for i in range(1, hist.GetNbinsX() + 1):
                            hunc.SetBinContent(i, error_scale * hist.GetBinError(i))
                else:
                    hunc = infile.Get(HUNC_NAME)

                for syst, shift in VARIATIONS.items():
                    hsyst = hist.Clone(f"{HIST_NAME}_{syst}")
                    hsyst.Add(hunc, shift)
                    hsyst.Write()
                    print(f"  Writing {CORRS[name]['file']}:{HIST_NAME}_{syst}...")

        # Load correction objects
        corr_items = {
            "nominal": correctionlib.convert.from_uproot_THx(
                f"{CORRS[name]['file']}:{HIST_NAME}", list(INPUTS.keys()), FLOW
            ),
        }
        for syst in VARIATIONS:
            corr_items[syst] = correctionlib.convert.from_uproot_THx(
                f"{CORRS[name]['file']}:{HIST_NAME}_{syst}", list(INPUTS.keys()), FLOW
            )

        if flatten:
            # Append correction objects
            for syst, item in corr_items.items():
                item.name = f"{name}_{syst}" if syst != "nominal" else name
                item.description = CORRS[name]["desc"]
                for i, val in enumerate(INPUTS.values()):
                    item.inputs[i].description = val
                item.output.name = OUTPUT["name"]
                item.output.description = OUTPUT["desc"]
                corrections.append(item)
        else:
            # Create combined correction object
            systematics = [cs.CategoryItem(key=syst, value=corr_items[syst].data) for syst in corr_items]
            corr_inputs = [cs.Variable(name=key, type="real", description=val) for key, val in INPUTS.items()]
            corrections.append(
                cs.Correction(
                    name=name,
                    version=1,
                    description=CORRS[name]["desc"],
                    inputs=corr_inputs
                    + [
                        cs.Variable(name="systematic", type="string", description="nominal/up/down"),
                    ],
                    output=cs.Variable(name=OUTPUT["name"], type="real", description=OUTPUT["desc"]),
                    data=cs.Category(
                        nodetype="category",
                        input="systematic",
                        content=systematics,
                    ),
                )
            )

    cset = cs.CorrectionSet(schema_version=2, corrections=corrections, description=DESC)

    with open(fname, "w") as outfile:
        json.dump(json.loads(cset.json(exclude_unset=True)), outfile, indent=2)


def main():
    data_file = "data.json"
    if not os.path.isfile(data_file):
        print(f"invalid input JSON file: {data_file}")
        exit(1)
    with open(data_file) as infile:
        info = json.load(infile)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--redo-systs", action="store_true", help="re-calculate up/down systematic histograms")
    parser.add_argument("-o", "--outfile", default="", help="output JSON file or directory (default: {name}.json)")
    parser.add_argument(
        "--flatten", action="store_true", help="store systematic up/down variations as separate corrections"
    )
    parser.add_argument("key", choices=info.keys(), help="convert SFs for the provided key")
    args = parser.parse_args()

    if args.outfile == "" or os.path.isdir(args.outfile):
        args.outfile = os.path.join(args.outfile, f"{info[args.key]['name']}.json")

    print(f"Writing correction JSON to {args.outfile}...")
    writeSFs(info[args.key], args.outfile, args.redo_systs, args.flatten)

    print("Done.")


if __name__ == "__main__":
    main()
