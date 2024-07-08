# Setup ScaleFactor objects to be "registered" with ROOT,
# allowing them to be called from TTree.Draw(), for example.
# Currently used for lepton scale factors and pileup weights.
#
# Modified from N. Smith, U. Wisconsin
# 

#!/usr/bin/env python
import ROOT
import argparse
import os
import sys
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

def float2double(hist):
    if hist.ClassName() == 'TH1D' or hist.ClassName() == 'TH2D':
        return hist
    elif hist.ClassName() == 'TH1F':
        new = ROOT.TH1D()
        hist.Copy(new)
    elif hist.ClassName() == 'TH2F':
        new = ROOT.TH2D()
        hist.Copy(new)
    else:
        raise Exception("Bad hist, dummy")
    return new

def invert2DHist(hist):
    new_hist = hist.Clone()
    ROOT.SetOwnership(new_hist, False)
    for x in range(hist.GetNbinsX()+1):
        for y in range(hist.GetNbinsY()+1):
            value = hist.GetBinContent(x, y)
            new_hist.SetBinContent(y, x, value)
    new_hist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle())
    new_hist.GetYaxis().SetTitle(hist.GetYaxis().GetTitle())
    return new_hist

parser = argparse.ArgumentParser()

def getComLineArgs():
    parser.add_argument("--year", type=str,default="default", help="Year of Analysis")
    parser.add_argument("-t", "--tightfr_file", type=str,
            default="")
    parser.add_argument("--output_file", "-o", type=str,
            default="test.root", help="Output file name")

    return vars(parser.parse_args())

args = getComLineArgs()

year = args["year"]
frfile = args["tightfr_file"]
fScales = ROOT.TFile(args['output_file'], 'recreate')



# For nTruePU reweighting
if year=="2016":
    print("2016 PU reweighting")
    pileupSF = ROOT.ScaleFactor("pileupSF", "Run2016B-H 35.9/fb Pileup profile over RunIISummer16 MC Scale Factor, x=NTruePU")
    pileupFile = ROOT.TFile.Open('PileupWeights16/PU_Central.root')
    pileupFileUp = ROOT.TFile.Open('PileupWeights16/PU_minBiasUP.root')
    pileupFileDown = ROOT.TFile.Open('PileupWeights16/PU_minBiasDOWN.root')
elif year=="2017":
    pileupSF = ROOT.ScaleFactor("pileupSF", "Run2017B-F 41.5/fb Pileup profile over RunIIFall17 MC Scale Factor, x=NTruePU")
    pileupFile = ROOT.TFile.Open('PileupWeights17/PU_Central.root')
    pileupFileUp = ROOT.TFile.Open('PileupWeights17/PU_minBiasUP.root')
    pileupFileDown = ROOT.TFile.Open('PileupWeights17/PU_minBiasDOWN.root')
elif year=="2018":
    pileupSF = ROOT.ScaleFactor("pileupSF", "Run2018A-D 59.95/fb Pileup profile over RunIIFall18 MC Scale Factor, x=NTruePU")
    pileupFile = ROOT.TFile.Open('PileupWeights18/PU_Central.root')
    pileupFileUp = ROOT.TFile.Open('PileupWeights18/PU_minBiasUP.root')
    pileupFileDown = ROOT.TFile.Open('PileupWeights18/PU_minBiasDOWN.root')
else:
    print("You forgot to specify the year for which you want scale factors")
    sys.exit()
pileupSF.Set1DHist(pileupFile.Get('pileup'), pileupFileUp.Get('pileup'), pileupFileDown.Get('pileup'))
fScales.cd()
pileupSF.Write()


if year=="2016":
    print("Doing 2016 Lepton SF")
    electronLowReco16SF = ROOT.ScaleFactor("electronLowReco16SF", "Run '16 Electron Low Reco SF, x=Eta, y=Pt")
    eLowRecoFile = ROOT.TFile.Open('data/Ele_Reco_LowEt_2016.root')
    electronLowReco16SF.Set2DHist(float2double(eLowRecoFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronLowReco16SF.Write()
    
    #Electron (Pt>20 Reco SF from POG https://twiki.cern.ch/twiki/bin/viewauth/CMS/Egamma2016DataRecommendations
    electronReco16SF = ROOT.ScaleFactor("electronReco16SF", "Run '16 Electron Reco SF, x=Eta, y=Pt")
    eRecoFile = ROOT.TFile.Open('data/Ele_Reco_2016.root')
    electronReco16SF.Set2DHist(float2double(eRecoFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronReco16SF.Write()
    
    electronRun16SF = ROOT.ScaleFactor("electronRun16SF", "Run '16 Electron HZZ ID SF, x=Eta, y=Pt")
    eidFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2016_NoGap.root')
    electronRun16SF.Set2DHist(float2double(eidFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronRun16SF.Write()
    
    electronRun16GapSF = ROOT.ScaleFactor("electronRun16GapSF", "Run '16 GapElectron HZZ ID SF, x=Eta, y=Pt")
    eleGsfFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2016_Gap.root')
    electronRun16GapSF.Set2DHist(float2double(eleGsfFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronRun16GapSF.Write()
    
    muonRun16SF = ROOT.ScaleFactor("muonRun16SF", "Muon Run '16 Trk+ID+ISO SF, x=abs(Eta), y=Pt")
    mid16File = ROOT.TFile.Open('data/MoriondSFs/final_HZZ_SF_2016_legacy_mupogsysts_newLoose_noTracking_1610.root')
    muonRun16SF.Set2DHist(float2double(mid16File.Get('FINAL')),float2double(mid16File.Get('ERROR')),float2double(mid16File.Get('ERROR')))
    fScales.cd()
    muonRun16SF.Write()
elif year=="2017":
    electronLowReco17SF = ROOT.ScaleFactor("electronLowReco17SF", "Run '17 Electron Low Reco SF, x=Eta, y=Pt")
    eLowRecoFile = ROOT.TFile.Open('data/Ele_Reco_LowEt_2017.root')
    electronLowReco17SF.Set2DHist(float2double(eLowRecoFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronLowReco17SF.Write()
    
    #Electron (Pt>20 Reco SF from POG https://twiki.cern.ch/twiki/bin/viewauth/CMS/Egamma2017DataRecommendations
    electronReco17SF = ROOT.ScaleFactor("electronReco17SF", "Run '17 Electron Reco SF, x=Eta, y=Pt")
    eRecoFile = ROOT.TFile.Open('data/Ele_Reco_2017.root')
    electronReco17SF.Set2DHist(float2double(eRecoFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronReco17SF.Write()
    
    electronRun17SF = ROOT.ScaleFactor("electronRun17SF", "Run '17 Electron HZZ ID SF, x=Eta, y=Pt")
    eidFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2017_NoGap.root')
    electronRun17SF.Set2DHist(float2double(eidFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronRun17SF.Write()
    
    electronRun17GapSF = ROOT.ScaleFactor("electronRun17GapSF", "Run '17 GapElectron HZZ ID SF, x=Eta, y=Pt")
    eleGsfFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2017_Gap.root')
    electronRun17GapSF.Set2DHist(float2double(eleGsfFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronRun17GapSF.Write()
    
    muonRun17SF = ROOT.ScaleFactor("muonRun17SF", "Muon Run '17 Trk+ID+ISO SF, x=abs(Eta), y=Pt")
    midFile = ROOT.TFile.Open('data/MoriondSFs/ScaleFactors_mu_Moriond2018_final.root')
    muonRun17SF.Set2DHist(float2double(midFile.Get('FINAL')),float2double(midFile.Get('ERROR')),float2double(midFile.Get('ERROR')))
    fScales.cd()
    muonRun17SF.Write()
elif year=="2018":
    #Electron (Pt<20 Reco SF from POG https://twiki.cern.ch/twiki/bin/viewauth/CMS/Egamma2018DataRecommendations
    electronLowReco18SF = ROOT.ScaleFactor("electronLowReco18SF", "Run '18 Electron Low Reco SF, x=Eta, y=Pt")
    eLowRecoFile = ROOT.TFile.Open('data/Ele_Reco_LowEt_2018.root')
    electronLowReco18SF.Set2DHist(float2double(eLowRecoFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronLowReco18SF.Write()
    
    #Electron (Pt>20 Reco SF from POG https://twiki.cern.ch/twiki/bin/viewauth/CMS/Egamma2018DataRecommendations
    electronReco18SF = ROOT.ScaleFactor("electronReco18SF", "Run '18 Electron Reco SF, x=Eta, y=Pt")
    eRecoFile = ROOT.TFile.Open('data/Ele_Reco_2018.root')
    electronReco18SF.Set2DHist(float2double(eRecoFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronReco18SF.Write()
    
    electronRun18SF = ROOT.ScaleFactor("electronRun18SF", "Run '18 Electron HZZ ID SF, x=Eta, y=Pt")
    eidFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2018_NoGap.root')
    electronRun18SF.Set2DHist(float2double(eidFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronRun18SF.Write()
    
    electronRun18GapSF = ROOT.ScaleFactor("electronRun18GapSF", "Run '18 GapElectron HZZ ID SF, x=Eta, y=Pt")
    eleGsfFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2018_Gap.root')
    electronRun18GapSF.Set2DHist(float2double(eleGsfFile.Get('EGamma_SF2D')))
    fScales.cd()
    electronRun18GapSF.Write()
    
    muonRun18SF = ROOT.ScaleFactor("muonRun18SF", "Muon Run '18 Trk+ID+ISO SF, x=abs(Eta), y=Pt")
    mid18File = ROOT.TFile.Open('data/final_HZZ_muon_SF_2018_IsBDT_0610.root')
    muonRun18SF.Set2DHist(float2double(mid18File.Get('FINAL')),float2double(mid18File.Get('ERROR')),float2double(mid18File.Get('ERROR')))
    fScales.cd()
    muonRun18SF.Write()

#For every year there is a separate fakeRate file
if os.path.isfile(frfile):
    print("INFO: Adding tight fake rates to %s" % args["output_file"])
    fakeRateFile = ROOT.TFile.Open(frfile)
    eZZTightFakeRate = ROOT.ScaleFactor("eZZTightFakeRate", "Fake rate from Z+jet")
    eZZTightFakeRate.Set2DHist(fakeRateFile.Get('DataEWKCorrected/ratioE2D_allE'), 0, 0, ROOT.ScaleFactor.AsInHist)
    mZZTightFakeRate = ROOT.ScaleFactor("mZZTightFakeRate", "Fake rate from Z+jet")
    mZZTightFakeRate.Set2DHist(fakeRateFile.Get('DataEWKCorrected/ratioMu2D_allMu'), 0, 0, ROOT.ScaleFactor.AsInHist)
    fScales.cd()
    mZZTightFakeRate.Write()
    eZZTightFakeRate.Write()
