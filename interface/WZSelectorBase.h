#ifndef WZSelectorBase_h
#define WZSelectorBase_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TH1.h>
#include <TH2.h>
#include <exception>
#include <iostream>
#include <set>

// Headers needed by this particular selector
#include <vector>

class WZSelectorBase : public TSelector {
public :
    TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain
    enum Channel {
        eee,
        eem,
        emm,
        mmm,
        Unknown,
    }; 
    enum Selection {
        tightleptons,
        VBSselection,
        VBSselection_Tight,
    }; 
    TList *currentHistDir_{nullptr};
    TH2D* passingTight2D_;
    TH1D* passingTight1DPt_;
    TH1D* passingTight1DEta_;
    TH2D* passingLoose2D_;
    TH1D* passingLoose1DPt_;
    TH1D* passingLoose1DEta_;
    TH2D* ratio2D_;
    TH1D* ratio1DPt_;
    TH1D* ratio1DEta_;

    bool isVBS_;
    bool passesLeptonVeto;
    Float_t genWeight;
    Float_t Zmass;
    Float_t type1_pfMETEt;
    UInt_t nCBVIDTightElec;
    UInt_t nWZTightMuon;
    Bool_t l1IsTight;
    Bool_t l2IsTight;
    Bool_t l3IsTight;
    Bool_t e1IsEB;
    Bool_t e2IsEB;
    Bool_t e3IsEB;
    Float_t e1PVDXY;
    Float_t e2PVDXY;
    Float_t e3PVDXY;
    Float_t e1PVDZ;
    Float_t e2PVDZ;
    Float_t e3PVDZ;
    Float_t m1RelPFIsoDBR04;
    Float_t m2RelPFIsoDBR04;
    Float_t m3RelPFIsoDBR04;
    Float_t l3Eta;
    Float_t l1Pt;
    Float_t l2Pt;
    Float_t l3Pt;
    Float_t l3MtToMET;
    Float_t Flag_BadChargedCandidateFilterPass;
    Float_t Flag_BadPFMuonFilterPass;
    Bool_t Flag_duplicateMuonsPass;
    Bool_t Flag_badMuonsPass;
    Bool_t Flag_HBHENoiseFilterPass;
    Bool_t Flag_HBHENoiseIsoFilterPass;
    Bool_t Flag_EcalDeadCellTriggerPrimitiveFilterPass;
    Bool_t Flag_goodVerticesPass;
    Bool_t Flag_eeBadScFilterPass;
    Bool_t Flag_globalTightHalo2016FilterPass;
    
    TBranch* b_genWeight;
    TBranch* b_Zmass;
    TBranch* b_type1_pfMETEt;
    TBranch* b_nCBVIDTightElec;
    TBranch* b_nWZTightMuon;
    TBranch* b_l1IsTight;
    TBranch* b_l2IsTight;
    TBranch* b_l3IsTight;
    TBranch* b_e1IsEB;
    TBranch* b_e2IsEB;
    TBranch* b_e3IsEB;
    TBranch* b_e1PVDXY;
    TBranch* b_e2PVDXY;
    TBranch* b_e3PVDXY;
    TBranch* b_e1PVDZ;
    TBranch* b_e2PVDZ;
    TBranch* b_e3PVDZ;
    TBranch* b_m1RelPFIsoDBR04;
    TBranch* b_m2RelPFIsoDBR04;
    TBranch* b_m3RelPFIsoDBR04;
    TBranch* b_l3Eta;
    TBranch* b_l1Pt;
    TBranch* b_l2Pt;
    TBranch* b_l3Pt;
    TBranch* b_l3MtToMET;
    TBranch* b_Flag_BadChargedCandidateFilterPass;
    TBranch* b_Flag_BadPFMuonFilterPass;
    TBranch* b_Flag_badMuonsPass;
    TBranch* b_Flag_duplicateMuonsPass;
    TBranch* b_Flag_HBHENoiseFilterPass;
    TBranch* b_Flag_HBHENoiseIsoFilterPass;
    TBranch* b_Flag_EcalDeadCellTriggerPrimitiveFilterPass;
    TBranch* b_Flag_goodVerticesPass;
    TBranch* b_Flag_eeBadScFilterPass;
    TBranch* b_Flag_globalTightHalo2016FilterPass;

    // Readers to access the data (delete the ones you do not need).
    WZSelectorBase(TTree * /*tree*/ =0) { }
    virtual ~WZSelectorBase() { }
    virtual Int_t   Version() const { return 2; }
    virtual void    Begin(TTree *tree);
    virtual void    SlaveBegin(TTree *tree);
    virtual void    Init(TTree *tree);
    virtual Bool_t  Notify();
    virtual Bool_t  Process(Long64_t entry);
    virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
    virtual void    SetOption(const char *option) { fOption = option; }
    virtual void    SetObject(TObject *obj) { fObject = obj; }
    virtual void    SetInputList(TList *input) { fInput = input; }
    virtual TList  *GetOutputList() const { return fOutput; }
    virtual void    SlaveTerminate();
    virtual void    Terminate();

    // We'll collect pointers to objects from derived classes
    // as they are registered with AddObject, and update them to
    // the new object when a dataset is switched
    std::set<TNamed**> allObjects_;
    // Derived classes override (and call) this to register new objects
    // With AddObject<Type>(localPtr, ...);
    virtual void SetupNewDirectory();

    template<typename T, typename... Args>
    void AddObject(T* &ptr, Args... args) {
        static_assert(std::is_base_of<TNamed, T>::value, "Objects must inheirit from ROOT TNamed to be streamable from PROOF sessions");
        ptr = new T(args...);
        ptr->SetDirectory(gROOT);
        currentHistDir_->Add(ptr);
        allObjects_.insert((TNamed**) &ptr);
    };
    void UpdateDirectory();
    ClassDef(WZSelectorBase,0);

protected:
    std::string name_ = "Unnamed";
    std::string channelName_ = "Unnamed";
    Channel channel_ = Unknown;
    std::string selectionName_ = "tightleptons";
    Selection selection_ = tightleptons;
    bool isMC_;
    const float FR_MAX_PT_ = 50;
    const float FR_MAX_ETA_ = 2.5;
    bool zlep1IsTight();
    bool zlep2IsTight();
    bool lepton3IsTight();
    bool tightZLeptons();
};

#endif

