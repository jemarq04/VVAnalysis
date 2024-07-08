import ROOT as r
import os
import pdb
import json
import subprocess
from optparse import OptionParser

lumitext = "36.3"

def getLumiTextBox():
    texS = r.TLatex(0.65,0.96, lumitext+" fb^{-1} (13 TeV)")
    texS.SetNDC()
    texS.SetTextFont(42)
    texS.SetTextSize(0.045)
    texS.SetTextColor(r.kBlack)
    texS.Draw()
    texS1 = r.TLatex(0.15,0.96,"#bf{CMS}")
    texS1.SetNDC()
    texS1.SetTextFont(42)
    texS1.SetTextColor(r.kBlack)
    texS1.SetTextSize(0.045)
    texS1.Draw()

    texS2 = r.TLatex(0.25,0.96,"Preliminary")
    texS2.SetNDC()
    texS2.SetTextFont(52)
    texS2.SetTextColor(r.kBlack)
    texS2.SetTextSize(0.045)
    texS2.Draw()

    return texS,texS1,texS2

def redrawXaxis(h,varName):
    
    if "Full" in varName and "Mass" in varName:
            xaxis = r.TGaxis(h.GetXaxis().GetXmin(),h.GetMinimum(),h.GetXaxis().GetXmax(),h.GetMinimum(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax(),510,"G")
        
            xaxis.SetMoreLogLabels(True)
            xaxis.SetTickLength(0.03)
            #xaxis.SetLabelSize(0.025)
            xaxis.ChangeLabel(1,-1,0.,-1,-1,-1,"")
    elif varName == "nJets":
        xaxis = r.TGaxis(h.GetXaxis().GetXmin(),h.GetMinimum(),h.GetXaxis().GetXmax(),h.GetMinimum(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax(),505)
        xaxis.CenterLabels(True)
        xaxis.ChangeLabel(4,-1,-1,-1,-1,-1,"#geq 3")
    else:
        xaxis = r.TGaxis(h.GetXaxis().GetXmin(),h.GetMinimum(),h.GetXaxis().GetXmax(),h.GetMinimum(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax(),510)
    xaxis.SetTitle(prettyVars[varName]+''+units[varName])
    xaxis.SetLabelFont(42)
    xaxis.SetLabelOffset(0.01)
    #xaxis.SetTickLength(0.1)
    if "Full" in varName and "Mass" in varName:
        xaxis.SetLabelSize(0.04)
    else:
        xaxis.SetLabelSize(0.04)
    xaxis.SetTitleFont(42)
    xaxis.SetTitleSize(0.05)
    xaxis.SetTitleOffset(0.9)
    #if varName=="mass":
    #    xaxis.SetNoExponent(True)
    xaxis.Draw("SAME")
    #pdb.set_trace()
    return xaxis


def titleAndRatio(t):
    tex = r.TLatex(0.4,0.9,t)
    tex.SetNDC()
    tex.SetTextFont(52)
    tex.SetTextColor(r.kBlue)
    tex.SetTextSize(0.035)
    tex.Draw()

    return tex #,rtex

def plotHist(h1,h2,h3,k1,k2,k3):
    h1.GetYaxis().SetTitle("Events")
    h1.GetYaxis().SetTitleOffset(1.1)

    h1.Draw("HIST")
    h2.Draw("HIST SAME")
    h3.Draw("HIST SAME")
    legend = r.TLegend (0.6 ,0.75 ,0.9 ,0.85)
    #legend = r.TLegend (0.5 ,0.9 ,0.9 ,1.2)
    legend.SetBorderSize(1)
    legend.SetFillColor(r.kWhite)
    #legend.SetBorderSize(2)
    legend.AddEntry(h1,k1,"l")
    legend.AddEntry(h2,k2,"l")
    legend.AddEntry(h3,k3,"l")
    legend.SetTextSize(0.03)
    #legend.SetLineWidth (0)
    legend.Draw("same")
    #portion = h2.Integral(1,h2.GetNbinsX())/h1.Integral(1,h1.GetNbinsX())
    return legend

def extraTex(x,y,tex):

    texf = r.TLatex(x,y,tex)
    texf.SetNDC()
    texf.SetTextFont(52)
    texf.SetTextColor(r.kBlack)
    texf.SetTextSize(0.03)
    texf.Draw()
    return texf

#varstr="nJets Mass mjj" #dEtajj jetPt[0] jetPt[1] absjetEta[0] absjetEta[1] MassAllj Mass0j Mass1j Mass2j Mass34j MassFull Mass0jFull Mass1jFull Mass2jFull Mass34jFull"
varstr="nJets Mass mjj dEtajj jetPt[0] jetPt[1] absjetEta[0] absjetEta[1] Mass0j Mass1j Mass2j Mass3j Mass4j"
vars = varstr.split(" ")

outdir = "2016L1Plots"
pdfcommand=['convert']
pdfcommand2=['convert']

if not os.path.isdir(outdir):
    os.mkdir(outdir)

with open('varsFile.json') as var_json_file:
    myvar_dict = json.load(var_json_file)
units = {}
prettyVars = {}
for key in list(myvar_dict.keys()): #key is the variable
    
    units[key] = myvar_dict[key]["units"]
    prettyVars[key] = myvar_dict[key]["prettyVars"]

units["Mass"] = units["MassAllj"]
prettyVars["Mass"] = prettyVars["MassAllj"]

fin = r.TFile("L1HistOutput.root")
channels = ["eeee","eemm","mmmm","total"]

r.gStyle.SetOptDate(False)
r.gStyle.SetOptStat(0)
canvas_dimensions = [600, 800]
c1 = r.TCanvas("c", "canvas",*canvas_dimensions)
c1.SetTopMargin(0.05)
c1.cd()

lineStyles = [1,2,3]
colors = [r.kOrange,r.kBlue,r.kRed]
for var in vars:
    for chan in channels:
        chanp = chan
        if chan == "total":
            chanp = "Total"
          
            
        h1,h2,h3 = fin.Get(var+"_"+chanp+"NoConfusion"),fin.Get(var+"_"+chanp+"_ULFullNoConfusion"),fin.Get(var+"_"+chanp+"_ULEcalNoConfusion")
        
        max1 = max(h1.GetMaximum(),h2.GetMaximum(),h3.GetMaximum())
        
        min1 = min(h1.GetMinimum(),h2.GetMinimum(),h3.GetMinimum(),0.)
        
        maxfac = 1.2
        if var=="Mass34jFull":
            maxfac = 1.5
        for i,h in enumerate([h1,h2,h3]):
            h.SetMaximum(maxfac*max1)
            h.SetMinimum(min1)
          
            h.SetLineStyle(lineStyles[i])
            h.SetLineColor(colors[i])
            h.GetXaxis().SetLabelSize(0)
            h.GetXaxis().SetTickLength(0)
            h.SetLineWidth(4*h.GetLineWidth())

              
        #c1.Divide(2,1)

        c1.cd()
        if "Full" in var:
            r.gPad.SetLogx()
        else:
            r.gPad.SetLogx(0)  

        legend1 = plotHist(h1,h2,h3,"Prelegacy","UL L1Full","UL L1ECAL")
        t1,t2,t3 = getLumiTextBox()
        tex1= titleAndRatio("RECO Events %s"%chanp)
        xa1 = redrawXaxis(h1,var)

        if "Full" in var:
            texf = extraTex(0.65,0.68,"Full mass range")
            #texEty = extraTex(0.65,0.6,str(hR.GetEntries()))
        elif "Mass" in var:
            texf = extraTex(0.65,0.68,"On-shell ZZ")
            if "j" in var:
                tmp_nj = int(var.replace("Mass","").replace("j",""))
                geq = ""
                if tmp_nj ==4:
                    geq = "#geq"
                texf2 = extraTex(0.65,0.5,"Events with %s%s jet(s)"%(geq,tmp_nj))
        if "[0]" in var:
            texf = extraTex(0.65,0.68,"Events with #geq 1 jet")    
        if "[1]" in var:
            texf = extraTex(0.65,0.68,"Events with #geq 2 jets")   

       
        c1.SaveAs(os.path.join(outdir,"%s_%s.png"%(var,chan)))

        if chan == "total":
            pdfcommand.append(os.path.join(outdir,"%s_%s.png"%(var,chan)))
        #else:
        #    pdfcommand2.append(os.path.join(outdir,"%s_%s.png"%(var,chan)))

        c1.Clear()

pdfcommand.append(os.path.join("./","2016L1.pdf"))  
subprocess.call(pdfcommand)

