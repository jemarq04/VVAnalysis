"""

Little script to plot Senka's 1D limit curves as a function of mass cutoff
in the same style as the rest of the paper.

Nate Woods, U. Wisconsin

"""

import logging

from rootpy import log as rlog

rlog = rlog["/aTGCLimits1D"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.ROOT import gStyle

from PlotTools import CMS_lumi, PlotStyle, pdfViaTex

CMS_lumi.lumiTextSize = 1.2
CMS_lumi.cmsTextSize = 1.3
CMS_lumi.lumiTextOffset = 0.01
CMS_lumi.cmsTextOffset = 0.01

from os import makedirs as mkdirp
from os.path import exists, isdir
from os.path import join as pjoin

indir = "/data/nawoods/aTGCLimits1D"
fTemplate = "aTGCCutoff_canvas_f{}{}.root"  #'plot_expObs_Cutoff_f{}{}_noPrelim_May10_fit_.root'
fNames = {vf + str(nf): pjoin(indir, fTemplate.format(nf, vf)) for nf in (4, 5) for vf in "gz"}

outdir = "/afs/cern.ch/user/n/nawoods/www/aTGCLimits1D_paper"
texdir = pjoin(outdir, "texs")
pdfdir = pjoin(outdir, "pdfs")

if not exists(texdir):
    mkdirp(texdir)
elif not isdir(texdir):
    raise OSError(f"There is already some non-directory object called {texdir}.")
if not exists(pdfdir):
    mkdirp(pdfdir)
elif not isdir(pdfdir):
    raise OSError(f"There is already some non-directory object called {pdfdir}.")

style = PlotStyle(False)
gStyle.SetOptFit(0)
gStyle.SetPadColor(0)
gStyle.SetOptTitle(0)

vName = {
    "g": r"\\gamma",
    "z": r"\\text{Z}",
}

for fType, fName in fNames.items():
    with root_open(fName) as f:
        c = asrootpy(f.c1_par_pol2bs_fit)  # c1_par_expobs_fit)

        sub = {
            # totally redo y-axis title
            rf"$f^{vName[fType[0]]}_{fType[1]}\\ 95\\% \\ \\text{{CL}}$": r"\} 95\\%CL",
            # make x-axis title bold
            r"m_{4\\ell} \\ \\text{cutoff (GeV)}": r"m_\{4\\ell\}\\ \\text\{cut-off \(GeV\)\}",
            # center infinity
            r"\\!\\!\\infty": r"\\infty",
        }

        style.setCMSStyle(c, "", True, "", intLumi=35860.0, forLatex=True)
        c.Draw()
        c.Print(pjoin(outdir, f"limits1DVsCutoff_{fType}.png"))
        pdfViaTex(c, f"limits1DVsCutoff_{fType}", texdir, pdfdir, **sub)
