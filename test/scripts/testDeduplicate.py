#!/usr/bin/env python
import ROOT

#myfile = ROOT.TFile("/data/kelong/DibosonAnalysisData/Preselection/2016-11-02-wz3lnu-powheg-WZxsec2016-preselection-v1/skim-ntuplize_cfg-086609CA-D81B-E611-BF6C-002590D9D896.root")
#chain = myfile.Get("eee/ntuple")

for state in ['eee', 'eem', 'emm', 'mmm']:
    chain = ROOT.TChain("%s/ntuple" % state)
    chain.Add("/data/kelong/DibosonAnalysisData/Preselection/2016-11-02-wz3lnu-powheg-WZxsec2016-preselection-v1/skim-ntuplize_cfg-086609CA-D81B-E611-BF6C-002590D9D896.root")
    selector = ROOT.TSelector.GetSelector("../../Utilities/Selectors/disambiguateFinalStates.C+") 
    print( '-'*80)
    print( 'channel is %s' % state )
    print( "Initial number of entries is %i" % chain.GetEntries())
    print( "Events with list %i " % chain.Draw("Mass", ""))
    zcand_name = "e1_e2_Mass" if state.count('e') >= 2 else "m1_m2_Mass"
    selector.setZCandidateBranchName(zcand_name)
    chain.Process(selector)
    entryList = selector.GetOutputList().FindObject('bestCandidates')
    new_chain = chain.CopyTree("")
    new_chain.SetEntryList(entryList)
    print( "Events in the list %i" % entryList.GetN())
    print( "Events with list %i " % new_chain.Draw("Mass", ""))
    del entryList

#chain.Draw(">>mylist", "Mass > 80")
#entryList = ROOT.gDirectory.Get("mylist")
