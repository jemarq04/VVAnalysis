#!/usr/bin/env python
import ROOT
import glob
import math
import gdb_debugger
from python import SelectorTools
from python import UserInput
from python import OutputTools
from python import ConfigureJobs
from python import HistTools
import makeSimpleHtml
from PlotTools import PlotStyle as Style, pdfViaTex
from PlotTools import makeLegend, addPadsBelow, makeRatio, fixRatioAxes
import os
import sys,pdb
import datetime
import array
from ROOT import vector as Vec
VFloat = Vec('float')

#pdb.set_trace()
style = Style()
ROOT.gStyle.SetLineScalePS(1.8)

channels = ["eeee","eemm","mmmm"]
#channels = ["eeee"]
def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float,
        default=41.5, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str,
        default="", help="Output file name")
    parser.add_argument("--test", action='store_true',
        help="Run test job (no background estimate)")
    parser.add_argument("--uwvv", action='store_true',
        help="Use UWVV format ntuples in stead of NanoAOD")
    parser.add_argument("--with_background", action='store_true',
        help="Don't run background selector")
    parser.add_argument("--noHistConfig", action='store_true',
        help="Don't rely on config file to specify hist info")
    parser.add_argument("-j", "--numCores", type=int, default=1,
        help="Number of cores to use (parallelize by dataset)")
    parser.add_argument("--input_tier", type=str,
        default="", help="Selection stage of input files")
    parser.add_argument("--year", type=str,
        default="default", help="Year of Analysis")
    parser.add_argument("-c", "--channels",
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["eee","eem","emm","mmm"], help="List of channels"
                        "separated by commas. NOTE: set to Inclusive for NanoAOD")
    parser.add_argument("--scalefactors_file", "-sf", type=str,
        default="", help="ScaleFactors file name")
    parser.add_argument("--leptonSelections", "-ls", type=str,
        default="TightLeptons", help="Either All Loose or Tight")
    parser.add_argument("--output_selection", type=str,
        default="", help="Selection stage of output file "
        "(Same as input if not give)")
    parser.add_argument("-b", "--hist_names",
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["all"], help="List of histograms, "
                        "as defined in ZZ4lRun2DatasetManager, separated "
                        "by commas")
    parser.add_argument("--variable", "-vr", type=str,
        default="all", help="variableName")
    parser.add_argument('--noNorm', action='store_true',
                        help='Leave differential cross sections in abolute normalization rather than normalizing to unity area.')
    parser.add_argument('--NormFb', action='store_true',
                        help='Normalize differential cross sections to the luminosity')
    parser.add_argument('--plotResponse', action='store_true',
                        help='plot Response Matrices and covariance matrices.')
    parser.add_argument('--plotSystResponse', action='store_true',
                        help='plotResponse Matrices varied up or down with systematics.')
    parser.add_argument('--makeTotals', action='store_true',
                        help='plot total unfolded with uncertainities.')
    parser.add_argument('--noSyst', action='store_true',
                        help='No Systematics calculations.')
    parser.add_argument('--logy', '--logY', '--log', action='store_true',
                        help='Put vertical axis on a log scale.')
    parser.add_argument('--plotDir', type=str, nargs='?',
                        default='/afs/cern.ch/user/h/hehe/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/AltTest2_NoOverflow_RespMat_Moriond2019IDMuSF_Oct13_notZZjj',
                        help='Directory to put response and covariance plots in')
    parser.add_argument('--unfoldDir', type=str, nargs='?',
                        default='/afs/cern.ch/user/h/hehe/www/ZZFullRun2/PlottingResults/ZZ4l2016/ZZSelectionsTightLeps/ANPlots/ZZ4l2016/AltTest2_LogDiff_Oct13_inverted__not_ZZjj',
                        help='Directory to put response and covariance plots in')
    parser.add_argument('--nIter', type=int, nargs='?', default=4,
                        help='Number of iterations for D\'Agostini method')
    return vars(parser.parse_args())

args = getComLineArgs()
pdb.set_trace()
manager_path = ConfigureJobs.getManagerPath()
selection = args['selection']
if selection == "":
    selection = "LooseLeptons"
    print("Info: Using BasicZZSelections for hist defintions")
#analysis = "/".join([args['analysis'], selection])
analysis=args['analysis']
_binning = {
    'pt' : [25.*i for i in range(4)] + [100., 150., 200., 300.],
    'jetPt0':[30.,70.,110.,150.,190.,230.,270.,310.,350.,390.,430.],
    #'mass' : [100.+100.*i for i in range(12)],
    'mass' : [100.] + [200.+50.*i for i in range(5)] + [500.,600.,800.],
    'massFull' : [80.,100.,120.,130.,150.,180.,200.,240.,300.,400.,1000],
    'eta' : [6,0.,6.],
    'zmass' : [60., 80., 84., 86.] + [87.+i for i in range(10)] + [98., 102., 120.], #[12, 60., 120.],
    'z1mass' : [60., 80., 84., 86.] + [87.+i for i in range(10)] + [98., 102., 120.], #[12, 60., 120.],
    'z2mass' : [60., 75., 83.] + [84.+i for i in range(14)] + [105., 120.],#[12, 60., 120.],
    'z1pt' : [i * 25. for i in range(7)] + [200., 300.],
    'z2pt' : [i * 25. for i in range(7)] + [200., 300.],
    'zpt' : [i * 25. for i in range(7)] + [200., 300.],
    'zHigherPt' : [i * 25. for i in range(7)] + [200., 300.],
    'zLowerPt' : [i * 25. for i in range(7)] + [200., 300.],
    'leppt' : [i * 15. for i in range(11)],
    'l1Pt' : [0.,15.,30.,40.,50.]+[60.+15.*i for i in range(9)]+[195.,225.],#[14,0.,210.],#[15, 0., 150.],
    'dphiz1z2': [0.,1.5,2.0,2.25,2.5,2.75,3.0,3.25],
    'drz1z2': [0.,1.0,2.0,3.0,4.0,5.0,6.0]
    }

units = {
    'pt' : '[GeV]',
    'jetPt0' : '[GeV]',
    'mass' : '[GeV]',
    'massFull' : '[GeV]',
    'eta' : '',
    'zmass' : '[GeV]',
    'z1mass' : '[GeV]',
    'z2mass' : '[GeV]',
    'zpt' : '[GeV]',
    'z1pt' : '[GeV]',
    'z2pt' : '[GeV]',
    'zHigherPt' : '[GeV]',
    'zLowerPt' : '[GeV]',
    'leppt' : '[GeV]',
    'l1Pt' : '[GeV]',
    'dphiz1z2': '',
    'drz1z2':'',
    }

yaxisunits = {
    'pt' : 'GeV',
    'jetPt0' : 'GeV',
    'mass' : 'GeV',
    'massFull' : 'GeV',
    'eta' : '',
    'zmass' : 'GeV',
    'z1mass' : 'GeV',
    'z2mass' : 'GeV',
    'zpt' : 'GeV',
    'z1pt' : 'GeV',
    'z2pt' : 'GeV',
    'zHigherPt' : 'GeV',
    'zLowerPt' : 'GeV',
    'leppt' : 'GeV',
    'l1Pt' : 'GeV',
    'dphiz1z2': '',
    'drz1z2':'',
    }

prettyVars = {
    'pt' : 'p_{T}^{4\\ell}',
    'jetPt0' : 'jetPt0',
    'mass' : 'm_{4\\ell}',
    'massFull' : 'm_{4\\ell}',
    'eta' : '\\eta_{4\\ell}',
    'zmass' : 'm_{Z}',
    'z1mass' : 'm_{Z_{1}}',
    'z2mass' : 'm_{Z_{2}}',
    'z1pt' : 'p_{T}^{Z_{1}}',
    'z2pt' : 'p_{T}^{Z_{2}}',
    'zpt' : 'p_{T}^{Z}',
    'zHigherPt' : 'p_\\text{T}^{\\text{Z}_{\\text{lead}}}',
    'zLowerPt' : 'p_\\text{T}^{\\text{Z}_{\\text{sublead}}}',
    'leppt' : 'p_{T}^{\\ell}',
    'l1Pt' : 'p_\\text{T}^{\\ell_1}',
    'dphiz1z2': '\\Delta\\phi_{Z_{1},Z_{2}}',
    'drz1z2':'\\Delta\\text{R}_{Z_{1},Z_{2}}}',
    }

_xTitle = {}
_yTitle = {}
_yTitleNoNorm = {}

_yTitleTemp = '{prefix} \\frac{{d\\sigma_{{\\text{{fid}}}}}}{{d{xvar}}} {units}'
for var, prettyVar in prettyVars.iteritems():
    xt = prettyVar
    if yaxisunits[var]:
        xt += ' \\, \\left(\\text{{{}}}\\right)'.format(yaxisunits[var])
        yt = _yTitleTemp.format(xvar=prettyVar,
                                prefix='\\frac{1}{\\sigma_{\\text{fid}}}',
                                units='\\, \\left( \\frac{{1}}{{\\text{{{unit}}}}} \\right)'.format(unit=yaxisunits[var]))
        ytnn = _yTitleTemp.format(xvar=prettyVar, prefix='',
                                  units='\\, \\left( \\frac{{\\text{{fb}}}}{{\\text{{{unit}}}}} \\right)'.format(unit=yaxisunits[var]))
    else:
        yt = _yTitleTemp.format(prefix='\\frac{1}{\\sigma_{\\text{fid}}}',
                                xvar=prettyVar, units='')
        ytnn = _yTitleTemp.format(prefix='', xvar=prettyVar, units='\\left( \\text{fb} \\right)')

    _xTitle[var] = xt
    _yTitle[var] = yt
    _yTitleNoNorm[var] = ytnn

# Names of compiled C++ classes to make response matrices fast
# (this is extremely slow in Python because it requires a combination of
# information from multiple trees, which can't be done with TTree::Draw())
responseClassNames = {
    'mass' : {c:'FloatBranchResponseMatrixMaker' for c in channels},
    'jetPt0' : {c:'testJet' for c in channels},
    #'massFull' : {c:'FullSpectrumFloatResponseMatrixMaker' for c in channels},
    'pt' : {c:'FloatBranchResponseMatrixMaker' for c in channels},
    'eta' : {c:'AbsFloatBranchResponseMatrixMaker' for c in channels},
    'z1mass' : {'eeee':'FloatBranchResponseMatrixMaker',
                'mmmm':'FloatBranchResponseMatrixMaker',
                'eemm':'Z1ByMassResponseMatrixMaker',},
    'z2mass' : {'eeee':'FloatBranchResponseMatrixMaker',
                'mmmm':'FloatBranchResponseMatrixMaker',
                'eemm':'Z2ByMassResponseMatrixMaker',},
    'z1pt' : {'eeee':'FloatBranchResponseMatrixMaker',
              'mmmm':'FloatBranchResponseMatrixMaker',
              'eemm':'Z1ByMassResponseMatrixMaker',},
    'z2pt' : {'eeee':'FloatBranchResponseMatrixMaker',
              'mmmm':'FloatBranchResponseMatrixMaker',
              'eemm':'Z2ByMassResponseMatrixMaker',},
    #'zHigherPt' : {c:'Z1ByPtResponseMatrixMaker' for c in channels},
    #'zLowerPt' : {c:'Z2ByPtResponseMatrixMaker' for c in channels},
    'leppt' : {c:'AllLeptonBranchResponseMatrixMaker' for c in channels},
    #'l1Pt' : {c:'LeptonMaxBranchResponseMatrixMaker' for c in channels},
    'zpt' : {c:'BothZsBranchResponseMatrixMaker' for c in channels},
    'zmass' : {c:'BothZsBranchResponseMatrixMaker' for c in channels},
    'dphiz1z2':{c:'ZZAbsDeltaPhiResponseMatrixMaker' for c in channels},
    'drz1z2':{c:'ZZDeltaRResponseMatrixMaker' for c in channels},
    }

# Variable names usable by response maker classes
varNamesForResponseMaker = {
    'mass' : {c:'Mass' for c in channels},
    'jetPt0' : {c:'jetPt0' for c in channels},
    #'massFull' : {c:'Mass' for c in channels},
    'pt' : {c:'Pt' for c in channels},
    'eta' : {c:'Eta' for c in channels},
    'z1mass' : {'eeee':'e1_e2_Mass','mmmm':'m1_m2_Mass','eemm':'Mass'}, # 4e/4mu just use 1 variable because that's easy
    'z2mass' : {'eeee':'e3_e4_Mass','mmmm':'m3_m4_Mass','eemm':'Mass'}, # for 2e2mu, the response maker class will figure it out
    'z1pt' : {'eeee':'e1_e2_Pt','mmmm':'m1_m2_Pt','eemm':'Pt'}, # 4e/4mu just use 1 variable because that's easy
    'z2pt' : {'eeee':'e3_e4_Pt','mmmm':'m3_m4_Pt','eemm':'Pt'}, # for 2e2mu, the response maker class will figure it out
    'zpt' : {c:'Pt' for c in channels},
    'zmass' : {c:'Mass' for c in channels},
    #'zHigherPt' : {c:'Pt' for c in channels},
    #'zLowerPt' : {c:'Pt' for c in channels},
    'leppt' : {c:'Pt' for c in channels},
    #'l1Pt' : {c:'Pt' for c in channels},
    #'zPt' : {c:'Pt' for c in channels},
    'dphiz1z2': {c:'' for c in channels}, #variable names already set in ResponseMatrix.cxx
    'drz1z2': {c:'' for c in channels},
}

# list of variables not counting systematic shifts
varList=['Mass','ZZPt','ZPt','LepPt','dPhiZ1Z2','dRZ1Z2','jetPt[0]']

# Sometimes need to more or resize legend
legDefaults = {
    'textsize' : 0.034, #.027,#2,
    'leftmargin' : 0.35,
    'entryheight' : 0.037,
    'rightmargin' : 0.03,
    }
legParams = {v.lower():legDefaults.copy() for v in varList}
legParams['z1mass'] = {
    'textsize' : .026,
    'leftmargin' : .03,
    'rightmargin' : .46,
    'entryheight' : .034,#23
    'entrysep' : .007,
    }
legParams['pt'] = legParams['zzpt'].copy()
legParams['zmass'] = legParams['z1mass'].copy()
legParams['z2mass'] = legParams['z1mass'].copy()
legParams['deltaEtajj'] = legParams['z1mass'].copy()
legParams['deltaEtajj']['leftmargin'] = .5
legParams['deltaEtajj']['rightmargin'] = .03
legParams['deltaEtajj']['topmargin'] = .05
legParams['eta'] = legParams['deltaEtajj'].copy()
#legParams['massFull']['leftmargin'] = 0.25

legParamsLogy = {v:p.copy() for v,p in legParams.iteritems()}
#legParamsLogy['l1Pt']['topmargin'] = 0.65
#legParamsLogy['l1Pt']['leftmargin'] = 0.2
#legParamsLogy['l1Pt']['rightmargin'] = 0.18
legParamsLogy['mass']['topmargin'] = 0.075
legParamsLogy['mass']['leftmargin'] = 0.35
legParamsLogy['mass']['rightmargin'] = 0.025
legParamsLogy['mass']['textsize'] = 0.033
legParamsLogy['leppt']['topmargin'] = 0.05
#legParamsLogy['zHigherPt']['topmargin'] = 0.045
#legParamsLogy['massFull']['topmargin'] = 0.035

def normalizeBins(h):
    binUnit = 1 # min(h.GetBinWidth(b) for b in range(1,len(h)+1))
    for ib in range(1,h.GetNbinsX()+1):
        w = h.GetBinWidth(ib)
        h.SetBinContent(ib, h.GetBinContent(ib) * binUnit / w)
        h.SetBinError(ib, h.GetBinError(ib) * binUnit / w)
        if h.GetBinError(ib) > h.GetBinContent(ib):
            h.SetBinError(ib, h.GetBinContent(ib))
    h.Sumw2()

def unnormalizeBins(h):
    binUnit = 1 # min(h.GetBinWidth(b) for b in range(1,len(h)+1))
    for ib in range(1,h.GetNbinsX()+1):
        w = h.GetBinWidth(ib)
        h.SetBinContent(ib, h.GetBinContent(ib) * w / binUnit)
        h.SetBinError(ib, h.GetBinError(ib) * w / binUnit)
        if h.GetBinError(ib) > h.GetBinContent(ib):
            h.SetBinError(ib, h.GetBinContent(ib))
    h.Sumw2()

def createRatio(h1, h2):
    Nbins = h1.GetNbinsX()
    Ratio = h1.Clone("Ratio")
    hStackLast = h2.Clone("hStackLast")
    try:
        Ratio.Sumw2()
    except AttributeError:
        pass
    try:
        hStackLast.Sumw2()
    except AttributeError:
        pass
    for i in range(1,Nbins+1):
        stackcontent = hStackLast.GetBinContent(i)
        stackerror = hStackLast.GetBinError(i)
        datacontent = h1.GetBinContent(i)
        dataerror = h1.GetBinError(i)
        print("stackcontent: ",stackcontent," and data content: ",datacontent)
        ratiocontent=0
        if(datacontent!=0):
            ratiocontent = datacontent/stackcontent
        if(datacontent!=0):
            error = ratiocontent*(math.sqrt(math.pow((dataerror/datacontent),2) + math.pow((stackerror/stackcontent),2)))
        else:
            error = 2.07
        print("ratio content: ",ratiocontent)
        print("stat error: ", error)
        Ratio.SetBinContent(i,ratiocontent)
        Ratio.SetBinError(i,error)

    Ratio.GetYaxis().SetRangeUser(0.4,1.8)
    Ratio.SetStats(0)
    Ratio.GetYaxis().CenterTitle()
    Ratio.SetMarkerStyle(20)
    Ratio.SetMarkerSize(0.7)

    line = ROOT.TLine(h1.GetXaxis().GetXmin(), 1.,h1.GetXaxis().GetXmax(), 1.)
    line.SetLineStyle(7)

    Ratio.GetYaxis().SetLabelSize(0.14)
    Ratio.GetYaxis().SetTitleSize(0.12)
    Ratio.GetYaxis().SetLabelFont(42)
    Ratio.GetYaxis().SetTitleFont(42)
    Ratio.GetYaxis().SetTitleOffset(0.25)
    Ratio.GetYaxis().SetNdivisions(100)
    Ratio.GetYaxis().SetTickLength(0.05)

    Ratio.GetXaxis().SetLabelSize(0)
    Ratio.GetXaxis().SetTitleSize(0)
    #Ratio.GetXaxis().SetLabelFont(42)
    #Ratio.GetXaxis().SetTitleFont(42)
    #Ratio.GetXaxis().SetTitleOffset(0.90)
    #Ratio.GetXaxis().SetTickLength(0.05)
    #Ratio.Draw("pex0")
    #line.SetLineColor(kBlack)
    #line.Draw("same");

    return Ratio,line

def createCanvasPads():
    c = ROOT.TCanvas("c", "canvas")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLegendBorderSize(0)
    # Upper histogram plot is pad1
    pad1 = ROOT.TPad("pad1", "pad1", 0.01, 0.33, 0.99, 0.99)
    pad1.Draw()
    pad1.cd()
    #if varName!="drz1z2":
    #    pad1.SetLogy()
    pad1.SetFillColor(0)
    pad1.SetFrameBorderMode(0)
    pad1.SetBorderMode(0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    #pad1.SetGridx()
    #pad1.Draw()
    return c,pad1

def createPad2(canvas):
    # Lower ratio plot is pad2
    canvas.cd()  # returns to main canvas before defining pad2
    pad2 = ROOT.TPad("pad2", "pad2", 0.01, 0.20, 0.99, 0.33)
    pad2.Draw()
    pad2.cd()
    pad2.SetFillColor(0)
    pad2.SetFrameBorderMode(0)
    pad2.SetBorderMode(1)#bordermode = -1 box looks as it is behind the screen
   # bordermode = 0 no special effects
   # bordermode = 1 box looks as it is in front of the screen
    pad2.SetTopMargin(0)  # joins upper and lower plot
    pad2.SetBottomMargin(0)
    #pad2.SetGridx()
    #pad2.Draw()
    return pad2

def createPad3(canvas):
    # Lower ratio plot is pad3
    canvas.cd()  # returns to main canvas before defining pad3
    pad3 = ROOT.TPad("pad3", "pad3", 0.01, 0.03, 0.99, 0.20)
    pad3.Draw()
    pad3.cd()
    pad3.SetFillColor(0)
    pad3.SetFrameBorderMode(0)
    #pad3.SetFrameFillStyle(4000)
    pad3.SetBorderMode(0)
    pad3.SetTopMargin(0)  # joins upper and lower plot
    pad3.SetBottomMargin(0.35)
    #pad3.SetGridx()
    #pad3.Draw()
    return pad3
def generateAnalysisInputs():
    #dictionary of SF histograms
    hSF = {}
    eLowRecoFile = ROOT.TFile.Open('data/Ele_Reco_LowEt_2016.root')
    hSF['eLowReco'] = eLowRecoFile.Get('EGamma_SF2D').Clone()
    hSF['eLowReco'].SetDirectory(0)
    eLowRecoFile.Close()

    eRecoFile = ROOT.TFile.Open('data/Ele_Reco_2016.root')
    hSF['eReco'] = eRecoFile.Get('EGamma_SF2D').Clone()
    hSF['eReco'].SetDirectory(0)
    eRecoFile.Close()

    eIdFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2016_NoGap.root')
    hSF['eSel'] = eIdFile.Get('EGamma_SF2D').Clone()
    hSF['eSel'].SetDirectory(0)
    eIdFile.Close()

    eIdGapFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2016_Gap.root')
    hSF['eSelGap'] = eIdGapFile.Get('EGamma_SF2D').Clone()
    hSF['eSelGap'].SetDirectory(0)
    eIdGapFile.Close()

    mIdFile = ROOT.TFile.Open('data/final_HZZ_SF_2016_legacy_mupogsysts_newLoose_noTracking_1610.root')
    hSF['m'] = mIdFile.Get('FINAL').Clone()
    hSF['m'].SetDirectory(0)

    hSF['mErr'] = mIdFile.Get('ERROR').Clone()
    hSF['mErr'].SetDirectory(0)
    mIdFile.Close()

    #dictionary of PU weights
    hPU={}
    pileupFile = ROOT.TFile.Open('data/PileupWeights2016/PU_Central.root')
    hPU[''] = pileupFile.Get('pileup')
    hPU[''].SetDirectory(0)
    pileupFile.Close()

    pileupFileUp = ROOT.TFile.Open('data/PileupWeights2016/PU_minBiasUP.root')
    hPU['Up'] = pileupFileUp.Get('pileup')
    hPU['Up'].SetDirectory(0)
    pileupFileUp.Close()

    pileupFileDown = ROOT.TFile.Open('data/PileupWeights2016/PU_minBiasDOWN.root')
    hPU['Down'] = pileupFileDown.Get('pileup')
    hPU['Down'].SetDirectory(0)
    pileupFileDown.Close()

    return hSF,hPU
#ROOT.gSystem.Load('Utilities/scripts/ResponseMatrixMaker_cxx')
#sigSamples is a dictionary containing sample names and kfactor*cross-section
#sumW is a dictionary with sigsample:sumweights stored
ROOT.gSystem.Load('Utilities/scripts/ResponseMatrixMaker_cxx')
#gdb_debugger.hookDebugger()
def generateResponseClass(varName, channel,sigSamples,sigSamplesPath,sumW,hPUWt,hSF={}):
    #pdb.set_trace()
    className = responseClassNames[varName][channel]

    for h in hSF.values()+hPUWt.values():
        ROOT.SetOwnership(h,False)

    if hSF:
        className = 'SFHist'+className

    #if not hasattr(ROOT,className):
    #        ROOT.gSystem.Load('Utilities/scripts/ResponseMatrixMaker_cxx','kTRUE')

    #for example C=<class 'ROOT.BranchValueResponseMatrixMaker<float>'>
    C = getattr(ROOT, className)
    print("className:",C)

    #filelist=["zz4l-powheg"]
    filelist=[str(i) for i in sigSamples.keys()]
    #improve this by getting this info from ZZDatasetManager just like its done in makeCompositeHists
    #sigConstWeights = {sample : (1.256*35900*1.0835)/sumW
    #                   for sample in ConfigureJobs.getListOfFiles(filelist, selection)}

    sigConstWeights = {sample : (sigSamples[sample.split("__")[0]]*1000*args['lumi'])/sumW[sample]
                       for sample in [str(i) for i in sigSamples.keys()] }
    #print "sigConstWeights: ",sigConstWeights
    #print("_binning: ",_binning)
    binning = _binning[varName]
    vBinning = VFloat()
    ROOT.SetOwnership(vBinning,False)
    #print("vBinning: ",vBinning)
    #print("Content of the ROOT vector object: {}".format([x for x in vBinning]))
    #print("binning: ",binning)
    if len(binning) == 3:
        binningTemp = [binning[1] + i * (binning[2] - binning[1])/float(binning[0]) for i in xrange(binning[0]+1)]
        #print("binningTemp: ",binningTemp)
        for b in binningTemp:
            #print("b: ",b)
            vBinning.push_back(b)
    else:
        for b in binning:
            vBinning.push_back(b)

    print("Content of the ROOT vector object: {}".format([x for x in vBinning]))
    #print("vBinning: ",vBinning)
    responseMakers = {}
    #for sample, file_path in sigFileNames.items():
    #for sample in ConfigureJobs.getListOfFiles(filelist,selection):
    for sample in sigSamplesPath.keys():
        if sample=="zz4l-amcatnlo":
            continue
        #print "sample:", sample #expect zz4l-powheg
        #file_path = ConfigureJobs.getInputFilesPath(sample,selection,analysis)
        file_path=sigSamplesPath[sample]
        #print("where are the histos leaking")
        #pdb.set_trace()
        resp = C(channel, varNamesForResponseMaker[varName][channel], vBinning)
        #ROOT.SetOwnership(resp,False)
        file_path=file_path.encode("utf-8")
        #print "file_path: ",file_path
        fileList=glob.glob(file_path)
        #print "type in fileList should be str: ",type(fileList[0])
        for fName in fileList:
            resp.registerFile(fName)
        resp.registerPUWeights(hPUWt[''])
        resp.registerPUWeights(hPUWt['Up'], 'Up')
        resp.registerPUWeights(hPUWt['Down'], 'Down')
        resp.setConstantScale(sigConstWeights[sample])
        if hSF:
            resp.registerElectronSelectionSFHist(hSF['eSel'])
            resp.registerElectronSelectionGapSFHist(hSF['eSelGap'])
            resp.registerElectronLowRecoSFHist(hSF['eLowReco'])
            resp.registerElectronRecoSFHist(hSF['eReco'])
            resp.registerMuonSFHist(hSF['m'])
            resp.registerMuonSFErrorHist(hSF['mErr'])
            #print("scale factors are being added")

        responseMakers[sample] = resp

    altResponseMakers = {}
    for sample in ["zz4l-amcatnlo"]:
        #we only need to make new responseMatrix for zz4l-amcatnlo, ggZZ responseMatrices are already done above.
        file_path=sigSamplesPath[sample]
        #print("where are the histos leaking")
        resp = C(channel, varNamesForResponseMaker[varName][channel], vBinning)
        #ROOT.SetOwnership(resp,False)
        file_path=file_path.encode("utf-8")
        #print "file_path: ",file_path
        fileList=glob.glob(file_path)
        #print "type in fileList should be str: ",type(fileList[0])
        for fName in fileList:
            resp.registerFile(fName)
        resp.registerPUWeights(hPUWt[''])
        resp.registerPUWeights(hPUWt['Up'], 'Up')
        resp.registerPUWeights(hPUWt['Down'], 'Down')
        resp.setConstantScale(sigConstWeights[sample])
        if hSF:
            resp.registerElectronSelectionSFHist(hSF['eSel'])
            resp.registerElectronSelectionGapSFHist(hSF['eSelGap'])
            resp.registerElectronLowRecoSFHist(hSF['eLowReco'])
            resp.registerElectronRecoSFHist(hSF['eReco'])
            resp.registerMuonSFHist(hSF['m'])
            resp.registerMuonSFErrorHist(hSF['mErr'])
            #print("scale factors are being added")

        altResponseMakers[sample] = resp
        #print "resp: ",resp
        #del resp

    for sample in responseMakers.keys():
        print("sigSamples: " ,sample)

    for sample in altResponseMakers.keys():
        print("altsigSamples: " ,sample)

    for Resp in responseMakers.values()+altResponseMakers.values():
        ROOT.SetOwnership(Resp,False)

    return responseMakers,altResponseMakers

_printCounter = 0
#Load the RooUnfold library into ROOT
ROOT.gSystem.Load("RooUnfold/libRooUnfold")
def unfold(varName,chan,responseMakers,altResponseMakers,hSigDic,hAltSigDic,hSigSystDic,hTrueDic,hAltTrueDic,hDataDic,hbkgDic,hbkgMCDic,hbkgMCSystDic,nIter,plotDir=''):
    global _printCounter
    #get responseMakers from the function above- this is the whole game.
    #responseMakers = generateResponseClass(varName, chan,sigSamples,sumW,hSF)

    # outputs
    hUnfolded = {}
    hTruth={}
    hTrueAlt = {}
    hResponseNominal={}
    print("responseMakers: ",responseMakers)
    hResponseNominal = {s:resp for s,resp in responseMakers.items()}
    print("hResponseNominal:",hResponseNominal)

    #Setup() is called here for all signals?
    hResponseSig1 = hResponseNominal["ggZZ4e"].getResponse("pu_Up")
    hResponseSig2 = hResponseNominal["ggZZ4m"].getResponse("pu_Up")
    hResponseSig3 = hResponseNominal["ggZZ4t"].getResponse("pu_Up")
    hResponseSig4 = hResponseNominal["ggZZ2e2tau"].getResponse("pu_Up")
    hResponseSig5 = hResponseNominal["ggZZ2e2mu"].getResponse("pu_Up")
    hResponseSig6 = hResponseNominal["zz4l-powheg"].getResponse("pu_Up")
    #This will pop the powheg response matrix from the hResponseNominal Dictionary
    hResponseNominalTotal = hResponseNominal.pop("zz4l-powheg")
    #print "hRespNominalTotal: ",hResponseNominalTotal
    #This gets us the response matrix as a TH2D for "zz4l-powheg"
    print("This hResponse is full of leaks here")
    hResponse = hResponseNominalTotal.getResponse('nominal')
    hResponse.SetDirectory(0)
    #ROOT.SetOwnership(hResponse,False)
    #print("where are all the leaks")
    #print "type of hResp: " ,hResponse
    #Now we need to add the rest of the response matrices (MCFMs) to this POHWEG matrix
    #Looping over the values of the dictionary (it doesn't have powheg anymore)
    #print "hResponseNominal after zz-pohwheg:",hResponseNominal
    for response in hResponseNominal.values():
        print("Is the leak here")
        print("response: ",response)
        respMat = response.getResponse('nominal')
        #ROOT.SetOwnership(respMat,False)
        hResponse.Add(respMat)
        respMat.SetDirectory(0)
        print("Is the leak where")
        #ROOT.SetOwnership(respMat,False)
        del respMat
        #respMat.Delete()

    #print ("The leaks happen in this for loop")
    #hResponseNominalTotal = sum(resp for resp in hResponseNominal.values())


    #print "type of Total hResp: " ,hResponse
    # But its better to use RooUnfoldResponse here
    #RooUnfoldResponse constructor - create from already-filled histograms
    # "response" gives the response matrix, measured X truth.
    #  "measured" and "truth" give the projections of "response" onto the X-axis and Y-axis respectively,
    #   but with additional entries in "measured" for measurements with no corresponding truth (fakes/background) and
    #    in "truth" for unmeasured events (inefficiency).
    #     "measured" and/or "truth" can be specified as 0 (1D case only) or an empty histograms (no entries) as a shortcut
    #      to indicate, respectively, no fakes and/or no inefficiency.


    ## Give hSig and hTrue in the form of histograms

    varNames={'mass': 'Mass','pt':'ZZPt','zpt':'ZPt','leppt':'LepPt','dphiz1z2':'dPhiZ1Z2','drz1z2':'dRZ1Z2','jetPt0':'jetPt[0]'}
    #varNames={'zmass':'ZMass','mass': 'Mass','pt':'ZZPt','eta':'ZZEta','z1mass':'Z1Mass','z1pt':'Z1Pt','z2mass':'Z2Mass','z2pt':'Z2Pt','zpt':'ZPt','leppt':'LepPt'}

    hSigNominal = hSigDic[chan][varNames[varName]]
    #print "sigHist: ", hSigNominal,", ",hSigNominal.Integral()

    hTrue = hTrueDic[chan]["Gen"+varNames[varName]]
    #histTrue.Scale((1.256*35900*1.0835)/zzSumWeights)
    hData = hDataDic[chan][varNames[varName]]
    #print "dataHist: ",hData,", ",hData.Integral()
    #Get the background hists - #Get the histName_Fakes_chan histos
    hBkgNominal = hbkgDic[chan][varNames[varName]+"_Fakes"]
    #print "NonPromptHist: ",hBkgNominal,", ",hBkgNominal.Integral()
    hBkgMCNominal = hbkgMCDic[chan][varNames[varName]]
    #print "VVVHist: ",hBkgMCNominal,", ",hBkgMCNominal.Integral()
    #Add the two backgrounds
    hBkgTotal=hBkgNominal.Clone()
    hBkgTotal.Add(hBkgMCNominal)
    #print "TotBkgHist: ",hBkgTotal,", ",hBkgTotal.Integral()

    #No need to rebin certain variables
    #if varNames[varName] not in ['ZZEta']:
        #bins=array.array('d',_binning[varName])
        #Nbins=len(bins)-1
        #hSigNominal=hSigNominal.Rebin(Nbins,"",bins)
        #hTrue=hTrue.Rebin(Nbins,"",bins)
        #hData=hData.Rebin(Nbins,"",bins)
        #hBkgTotal=hBkgTotal.Rebin(Nbins,"",bins)
    #using the rebin function which takes care of overflow bins
    hSigNominal=rebin(hSigNominal,varName)
    hTrue=rebin(hTrue,varName)
    hData=rebin(hData,varName)
    hBkgTotal=rebin(hBkgTotal,varName)

    xaxisSize = hSigNominal.GetXaxis().GetTitleSize()
    yaxisSize = hTrue.GetXaxis().GetTitleSize()
    #print "xaxisSize: ",xaxisSize
    print("trueHist: ",hTrue,", ",hTrue.Integral())
    #print "TotBkgHist after rebinning: ",hBkgTotal,", ",hBkgTotal.Integral()
    hTruth['']=hTrue
    #pdb.set_trace()
    hUnfolded[''], hCov, hResp = getUnfolded(hSigNominal,hBkgTotal,hTruth[''],hResponse,hData, nIter,True)

    #print "hUnfolded['']: ",hUnfolded[''].Integral()

    #print("hResp: ",hResp)
    #del hResponse
    # plot covariance and response
    if plotDir and args['plotResponse']:
        cRes = ROOT.TCanvas("c","canvas")
        if varName == 'massFull':
            cRes.SetLogx()
            cRes.SetLogy()
        #hResp.Draw('colz text45')
        draw_opt = "colz text45"
        hResp.GetXaxis().SetTitle('Reco '+prettyVars[varName]+''+units[varName])
        hResp.GetYaxis().SetTitle('True '+prettyVars[varName]+''+units[varName])
        hResp.GetXaxis().SetTitleSize(0.75*xaxisSize)
        hResp.GetYaxis().SetTitleSize(0.75*yaxisSize)
        hResp.Draw(draw_opt)
        texS,texS1=getLumiTextBox()

        #style.setCMSStyle(cRes, '', dataType='  Preliminary', intLumi=35900.)
        #print "plotDir: ",plotDir
        cRes.Print("%s/response_%s.png" % (plotDir,varName))
        cRes.Print("%s/response_%s.pdf" % (plotDir,varName))

        del cRes
        cCov = ROOT.TCanvas("c","canvas")
        if varName == 'massFull':
            cCov.SetLogx()
            cCov.SetLogy()
        draw_opt = "colz text45"
        hCov.Draw(draw_opt)
        texS,texS1=getLumiTextBox()
        #style.setCMSStyle(cCov, '', dataType='Preliminary', intLumi=35900.)
        cCov.Print("%s/covariance_%s.png" % (plotDir,varName))
        cCov.Print("%s/covariance_%s.pdf" % (plotDir,varName))
        del cCov
    if not args['noSyst']:
        # luminosity
        lumiUnc = 0.023
        lumiScale = {'Up':1.+lumiUnc,'Down':1.-lumiUnc}
        for sys, scale in lumiScale.iteritems():
            #print "lumi uncert.",sys
            #print "scale: ",scale
            hSigLumi = hSigNominal * scale
            hSigLumi.SetDirectory(0)

            hBkgLumi = hbkgDic[chan][varNames[varName]+"_Fakes"]
            hBkgLumi.SetDirectory(0)
            hBkgMCLumi = hbkgMCDic[chan][varNames[varName]]
            hBkgMCLumi.SetDirectory(0)
            hBkgMCLumi.Scale(scale)
            hBkgTotalLumi=hBkgLumi.Clone()
            hBkgTotalLumi.Add(hBkgMCLumi)

            hTrueLumiShift = hTruth[''] * scale
            hTrueLumiShift.SetDirectory(0)
            hResponseLumi = hResponse.Clone()
            hResponseLumi.Scale(scale)
            hResponseLumi.SetDirectory(0)
            #print "SigLumiHist: ",hSigLumi,", ",hSigLumi.Integral()
            #print "VVVHist: ",hBkgMCLumi,", ",hBkgMCLumi.Integral()
            #Add the two backgrounds

            hBkgTotalLumi=rebin(hBkgTotalLumi,varName)

            #print "trueHist: ",hTrueLumiShift,", ",hTrueLumiShift.Integral()
            #print "TotBkgHistLumi after rebinning: ",hBkgTotalLumi,", ",hBkgTotalLumi.Integral()

            hUnfolded['lumi_'+sys],hCovLumi,hRespLumi = getUnfolded(hSigLumi,hBkgTotalLumi,hTrueLumiShift,hResponseLumi,hData, nIter,True)

            del hSigLumi
            del hBkgMCLumi
            del hBkgLumi
            del hTrueLumiShift

            #print "hUnfolded['lumi_']: ",hUnfolded['lumi_'+sys].Integral()

            if plotDir and args['plotSystResponse']:
                cResLumi = ROOT.TCanvas("c","canvas",800,800)
                if varName == 'massFull':
                    cRes.SetLogx()
                    cRes.SetLogy()
                draw_opt = "colz text45"
                hRespLumi.GetXaxis().SetTitle('Reco '+prettyVars[varName]+''+units[varName])
                hRespLumi.GetYaxis().SetTitle('True '+prettyVars[varName]+''+units[varName])
                hRespLumi.GetXaxis().SetTitleSize(0.75*xaxisSize)
                hRespLumi.GetYaxis().SetTitleSize(0.75*yaxisSize)
                hRespLumi.Draw(draw_opt)
                style.setCMSStyle(cResLumi, '', dataType='  Preliminary', intLumi=35900.)
                #print "plotDir: ",plotDir
                cResLumi.Print("%s/response_%s_%s.png" % (plotDir,varName,'lumi'+sys))
                cResLumi.Print("%s/response_%s_%s.pdf" % (plotDir,varName,'lumi'+sys))

                del cResLumi

        hResponsePU = {s:resp for s,resp in responseMakers.items()}
        hRespPUTot = hResponsePU.pop("zz4l-powheg")
        print("No errors in PU chain?")
        # PU reweight uncertainty
        for sys in ['Up','Down']:
            hRespPU = hRespPUTot.getResponse('pu_'+sys)
            hRespPU.SetDirectory(0)
            for resp in hResponsePU.values():
                respMatPU = resp.getResponse('pu_'+sys)
                hRespPU.Add(respMatPU)
                respMatPU.SetDirectory(0)
                del respMatPU
            #print "hSigSystDic: ",hSigSystDic
            hSigPU = hSigSystDic[chan][varNames[varName]+"_CMS_pileup"+sys]
            hSigPU.SetDirectory(0)
            #print 'pu_'+sys
            #print "sigHist: ", hSigPU,", ",hSigPU.Integral()
            hBkgPU = hbkgDic[chan][varNames[varName]+"_Fakes"]
            hBkgPU.SetDirectory(0)
            #print "NonPromptHist: ",hBkgPU,", ",hBkgPU.Integral()
            hBkgMCPU = hbkgMCSystDic[chan][varNames[varName]+"_CMS_pileup"+sys]
            hBkgMCPU.SetDirectory(0)
            #print "VVVHist: ",hBkgMCPU,", ",hBkgMCPU.Integral()
            hBkgPUTotal=hBkgPU.Clone()
            hBkgPUTotal.Add(hBkgMCPU)
            #print "TotBkgPUHist: ",hBkgPUTotal,", ",hBkgPUTotal.Integral()
            hSigPU=rebin(hSigPU,varName)
            hBkgPUTotal=rebin(hBkgPUTotal,varName)
            #print "TotBkgPUHist after Rebinning: ",hBkgPUTotal,", ",hBkgPUTotal.Integral()

            hUnfolded['pu_'+sys] = getUnfolded(hSigPU,
                                                     hBkgPUTotal,
                                                     hTruth[''],
                                                     hRespPU,
                                                     hData, nIter)
            del hSigPU
            del hBkgMCPU
            del hBkgPU
            del hRespPU

        # lepton efficiency uncertainty
        for lep in set(chan):
            hResponseSyst = {s:resp for s,resp in responseMakers.items()}
            hRespSystTot = hResponseSyst.pop("zz4l-powheg")
            print("No errors in systematics chain?")
            for sys in ['Up','Down']:
                hRespSyst = hRespSystTot.getResponse(lep+'Eff_'+sys)
                hRespSyst.SetDirectory(0)
                for response in hResponseSyst.values():
                    respMatSyst = response.getResponse(lep+'Eff_'+sys)
                    hRespSyst.Add(respMatSyst)
                    respMatSyst.SetDirectory(0)
                    del respMatSyst
                #print "hSigSystDic: ",hSigSystDic
                hSigSyst = hSigSystDic[chan][varNames[varName]+"_CMS_eff_"+lep+sys]
                hSigSyst.SetDirectory(0)
                #print lep+'Eff_'+sys
                #print "sigHist: ", hSigSyst,", ",hSigSyst.Integral()
                hBkgSyst = hbkgDic[chan][varNames[varName]+"_Fakes"]
                hBkgSyst.SetDirectory(0)
                #print "NonPromptHist: ",hBkgSyst,", ",hBkgSyst.Integral()
                hBkgMCSyst = hbkgMCSystDic[chan][varNames[varName]+"_CMS_eff_"+lep+sys]
                hBkgMCSyst.SetDirectory(0)
                #print "VVVHist: ",hBkgMCSyst,", ",hBkgMCSyst.Integral()
                hBkgSystTotal=hBkgSyst.Clone()
                hBkgSystTotal.Add(hBkgMCSyst)
                #print "TotBkgSystHist: ",hBkgSystTotal,", ",hBkgSystTotal.Integral()
                hSigSyst=rebin(hSigSyst,varName)
                hBkgSystTotal=rebin(hBkgSystTotal,varName)
                #print "TotBkgSystHist after Rebinning: ",hBkgSystTotal,", ",hBkgSystTotal.Integral()

                hUnfolded[lep+'Eff_'+sys] ,hCovLep,hRespLep = getUnfolded(hSigSyst,
                                                         hBkgSystTotal,
                                                         hTruth[''],
                                                         hRespSyst,
                                                         hData, nIter,True)
                del hSigSyst
                del hBkgMCSyst
                del hBkgSyst
                del hRespSyst

                if plotDir and args['plotSystResponse']:
                    cResSyst = ROOT.TCanvas("c","canvas",1200,1200)
                    if varName == 'massFull':
                        cResSyst.SetLogx()
                        cResSyst.SetLogy()
                    draw_opt = "colz text45"
                    hRespLep.GetXaxis().SetTitle('Reco '+prettyVars[varName]+sys+''+units[varName])
                    hRespLep.GetYaxis().SetTitle('True '+prettyVars[varName]+sys+''+units[varName])
                    hRespLep.GetXaxis().SetTitleSize(0.75*xaxisSize)
                    hRespLep.GetYaxis().SetTitleSize(0.75*yaxisSize)
                    hRespLep.Draw(draw_opt)
                    style.setCMSStyle(cResSyst, '', dataType='  Preliminary', intLumi=35900.)
                    #print "plotDir: ",plotDir
                    cResSyst.Print("%s/response_%s_%s.png" % (plotDir,varName,lep+'Eff_'+sys))
                    cResSyst.Print("%s/response_%s_%s.pdf" % (plotDir,varName,lep+'Eff_'+sys))
                    del cResSyst

    del hResponse

    #Alternative signal zz4l-amcatnlo
    hResponseAltNominal={}
    print("AltresponseMakers: ",altResponseMakers)
    hResponseAltNominal = {s:resp for s,resp in altResponseMakers.items()}
    print("hResponseNominal:",hResponseNominal)
    print("hResponseAltNominal:",hResponseAltNominal)

    hResponseSig7 = hResponseAltNominal["zz4l-amcatnlo"].getResponse("pu_Up")
    #This will pop the amcnlo response matrix from the hResponseAltNominal Dictionary
    hResponseAltNominalTotal = hResponseAltNominal.pop("zz4l-amcatnlo")

    hAltResponse = hResponseAltNominalTotal.getResponse('nominal')
    hAltResponse.SetDirectory(0)

    for response in hResponseNominal.values():
        print("response: ",response)
        respMat = response.getResponse('nominal')
        hAltResponse.Add(respMat)
        respMat.SetDirectory(0)
        del respMat

    hAltSigNominal = hAltSigDic[chan][varNames[varName]]

    hAltTrue = hAltTrueDic[chan]["Gen"+varNames[varName]]

    hAltSigNominal=rebin(hAltSigNominal,varName)
    hAltTrue=rebin(hAltTrue,varName)

    print("AltTrueHist: ",hAltTrue,", ",hAltTrue.Integral())

    hTrueAlt['']=hAltTrue

    hUnfolded['generator']  = getUnfolded(hAltSigNominal,hBkgTotal,hTrueAlt[''],hAltResponse,hData, nIter)

    # make everything local (we'll cache copies)
    for h in hUnfolded.values()+hTruth.values()+hTrueAlt.values():
        ROOT.SetOwnership(h,False)
        print("histos: ",h)
        print ("hTruthOut of Unfold: ",h.Integral())
        #h.SetDirectory(0)

    return hUnfolded,hTruth,hTrueAlt

#rebin histos and take care of overflow bins
def rebin(hist,varName):
    ROOT.SetOwnership(hist, False)
    #No need to rebin certain variables but still might need overflow check
    if varName not in ['eta']:
        bins=array.array('d',_binning[varName])
        Nbins=len(bins)-1
        hist=hist.Rebin(Nbins,"",bins)
    else:
        Nbins = hist.GetSize() - 2
    add_overflow = hist.GetBinContent(Nbins) + hist.GetBinContent(Nbins + 1)
    hist.SetBinContent(Nbins, add_overflow)
    return hist

def getUnfolded(hSig, hBkg, hTrue, hResponse, hData, nIter,withRespAndCov=False):
    Response = getattr(ROOT,"RooUnfoldResponse")

    print("TrueBeforeResponse: ", hTrue,", ",hTrue.Integral())
    print("SigBeforeResponse: ", hSig,", ",hSig.Integral())
    print("======================================================")
    print("binsize %s %s"%(hSig.GetNbinsX(),hTrue.GetNbinsX()))
    response = Response(hSig, hTrue.Clone(), hResponse.Clone())
    ROOT.SetOwnership(response,False)
    ROOT.SetOwnership(hData,False)
    #Response matrix as a 2D-histogram: (x,y)=(measured,truth)
    hResp = response.Hresponse()
    #pdb.set_trace()
    my_mResp=response.Mresponse()
    inv_mResp=my_mResp.Clone()
    inv_mResp.Invert()
    #hResp = hResponse
    #print "hResp out of response: ",hResp

    #RooUnfoldIter = getattr(ROOT,"RooUnfoldBayes")

    RooUnfoldInv = getattr(ROOT,"RooUnfoldInvert")
    RooUnfoldSvd = getattr(ROOT,"RooUnfoldSvd")
    RooUnfoldBayes = getattr(ROOT,"RooUnfoldBayes")

    #RooUnfoldBinbyBin = getattr(ROOT,"RooUnfoldBinByBin")
    try:
        svd = ROOT.TDecompSVD(response.Mresponse())
        sig = svd.GetSig()
        try:
            condition = sig.Max() / max(0., sig.Min())
        except ZeroDivisionError:
            condition = float('inf')
            raise

        print("channel: ",chan)
        print("variable: ",varNames[varName])
        print("hResp out of response: ",hResp)
        print('')
        print('condition: {}'.format(condition))
        print('')

    except:
        print("It broke! Printing debug info")
        print("Sig: {}, bkg: {}, true: {}, response: {}".format(hSig.Integral(), hBkg.Integral(), hTrue.Integral(), hResponse.Integral()))
        c = ROOT.TCanvas("c1","canvas",800,800)
        hSig.Draw()
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/sig{}.png".format(_printCounter))
        hBkg.draw()
        _style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("bkg{}.png".format(_printCounter))
        hTrue.Draw()
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/true{}.png".format(_printCounter))
        hData.Draw()
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/data{}.png".format(_printCounter))
        draw_opt = "colz text45"
        hResponse.Draw(draw_opt)
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/resp{}.png".format(_printCounter))
        c.Print("DebugPlots/resp{}.root".format(_printCounter))
        _printCounter += 1

    print("hData: ", hData.Integral())
    hDataMinusBkg = hData.Clone()
    hDataMinusBkg.Reset()
    print("hBkg: ", hBkg.Integral())
    hDataMinusBkg.Add(hData,1)
    hDataMinusBkg.Add(hBkg,-1)
    #hDataMinusBkg.Add(hBkg,-1)
    #HistTools.zeroNegativeBins(hDataMinusBkg)
    print("DataMinusbkgIntegral: ",hDataMinusBkg, ", ",hDataMinusBkg.Integral())
    #Unfolding using 4 iterations and then stopping
    #if varNames[varName] not in ["Z1Mass","Z2Mass"]:
    #    nIter=8
    #print "No.of iterations: ",nIter
    print("response: ",response)

    #Simply inverting the matrix
    unf = RooUnfoldInv(response, hDataMinusBkg)
    unf2 = RooUnfoldSvd(response, hDataMinusBkg,4)
    unf3 = RooUnfoldBayes(response, hDataMinusBkg,2)
    #unf = RooUnfoldIter(response, hDataMinusBkg, nIter)
    print("unf: ",unf2 )

    #Unfolds using the method of correction factors
    #unf = RooUnfoldBinbyBin(response, hSig)

    #del hDataMinusBkg
    #This is the unfolded "data" distribution
    hOut = unf.Hreco()
    hOut2=unf2.Hreco()
    hOut3=unf3.Hreco()

    #ROOT.SetOwnership(hOut,False)
    if not hOut:
        print(hOut)
        raise ValueError("The unfolded histogram got screwed up somehow!")
    print("hOut: ",hOut,"",hOut.Integral())
    #Returns covariance matrices for error calculation of type withError
    #0: Errors are the square root of the bin content
    #1: Errors from the diagonals of the covariance matrix given by the unfolding
    #2: Errors from the covariance matrix given by the unfolding => We use this one for now
    #3: Errors from the covariance matrix from the variation of the results in toy MC tests
    hCov = unf.Ereco(2)
    hCov2=unf2.Ereco(2)
    hCov3=unf3.Ereco(2)
    #hOut.SetDirectory(0)
    #hResp.SetDirectory(0)
    #ROOT.SetOwnership(hCov,False)
    print("hCov: ",hCov)
    print("where is the crash happening?")
    #return hCov.Clone(),hResp.Clone()
    #return hOut
    if withRespAndCov:
        return hOut,hCov.Clone(),hResp.Clone() #inv_mResp.Clone()#hResp.Clone()

    #del hDataMinusBkg
    #print "DataMinusbkgIntegral: ",hDataMinusBkg, ", ",hDataMinusBkg.Integral()
    return hOut

def RatioErrorBand(Ratio,hUncUp,hUncDn,hTrueNoErrs,varName):
        ratioGraph=ROOT.TGraphAsymmErrors(Ratio)
        ROOT.SetOwnership(ratioGraph,False)
        tmpData = Ratio.Clone("tmp")
        for i in range(1, tmpData.GetNbinsX()+1):
            if hTrueNoErrs.GetBinContent(i)==0:
                continue
            eUp=hUncUp.GetBinContent(i)
            eDn=hUncDn.GetBinContent(i)
            tru=hTrueNoErrs.GetBinContent(i)
            #print "eUp: ",eUp, "","eDn: ",eDn
            errorUp = tmpData.GetBinContent(i) + math.sqrt(math.pow(tmpData.GetBinError(i),2) + math.pow((eUp/tru),2))
            errorUp -= Ratio.GetBinContent(i)
            errorDn = max(tmpData.GetBinContent(i) - math.sqrt(math.pow(tmpData.GetBinError(i),2) + math.pow((eDn/tru),2)),0)
            errorDn = Ratio.GetBinContent(i) - errorDn
            print("stat. error: ",tmpData.GetBinError(i))
            print ("eUp/tru: ",eUp/tru)
            print ("eDn/tru: ",eDn/tru)
            print ("errorUp: ",errorUp, "","errorDn: ",errorDn)
            ratioGraph.SetPointEYhigh(i-1, errorUp)
            ratioGraph.SetPointEYlow(i-1, errorDn)
        ratioGraph.SetFillColorAlpha(1,0.5)
        ratioGraph.SetFillStyle(3001)
        ratioGraph.GetXaxis().SetLabelSize(0)
        ratioGraph.GetXaxis().SetTitleSize(0)
        #ratioGraph.GetYaxis().SetLabelSize(0)
        #ratioGraph.GetYaxis().SetTitleSize(0)
        ratioGraph.GetXaxis().SetLimits(Ratio.GetXaxis().GetXmin(),Ratio.GetXaxis().GetXmax())
        if varName=="drz1z2":
            ratioGraph.SetMaximum(1.8)
            ratioGraph.SetMinimum(0.4)
        else:
            ratioGraph.SetMaximum(1.8)
            ratioGraph.SetMinimum(0.4)
        return ratioGraph

def MainErrorBand(hMain,hUncUp,hUncDn,varName,norm,normFb):
        MainGraph=ROOT.TGraphAsymmErrors(hMain)
        ROOT.SetOwnership(MainGraph,False)
        tmpData = hMain.Clone("tmp")
        for i in range(1, tmpData.GetNbinsX()+1):
            if hMain.GetBinContent(i)==0:
                continue
            eUp=hUncUp.GetBinContent(i)
            eDn=hUncDn.GetBinContent(i)
            #print "eUp: ",eUp, "","eDn: ",eDn
            errorUp = tmpData.GetBinContent(i) + math.sqrt(math.pow(tmpData.GetBinError(i),2) + math.pow(eUp,2))
            errorUp -= hMain.GetBinContent(i)
            errorDn = max(tmpData.GetBinContent(i) - math.sqrt(math.pow(tmpData.GetBinError(i),2) + math.pow(eDn,2)),0)
            errorDn = hMain.GetBinContent(i) - errorDn
            print("errorUp: ",errorUp, "","errorDn: ",errorDn)
            MainGraph.SetPointEYhigh(i-1, errorUp)
            MainGraph.SetPointEYlow(i-1, errorDn)
        MainGraph.SetFillColorAlpha(1,0.7)
        MainGraph.SetFillStyle(3001)
        if norm:
            drawyTitle = _yTitle[varName]
        elif normFb:
            drawyTitle = _yTitleNoNorm[varName]
        else:
            drawyTitle = "Events"
        MainGraph.GetYaxis().SetTitle(drawyTitle)

        #MainGraph.GetYaxis().SetTitleSize(*hMain.GetYaxis().GetTitleSize())
        MainGraph.GetYaxis().SetLabelSize(0.8*hMain.GetYaxis().GetLabelSize())
        if varName=="drz1z2":
            MainGraph.GetYaxis().SetTitleOffset(1.0)
        else:
            MainGraph.GetYaxis().SetLabelOffset(0.0)
            MainGraph.GetYaxis().SetTitleOffset(1.0)
        #MainGraph.GetXaxis().SetLabelSize(0)
        #MainGraph.GetXaxis().SetTitleSize(0)
        #MainGraph.GetYaxis().SetLabelSize(0)
        #MainGraph.GetYaxis().SetTitleSize(0)
        MainGraph.GetXaxis().SetLimits(hMain.GetXaxis().GetXmin(),hMain.GetXaxis().GetXmax())
        #MainGraph.SetMaximum(1.5)

        MainGraph.SetMaximum(1.2*(hMain.GetMaximum()))
        MainGraph.SetMinimum(0.5*(hMain.GetMinimum()))
        #if varName=="drz1z2":
        #    MainGraph.SetMinimum(0.0)
        #else:
            #MainGraph.SetMinimum(0.5*(hMain.GetMinimum()))
        return MainGraph
def generatePlots(hUnfolded,hUncUp,hUncDn,hTruth,hTruthAlt,varName,norm,normFb,lumi,unfoldDir=''):
    UnfHists=[]
    TrueHists=[]
    # for normalization if needed
    nomArea = hUnfolded.Integral(0,hUnfolded.GetNbinsX()+1)
    # Make uncertainties out of the unfolded histos
    ### plot
    hUnf = hUnfolded.Clone()
    hTrue = hTruth.Clone()
    #Alt Signal
    hTrueAlt = hTruthAlt.Clone()
    hTrueLeg = hTruthAlt.Clone()
    #lumi provided already in fb-1
    lumifb = lumi

    if norm:
        hUnf.Scale(1.0/(hUnf.Integral(0,hUnf.GetNbinsX()+1)))
    elif normFb:
        hUnf.Scale(1.0/lumifb)
    else:
        print("no special normalization")

    print ("hTrue histo here: ",hTrue)
    #print ("unfoldDir: ",unfoldDir)
    xaxisSize = hUnf.GetXaxis().GetTitleSize()
    yaxisSize = hTrue.GetXaxis().GetTitleSize()
    if unfoldDir:
        #Create a ratio plot
        c,pad1 = createCanvasPads()
        #Unfmaximum = hUnf.GetMaximum()

        #hTrue.SetFillColor(ROOT.TColor.GetColor("#99ccff"))
        hTrue.SetLineColor(ROOT.TColor.GetColor('#000099'))
        #hTrue.SetFillStyle(3010)
        #AltSignal
        hTrueAlt.SetFillColor(2)
        hTrueAlt.SetLineStyle(10)#dashes
        hTrueAlt.SetFillStyle(0)#hollow
        hTrueAlt.SetLineColor(ROOT.kRed)
        print("Total Truth Integral",hTrue.Integral())
        print("Total Alt Truth Integral",hTrueAlt.Integral())
        print("Total Unf Data Integral",hUnf.Integral())
        #Truthmaximum = hTrue.GetMaximum()
        hTrue.SetLineWidth(2*hTrue.GetLineWidth())
        hTrueAlt.SetLineWidth(2*hTrueAlt.GetLineWidth())

        if not norm and normFb:
            print("Inclusive fiducial cross section = {} fb".format(hUnf.Integral(0,hUnf.GetNbinsX()+1)))
        if norm or normFb:
            normalizeBins(hUnf)

        if norm:
            hUncUp.Scale(1.0/hUnfolded.Integral(0,hUnfolded.GetNbinsX()+1))
            hUncDn.Scale(1.0/hUnfolded.Integral(0,hUnfolded.GetNbinsX()+1))
        elif normFb:
            hUncUp.Scale(1.0/lumifb)
            hUncDn.Scale(1.0/lumifb)
        else:
            print("no special normalization")

        if norm or normFb:
            normalizeBins(hUncUp)
            normalizeBins(hUncDn)

        if norm:
            trueInt = hTrue.Integral(0,hTrue.GetNbinsX()+1)
            hTrue.Scale(1.0/trueInt)
            #hTrueUncUp /= trueInt # (trueInt + hTrueUncUp.Integral(0,hTrueUncUp.GetNbinsX()+1))
            #hTrueUncDn /= trueInt # (trueInt - hTrueUncDn.Integral(0,hTrueUncDn.GetNbinsX()+1))
            #Alt Signal
            AltTrueInt = hTrueAlt.Integral(0,hTrueAlt.GetNbinsX()+1)
            hTrueAlt.Scale(1.0/AltTrueInt)
        elif normFb:
            hTrue.Scale(1.0/lumifb)
            #hTrueUncUp /= lumifb
            #hTrueUncDn /= lumifb
            hTrueAlt.Scale(1.0/lumifb)
        else:
            print("no special normalization")

        if norm or normFb:
            normalizeBins(hTrue)
            #normalizeBins(hTrueUncUp)
            #normalizeBins(hTrueUncDn)
            normalizeBins(hTrueAlt)

        hTrue.Draw("HIST")
        hTrueAlt.Draw("HIST")
        Unfmaximum = hUnf.GetMaximum()
        Truthmaximum = hTrue.GetMaximum()
        #pdb.set_trace()
        if(Unfmaximum > Truthmaximum):
            hTrue.SetMaximum(Unfmaximum*1.2)
        else:
            hTrue.SetMaximum(Truthmaximum*1.2)

        hTrue.GetXaxis().SetTitle("")

        #hUnf.SetMinimum(0.0)
        #hTrue.SetMinimum(0.0)
        UnfErrBand = MainErrorBand(hUnf,hUncUp,hUncDn,varName,norm,normFb)
        #print "UnfErrBand: ",UnfErrBand

        UnfErrBand.Draw("a2")

        #UnfErrBand.Draw("PSAME")
        hTrue.GetXaxis().SetLabelSize(0)
        hTrue.GetXaxis().SetTitleSize(0)
        #hTrue.GetYaxis().SetTitle("Events")
        #hTrue.GetYaxis().SetTitleOffset(1.0)
        hTrueAlt.GetXaxis().SetLabelSize(0)
        hTrueAlt.GetXaxis().SetTitleSize(0)
        hTrueAlt.Draw("HISTSAME")
        hTrue.Draw("HISTSAME")
        #hUnf.Sumw2(False)
        #hUnf.SetBinErrorOption(ROOT.TH1.kPoisson)
        hUnf.SetLineColor(ROOT.kBlack)
        hUnf.SetMarkerStyle(20)
        hUnf.SetMarkerSize(0.7)
        hUnf.GetXaxis().SetTitle("")
        hUnf.GetXaxis().SetLabelSize(0)
        hUnf.GetXaxis().SetTitleSize(0)
        hUnf.Draw("PE1SAME")

        texS,texS1=getLumiTextBox()
        sigLabel = "POWHEG+MCFM+Pythia8"
        sigLabelAlt = "MG5_aMC@NLO+MCFM+Pythia8"
        if varName=="dphiz1z2" or varName=="drz1z2":
            leg = ROOT.TLegend(0.15,0.60,0.15+0.015*len(sigLabelAlt),0.90,"")
        elif varName=="leppt":
            leg = ROOT.TLegend(0.20,0.18,0.20+0.015*len(sigLabelAlt),0.48,"")
        else:
            leg = ROOT.TLegend(0.55,0.60,0.55+0.015*len(sigLabelAlt),0.90,"")
        leg.AddEntry(hUnf,"Data + stat. unc.","lep")
        leg.AddEntry(UnfErrBand, "Stat. #oplus syst. unc.","f")
        leg.AddEntry(hTrue, sigLabel,"lf")

        hTrueLeg.SetFillColor(2)
        hTrueLeg.SetLineStyle(10)#dashes
        hTrueLeg.SetFillColorAlpha(2,0.4)
        hTrueLeg.SetFillStyle(3001)#solid
        hTrueLeg.SetLineColor(ROOT.kRed)
        #hTrueLeg.SetLineColor(ROOT.TColor.GetColor('#ff9898'))
        hTrueLeg.SetLineWidth(4*hTrueLeg.GetLineWidth())
        leg.AddEntry(hTrueLeg, sigLabelAlt,"l")
        leg.SetFillColor(ROOT.kWhite)
        leg.SetBorderSize(1)
        leg.SetFillStyle(1001)
        leg.SetTextSize(0.025)
        leg.Draw()

        #SecondPad
        pad2 = createPad2(c)

        hTrueNoErrs = hTrue.Clone() # need central value only to keep ratio uncertainties consistent
        nbins=hTrueNoErrs.GetNbinsX()
        print("trueNbins: ",nbins)

        Unfbins=hUnf.GetNbinsX()
        print("UnfNbins: ",Unfbins)
        #hTrueNoErrs.SetError(array.array('d',[0.]*nbins))
        #Starting the ratio proceedure
        Ratio,line = createRatio(hUnf, hTrueNoErrs)
        ratioErrorBand = RatioErrorBand(Ratio,hUncUp,hUncDn,hTrueNoErrs,varName)


        #ratioErrorBand.GetYaxis().SetTitle("Data/Theo")
        #ratioErrorBand.GetYaxis().SetNdivisions(328,True)
        #ratioErrorBand.GetYaxis().SetLabelFont(42)
        #ratioErrorBand.GetYaxis().SetLabelOffset(0.01)
        #ratioErrorBand.GetYaxis().SetLabelSize(0.14)
        #ratioErrorBand.GetYaxis().SetTitleFont(42)
        #ratioErrorBand.GetYaxis().SetTitleSize(0.14)
        #ratioErrorBand.GetYaxis().SetTitleOffset(0.30)

        ratioErrorBand.GetYaxis().SetLabelSize(0)
        ratioErrorBand.GetYaxis().SetTitleSize(0)
        ratioErrorBand.Draw("a2")

        sigTex = getSigTextBox(0.15,0.8,sigLabel,0.12)
        Ratio.Draw("PE1SAME")
        #ratioErrorBand.Draw("p")
        line.SetLineColor(ROOT.kBlack)
        line.Draw("same")

        Altyaxis = ROOT.TGaxis(hUnf.GetXaxis().GetXmin(),ratioErrorBand.GetMinimum(),hUnf.GetXaxis().GetXmin(),ratioErrorBand.GetMaximum(),ratioErrorBand.GetMinimum(),ratioErrorBand.GetMaximum())
        Altyaxis.SetNdivisions(3)
        Altyaxis.SetTitle("Data/Theo")
        Altyaxis.SetLabelFont(42)
        Altyaxis.SetLabelOffset(0.01)
        Altyaxis.SetLabelSize(0.14)
        Altyaxis.SetTitleFont(42)
        Altyaxis.SetTitleSize(0.14)
        Altyaxis.SetTitleOffset(0.30)
        Altyaxis.Draw("SAME")

        #ThirdPad
        pad3 = createPad3(c)


        hTrueAltNoErrs = hTrueAlt.Clone() # need central value only to keep ratio uncertainties consistent
        #nbins=hTrueNoErrs.GetNbinsX()
        #print("trueNbins: ",nbins)

        #Unfbins=hUnf.GetNbinsX()
        #print("UnfNbins: ",Unfbins)

        #hTrueNoErrs.SetError(array.array('d',[0.]*nbins))
        #Starting the ratio proceedure
        AltRatio,Altline = createRatio(hUnf, hTrueAltNoErrs)
        AltRatioErrorBand = RatioErrorBand(AltRatio,hUncUp,hUncDn,hTrueAltNoErrs,varName)
        AltRatioErrorBand.GetYaxis().SetLabelSize(0)
        AltRatioErrorBand.GetYaxis().SetTitleSize(0)
        AltRatioErrorBand.Draw("a2")
        AltRatio.Draw("PE1SAME")
        #ratioErrorBand.Draw("p")
        Altline.SetLineColor(ROOT.kRed)
        Altline.Draw("same")

        AltTex = getSigTextBox(0.15,0.8,sigLabelAlt,0.10)
        #redraw axis
        xaxis = ROOT.TGaxis(hUnf.GetXaxis().GetXmin(),ratioErrorBand.GetMinimum(),hUnf.GetXaxis().GetXmax(),ratioErrorBand.GetMinimum(),hUnf.GetXaxis().GetXmin(),hUnf.GetXaxis().GetXmax(),510)
        xaxis.SetTitle(prettyVars[varName]+''+units[varName])
        #labelTex = getSigTextBox(0.9,0.8,prettyVars[varName]+''+units[varName])
        xaxis.SetLabelFont(42)
        xaxis.SetLabelOffset(0.03)
        xaxis.SetLabelSize(0.12)
        xaxis.SetTitleFont(42)
        xaxis.SetTitleSize(0.18)
        xaxis.SetTitleOffset(0.80)
        xaxis.Draw("SAME")

        yaxis = ROOT.TGaxis(hUnf.GetXaxis().GetXmin(),ratioErrorBand.GetMinimum(),hUnf.GetXaxis().GetXmin(),ratioErrorBand.GetMaximum(),ratioErrorBand.GetMinimum(),ratioErrorBand.GetMaximum())
        yaxis.SetNdivisions(3)
        yaxis.SetTitle("Data/Theo")
        yaxis.SetLabelFont(42)
        yaxis.SetLabelOffset(0.01)
        yaxis.SetLabelSize(0.11)
        yaxis.SetTitleFont(42)
        yaxis.SetTitleSize(0.11)
        yaxis.SetTitleOffset(0.35)
        yaxis.Draw("SAME")
        #style.setCMSStyle(c, '', dataType='  Preliminary', intLumi=35900.)
        c.Print("%s/Ratio_%s.png" % (unfoldDir,varName))
        c.Print("%s/Ratio_%s.pdf" % (unfoldDir,varName))
        c.Update()

        del c

def getLumiTextBox():
    texS = ROOT.TLatex(0.8,0.955, str(args['lumi'])+" fb^{-1} (13 TeV)")
    texS.SetNDC()
    texS.SetTextFont(42)
    texS.SetTextSize(0.040)
    texS.Draw()
    texS1 = ROOT.TLatex(0.11,0.955,"#bf{CMS} #it{Preliminary}")
    texS1.SetNDC()
    texS1.SetTextFont(42)
    texS1.SetTextSize(0.040)
    texS1.Draw()
    return texS,texS1

def getSigTextBox(x,y,sigLabel,size):
    texS = ROOT.TLatex(x,y, str(sigLabel))
    texS.SetNDC()
    texS.SetTextFont(42)
    texS.SetTextSize(size)
    texS.Draw()

def _generateUncertainties(hDict,norm):

    nominalArea = hDict[''].Integral(0,hDict[''].GetNbinsX()+1)
    hErr = {'Up':{},'Down':{}}
    for sys, h in hDict.iteritems():
        if not sys:
            continue

        he = h.Clone()

        if norm:
            he.Scale(nominalArea/(he.Integral(0,he.GetNbinsX()+1)))

        #Subtract the nominal histogram from the SysUp or Down histogram

        he.Add(hDict[''],-1)
        sysName = sys.replace('_Up','').replace('_Down','')

        if '_Up' in sys:
            hErr['Up'][sysName] = he
        elif '_Down' in sys:
            hErr['Down'][sysName] = he
        else:
            hErr['Up'][sysName] = he
            he2 = he.Clone()
            hErr['Down'][sysName] = he2

    return hErr

def _sumUncertainties(errDict,varName):
    if varName == "eta":
        histbins=array.array('d',[0.,1.0,2.0,3.0,4.0,5.0,6.0])
    else:
        histbins=array.array('d',_binning[varName])
    #print "histbins: ",histbins
    hUncUp=ROOT.TH1D("hUncUp","Total Up Uncert.",len(histbins)-1,histbins)
    hUncDn=ROOT.TH1D("hUncDn","Total Dn Uncert.",len(histbins)-1,histbins)
    sysList = errDict['Up'].keys()
    #print "sysList: ",sysList
    #print "hUncUp: ",hUncUp,"",hUncUp.Integral()
    #print "hUncDown: ",hUncDn,"",hUncDn.Integral()
    totUncUp=totUncDn=0.
    UncUpHistos= [errDict['Up'][sys] for sys in sysList]
    UncDnHistos= [errDict['Down'][sys] for sys in sysList]
    LumiUp = errDict['Up']['lumi']
    LumiDn = errDict['Down']['lumi']
    #print "LumiUp: ",LumiUp.Integral()
    #print "LumiDn: ",LumiDn.Integral()
    for i in range(1,hUncUp.GetNbinsX()+1):
        for h1, h2 in zip(UncUpHistos,UncDnHistos):
            #print "histUp: ",h1,"",h1.Integral()
            #print "histDn: ",h2,"",h2.Integral()
            totUncUp += max(h1.GetBinContent(i),h2.GetBinContent(i))**2
            totUncDn += min(h1.GetBinContent(i),h2.GetBinContent(i))**2

        totUncUp = math.sqrt(totUncUp)
        totUncDn = math.sqrt(totUncDn)
        #print "totUncUp: ",totUncUp
        #print "totUncDn: ",totUncDn
        hUncUp.SetBinContent(i,totUncUp)
        hUncDn.SetBinContent(i,totUncDn)
    print("hUncUp: ",hUncUp,"",hUncUp.Integral())
    print("hUncDown: ",hUncDn,"",hUncDn.Integral())

    return hUncUp, hUncDn

def _combineChannelUncertainties(*errDicts):
    hUncTot = {}
    uncList = []
    for errDict in errDicts:
        for sys in ['Up','Down']:
            uncList += errDict[sys].keys()
    uncList = set(uncList)
    print("uncList:",uncList)
    for sys in ['Up','Down']:
        hUncTot[sys] = {}
        for unc in uncList:
            if varName == "eta":
                histbins=array.array('d',[0.,1.0,2.0,3.0,4.0,5.0,6.0])
            else:
                histbins=array.array('d',_binning[varName])
            #print "histTot histbins: ",histbins
            histTot=ROOT.TH1D("histTot","Tot Uncert.",len(histbins)-1,histbins)
            ROOT.SetOwnership(histTot,False)
            hUncTot[sys][unc] = histTot
            for errDict in errDicts:
                try:
                    hUncTot[sys][unc].Add(errDict[sys][unc])
                except KeyError:
                    continue

    return hUncTot

def addTheoryVar(processName, varName, entries, central=0, exclude=[]):
    theoryVariations={}
    if "scale" not in varName.lower() and "pdf" not in varName.lower():
        raise ValueError("Invalid theory uncertainty %s. Must be type 'scale' or 'pdf'" % varName)
    name = "scale" if "scale" in varName.lower() else "pdf"

    if not processName in theoryVariations:
        theoryVariations[processName] = {}

    theoryVariations[processName].update({ name : {
            "entries" : entries,
            "central" : central,
            "exclude" : exclude,
        }
    })
    return theoryVariations

def weightHistName(channel, variable):
    return "_".join([variable, "lheWeights", channel])
#if __name__ == "__main__":

def mkdir(plotDir):
    for outdir in [plotDir]:
        try:
            os.makedirs(os.path.expanduser(outdir))
        except OSError as e:
            print(e)
            pass

plotDir=args['plotDir']
UnfoldDir=args['unfoldDir']
nIterations=args['nIter']

varNames={'mass': 'Mass','pt':'ZZPt','zpt':'ZPt','leppt':'LepPt','dphiz1z2':'dPhiZ1Z2','drz1z2':'dRZ1Z2','jetPt0':'jetPt[0]'}


#Dictionary where signal samples are keys with cross-section*kfactors as values
sigSampleDic=ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfEWK())
sigSampleList=[str(i) for i in sigSampleDic.keys()]
print("sigSamples: ",sigSampleList)

AltsigSampleDic=ConfigureJobs.getListOfFilesWithXSec(["zz4l-amcatnlo",])
AltsigSampleList=[str(i) for i in AltsigSampleDic.keys()]
print("AltsigSamples: ",AltsigSampleList)

#Combine sigSamples
TotSigSampleList = list(set(sigSampleList) | set(AltsigSampleList))
sigSampleDic.update(AltsigSampleDic)
#Replace fOut with fUse once you have run all the data samples and the backgrounds - right now unfolded data looking really big- subtract backgrounds
if args['test']:
    sigSamplesPath={}
    fUse = ROOT.TFile("SystGenFiles/originalWithGenandSyst_forJets_1jetCutBoth_Hists12Oct2020-ZZ4l2016_Moriond.root","update")
    #fUse = ROOT.TFile("SystGenFiles/originalWithGenandSyst_forJets_Hists30Sep2020-ZZ4l2016_Moriond.root","update")
    #fUse = ROOT.TFile("SystGenFiles/originalWithGenandSyst_forJets_ZZjj_Hists09Oct2020-ZZ4l2016_Moriond.root","update")
    fOut=fUse
    for dataset in TotSigSampleList:
        file_path = ConfigureJobs.getInputFilesPath(dataset,selection, analysis)
        #print "file_path:",file_path
        sigSamplesPath[dataset]=file_path

#Dictionary where signal samples are keys with cross-section*kfactors as values
#sigSampleDic=ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfEWK())
#sigSampleList=[str(i) for i in sigSampleDic.keys()]
#print "sigSamples: ",sigSampleList
#Get the Gen Histograms
#sigSamplesPath = SelectorTools.applyGenSelector(varList,sigSampleList,selectChannels, "ZZGenSelector", args['selection'], fOut,args['analysis'],
#        extra_inputs=hist_inputs+tselection,
#        addSumweights=False, proof=args['proof'])

#print "sigSamplesPath: ",sigSamplesPath
#Sum all data and return a TList of all histograms that are booked. And an empty datSumW dictionary as there are no sumWeights
alldata,dataSumW = HistTools.makeCompositeHists(fOut,"AllData",
    ConfigureJobs.getListOfFilesWithXSec([args['analysis']+"data"],manager_path), args['lumi'],
    underflow=False, overflow=False)

#Sum all the signal which is just zz4l-powheg for now, makeCompositeHists will also scale the histogram with cross-section*kfactor*1000*lumi/sumWeights
#allzzPowheg,zzSumW= HistTools.makeCompositeHists(fOut,"zzPowheg", ConfigureJobs.getListOfFilesWithXSec(
#    ConfigureJobs.getListOfSignalFilenames(),manager_path), args['lumi'],
#    underflow=False, overflow=False)

#all ewkmc/this is also allSignal histos, scaled properly, kind of a repeat of above but with ggZZ added
ewkmc,ewkSumW = HistTools.makeCompositeHists(fOut,"AllEWK", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfEWK(), manager_path), args['lumi'],
    underflow=False, overflow=False)

altSigmc,altSigSumW = HistTools.makeCompositeHists(fOut,"AltSig", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfaltSig(), manager_path), args['lumi'],
    underflow=False, overflow=False)

#Update ewkSumW dictionary with sumWeights value of zz4l-amcatnlo from altSigSumW, the common keys should not be duplicated
ewkSumW.update(altSigSumW)

#all mcbkg that needs to be subtracted
allVVVmc,VVVSumW = HistTools.makeCompositeHists(fOut,"AllVVV", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfVVV(), manager_path), args['lumi'],
    underflow=False, overflow=False)

#This is the non-prompt background
ewkcorr = HistTools.getDifference(fOut, "DataEWKCorrected", "AllData", "AllEWK")
#print zzSumW
#print the sum for a sample (zz4l-powheg)
#zzSumWeights = zzSumW["zz4l-powheg"]

print("Signals: ",ewkSumW)
#print the sum for a sample (zz4l-powheg)
zzSumWeights = ewkSumW["zz4l-powheg"]
#print "sumW (zz4l-powheg): ",zzSumWeights

#getHistInDic function also takes care of adding the histograms in eemm+mmee, hence the input here is channels=[eeee,eemm,mmmm]
#dataHists dictionary
hDataDic=OutputTools.getHistsInDic(alldata,varList,channels)

#SigHists dictionary
#hSigDic=OutputTools.getHistsInDic(allzzPowheg,varList,channels)

hSigDic=OutputTools.getHistsInDic(ewkmc,varList,channels)

#Alt signals containing zzl4-amcatnlo instead of zz4l-powheg
hAltSigDic=OutputTools.getHistsInDic(altSigmc,varList,channels)

#TrueHists dictionary
#hTrueDic=OutputTools.getHistsInDic(allzzPowheg,["Gen"+s for s in varList],channels)
hTrueDic=OutputTools.getHistsInDic(ewkmc,["Gen"+s for s in varList],channels)

#Alt signals containing zzl4-amcatnlo instead of zz4l-powheg
hAltTrueDic=OutputTools.getHistsInDic(altSigmc,["Gen"+s for s in varList],channels)

#print "hTrueDic: ",hTrueDic["GenZZPt_eeee"].Integral()
#ewkmcDic=OutputTools.getHistsInDic(ewkmc,varList,channels)

#Non-prompt background dictionary
hbkgDic=OutputTools.getHistsInDic(ewkcorr,[s+"_Fakes" for s in varList],channels)
#strange python debug
print("channels: ",channels)
if "mmee" in channels:
    channels.remove("mmee")
#VVV background dictionary
hbkgMCDic=OutputTools.getHistsInDic(allVVVmc,varList,channels)
print("hbkgMCDic: ",hbkgMCDic)

runVariables=[]
runVariables.append(args['variable'])
print("runVariables: ",runVariables)

##Systematic histos
systList=[]
for chan in channels:
    for sys in ["Up","Down"]:
        for s in runVariables:
            systList.append(varNames[s]+"_CMS_pileup"+sys)
            for lep in set(chan):
                systList.append(varNames[s]+"_CMS_eff_"+lep+sys)

print(systList)
hSigSystDic=OutputTools.getHistsInDic(ewkmc,systList,channels)

hbkgMCSystDic=OutputTools.getHistsInDic(allVVVmc,systList,channels)


#for chan in channels:
#    for varName in varList:
##Scale and PDF Thoeretical uncertainties
#        for processName in sigSampleList:
#            theoryVariations = addTheoryVar(processName, 'scale', range(1, 10), exclude=[7, 9], central=0)
#            if processName in theoryVariations:
#                weightHist = ewkmc.FindObject(weightHistName(chan, varName))
#                if not weightHist:
#                    logging.warning("Failed to find %s. Skipping" % self.weightHistName(chan, processName))
#                    continue
#                theoryVars = theoryVariations[processName]
#                scaleHists = HistTools.getScaleHists(weightHist, processName, self.rebin,
#                                entries=theoryVars['scale']['entries'], central=theoryVars['scale']['central'])
#                #Adding scale Histograms to ewkmc (signal) group
#                ewkmc.extend(scaleHists)
#dictionaries to store output paths
OutputDirs={}
UnfoldOutDirs={}

SFhistos,PUhistos = generateAnalysisInputs()
#So even when selector runs, run the unfolding procedure only on the variables provided.

#Make differential cross sections normalizing to unity area.')
norm = not args['noNorm']
#normalize with the luminosity instead of area under the curve
normFb = args['NormFb']
#for varName in varNames.keys():
for varName in runVariables:
    print("varName:", varNames[varName])
    # save unfolded distributions by channel, then systematic
    hUnfolded = {}
    hTrue = {}
    hTrueAlt = {}
    hErr = {}
    hErrTrue = {}
    for chan in channels:
        print("channel: ",chan)
        print("hUnfolded: ",hUnfolded)
        print("hTrue: ",hTrue)
        OutputDir=plotDir+"/"+chan+"/plots"
        if chan not in OutputDirs:
            OutputDirs[chan]=OutputDir
        if not os.path.exists(OutputDir):
            mkdir(OutputDir)
            OutputDirs[chan]=OutputDir
        UnfoldOutDir=UnfoldDir+"/"+chan+"/plots"
        if chan not in UnfoldOutDirs:
            UnfoldOutDirs[chan]=UnfoldOutDir
        if not os.path.exists(UnfoldOutDir):
            mkdir(UnfoldOutDir)
        #print "varName:", varNames[varName]
        #ewkSig = ewkmcDic[chan][varNames[varName]]
        #print "TotSigHist: ", ewkSig,", ",ewkSig.Integral()
        #pdb.set_trace()
        responseMakers,altResponseMakers = generateResponseClass(varName, chan,sigSampleDic,sigSamplesPath,ewkSumW,PUhistos,SFhistos)
        #gdb_debugger.hookDebugger()
        #pdb.set_trace()
        hUnfolded[chan], hTrue[chan],hTrueAlt[chan] = unfold(varName,chan,responseMakers,altResponseMakers,hSigDic,hAltSigDic,hSigSystDic,hTrueDic,hAltTrueDic,hDataDic,hbkgDic,hbkgMCDic,hbkgMCSystDic,nIterations,OutputDir)
        print("returning unfolded? ",hUnfolded[chan])
        print("returning truth? ",hTrue[chan])
        #print ("UnfoldOutDir: ",UnfoldOutDir)

        if not args['noSyst']:
            hErr[chan]= _generateUncertainties(hUnfolded[chan],norm)
            print("hErr[",chan,"]: ",hErr[chan])
            (hUncUp, hUncDn) = _sumUncertainties(hErr[chan],varName)
        #hErrTrue[chan] = _generateUncertainties(hTrue[chan],norm)
        #(hTrueUncUp, hTrueUncDn) = _sumUncertainties(hErrTrue[chan],varName)

            generatePlots(hUnfolded[chan][''],hUncUp,hUncDn,hTrue[chan][''],hTrueAlt[chan][''],varName,norm,normFb,args['lumi'],UnfoldOutDir)
    if args['makeTotals']:
        if "eeee" in channels:
            hTot = hUnfolded["eeee"]['']
            hTrueTot = hTrue["eeee"]['']
            hTrueAltTot = hTrueAlt["eeee"]['']
            #channels.remove("eeee")
        print("channels before adding histos: ",channels)
        for c in ["eemm","mmmm"]:
            hTot.Add(hUnfolded[c][''])
            hTrueTot.Add(hTrue[c][''])
            hTrueAltTot.Add(hTrueAlt[c][''])
        #Make OutputDir for total (4e+2e2m+4m) unfolded plots
        UnfoldOutDir=UnfoldDir+"/"+"tot"+"/plots"
        if "tot" not in UnfoldOutDirs:
            UnfoldOutDirs["tot"]=UnfoldOutDir
        if not os.path.exists(UnfoldOutDir):
            mkdir(UnfoldOutDir)
        print("hErr.values(): ",hErr.values())
        hErrTot = _combineChannelUncertainties(*hErr.values())
        hTotUncUp, hTotUncDn = _sumUncertainties(hErrTot,varName)
        generatePlots(hTot,hTotUncUp,hTotUncDn,hTrueTot,hTrueAltTot,varName,norm,normFb,args['lumi'],UnfoldOutDir)

#print(OutputDirs)
#print(UnfoldOutDirs)
#for cat in channels:
for cat in ["eeee","eemm","mmmm","tot"]:
    #This is where we save all the plots
    #print(os.path.expanduser(OutputDirs[cat].replace("/plots", "")))
    #print(os.path.expanduser(OutputDirs[cat].replace("/plots", "")).split("/")[-1])
    if args['plotResponse'] and cat!="tot":
        makeSimpleHtml.writeHTML(os.path.expanduser(OutputDirs[cat].replace("/plots", "")), "2D ResponseMatrices (from MC)")
    #print(os.path.expanduser(UnfoldOutDirs[cat].replace("/plots", "")).split("/")[-1])
    makeSimpleHtml.writeHTML(os.path.expanduser(UnfoldOutDirs[cat].replace("/plots", "")), "Unfolded Distributions (from MC)")
    #print("it crashes already")

#if args['test']:
#    exit(0)

#
