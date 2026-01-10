#include "Analysis/VVAnalysis/interface/FakeRateSelector.h"
#include <TStyle.h>

Bool_t FakeRateSelector::Process(Long64_t entry)
{
    WZSelectorBase::Process(entry);

    b_Zmass->GetEntry(entry);
    b_type1_pfMETEt->GetEntry(entry);

    b_l1Pt->GetEntry(entry);
    b_l2Pt->GetEntry(entry);
    b_l3Pt->GetEntry(entry);
    b_l3Eta->GetEntry(entry);
    b_l3MtToMET->GetEntry(entry);

    if (!passesLeptonVeto)
        return true;
    if (l1Pt < 25 || l2Pt < 15)
        return true;
    if (Zmass > 111.1876 || Zmass < 81.1876)
        return true;
    if (type1_pfMETEt > 30)
        return true;
    //if (l3MtToMET > 30)
    //    return true;
    if (!tightZLeptons())
        return true;
    float pt_fillval = l3Pt < FR_MAX_PT_ ? l3Pt : FR_MAX_PT_ - 0.01;
    float eta_fillval = std::abs(l3Eta) < FR_MAX_ETA_ ? std::abs(l3Eta) : FR_MAX_ETA_ - 0.01;
    passingLoose2D_->Fill(pt_fillval, eta_fillval, genWeight);
    passingLoose1DPt_->Fill(pt_fillval, genWeight);
    passingLoose1DEta_->Fill(eta_fillval, genWeight);
    if (lepton3IsTight()) {
        passingTight2D_->Fill(pt_fillval, eta_fillval, genWeight);
        passingTight1DPt_->Fill(pt_fillval, genWeight);
        passingTight1DEta_->Fill(eta_fillval, genWeight);
    }
    return kTRUE;
}

void FakeRateSelector::Init(TTree *tree)
{
    WZSelectorBase::Init(tree);

    fChain->SetBranchAddress("type1_pfMETEt", &type1_pfMETEt, &b_type1_pfMETEt);

    if (channel_ == eee) {
        fChain->SetBranchAddress("e1_e2_Mass", &Zmass, &b_Zmass);
        fChain->SetBranchAddress("e1Pt", &l1Pt, &b_l1Pt);
        fChain->SetBranchAddress("e2Pt", &l2Pt, &b_l2Pt);
        fChain->SetBranchAddress("e3Pt", &l3Pt, &b_l3Pt);
        fChain->SetBranchAddress("e3Eta", &l3Eta, &b_l3Eta);
        fChain->SetBranchAddress("e3MtToMET", &l3MtToMET, &b_l3MtToMET);
    }
    else if (channel_ == eem) {
        fChain->SetBranchAddress("e1_e2_Mass", &Zmass, &b_Zmass);

        fChain->SetBranchAddress("e1Pt", &l1Pt, &b_l1Pt);
        fChain->SetBranchAddress("e2Pt", &l2Pt, &b_l2Pt);
        fChain->SetBranchAddress("mPt", &l3Pt, &b_l3Pt);
        fChain->SetBranchAddress("mEta", &l3Eta, &b_l3Eta);
        fChain->SetBranchAddress("mMtToMET", &l3MtToMET, &b_l3MtToMET);
    }
    else if (channel_ == emm) {
        fChain->SetBranchAddress("m1_m2_Mass", &Zmass, &b_Zmass);
        fChain->SetBranchAddress("m1Pt", &l1Pt, &b_l1Pt);
        fChain->SetBranchAddress("m2Pt", &l2Pt, &b_l2Pt);
        fChain->SetBranchAddress("ePt", &l3Pt, &b_l3Pt);
        fChain->SetBranchAddress("eEta", &l3Eta, &b_l3Eta);
        fChain->SetBranchAddress("eMtToMET", &l3MtToMET, &b_l3MtToMET);
    }
    else if (channel_ == mmm) {
        fChain->SetBranchAddress("m1_m2_Mass", &Zmass, &b_Zmass);
        fChain->SetBranchAddress("m1Pt", &l1Pt, &b_l1Pt);
        fChain->SetBranchAddress("m2Pt", &l2Pt, &b_l2Pt);
        fChain->SetBranchAddress("m3Pt", &l3Pt, &b_l3Pt);
        fChain->SetBranchAddress("m3Eta", &l3Eta, &b_l3Eta);
        fChain->SetBranchAddress("m3MtToMET", &l3MtToMET, &b_l3MtToMET);
    }
}

void FakeRateSelector::SetupNewDirectory()
{
    WZSelectorBase::SetupNewDirectory();

    AddObject<TH2D>(passingTight2D_, ("passingTight2D_"+channelName_).c_str(), "#eta; p_{T} [GeV]", 4, 10, 50, 3, 0, 2.5);
    AddObject<TH1D>(passingTight1DPt_, ("passingTight1DPt_"+channelName_).c_str(), "Tight leptons; p_{T} [GeV]", 4, 10, 50);
    AddObject<TH1D>(passingTight1DEta_, ("passingTight1DEta_"+channelName_).c_str(), "Tight leptons; #eta", 3, 0, 2.5);

    AddObject<TH2D>(passingLoose2D_, ("passingLoose2D_"+channelName_).c_str(), "#eta; p_{T} [GeV]", 4, 10, 50, 3, 0, 2.5);
    AddObject<TH1D>(passingLoose1DPt_, ("passingLoose1DPt_"+channelName_).c_str(), "Loose leptons; p_{T} [GeV]", 4, 10, 50);
    AddObject<TH1D>(passingLoose1DEta_, ("passingLoose1DEta_"+channelName_).c_str(), "Loose leptons; #eta", 3, 0, 2.5);
}
