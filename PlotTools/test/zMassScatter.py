"""

Make a scatter plot of m_Z2 vs m_Z1.

Author: Nate Woods, U. Wisconsin

"""

import logging

from rootpy import log as rlog

rlog = rlog["/zMassScatter"]
# don't show most silly ROOT messages
logging.basicConfig(level=logging.WARNING)
rlog["/ROOT.TUnixSystem.SetDisplay"].setLevel(rlog.ERROR)

from os import makedirs as mkdir
from os.path import exists, isdir, join

from Analysis import standardZZData
from rootpy.plotting import Canvas, Graph, Legend
from rootpy.plotting.utils import draw

from PlotTools import PlotStyle as _Style
from Utilities import Z_MASS

inDir = "uwvvNtuples_data_10mar2017_LooseSIPLooseVtx"
outDir = "/afs/cern.ch/user/n/nawoods/www/UWVVPlots/zMassScatter_LooseSIP"
lumi = 35860.0

colors = {"eeee": "b", "eemm": "r", "mmmm": "forestgreen"}
markers = {"eeee": 20, "eemm": 21, "mmmm": 22}
titles = {"eeee": "4\\text{e}", "eemm": "2\\text{e}2\\mu", "mmmm": "4\\mu"}

if not exists(outDir):
    mkdir(outDir)
elif not isdir(outDir):
    raise OSError(f"There is already some non-directory object called {outDir}.")


def getMZ1_2e2m(row):
    if abs(row.e1_e2_Mass - Z_MASS) < abs(row.m1_m2_Mass - Z_MASS):
        return row.e1_e2_Mass
    return row.m1_m2_Mass


def getMZ2_2e2m(row):
    if abs(row.e1_e2_Mass - Z_MASS) < abs(row.m1_m2_Mass - Z_MASS):
        return row.m1_m2_Mass
    return row.e1_e2_Mass


getMZ1 = {
    "eeee": lambda row: row.e1_e2_Mass,
    "eemm": getMZ1_2e2m,
    "mmmm": lambda row: row.m1_m2_Mass,
}
getMZ2 = {
    "eeee": lambda row: row.e3_e4_Mass,
    "eemm": getMZ2_2e2m,
    "mmmm": lambda row: row.m3_m4_Mass,
}

style = _Style()

legParams = {
    "full": {
        "leftmargin": 0.1,
        "rightmargin": 0.55,
    },
    "z4l": {
        "leftmargin": 0.6,
    },
}

for ana in ["full", "z4l"]:
    data = standardZZData("zz", inDir, ana)

    g = {}
    for ch, sample in data.itersamples():
        nPts = sample.getEntries()
        g[ch] = Graph(nPts, title=titles[ch])
        g[ch].color = colors[ch]
        g[ch].markerstyle = markers[ch]
        g[ch].drawstyle = "P"
        g[ch].SetMarkerSize(g[ch].GetMarkerSize() * 1.5)
        if ch == "mmmm":
            g[ch].SetMarkerSize(g[ch].GetMarkerSize() * 1.18)

        for i, row in enumerate(sample.rows()):
            g[ch].SetPoint(i, getMZ1[ch](row), getMZ2[ch](row))

    if ana == "z4l":
        xlimits = (40.0, 90.0)
        ylimits = (0.0, 60.0)
    else:
        xlimits = (40.0, 120.0)
        ylimits = (0.0, 120.0)

    c = Canvas(1000, 1000)
    (xaxis, yaxis), things = draw(
        g.values(),
        c,
        xtitle="m_{\\text{Z}_1} \\, [\\text{GeV}]",
        ytitle="m_{\\text{Z}_2} \\, [\\text{GeV}]",
        xlimits=xlimits,
        ylimits=ylimits,
    )
    yaxis.SetTitleSize(yaxis.GetTitleSize() * 0.9)
    c.Update()
    leg = Legend(
        g.values(), c, textsize=0.04, header="\\text{     Data}", entrysep=0.01, entryheight=0.04, **legParams[ana]
    )
    leg.Draw("same")
    style.setCMSStyle(c, "", True, "", 13, lumi)

    c.Print(join(outDir, f"mZ2VsmZ1_{ana}.png"))
