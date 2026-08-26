#!/usr/bin/env python
import ROOT
import datetime
import os
import makeSimpleHtml
import array

ROOT.gROOT.SetBatch(True)
canvas = ROOT.TCanvas("canvas", "canvas")

def getTGraphAsymmErrors(frfile, folder, param, obj):
    tight_hist = frfile.Get("%s/passingTight%s_all%s" % (folder, param, obj))
    loose_hist = frfile.Get("%s/passingLoose%s_all%s" % (folder, param, obj))
    graph = ROOT.TGraphAsymmErrors(tight_hist, loose_hist)
    graph.SetMarkerStyle(6)
    graph.SetMinimum(0)
    graph.SetMaximum(0.8)
    return graph

def getTextBox(obj, extra_text=""):
    text_box = ROOT.TPaveText(0.2, 0.92, 0.4+0.02*len(extra_text), 0.86, "blNDC")
    text_box.SetFillColor(0)
    text_box.SetLineColor(ROOT.kBlack)
    text_box.SetTextFont(42)
    text_box.AddText(" %s Fake Rate %s" % ("#mu" if "Mu" in obj else "e", extra_text))
    text_box.SetBorderSize(1)
    ROOT.SetOwnership(text_box, False)
    return text_box

def invert2DHist(hist):
    new_hist = ROOT.TH2D(hist.GetName(), hist.GetTitle(),
            3, 0, 2.5,
            3, array.array('d', [10,20,30,50]))
    ROOT.SetOwnership(new_hist, False)
    for x in range(hist.GetNbinsX()+1):
        for y in range(hist.GetNbinsY()+1):
            value = hist.GetBinContent(x, y)
            new_hist.SetBinContent(y, x, value)
    new_hist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle())
    new_hist.GetYaxis().SetTitle(hist.GetYaxis().GetTitle())
    return new_hist

def makeDataPlots(param, obj, outdir):
    data_ewkcorr_graph = frfile.Get("DataEWKCorrected/ratio%s_all%s" % (param, obj)) \
        if "2D" in param else getTGraphAsymmErrors(frfile, "DataEWKCorrected", param, obj)
    data_ewkcorr_graph.SetLineColor(ROOT.kRed)
    draw_opt = "PA" if "2D" not in param else "colz text"
    if "2D" in param:
        data_ewkcorr_graph = invert2DHist(data_ewkcorr_graph)
        #data_ewkcorr_graph.GetYaxis().SetTitle("#eta")
        data_ewkcorr_graph.GetYaxis().SetTitle("p_{T} [GeV]")
        data_ewkcorr_graph.GetXaxis().SetTitle("#eta")
    else:
        data_ewkcorr_graph.GetYaxis().SetTitle("Passing Tight / Passing Loose")
        xlabel = "p_{T} [GeV]" if "Pt" in param else "#eta"
        data_ewkcorr_graph.GetXaxis().SetTitle(xlabel)
    data_ewkcorr_graph.Draw(draw_opt)

    text_box = getTextBox(obj)
    text_box.Draw()

    if not "2D" in param:
        data_uncorr_graph = getTGraphAsymmErrors(frfile, "AllData", param, obj)
        data_uncorr_graph.Draw("P")

        legend = ROOT.TLegend(0.2,.85,.55,.70)
        legend.AddEntry(data_uncorr_graph, "Data", "l")
        legend.AddEntry(data_ewkcorr_graph, "Data - EWK", "l")
        legend.Draw()

    canvas.Print("%s/ratio%s_all%s.png" % (outdir, param, obj))
    canvas.Print("%s/ratio%s_all%s.pdf" % (outdir, param, obj))

def makeMCPlots(param, obj, outdir):
    graph = frfile.Get("NonpromptMC/ratio%s_all%s" % (param, obj)) \
        if "2D" in param else getTGraphAsymmErrors(frfile, "NonpromptMC", param, obj)
    graph.SetLineColor(ROOT.kRed)
    draw_opt = "PA" if "2D" not in param else "colz text"
    if "2D" in param:
        graph.GetYaxis().SetTitle("#eta")
    else:
        graph.GetYaxis().SetTitle("Passing Tight / Passing Loose")
        xlabel = "p_{T} [GeV]" if "Pt" in param else "#eta"
        graph.GetXaxis().SetTitle(xlabel)
    graph.Draw(draw_opt)

    text_box = getTextBox(obj, "(MC)")
    text_box.Draw()

    if not "2D" in param:
        legend = ROOT.TLegend(0.2,.85,.55,.70)
        legend.AddEntry(graph, "Nonprompt MC", "l")
        legend.Draw()


    canvas.Print("%s/ratio%s_all%s.png" % (outdir, param, obj))
    canvas.Print("%s/ratio%s_all%s.pdf" % (outdir, param, obj))

frfile = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/FakeRates/fakeRateMar2018-TightLepsFrom3MediumLeptons.root")


data_folder_name = datetime.date.today().strftime("%Y%b"+"_ScaleFacs")
data_outdir = "~/www/DibosonAnalysisData/PlottingResults/WZxsec2016/FakeRates/" + data_folder_name + "/plots"
mc_outdir = "~/www/DibosonAnalysisData/PlottingResults/WZxsec2016/FakeRates/" + data_folder_name + "-MC/plots"

for outdir in [data_outdir, mc_outdir]:
    try:
        os.makedirs(os.path.expanduser(outdir))
    except OSError as e:
        print(e)
        pass

for param in ["1DPt", "1DEta", "2D"]:
    for obj in ["Mu", "E"]:
        makeDataPlots(param, obj, data_outdir)
        makeMCPlots(param, obj, mc_outdir)
makeSimpleHtml.writeHTML(os.path.expanduser(data_outdir.replace("/plots", "")), "Fake Rates (from data)")
makeSimpleHtml.writeHTML(os.path.expanduser(mc_outdir.replace("/plots", "")), "Fake Rates (from MC)")
