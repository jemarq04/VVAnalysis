# coding: utf-8
import ROOT
ROOT.gStyle.SetPalette(ROOT.kCMYK)
rtfile = ROOT.TFile("/eos/user/k/kelong/DibosonAnalysisData/PlottingResults/WZxsec2016/VBSselection/aQGCComparison/aQGC-FM/plots/MTWZ.root")
canvas = rtfile.Get("MTWZ_canvas")
pad = canvas.GetListOfPrimitives().FindObject("stackPad")
stack = pad.GetListOfPrimitives().FindObject("stack_MTWZ")

hist2D = ROOT.TH2D("hist", "hist", 5, -2, 18, 5, -2, 18)

for i in ['0', '4', 'm4', '8', 'm8', '16', 'm16']:
    for j in ['0', '4', 'm4', '8', 'm8', '16', 'm16']:
        if i == '0' and i == j:
            continue
        xval = float(i[1:])*-1 if "m" in i else float(i)
        yval = float(j[1:])*-1 if "m" in j else float(j)
        hist = stack.GetHists().FindObject("wzjj-aqgcfm__fm0-%s_fm1-%s_WZxsec2016_VBSselection_MTWZ" % (i, j))
        print("wzjj-aqgcfm__fm0-%s_fm1-%s_WZxsec2016_VBSselection_MTWZ" % (i, j))
        hist2D.Fill(xval, yval, hist.Integral())

c = ROOT.TCanvas("canvas", "canvas")
hist2D.Draw("colz text")
hist2D.GetZaxis().SetRangeUser(15,30)
hist2D.GetXaxis().SetTitle("f_{M0}/#Lambda^{4}")
hist2D.GetYaxis().SetTitle("f_{M1}/#Lambda^{4}")

hist2D.Draw("colz text")
c.Print("temp.pdf")
