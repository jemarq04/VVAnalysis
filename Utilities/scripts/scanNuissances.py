import ROOT
import subprocess
import math

def getMuAndErr(arg):
    if subprocess.call(["bash", "runCombine.sh", "mu", arg, "noBlind", ]):
        return (0, 0, 0)
    rtfile = ROOT.TFile("fitDiagnostics.root")
    tree = rtfile.Get("tree_fit_sb")
    row = next(tree.__iter__())

    return (row.r, row.rLoErr, row.rHiErr)

muCentral, muCentralErrDown, muCentralErrUp = getMuAndErr("")

results = {}

nuisances = {
    #"CMS_res_j" : "simple",
    #"CMS_pileup" : "simple",
    "CMS_scale_j" : "simple",
    #"lepton_unc" : "group",
    #"lumi2016_13TeV" : "simple",
    #"CMS_eff_b" : "simple",
    #"QCDscale_EW-WZjj,pdf_EW-WZjj" : "simple",
    #"CMS_norm_QCD-WZjj,pdf_QCD-WZjj,QCDscale_QCD-WZjj" : "simple",
    #"nonprompt_all" : "group" ,
    #"background_theory" : "group",
    #"prop_binmmm_bin0,prop_binemm_bin0,prop_bineem_bin0,prop_bineee_bin0": "simple" ,
}
for nuisance, nutype in nuisances.items():
    if nutype == "simple":
        arg = "--freezeParameters=%s" % nuisance
    else:
        arg = "--freezeNuisanceGroup=%s" % nuisance
    mu, muErrDown, muErrUp = getMuAndErr(arg)
    muErrDownRel = muErrDown/mu if mu > 0 else 0
    muErrUpRel = muErrUp/mu if mu > 0 else 0
    print("muErrUpRel", muErrUpRel)
    print("muErrDownRel", muErrDownRel)
    muCentralErrDownRel = muCentralErrDown/muCentral
    muCentralErrUpRel = muCentralErrUp/muCentral
    print("muCentralErrUpRel", muCentralErrUpRel)
    print("muCentralErrDownRel", muCentralErrDownRel)
    print("muCentral", muCentral)
    print("muCentralErrUp", muCentralErrUp)
    print("muCentralErrDown", muCentralErrDown)

    nuErrDown = math.sqrt(abs(muCentralErrDownRel**2-muErrDownRel**2))
    nuErrUp = math.sqrt(abs(muCentralErrUpRel**2-muErrUpRel**2))
    results[nuisance] = { "mu" : mu,
        "errDown" : muErrDown,
        "errUp" : muErrUp,
        "nuOnlyErrDown" : nuErrDown,
        "nuOnlyErrUp" : nuErrUp,
    }

print("-"*80)
print("    Full fit gives %0.3f^{%0.3f}_{%0.3f}" % (muCentral, muCentralErrUp, muCentralErrDown))
print("")
for nuisance in nuisances:
    res = results[nuisance]
    print("-"*80)
    print("    Nuisance %s" % nuisance)
    print("    Removing nuisance gives %0.3f^{%0.3f}_{%0.3f}" % \
            (res["mu"], res["errUp"], res["errDown"]))
    print("    Only from nuisance: +%0.3f -%0.3f" % \
            (res["nuOnlyErrUp"], res["nuOnlyErrDown"]))

