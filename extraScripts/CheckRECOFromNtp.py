import ROOT 
import pdb 
import json
import array
import math

with open('varsFile.json') as var_json_file:
    myvar_dict = json.load(var_json_file)

_binning = {}
for key in myvar_dict.keys(): #key is the variable
    if "Mass" in key and not "Full" in key:
        _binning[key] = myvar_dict["MassAllj"]["_binning"]
    else:
        _binning[key] = myvar_dict[key]["_binning"]
_binning["Mass"] = _binning["MassAllj"]

def rebin(hist,varName):
    ROOT.SetOwnership(hist, False)
    #No need to rebin certain variables but still might need overflow check
    if varName not in ['eta']:
        bins=array.array('d',_binning[varName])
        Nbins=len(bins)-1 
        hist=hist.Rebin(Nbins,hist.GetName()+"NoConfusion",bins)
    else:
        Nbins = hist.GetSize() - 2
    add_overflow = hist.GetBinContent(Nbins) + hist.GetBinContent(Nbins + 1)
    lastbin_error = math.sqrt(math.pow(hist.GetBinError(Nbins),2)+math.pow(hist.GetBinError(Nbins+1),2))
    hist.SetBinContent(Nbins, add_overflow)
    hist.SetBinError(Nbins, lastbin_error)
    hist.SetBinContent(Nbins+1,0)
    hist.SetBinError(Nbins+1,0)
    if not hist.GetSumw2(): hist.Sumw2()
    return hist

def listh(h): #return list
    
    list = [h.GetBinContent(i) for i in range(1,h.GetNbinsX()+1)]
    return list

def percentDiff(h1,h2):
    list = [abs(h1.GetBinContent(i)-h2.GetBinContent(i))/(h1.GetBinContent(i)+h2.GetBinContent(i))*2.*100. for i in range(1,h1.GetNbinsX()+1)]
    return list

def printr(l,ro):
    print([round(x,ro) for x in l])

#VFP = "preVFP"
legacy_datasets = ["ZZTo4L","GluGluToContinToZZTo4e","GluGluToContinToZZTo2e2mu","GluGluToContinToZZTo4mu"]
pre_datasets = ["zz4l-powheg","ggZZ4e","ggZZ2e2mu","ggZZ4m"]
xsecspre = [1.256*1.0835,0.001586*1.7,0.003194*1.7,0.001586*1.7]
xsecsUL = [1.325 *1.0835,1.6175/1000.*1.7,3.29188/1000.*1.7,1.59718/1000.*1.7]
checkgen = False
if checkgen:
    xsecsUL = xsecspre


#on-shell ZZ files
#fUL = ROOT.TFile("TreeFile_ZZSelector_Hists15Aug2023-ZZ4l2016_Moriondsel_Inclusive.root")
#fhUL = ROOT.TFile("Hists15Aug2023-ZZ4l2016_Moriond.root")

#Full mass range files
fUL = ROOT.TFile("TreeFile_ZZSelector_Hists16Aug2023-ZZ4l2016_Moriondsel_Inclusive.root")
fhUL = ROOT.TFile("Hists16Aug2023-ZZ4l2016_Moriond.root")

#fpre = ROOT.TFile("TreeFile_ZZSelector_Hists25Jul2023-ZZ4l2016_Moriondsel_Inclusive.root")
#fhpre = ROOT.TFile("CentralJet_Hists25Jul2023-ZZ4l2016_Moriond.root")
#varstr="nJets Mass mjj dEtajj jetPt[0] jetPt[1] absjetEta[0] absjetEta[1] Mass0j Mass1j Mass2j Mass3j Mass4j"
varstr="MassFull Mass0jFull Mass1jFull Mass2jFull Mass3jFull Mass4jFull"
vars = varstr.split(" ")
#vars = ["Mass","nJets","mjj"]
#vars = ["nJets"]
treetag = "_fTreeNtuple_"
channels = ["eeee","eemm","mmee","mmmm"]
#Using older lumi values since this is what is available in the table
lumitot = 36.33
lumi1 = 19.52
lumi2 = 16.81
hdict = {}
initBins = {}
weightExpr = "weight"
if checkgen:
    weightExpr = "genWeight"

#=========================================
initBins["nJets"] = "8,0,8"
initBins["Mass"] = "1215,70,2500"
initBins["Mass0j"] = "1215,70,2500"
initBins["Mass1j"] = "1215,70,2500"
initBins["Mass2j"] = "1215,70,2500"
initBins["Mass3j"] = "1215,70,2500"
initBins["Mass4j"] = "1215,70,2500"

initBins["MassFull"] = "1215,70,2500"
initBins["Mass0jFull"] = "1215,70,2500"
initBins["Mass1jFull"] = "1215,70,2500"
initBins["Mass2jFull"] = "1215,70,2500"
initBins["Mass3jFull"] = "1215,70,2500"
initBins["Mass4jFull"] = "1215,70,2500"

initBins["mjj"] = "60,0,1200"
initBins["dEtajj"] = "80,0,8"
initBins["jetPt[0]"] = "50,30,530"
initBins["jetPt[1]"] = "50,30,530"
initBins["absjetEta[0]"] = "50,0,5"
initBins["absjetEta[1]"] = "50,0,5"
#=========================================
for var in vars:
    print(var)
    hdict[var] = {}
    #For each channel form 3 histograms
    for chan in channels:
        hdict[var][chan] = []
        #print("Running channel: %s"%chan)
        histname = var+"_"+chan

        #Have to do this manually for now
        #hpre is the prelagacy histogram
     
        exec("hpre = ROOT.TH1D(histname,histname,%s)"%initBins[var] )

        hULFull = hpre.Clone(histname+"_ULFull")
        hULEcal = hpre.Clone(histname+"_ULEcal")
        
        #Fill all relevant MC datasets to the 3 histograms
        for i,h in enumerate([hpre,hULFull,hULEcal]):
            if i == 0:
                datasets = pre_datasets
                fin = fUL
                fh = fhUL
                xsecs = xsecspre
                #tag = ""
                additional = ""
                lumipairs = [(lumitot,"")]
            else:
                datasets = legacy_datasets
                fin = fUL
                fh = fhUL
                xsecs = xsecsUL
                #tag = VFP + ("L1Full" if i==1 else "L1ECAL")
                additional = ""
                lumipairs = [(lumi1,"preVFP"),(lumi2,"postVFP")]
                #additional = "/evt.L1prefiringWeight"

            for lumi,VFP in lumipairs:
                if i == 0:
                    tag = ""
                else:
                    tag = VFP + ("L1Full" if i==1 else "L1ECAL")

                for j,ds in enumerate(datasets):
                    treename = ds + tag + treetag + chan
                    foldername = ds + tag
                    tree = fin.Get(treename)
                    h_sumw = fh.Get(foldername+"/"+"sumweights")
                    sumweights = h_sumw.Integral(0,h_sumw.GetNbinsX()+1)
                    if not tree:
                        print("something wrong getting tree %s"%treename)
                    #pdb.set_trace()
                    for evt in tree:
                        varp = var.replace("[0]","0").replace("[1]","1")
                        
                        if "abs" in varp:
                            exec("h.Fill(abs(evt.%s),evt.%s*xsecs[j]*lumi*1000/sumweights%s)"%(varp.replace("abs",""),weightExpr,additional))
                        elif "Mass" in var and "j" in var:
                            tmp_nj = int(var.replace("Mass","").replace("j","").replace("Full","") )
                            if tmp_nj == 4:
                                if evt.nJets>=4:    
                                    exec("h.Fill(evt.Mass,evt.%s*xsecs[j]*lumi*1000/sumweights%s)"%(weightExpr,additional))
                            else:
                                if evt.nJets == tmp_nj:
                                    exec("h.Fill(evt.Mass,evt.%s*xsecs[j]*lumi*1000/sumweights%s)"%(weightExpr,additional))
                        else:
                            varp = varp.replace("Full","") #Full and on-shell variables aren't processed together
                            exec("h.Fill(evt.%s,evt.%s*xsecs[j]*lumi*1000/sumweights%s)"%(varp,weightExpr,additional))
            
            h = rebin(h,var)
            hdict[var][chan].append(h)
            #print(h.GetName())
            
            #print(listh(h))
    
    # Analyze results

    for k,h in enumerate(hdict[var]["eemm"]):
        h.Add(hdict[var]["mmee"][k])

    hdict[var]["total"] = []
    for k,h in enumerate(hdict[var]["eeee"]):
        htot = h.Clone(h.GetName().replace("eeee","Total"))
        htot.Add(hdict[var]["eemm"][k])
        htot.Add(hdict[var]["mmmm"][k])
        hdict[var]["total"].append(htot)

    for chan in channels+["total"]:
        if chan == "mmee":
            continue
        print(chan)
        perlist = percentDiff(hdict[var][chan][1],hdict[var][chan][2])
        print(perlist)
        for perc in perlist:
            if chan == "total" and perc>=3.:
                print("WARNING: >3 percent for one entry in total")
            
            if chan == "mmmm" and perc>=5.:
                print("WARNING: >5 percent for one entry in 4m")
        
        #print("Weighted events prelegacy and legacy for ECAL weight")
        #print(hdict[var][chan][0].Integral(1,hdict[var][chan][0].GetNbinsX()))
        #print(hdict[var][chan][2].Integral(1,hdict[var][chan][0].GetNbinsX()))
    
fout = ROOT.TFile("L1HistOutput.root","RECREATE")
fout.cd()
for var in vars:
    for chan in channels+["total"]:
        if chan == "mmee":
            continue
        for h in hdict[var][chan]:
            h.Write()
fout.Close()
print("All variables processed")
