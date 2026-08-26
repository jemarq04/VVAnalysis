from DataFormats.FWLite import Handle, Events
import ROOT
ROOT.gStyle.SetPalette(ROOT.kCMYK)
events = Events("root://cmsxrootd.fnal.gov///store/mc/RunIISummer16MiniAODv2/WLLJJ_WToLNu_EWK_aQGC-FM_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/120000/027561E3-42BE-E611-AB10-001E674DA83D.root")

handle = Handle("LHEEventProduct")
hist2D = ROOT.TH2D("hist", "hist", 5, -2, 18, 5, -2, 18)
histRatio = ROOT.TH1D("ratio", "ratio", 40, 0, 4)

first=True
norm=0
for e in events:
    e.getByLabel("externalLHEProducer", handle)
    prod = handle.product()
    weights = {}
    for i,weight in enumerate(prod.weights()):
        if first:
            print("index %i, ID: %s" % (i, weight.id))
            print("Weight: %f" % weight.wgt)
        weights[weight.id] = weight.wgt
    first=False
    norm += 1
    for i in ['0', '4', 'm4', '8', 'm8',]:
        for j in ['0', '4', 'm4', '8', 'm8', ]:
            if i == '0' and i == j:
                continue
            if i == '4' and j == '0':
                continue
            xval = float(i[1:])*-1 if "m" in i else float(i)
            yval = float(j[1:])*-1 if "m" in j else float(j)
            hist2D.Fill(xval, yval, float(weights["fm0_%s__fm1_%s" % (i, j)])/float(weights["1"]))
    histRatio.Fill(weights["fm0_2__fm1_0"]/weights["fm0_0__fm1_2"])
hist2D.GetXaxis().SetTitle("f_{M0}/#Lambda^{4}")
hist2D.GetYaxis().SetTitle("f_{M1}/#Lambda^{4}")
#hist2D.Scale(1/norm)
