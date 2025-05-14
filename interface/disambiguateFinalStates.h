/*
 *
 * TSelector deduplicate events in combinatorical ntuple
 * by choosing event with l1_l2_Mass pairing closest to
 * M_PDG(Z) = 91.1876 
 * with the highest scalar Pt sum of the remaining leptons
 * used as a tiebreaker. 
 *
 * Modified from K. Long, U. Wisconsin
 *
 * https://https://github.com/kdlong/VVAnalysis/blob/master/src/disambiguateFinalStates.cc
 */
#ifndef disambiguateFinalStates_h
#define disambiguateFinalStates_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TEntryList.h>
#include <TTreeFormula.h>

class disambiguateFinalStates : public TSelector {
  public :
    TTree* fChain;

    float l1_l2_Mass;
    float l1_Pt;
    float l2_Pt;
    float l3_l4_Mass;
    float l3_Pt;
    float l4_Pt;
    bool l1IsTight;
    bool l2IsTight;
    bool l3IsTight;
    bool l4IsTight;
    bool l1IsIso;
    bool l2IsIso;
    bool l3IsIso;
    bool l4IsIso;
    ULong64_t evt;
    UInt_t run;

    TBranch* b_l1_l2_Mass;
    TBranch* b_l1_Pt; 
    TBranch* b_l2_Pt;
    TBranch* b_l3_l4_Mass;
    TBranch* b_l3_Pt;
    TBranch* b_l4_Pt;
    TBranch* b_l1IsTight;
    TBranch* b_l2IsTight;
    TBranch* b_l3IsTight;
    TBranch* b_l4IsTight; 
    TBranch* b_l1IsIso;
    TBranch* b_l2IsIso;
    TBranch* b_l3IsIso;
    TBranch* b_l4IsIso;

    TBranch* b_evt;
    TBranch* b_run;

    // TODO Add TTreeFormula, fix issue when using chain.Process 
    // over multiple files (currently segfaults)
    TEntryList     *fBestCandidateEntryList; 
    TTreeFormula   *fCutFormula;

    disambiguateFinalStates(TTree * /*tree*/ =0) : fChain(0), fBestCandidateEntryList(0),fCutFormula(0), fCurrentRun(-1), fCurrentEvt(-1) { }
    virtual ~disambiguateFinalStates() { SafeDelete(fBestCandidateEntryList);SafeDelete(fCutFormula); }
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
    virtual TList*  GetOutputList() const { return fOutput; }
    virtual void    SlaveTerminate();
    virtual void    Terminate();
    void setZCandidateBranchName(const char* name1,const char* name2, const char* name3,const char* name4,const char* name5,const char* name6,const char* name7,const char* name8, const char* name9,const char* name10,const char* name11,const char* name12,const char* name13,const char* name14) { 
      l1_l2_Cand_mass = const_cast<char*>(name1);  
      l1_Cand_pt = const_cast<char*>(name2);  
      l2_Cand_pt = const_cast<char*>(name3); 
      l3_l4_Cand_mass = const_cast<char*>(name4); 
      l3_Cand_pt = const_cast<char*>(name5);
      l4_Cand_pt = const_cast<char*>(name6);
      l1_Cand_Tight = const_cast<char*>(name7);  
      l2_Cand_Tight = const_cast<char*>(name8); 
      l3_Cand_Tight = const_cast<char*>(name9);
      l4_Cand_Tight = const_cast<char*>(name10);
      l1_Cand_Iso = const_cast<char*>(name11);  
      l2_Cand_Iso = const_cast<char*>(name12); 
      l3_Cand_Iso = const_cast<char*>(name13);
      l4_Cand_Iso = const_cast<char*>(name14); 
    }

    ClassDef(disambiguateFinalStates,0);

  private :
    void findBestEntry();
    bool lep1IsTight();
    bool lep2IsTight();
    bool lep3IsTight();
    bool lep4IsTight();
    bool tightZ1Leptons();
    bool tightZ2Leptons();
    UInt_t fCurrentRun;
    ULong64_t fCurrentEvt;
    std::vector<Long64_t> fEntriesToCompareTight;
    std::vector<float> fEntryDiscriminantsTight; 
    std::vector<float> fEntryZ2PtSumTight;
    std::vector<Long64_t> fEntriesToCompareLoose;
    std::vector<float> fEntryDiscriminantsLoose;
    std::vector<float> fEntryZ2PtSumLoose;
    char* l1_l2_Cand_mass; 
    char* l1_Cand_pt;
    char* l2_Cand_pt; 
    char* l3_l4_Cand_mass; 
    char* l3_Cand_pt;
    char* l4_Cand_pt;
    char* l1_Cand_Tight;
    char* l2_Cand_Tight; 
    char* l3_Cand_Tight;
    char* l4_Cand_Tight; 
    char* l1_Cand_Iso;
    char* l2_Cand_Iso; 
    char* l3_Cand_Iso;
    char* l4_Cand_Iso; 
};

#endif

