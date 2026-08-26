import ROOT
#rtfile = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Tight_Full-01Jun2018.root", "UPDATE")
rtfile = ROOT.TFile("/eos/user/k/kelong/WZAnalysisData/CombineData/VBSselection_Tight_Full-31May2018.root", "UPDATE")

variable = "mjj_etajj_unrolled_wCR"
variations = ["CMS_scale_jUp", "CMS_scale_jDown", "CMS_res_jUp", "CMS_res_jDown"]
for proc in rtfile.GetListOfKeys():
    if proc.GetName() in ["zg", "AllData", "DataEWKCorrected"]:
        continue
    proc_dir = rtfile.Get(proc.GetName())
    proc_dir.cd()
    print(proc_dir)
    curvars = variations + ["QCDscale_%sUp" % proc_dir.GetName(),
        "QCDscale_%sDown" % proc_dir.GetName(),
        "pdf_%sUp" % proc_dir.GetName(),
        "pdf_%sDown" % proc_dir.GetName(),
    ]
    for var in curvars:
        print(var)
        hist_cen = proc_dir.Get(variable)
        hist_var = proc_dir.Get("_".join([variable,var]))
        corr_by_bin = []
        for i in range(1, hist_cen.GetNbinsX()+1):
            corr_by_bin.append(hist_var.GetBinContent(i)/hist_cen.GetBinContent(i))
        for chan in ["eee", "eem", "emm", "mmm"]:
            chan_hist = proc_dir.Get("_".join([hist_cen.GetName(), chan]))
            new_hist = hist_var.Clone("_".join([hist_var.GetName(), chan]))
            for i,entry in enumerate(corr_by_bin):
                new_hist.SetBinContent(i+1, entry*chan_hist.GetBinContent(i+1))
            print(new_hist.Write())

