import ROOT
import json
from python import ApplySelection

#selection = "Zlep1IsTight && Zlep2IsTight && WlepIsTight && abs(nLooseLep -3) < 0.1 && metFiltersDataNoBadMuon && mjj > 100 && (dEtajj < 2.5 || mjj < 500)"
selection = "Zlep1IsTightNoIP && Zlep1_PVDZ < 1. && Zlep1_PVDXY < 1. && Zlep2IsTightNoIP && Zlep2_PVDZ < 1. && Zlep2_PVDXY < 1. && WlepIsTightNoIP && Wlep_PVDZ < 1. && Wlep_PVDXY < 1. && (nCBVIDHLTSafeElec+nWZMediumMuon) < 3.5  && metFiltersDataNoBadMuon && mjj > 100 && (dEtajj < 2.5 || mjj < 500)"
#selection = "Zlep1IsTightNoIP && Zlep1_PVDZ < 1. && Zlep1_PVDXY < 1. && Zlep2IsTightNoIP && Zlep2_PVDZ < 1. && Zlep2_PVDXY < 1. && WlepIsTightNoIP && Wlep_PVDZ < 1. && Wlep_PVDXY < 1. && abs(nCBVIDHLTSafeElecNoIP+nWZMediumMuon - 3) < 0.1  && metFiltersDataNoBadMuon && mjj > 100 && (dEtajj < 2.5 || mjj < 500)"
ptsort = True
with open("controlevent.txt", "w") as outfile:
    #file_info = json.load(open("/afs/cern.ch/user/k/kelong/work/AnalysisDatasetManager/FileInfo/WZxsec2016/WselectionMediumLeptons.json"))
    file_info = json.load(open("/afs/cern.ch/user/k/kelong/work/AnalysisDatasetManager/FileInfo/WZxsec2016/WselectionMediumLeptonsNoEIP.json"))
    for i, chan in enumerate(["mmm", "eem", "emm", "eee"]):
        chain = ROOT.TChain("%s/ntuple" % chan)
        for key, value in file_info.items():
            if "data" in key:
                chain.Add(value["file_path"])
        print("Chan is", chan)
        ApplySelection.setAliases(chain, chan, "Cuts/WZxsec2016/aliases.json")
        cut_chain = chain.CopyTree(selection) 
        print(cut_chain.GetEntries())
        for row in cut_chain:
            outfile.write("DATA "+" ".join([str(v) for v in [row.run,row.lumi,row.evt]]) + " " +
                " ".join([str(round(v,2)) for v in [row.jetPt[0],row.jetEta[0],row.jetPhi[0],
                    row.jetPt[1],row.jetEta[1], row.jetPhi[1],row.mjj,abs(row.jetEta[0]-row.jetEta[1]),len(row.jetPt)]]))
            if ptsort:
                pts = []
                if chan == "eee":
                    leps = list(reversed(sorted([(row.e1Pt, row.e1Eta),(row.e2Pt, row.e2Eta),(row.e3Pt, row.e3Eta)], key=lambda x: x[0])))
                elif chan == "eem":
                    leps = list(reversed(sorted([(row.e1Pt, row.e1Eta),(row.e2Pt, row.e2Eta),(row.mPt, row.mEta)], key=lambda x: x[0])))
                elif chan == "emm":
                    leps = list(reversed(sorted([(row.m1Pt, row.m1Eta),(row.m2Pt, row.m2Eta),(row.ePt, row.eEta)], key=lambda x: x[0])))
                if chan == "mmm":
                    leps = list(reversed(sorted([(row.m1Pt, row.m1Eta),(row.m2Pt, row.m2Eta),(row.m3Pt, row.m3Eta)], key=lambda x: x[0])))
                outfile.write(" " + " ".join([str(round(v,4)) for v in [leps[0][0],leps[0][1],leps[1][0],leps[1][1]]]) + " %i\n" %i)
            else:
                if chan == "eee":
                    outfile.write(" " + " ".join([str(round(v,2)) for v in [row.e1Pt,row.e1Eta,row.e2Pt,row.e2Eta]]) + " %i\n" %i)
                elif chan == "eem":
                    outfile.write(" " + " ".join([str(round(v,2)) for v in [row.e1Pt,row.e1Eta,row.e2Pt,row.e2Eta]]) + " %i\n" %i)
                elif chan == "emm":
                    outfile.write(" " + " ".join([str(round(v,2)) for v in [row.m1Pt,row.m1Eta,row.m2Pt,row.m2Eta]]) + " %i\n" %i)
                elif chan == "mmm":
                    outfile.write(" " + " ".join([str(round(v,2)) for v in [row.m1Pt,row.m1Eta,row.m2Pt,row.m2Eta]]) + " %i\n" %i)
