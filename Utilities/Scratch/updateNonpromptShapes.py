# coding: utf-8
import ROOT
rtfile = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Tight_Full-31May2018.root", "UPDATE")
nonprompt_dir = rtfile.Get("DataEWKCorrected")
nonprompt_dir.cd()

# Taken from loose selection
scale_facs = {
    "eee" : 0.157,
    "eem" : 0.213,
    "emm" : 0.333,
    "mmm" : 0.295,
}

# Taken from background control pt 30
#scale_facs = {
#    "eee" : 0.05,
#    "eem" : 0.16,
#    "emm" : 0.23,
#    "mmm" : 0.59,
#}

# Taken from background control pt 50
#scale_facs = {
#    "eee" : 0.12,
#    "eem" : 0.01,
#    "emm" : 0.42,
#    "mmm" : 0.47,
#}
 
# Taken from inclusive + 2j pt > 50
#scale_facs = {
#    "eee" : 0.12,
#    "eem" : 0.01,
#    "emm" : 0.42,
#    "mmm" : 0.47,
#}

# Taken from inclusive + 2j pt > 30
scale_facs = {
    "eee" : 10.36/134.4,
    "eem" : 21.44/134.4,
    "emm" : 44.1/134.4,
    "mmm" : 58.47/134.4,
}

for chan in ["eee", "eem", "emm", "mmm"]:
    hist_chan = nonprompt_dir.Get("mjj_etajj_unrolled_wCR_Fakes_%s;1" % chan)
    hist_cen = nonprompt_dir.Get("mjj_etajj_unrolled_wCR_Fakes")
    hist_chan_new = hist_cen.Clone()
    hist_chan_new.SetName(hist_chan.GetName())
    # To use the by-channel prediction from this selection
    #hist_chan_new.Scale(hist_chan.Integral()/hist_chan_new.Integral())
    # Use the channel breakdown from the CR
    # scale_fac = hist_chan.GetBinContent(1)/hist_cen.GetBinContent(1)
    # print("For channel %s CR yield is %0.2f" % (chan, hist_chan.GetBinContent(1)))
    scale_fac = scale_facs[chan]
    hist_chan_new.Scale(scale_fac)
    print("For chan %s, ratio chan/inclusive = %f" % (chan, scale_fac))
    # Don't rescale background control region
    # hist_chan_new.SetBinContent(1, hist_chan.GetBinContent(1))
    print(hist_chan_new.Write())
    for var in ["CMS_scale_jUp", "CMS_scale_jDown", "CMS_res_jUp", "CMS_res_jDown"]:
        hist_var = nonprompt_dir.Get("mjj_etajj_unrolled_wCR_Fakes_%s;1" % var)
        hist_chan_var = hist_var.Clone()
        hist_chan_var.SetName(hist_var.GetName()+"_"+chan)
        hist_chan_var.Scale(scale_fac)
        print(hist_chan_var.Write())

