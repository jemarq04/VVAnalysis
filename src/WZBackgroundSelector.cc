#include "Analysis/VVAnalysis/interface/WZBackgroundSelector.h"
#include <TStyle.h>

void WZBackgroundSelector::SlaveBegin(TTree * /*tree*/)
{
    fakeRate_allE_ = (ScaleFactor *) GetInputList()->FindObject("fakeRate_allE");
    if (fakeRate_allE_ == nullptr ) Abort("Must pass electron fake rate to input list!");
    fakeRate_allMu_ = (ScaleFactor *) GetInputList()->FindObject("fakeRate_allMu");
    if (fakeRate_allMu_ == nullptr ) Abort("Must pass muon fake rate to input list!");
}

void WZBackgroundSelector::SetupNewDirectory()
{
    WZSelector::SetupNewDirectory();

    // Insure that hist ranges are exactly the same as WZSelector, just change name
    for (const auto && obj : *currentHistDir_) {
        std::string name = obj->GetName();
        TNamed* named = dynamic_cast<TNamed*>(obj);
        named->SetName(name.insert(name.length()-3, "Fakes_").c_str());
    }

    AddObject<TH1D>(mjjHistPPF_, ("mjj_PPF_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
    AddObject<TH1D>(mjjHistPFP_, ("mjj_PFP_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
    AddObject<TH1D>(mjjHistFPP_, ("mjj_FPP_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
    AddObject<TH1D>(mjjHistFFP_, ("mjj_FFP_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
    AddObject<TH1D>(mjjHistFPF_, ("mjj_FPF_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
    AddObject<TH1D>(mjjHistPFF_, ("mjj_PFF_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
    AddObject<TH1D>(mjjHistFFF_, ("mjj_FFF_"+channelName_).c_str(), "mjj; m_{jj} [GeV]; Events;", 5, 0, 2500);
}

Bool_t WZBackgroundSelector::Process(Long64_t entry)
{
    LoadBranches(entry);

    if (!PassesBaseSelection(false, selection_))
        return true;
    if (isVBS_ && !PassesVBSSelection(true, mjj, jetPt, jetEta))
        return true;

    float evtwgt = 0;
    if (IsFPPRegion()) {
        mjjHistFPP_->Fill(mjj, genWeight);
        evtwgt = getl1FakeRate()*genWeight;
    }
    else if (IsPFPRegion()) {
        mjjHistPFP_->Fill(mjj, genWeight);
        evtwgt = getl2FakeRate()*genWeight;
    }
    else if (IsPPFRegion()) {
        mjjHistPPF_->Fill(mjj, genWeight);
        evtwgt = getl3FakeRate()*genWeight;
    }
    else if (IsFFFRegion()) {
        mjjHistFFF_->Fill(mjj, genWeight);
        evtwgt = getl1FakeRate()*getl2FakeRate()*getl3FakeRate()*genWeight;
    }
    else if (IsFPFRegion()) {
        mjjHistFPF_->Fill(mjj, genWeight);
        evtwgt = -1*getl1FakeRate()*getl3FakeRate()*genWeight;
    }
    else if (IsFFPRegion()) {
        mjjHistFFP_->Fill(mjj, genWeight);
        evtwgt = -1*getl1FakeRate()*getl2FakeRate()*genWeight;
    }
    else if (IsPFFRegion()) {
        mjjHistPFF_->Fill(mjj, genWeight);
        evtwgt = -1*getl2FakeRate()*getl3FakeRate()*genWeight;
    }
    else
        return true;

    FillHistograms(entry, evtwgt, true);

    return true;
}

float WZBackgroundSelector::getl1FakeRate() {
    float pt_fillval = l1Pt < FR_MAX_PT_ ? l1Pt : FR_MAX_PT_ - 0.01;
    float fr = 1;
    if (channel_ == eem|| channel_ == eee)
        fr = fakeRate_allE_->Evaluate2D(pt_fillval, std::abs(l1Eta));
    else
        fr = fakeRate_allMu_->Evaluate2D(pt_fillval, std::abs(l1Eta));
    return fr/(1-fr);
}

float WZBackgroundSelector::getl2FakeRate() {
    float pt_fillval = l2Pt < FR_MAX_PT_ ? l2Pt : FR_MAX_PT_ - 0.01;
    float fr = 1;
    if (channel_ == eem || channel_ == eee)
        fr = fakeRate_allE_->Evaluate2D(pt_fillval, std::abs(l2Eta));
    else
        fr = fakeRate_allMu_->Evaluate2D(pt_fillval, std::abs(l2Eta));
    return fr/(1-fr);
}

float WZBackgroundSelector::getl3FakeRate() {
    float pt_fillval = l3Pt < FR_MAX_PT_ ? l3Pt : FR_MAX_PT_ - 0.01;
    float fr = 1;
    if (channel_ == emm || channel_ == eee)
        fr = fakeRate_allE_->Evaluate2D(pt_fillval, std::abs(l3Eta));
    else
        fr = fakeRate_allMu_->Evaluate2D(pt_fillval, std::abs(l3Eta));
    return fr/(1-fr);
}

bool WZBackgroundSelector::IsFPPRegion() {
    return !zlep1IsTight() && zlep2IsTight() && lepton3IsTight();
}
bool WZBackgroundSelector::IsPFPRegion() {
    return zlep1IsTight() && !zlep2IsTight() && lepton3IsTight();
}

bool WZBackgroundSelector::IsPPFRegion() {
    return zlep1IsTight() && zlep2IsTight() && !lepton3IsTight();
}

bool WZBackgroundSelector::IsFPFRegion() {
    return !zlep1IsTight() && zlep2IsTight() && !lepton3IsTight();
}

bool WZBackgroundSelector::IsFFPRegion() {
    return !zlep1IsTight() && !zlep2IsTight() && lepton3IsTight();
}

bool WZBackgroundSelector::IsPFFRegion() {
    return zlep1IsTight() && !zlep2IsTight() && !lepton3IsTight();
}

bool WZBackgroundSelector::IsFFFRegion() {
    return !zlep1IsTight() && !zlep2IsTight() && !lepton3IsTight();
}
