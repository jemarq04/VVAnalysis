# coding: utf-8
import glob
import ROOT
from Utilities.python import ApplySelection
#comparison = "SvenjaNotKenneth"
comparison = "KennethNotSvenja"

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

for chan in ["eee", "eem", "emm", "mmm"]:
    print("Info for chan", chan)
    chain = ROOT.TChain("%s/ntuple" % chan)
    #for root_file in glob.glob("/data/kelong/DibosonAnalysisData/3LooseLeptons/2017-08-29-data_MuonEG_Run2016*/*"):
    for root_file in (glob.glob("/data/kelong/DibosonAnalysisData/3LooseLeptons/2017-08-17-data_Single*/*")
        + glob.glob("/data/kelong/DibosonAnalysisData/3LooseLeptons/2017-08-17-data_Double*/*")
        + glob.glob("/data/kelong/DibosonAnalysisData/3LooseLeptons/2017-08-31-data_MuonEG*/*")):
        chain.Add(root_file)
    events = []
    file_name = "/eos/user/k/kelong/WZAnalysisData/SyncWithSvenja/Differences_01Sep2017/all_data_Wselection/%s_%s.txt" % (comparison, chan)
    with open(file_name, "r") as file:
        for line in file.readlines():
            event_num = line.strip().split(",")
            if len(event_num) == 3:
                events.append("(run == {0} && lumi == {1} && evt == {2})".format(*event_num))
    
    for i, eventlist in enumerate(chunks(events, 40)):
        evtstring = " || ".join(eventlist)
        chain.GetPlayer().SetScanRedirect(True)
        #outfile_name = "/eos/user/k/kelong/WZAnalysisData/SyncWithSvenja/Differences_29Aug2017/3LooseLeptons/MuonEG/Details/%s_%s.txt" % (comparison, chan)
        outfile_name = file_name.replace("Wselection", "Wselection/Details") 
        if i > 0:
            outfile_name = outfile_name.replace(".txt", "%i.text" % i)
        chain.GetPlayer().SetScanFileName(outfile_name)
        expr = "run:lumi:evt:singleESingleMuPass:singleMuSingleEPass:doubleMuPass:doubleMuDZPass:doubleEPass:Flag_duplicateMuonsPass:Flag_BadPFMuonFilterPass:Flag_badMuonsPass:Flag_goodVerticesPass:{lep1}{lep1id}:{lep1}Pt:{lep1}Eta:{lep1}Phi:{lep1}PVDXY:{lep1}PVDZ:{lep1}RelPFIsoDBR04:{lep1}TrackIso/{lep1}Pt:{lep2}{lep2id}:{lep2}Pt:{lep2}Eta:{lep2}Phi:{lep2}PVDXY:{lep2}PVDZ:{lep2}RelPFIsoDBR04:{lep2}TrackIso/{lep2}Pt:{lep3}{lep3id}:{lep3}Pt:{lep3}Eta:{lep3}Phi:{lep3}PVDXY:{lep3}PVDZ:nCBVIDHLTSafeElec:nCBVIDTightElec:nWZLooseMuon:nWZTightMuon:{lep3}RelPFIsoDBR04:{lep3}TrackIso/{lep3}Pt"
        ApplySelection.setAliases(chain, chan, "Cuts/aliases.json")
        #trigger_shit = ":".join([ i + "Pass" for i in [
        #    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL",
        #    "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL",
        #    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
        #    "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ",
        #    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
        #    "HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
        #    "HLT_DoubleEle33_CaloIdL_GsfTrkIdVL",
        #    "HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL",
        #    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
        #    "HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
        #    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
        #    'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ',
        #    'HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ',
        #    "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL",
        #    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL",
        #    "HLT_DiMu9_Ele9_CaloIdL_TrackIdL",
        #    "HLT_TripleMu_12_10_5",
        #    "HLT_Ele25_eta2p1_WPTight_Gsf",
        #    "HLT_Ele27_WPTight_Gsf",
        #    "HLT_Ele27_eta2p1_WPLoose_Gsf",
        #    "HLT_IsoMu20",
        #    "HLT_IsoTkMu20",
        #    "HLT_IsoMu22",
        #    "HLT_IsoTkMu22",
        #    "HLT_Mu50",
        #    "HLT_Mu45_eta2p1",]
        #])
        #expr = expr.replace("Flag", trigger_shit + ":Flag")
        if chan == "eee":
            expr = expr.format(lep1="e1", lep2="e2", lep3="e3", lep1id="IsCBVIDHLTSafe", lep2id="IsCBVIDHLTSafe", lep3id="IsCBVIDHLTSafe")
        elif chan == "eem":
            expr = expr.format(lep1="e1", lep2="e2", lep3="m", lep1id="IsCBVIDHLTSafe", lep2id="IsCBVIDHLTSafe", lep3id="IsWZLoose")
        elif chan == "emm":
            expr = expr.format(lep1="m1", lep2="m2", lep3="e", lep1id="IsWZLoose", lep2id="IsWZLoose", lep3id="IsCBVIDHLTSafe")
        elif chan == "mmm":
            expr = expr.format(lep1="m1", lep2="m2", lep3="m3", lep1id="IsWZLoose", lep2id="IsWZLoose", lep3id="IsWZLoose")
        expr = expr.replace("eRelPFIsoDBR04:","")
        expr = expr.replace("e1RelPFIsoDBR04:","")
        expr = expr.replace("e2RelPFIsoDBR04:","")
        expr = expr.replace("e3RelPFIsoDBR04:","")
        expr = expr.replace(":e1TrackIso/e1Pt","")
        expr = expr.replace(":e2TrackIso/e2Pt","")
        expr = expr.replace(":e3TrackIso/e3Pt","")
        expr = expr.replace(":eTrackIso/ePt","")
        chain.Scan(expr, evtstring, "colsize=30")
