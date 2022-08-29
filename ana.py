from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
#import argparse

#parser = argparse.ArgumentParser(description = 'Run analysis step on specified sample')
#parser.add_argument('-p', dest='process', type=str, required=True, help='bstar or qstar')
#parser.add_argument('-m', dest='masspoint', type=int, required=True, help='masspoint in GeV')
#parser.add_argument('-f', dest='fpoint', type=str, required=True, help='fpoint in 1p0, 0p5, 0p1')

#args = parser.parse_args()

# LHAPDF related
import lhapdf
pset = lhapdf.getPDFSet("NNPDF31_lo_as_0130")
print(pset.description)
pcentral = pset.mkPDF(0)
pdfs = pset.mkPDFs()

class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile = True

    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self, histFile, histDirName)

        self.h_mass = {}
        for idx, pdfv in enumerate(pdfs):
            self.h_mass[idx] = ROOT.TH1F('mass'+str(idx), 'mass'+str(idx), 100, 0, 10000)
            self.addObject(self.h_mass[idx])

    def analyze(self, event):
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        genparticles = Collection(event, "GenPart")
        eventSum = ROOT.TLorentzVector()

        mass=0
        for genp in genparticles:  # loop on muons
            if genp.status==22 and abs(genp.pdgId)==4000005:
                #print genp.p4().Pt(),genp.mass,genp.status,genp.pdgId
                mass = genp.mass
        print mass

        # check also
        # https://cmssdt.cern.ch/lxr/source/PhysicsTools/Heppy/src/PdfWeightProducerTool.cc
        id1 = event.Generator_id1
        id2 = event.Generator_id2
        Q = event.Generator_scalePDF
        #print Q
        x1 = event.Generator_x1
        x2 = event.Generator_x2
        orgpdf1 = pcentral.xfxQ(id1, x1, Q) / x1;
        orgpdf2 = pcentral.xfxQ(id2, x2, Q) / x2;
        for idx, pdfv in enumerate(pdfs):
            newpdf1 = pdfs[idx].xfxQ(id1, x1, Q) / x1;
            newpdf2 = pdfs[idx].xfxQ(id2, x2, Q) / x2;
            #print idx,orgpdf1,orgpdf2,newpdf1,newpdf2,newpdf1/orgpdf1,newpdf2/orgpdf2
            self.h_mass[idx].Fill(mass,newpdf1/orgpdf1*newpdf2/orgpdf2)  # fill histogram

        # select events with at least 2 muons
        if len(muons) >= 2:
            for lep in muons:  # loop on muons
                eventSum += lep.p4()
            for lep in electrons:  # loop on electrons
                eventSum += lep.p4()
            for j in jets:  # loop on jets
                eventSum += j.p4()
            #self.h_vpt.Fill(eventSum.Pt())  # fill histogram

        return True

if __name__ == '__main__':

    preselection = ""

    process = args.process
    masspoint = args.masspoint
    fpoint = args.fpoint

    with open('/cms/data/jsamudio/ana/exo/CMSSW_10_2_13_patch1/src/NANO/tmp/das_cache/%s_m%d_f%s.txt' %(process, masspoint, fpoint)) as f:
            files = f.read().splitlines()
#files = [
        #"../files/NANO/8D3CEE65-EE1B-2B43-9E00-7D36F6E580C7.root"
#    "root://cmsxrootd.fnal.gov//store/mc/RunIIAutumn18NanoAODv7/BstarToGJ_M-7000_f-1p0_TuneCP5_13TeV-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/250000/8D3CEE65-EE1B-2B43-9E00-7D36F6E580C7.root",
#    "root://cmsxrootd.fnal.gov//store/mc/RunIIAutumn18NanoAODv7/BstarToGJ_M-7000_f-1p0_TuneCP5_13TeV-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/250000/9D638C8A-55E2-0D45-BF14-46BA9B53E6DF.root"]
    p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                      ExampleAnalysis()], noOut=True, histFileName="histOut_%s_%d_%s.root" %(process, masspoint, fpoint), histDirName="plots")
    p.run()

# /BstarToGJ*M-7000*/*Autumn*/NANOAODSIM
# /BstarToGJ_M-7000_f-1p0_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM

