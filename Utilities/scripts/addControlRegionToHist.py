from python import HistTools, OutputTools, ConfigureJobs
import ROOT
import array
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input_file", "-i", type=str,
    default="test.root", help="Output file name")
parser.add_argument("--hist_name", "-n", type=str,
    default="MTWZ", help="Name of histogram to add CR to")
parser.add_argument("--rebin", type=lambda x: [float(i) for i in x.split(",")], 
                    default=ConfigureJobs.getBinning(isHiggs=True),
                    help="Rebin values, comma separated list")
args = parser.parse_args()

saveToFile = True
input_file_name = args.input_file
input_file = ROOT.TFile(input_file_name, "update" if saveToFile else "read")

variations = [i for x in ["CMS_scale_j", "CMS_res_j", \
    "CMS_eff_m", "CMS_scale_m", "CMS_eff_e", "CMS_scale_e", "CMS_pileup", "CMS_scale_unclEnergy"] for i in [x+"Up", x+"Down"]]
jeVariations = [i for x in ["CMS_scale_j", "CMS_res_j"] for i in [x+"Up", x+"Down"]]

chans = ConfigureJobs.getChannels()
rebin = array.array('d', args.rebin)
output = []
for key in input_file.GetListOfKeys():
    folder = input_file.Get(key.GetName())
    new_folder = ROOT.TList()
    new_folder.SetName(key.GetName())
    ROOT.SetOwnership(new_folder, False)

    name = args.hist_name if "DataEWKCorrected" not in folder.GetName() else "_".join([args.hist_name, "Fakes"])
    hist_names = ["_".join([name, chan]) for chan in chans]
    if "data" not in folder.GetName().lower():
        hist_names += ["_".join([name, var, chan]) for var in variations for chan in chans]
    elif "DataEWKCorrected" in folder.GetName():
        hist_names += ["_".join([args.hist_name, var, "Fakes", chan]) for var in jeVariations for chan in chans]
    try:
        for hist_name in hist_names:
            h = folder.Get(hist_name+";1")
            if not h:
                raise RuntimeError("failed to find hist %s for folder %s" % (hist_name, folder))
            h.Clone("tmp")
            if rebin:
                h = h.Rebin(len(rebin)-1, hist_name, rebin)
            append = h.GetName().split("_")
            hist_name_end = name.split("_")[-1]
            append = append[append.index(hist_name_end)+1:]
            crhist_name = "_".join(["backgroundControlYield"] + append)
            control_hist = input_file.Get(folder.GetName() + "/" +crhist_name)
            if not control_hist:
                raise RuntimeError("failed to find hist %s for folder %s" % (crhist_name, folder))
            h.SetName(hist_name)
            hist = HistTools.addControlRegionToFitHist(control_hist, h, args.hist_name)
            new_folder.Add(hist)
    except RuntimeError as e:
        print(e)
        continue
    output.append(new_folder)

if saveToFile:
    for folder in output:
        OutputTools.writeOutputListItem(folder, input_file)

