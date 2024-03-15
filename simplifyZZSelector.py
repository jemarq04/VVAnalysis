import string,os,sys,pdb

#Overwrite: If true, the filled template file will be copied and overwrite the respective Selector.cc file
overwrite = False

def listToStr(list):
#Do something like ['a','b','c'] -> "{\"a\",\"b\",\"c\"}"
    empty = ""
    for i, st in enumerate(list):
        if i< len(list)-1:
            empty += '\"'+st+'\",'
        else:
            empty += '\"'+st+'\"'
    
    return '{%s}'%empty


dict = {}
ldict = {}
mapdict = {}
odict = {}

writeNtuple = True
baseList = ["yield", "Mass", "MassFull", "nJets", "jetPt[1]", "jetPt[0]", "jetEta[0]", "jetEta[1]", "absjetEta[0]", "absjetEta[1]", "mjj", "dEtajj", "Mass0j", "Mass1j", "Mass2j", "Mass3j", "Mass34j", "Mass4j", "Mass0jFull", "Mass1jFull", "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull"]
baseList2 = baseList[1:]
testList = ["yield", "Mass"]
testList2 = testList[1:]

#baseList = testList
#baseList2 = testList2

systHist_Ori= [
      "yield",
      "Mass",
      "MassFull",
      "nJets",
      "jetPt[1]",
      "jetPt[0]",
      "jetEta[0]",
      "jetEta[1]",
      "absjetEta[0]",
      "absjetEta[1]",
      "mjj",
      "dEtajj",
      "Mass0j",
      "Mass1j",
      "Mass2j",
      "Mass3j",
      "Mass34j",
      "Mass4j",
      "Mass0jFull",
      "Mass1jFull",
      "Mass2jFull",
      "Mass3jFull",
      "Mass34jFull",
      "Mass4jFull",
      "ZMass",
      "ZZPt",
      "ZZEta",
      "dPhiZ1Z2",
      "dRZ1Z2",
      "ZPt",
      "LepPt",
      "LepEta"]

systHistList = baseList
#systHistList = ["yield", "Mass", "MassFull", "nJets", "jetPt[1]", "jetPt[0]", "jetEta[0]", "jetEta[1]", "absjetEta[0]", "absjetEta[1]", "mjj", "dEtajj", 
#"Mass0j", "Mass1j", "Mass2j", "Mass3j", "Mass34j", "Mass4j", "Mass0jFull", "Mass1jFull", "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull"]


hist1D_Ori =[
      "yield", "Z1Mass", "Z2Mass", "ZMass", "ZZPt", "ZZEta", "dPhiZ1Z2", "dRZ1Z2", "ZPt", "LepPt", "LepPtFull", "LepEta", "PassTriggerFull",
      "LepPt1", "LepPt2", "LepPt3", "LepPt4", "LepPt1Full", "LepPt2Full", "LepPt3Full", "LepPt4Full", "e1PtSortedFull", "e2PtSortedFull", "e1PtSorted", "e2PtSorted",
      "Mass", "Mass0j", "Mass1j", "Mass2j", "Mass3j", "Mass34j", "Mass4j", "nJets",
      "MassFull", "Mass0jFull", "Mass1jFull", "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull",
      "jetPt[0]", "jetPt[1]", "jetPt[2]", "jetEta[0]", "jetEta[1]", "absjetEta[0]", "absjetEta[1]", "jetEta[2]",
      "jetPhi[0]", "jetPhi[1]", "jetPhi[2]", "mjj", "dEtajj", "SIP3D", "jetPt[01]", "jetEta[01]",
      "jetEtaAllj", "absjetEtaAllj", "jetEtaAllj50", "absjetEtaAllj50", "jetEtaAllj_120", "absjetEtaAllj_120", "jetEtaAllj50_120", "absjetEtaAllj50_120",
      "jetEtaAllj_180", "absjetEtaAllj_180", "jetEtaAllj50_180", "absjetEtaAllj50_180",
      "absjetEtaN1", "jetPtN1", "jetPtN2", "jetPtN3", "absjetEtaN1_100", "jetHEM_AB", "jetHEM_CD", "jetHEM2_AB", "jetHEM2_CD",
      "PVDZ", "deltaPVDZ_sameZ", "deltaPVDZ_diffZ"]

#hists1DList = baseList
hists1DList = [
      "yield", "Z1Mass", "Z2Mass", "ZMass", "ZZPt", "ZZEta", "dPhiZ1Z2", "dRZ1Z2", "ZPt", "LepPt", "LepPtFull", "LepEta", "PassTriggerFull",
      "LepPt1", "LepPt2", "LepPt3", "LepPt4", "LepPt1Full", "LepPt2Full", "LepPt3Full", "LepPt4Full", "e1PtSortedFull", "e2PtSortedFull", "e1PtSorted", "e2PtSorted",
      "Mass", "nJets", "MassFull", "SIP3D", "PVDZ", "deltaPVDZ_sameZ", "deltaPVDZ_diffZ"
]
#hists1DList = [ "yield", "Mass", "Mass0j", "Mass1j", "Mass2j", "Mass3j", "Mass34j", "Mass4j", "nJets", "MassFull", "Mass0jFull", "Mass1jFull", "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull", "jetPt[0]", "jetPt[1]","jetEta[0]", "jetEta[1]", "absjetEta[0]", "absjetEta[1]", "mjj", "dEtajj" ]

jetTest2D_Ori = ["jetPtN1", "jetPtN2", "jetPtN3", "jetHEM_AB", "jetHEM_CD", "jetHEM2_AB", "jetHEM2_CD"]
jetTest2DList = []

jethists1D_Ori = [
      "Mass",
      "Mass0j",
      "Mass1j",
      "Mass2j",
      "Mass3j",
      "Mass34j",
      "Mass4j",
      "MassFull",
      "Mass0jFull",
      "Mass1jFull",
      "Mass2jFull",
      "Mass3jFull",
      "Mass34jFull",
      "Mass4jFull",
      "nJets",
      "jetPt[0]",
      "jetPt[1]",
      "jetEta[0]",
      "jetEta[1]",
      "absjetEta[0]",
      "absjetEta[1]",
      "mjj",
      "dEtajj",
  ]
jethists1DList = baseList2

weighthists1D_Ori = [
      "yield",
      "Mass",
      "MassFull",
      "ZMass",
      "ZZPt",
      "ZZEta",
      "dPhiZ1Z2",
      "dRZ1Z2",
      "ZPt",
      "LepPt",
      "LepEta",
      "nJets",
      "jetPt[1]",
      "jetPt[0]",
      "jetEta[0]",
      "jetEta[1]",
      "absjetEta[0]",
      "absjetEta[1]",
      "mjj",
      "dEtajj",
      "Mass0j",
      "Mass1j",
      "Mass2j",
      "Mass3j",
      "Mass34j",
      "Mass4j",
      "Mass0jFull",
      "Mass1jFull",
      "Mass2jFull",
      "Mass3jFull",
      "Mass34jFull",
      "Mass4jFull"]

weighthists1DList = baseList
#weighthists1DList = ["yield", "Mass", "MassFull", "nJets", "jetPt[1]", "jetPt[0]", "jetEta[0]", "jetEta[1]", "absjetEta[0]", "absjetEta[1]", "mjj", "dEtajj", "Mass0j", "Mass1j", "Mass2j", "Mass3j", "Mass34j", "Mass4j", "Mass0jFull", "Mass1jFull", "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull"]

dict["systHists"] = listToStr(systHistList)
dict["hists1D"] = listToStr(hists1DList)
dict["jetTest2D"] = listToStr(jetTest2DList)
dict["jethists1D"] = listToStr(jethists1DList)
dict["weighthists1D"] = listToStr(weighthists1DList)

#systHists used in Selector code to check whether need to do syst, so hists1D enough to contain the list for purpose here
#ldict["systHists"] = systHistList

odict["hists1D"] = hist1D_Ori
odict["jetTest2D"] = jetTest2D_Ori
odict["jethists1D"] = jethists1D_Ori
odict["weighthists1D"] = weighthists1D_Ori

ldict["hists1D"] = hists1DList
ldict["jetTest2D"] = jetTest2DList
ldict["jethists1D"] = jethists1DList
ldict["weighthists1D"] = weighthists1DList

#mapdict["systHists"] = 
mapdict["hists1D"] = "histMap1D_"
mapdict["jetTest2D"] = "jetTestMap2D_"
mapdict["jethists1D"] = "jethistMap1D_"
mapdict["weighthists1D"] = "weighthistMap1D_"

ft = open("src/ZZSelector.template","r")
template = string.Template(ft.read())
output = template.substitute(dict)
with open("src/ZZSelectorTemplateFilledTmp.cc","w") as fout:
    fout.write(output)

with open("src/ZZSelectorTemplateFilledTmp.cc","r") as fout2:
    with open("src/ZZSelectorFilled.template","w") as foutf:
        for line in fout2:

            #For suppressing not used variables warning in compiling
            if not writeNtuple:
                if "//Begin filling ntuple" in line:
                    line = "/*" + line
                elif "//End filling ntuple" in line:
                    line = line + "*/\n"

            if not "LepPtFull" in hists1DList:
                if "// sort lepton pt" in line:
                    line = "/*" + line
                
                if "//finish sorting lepton pt" in line:
                    line = line + "*/" + "\n"

            if not "\n" in line:
                print("Line doesn't contain \\n")
                line+= "\n"

            if "SafeHistFill" in line:
                for key in mapdict.keys():
                    if mapdict[key] in line:
                        for item in odict[key]:
                            if item in line and line.find(item) < line.find("variation") and not item in ldict[key]:
                                if not "//" in line or line.find("//") > line.find("SafeHistFill"):
                                    line = "//" + line
            
            
            foutf.write(line)

print("src/ZZSelectorFilled.template produced")
os.remove("src/ZZSelectorTemplateFilledTmp.cc")


#Gen Selector
Gendict = {}
Genldict = {}
Genodict = {}
Genmapdict = {}

GenbaseList = ["Gen"+li for li in baseList]
GenbaseList2 = ["Gen"+li for li in baseList2]

Genhists1D_Ori = [
      "GenMass",
      "GenMass0j",
      "GenMass1j",
      "GenMass2j",
      "GenMass3j",
      "GenMass34j",
      "GenMass4j",
      "GenMassFull",
      "GenMass0jFull",
      "GenMass1jFull",
      "GenMass2jFull",
      "GenMass3jFull",
      "GenMass34jFull",
      "GenMass4jFull",
      "Genmjj",
      "GennJets",
      "Genyield",
      "GenZMass",
      "GenZZPt",
      "GenZZEta",
      "GenZPt",
      "GendPhiZ1Z2",
      "GendRZ1Z2",
      "GenLepPt",
      "GenLepEta",
      "GenjetPt[0]",
      "GenjetPt[1]",
      "GenjetEta[0]",
      "GenjetEta[1]",
      "GenabsjetEta[0]",
      "GenabsjetEta[1]",
      "GendEtajj",
]


Genodict["Genhists1D"] = Genhists1D_Ori
Genldict["Genhists1D"] = GenbaseList
Gendict["Genhists1D"] = listToStr(Genldict["Genhists1D"])

Genweighthists1D_Ori = [
      "Genyield",
      "GenMass",
      "GenMassFull",
      "GenZMass",
      "GenZZPt",
      "GenZZEta",
      "GendPhiZ1Z2",
      "GendRZ1Z2",
      "GenZPt",
      "GenLepPt",
      "GenLepEta",
      "GennJets",
      "GenjetPt[1]",
      "GenjetPt[0]",
      "GenjetEta[0]",
      "GenjetEta[1]",
      "GenabsjetEta[0]",
      "GenabsjetEta[1]",
      "Genmjj",
      "GendEtajj",
      "GenMass0j",
      "GenMass1j",
      "GenMass2j",
      "GenMass3j",
      "GenMass34j",
      "GenMass4j",
      "GenMass0jFull",
      "GenMass1jFull",
      "GenMass2jFull",
      "GenMass3jFull",
      "GenMass34jFull",
      "GenMass4jFull"]

Genodict["Genweighthists1D"] = Genweighthists1D_Ori
Genldict["Genweighthists1D"] = GenbaseList
Gendict["Genweighthists1D"] = listToStr(Genldict["Genweighthists1D"])

Genmapdict["Genhists1D"] = "histMap1D_"
Genmapdict["Genweighthists1D"] = "weighthistMap1D_"

ft2 = open("src/ZZGenSelector.template","r")
template2 = string.Template(ft2.read())
output2 = template2.substitute(Gendict)
with open("src/ZZGenSelectorTemplateFilledTmp.cc","w") as foutGen:
    foutGen.write(output2)

with open("src/ZZGenSelectorTemplateFilledTmp.cc","r") as fout2Gen:
    with open("src/ZZGenSelectorFilled.template","w") as foutfGen:
        for line in fout2Gen:

            if not writeNtuple:
                if "//Begin filling ntuple" in line:
                    line = "/*" + line
                elif "//End filling ntuple" in line:
                    line = line + "*/\n"
            #For suppressing not used variables warning in compiling
            #if not "LepPtFull" in hists1DList:
            #    if "// sort lepton pt" in line:
            #        line = "/*" + line
            #    
            #    if "//finish sorting lepton pt" in line:
            #        line = line + "*/" + "\n"

            if not "\n" in line:
                print("Line doesn't contain \\n")
                line+= "\n"

            if "SafeHistFill" in line:
                for key in Genmapdict.keys():
                    if Genmapdict[key] in line:
                        for item in Genodict[key]:
                            if item in line and line.find(item) < line.find("variation") and not item in Genldict[key]:
                                if not "//" in line or line.find("//") > line.find("SafeHistFill"):
                                    line = "//" + line
            
            
            foutfGen.write(line)

print("src/ZZGenSelectorFilled.template produced")
os.remove("src/ZZGenSelectorTemplateFilledTmp.cc")

if overwrite:
    os.system("cp src/ZZSelectorFilled.template src/ZZSelector.cc")
    os.system("cp src/ZZGenSelectorFilled.template src/ZZGenSelector.cc")
    print("Copied filled template to source codes")
