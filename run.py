import argparse
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description = 'Run analysis step on specified sample')
parser.add_argument('-p', dest='process', type=str, required=True, help='bstar or qstar')
parser.add_argument('-m', dest='masspoint', type=int, required=True, help='masspoint in GeV')
parser.add_argument('-f', dest='fpoint', type=str, required=True, help='fpoint in 1p0, 0p5, 0p1')
parser.add_argument('--noana', dest='noana', action ='store_true', required=False, help = 'Run Ana', default=False)
args = parser.parse_args()

from ana import ExampleAnalysis
import plotHist as pH

preselection = ""

process = args.process
masspoint = args.masspoint
fpoints = args.fpoint
if not args.noana:
    with open('/cms/data/jsamudio/ana/exo/CMSSW_10_2_13_patch1/src/NANO/tmp/das_cache/%s_m%d_f%s.txt' %(process, masspoint, fpoints)) as f:
        files = f.read().splitlines()
    p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
        ExampleAnalysis()], noOut=True, histFileName="histOut_%s_%d_%s.root" %(process, masspoint, fpoints), histDirName="plots")
    p.run()

bin_contents, edges, binError, xsec, signal_peak_frac, starred, fpoint = pH.build_plotpoints(process, masspoint, fpoints)
yield_mean, yield_err = pH.get_mean_PDFerror(xsec)
signal_peak_frac_mean, signal_peak_frac_err = pH.get_mean_PDFerror(signal_peak_frac)
pH.makeplot(bin_contents, edges, binError, process, masspoint, fpoint, fpoints, yield_err/yield_mean, signal_peak_frac_mean, signal_peak_frac_err/signal_peak_frac_mean, starred)
