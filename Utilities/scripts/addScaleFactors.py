import ROOT
from array import array

def addWeightsForState(original_file, state):
    tree = original_file.Get("%s/ntuple" % state)
    tree.SetBranchStatus("*", 0)
    if state == "eee":
        leps = ["e1", "e2", "e3"]
    elif state == "eem":
        leps = ["e1", "e2", "m"]
        mTightIso_weight = array('f', [0])
        mTightIso_branch = tree.Branch('mTightIsoSF', mTightIso_weight, 'mTightIsoSF/F') 
        tree.SetBranchStatus("mTightIsoSF", 1)
    elif state == "emm":
        leps = ["e", "m1", "m2"]
        m1TightIso_weight = array('f', [0])
        m1TightIso_branch = tree.Branch('m1TightIsoSF', m1TightIso_weight, 'm1TightIsoSF/F') 
        tree.SetBranchStatus("m1TightIsoSF", 1)
        m2TightIso_weight = array('f', [0])
        m2TightIso_branch = tree.Branch('m2TightIsoSF', m2TightIso_weight, 'm2TightIsoSF/F') 
        tree.SetBranchStatus("m2TightIsoSF", 1)
    elif state == "mmm":
        leps = ["m1", "m2", "m3"]
        m1TightIso_weight = array('f', [0])
        m1TightIso_branch = tree.Branch('m1TightIsoSF', m1TightIso_weight, 'm1TightIsoSF/F') 
        tree.SetBranchStatus("m1TightIsoSF", 1)
        m2TightIso_weight = array('f', [0])
        m2TightIso_branch = tree.Branch('m2TightIsoSF', m2TightIso_weight, 'm2TightIsoSF/F') 
        tree.SetBranchStatus("m2TightIsoSF", 1)
        m3TightIso_weight = array('f', [0])
        m3TightIso_branch = tree.Branch('m3TightIsoSF', m3TightIso_weight, 'm3TightIsoSF/F') 
        tree.SetBranchStatus("m3TightIsoSF", 1)
    else:
        print "That don't work :("
        exit(0)
    pileup_weight = array('f', [0])
    pileup_branch = tree.Branch('pileupSF', pileup_weight, 'pileupSF/F') 
    tree.SetBranchStatus("pileupSF", 1)

    lepTightId_weights = [array('f', [0]), array('f', [0]), array('f', [0])]
    lepTightId_branches = []
    lepMediumId_weights = [array('f', [0]), array('f', [0]), array('f', [0])]
    lepMediumId_branches = []
    tree.SetBranchStatus("pileupSF", 1)
    tree.SetBranchStatus("nvtx", 1)
    for i, lep in enumerate(leps):
        lepTightId_branches.append(tree.Branch('%sTightIDSF' % lep, lepTightId_weights[i], '%sTightIDSF/F' % lep)) 
        lepMediumId_branches.append(tree.Branch('%sMediumIDSF' % lep, lepMediumId_weights[i], '%sMediumIDSF/F' % lep)) 
        tree.SetBranchStatus("%sPt" % lep, 1)
        tree.SetBranchStatus("%sEta" % lep, 1)
        tree.SetBranchStatus("%sTightIDSF" % lep, 1)
        tree.SetBranchStatus("%sTightIDSF" % lep, 1)
    for entry in range(tree.GetEntries()):
        tree.GetEntry(entry)
        for i, lep in enumerate(leps):
            pt = getattr(tree, "%sPt" % lep)
            absEta = abs(getattr(tree, "%sEta" % lep))
            #print "pt ", pt
            #print "abs(eta) ", absEta
            if "e" in lep:
                lepTightId_weights[i][0] = ROOT.electronTightIdSF(absEta, pt)
                lepMediumId_weights[i][0] = ROOT.electronMedIdSF(absEta, pt)
            else: 
                lepTightId_weights[i][0] = ROOT.muonTightIdSF(absEta, pt)
                lepMediumId_weights[i][0] = ROOT.muonMedIdSF(absEta, pt)
            print "In the var ", lepTightId_weights[i][0]
            print "For electrons ", ROOT.electronTightIdSF(absEta,pt)
            print "For muons ", ROOT.muonTightIdSF(absEta,pt)
            print "For muons iso", ROOT.muonTightIsoSF(absEta,pt)
            lepTightId_branches[i].Fill()
        pileup_weight[0] = ROOT.pileupSF(tree.nvtx)
        pileup_branch.Fill()
        if state == "eem":
            mTightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.mEta), tree.mPt)
            mTightIso_branch.Fill()
        elif state == "emm":
            m1TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m1Eta), tree.m1Pt)
            m1TightIso_branch.Fill()
            m2TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m2Eta), tree.m2Pt)
            m2TightIso_branch.Fill()
        elif state == "mmm":
            m1TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m1Eta), tree.m1Pt)
            m1TightIso_branch.Fill()
            m2TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m2Eta), tree.m2Pt)
            m2TightIso_branch.Fill()
            m3TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m3Eta), tree.m3Pt)
            m3TightIso_branch.Fill()
    tree.SetBranchStatus("*", 1)
    original_file.cd(state)
    tree.Write("", ROOT.TObject.kOverwrite)

ROOT.gROOT.LoadMacro("../../ScaleFactors/ScaleFactor.C+")
fScales = ROOT.TFile('../../ScaleFactors/scaleFactors.root')

pileupSF = fScales.Get('pileupSF')
muonTightIsoSF = fScales.Get('muonTightIsoSF')
muonTightIdSF = fScales.Get('muonTightIdSF')
muonMedIdSF = fScales.Get('muonMedIdSF')
electronTightIdSF = fScales.Get('electronTightIdSF')
electronMedIdSF = fScales.Get('electronMedIdSF')

pileupSF.RegisterGlobalFunction(1) #1D function
muonTightIsoSF.RegisterGlobalFunction(2) # 2D function
muonTightIdSF.RegisterGlobalFunction(2) # 2D function
muonMedIdSF.RegisterGlobalFunction(2) # 2D function
electronTightIdSF.RegisterGlobalFunction(2) # 2D function
electronMedIdSF.RegisterGlobalFunction(2) # 2D function

file_name = "finalselection_temp.root"
original_file = ROOT.TFile(file_name, "UPDATE")

states = ['eee', 'eem', 'emm', 'mmm']
for state in states:
    addWeightsForState(original_file, state)

