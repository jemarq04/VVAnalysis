import ROOT
import math
import argparse

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--postfit_file", type=str, required=True,
                        help="Postfit file")
    parser.add_argument("-f", "--process", type=str, required=True,
                        help="Name of process")
    parser.add_argument("--backgroundOnly", action='store_true',
                        help="Use background only fit rather than s+b")
    parser.add_argument("-c", "--channels", type=lambda x: [str(i) for i in x.split(",")], 
                        default=["eee","mmm","eem","emm",],
                        help="List (separate by commas) of channels to plot") 
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bins", type=lambda x: [int(i) for i in x.split(",")], default=0,
                        help="Bins in the histogram to include (separate by commas)")
    group.add_argument("--integral", action='store_true',
                        help="Full normalization correction (across all bins)")
    return parser.parse_args()


args = getComLineArgs()

rtfile = ROOT.TFile(args.postfit_file)
prefit_hist = 0
fit_folder = "shapes_fit_s" if not args.backgroundOnly else "shapes_fit_b"

for chan in args.channels:
    prefit_chan_hist = rtfile.Get("/".join(["shapes_prefit", chan, args.process]))
    postfit_chan_hist = rtfile.Get("/".join([fit_folder, chan, args.process]))
    if not prefit_hist:
        prefit_hist = prefit_chan_hist
        postfit_hist = postfit_chan_hist
    else:
        prefit_hist.Add(prefit_chan_hist)
        postfit_hist.Add(postfit_chan_hist)

prefit_sum = 0
postfit_sum = 0
prefit_err = 0
postfit_err = 0
if args.integral:
    prefit_sum = prefit_hist.Integral()
    postfit_sum = postfit_hist.Integral()
else:
    for i in args.bins:
        prefit_sum += prefit_hist.GetBinContent(i)
        postfit_sum += postfit_hist.GetBinContent(i)
        prefit_err += prefit_hist.GetBinError(i)**2
        postfit_err += postfit_hist.GetBinError(i)**2
    prefit_err = math.sqrt(prefit_err)
    postfit_err = math.sqrt(postfit_err)
    
print("Prefit integral across all bins = %0.2f +/- %0.2f (stat)" % (prefit_sum, prefit_err))
print("Postfit integral across all bins = %0.2f +/- %0.2f (syst)" % (postfit_sum, postfit_err))
print("    Ratio = %0.3f +/- %0.3f" % ((postfit_sum/prefit_sum), (postfit_err/prefit_sum)))

