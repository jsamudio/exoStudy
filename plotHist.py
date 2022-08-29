import ROOT
import numpy as np
import  matplotlib.pyplot as plt
import argparse


tf = ROOT.TFile('histOut.root')

tf.cd("plots")
tf.ls()

npdf=100
th={}
xsec=[]
signal_peak_frac=[]
yvals = [[]]
# ---
def get_mean_PDFerror(arr):
    nparr = np.array(arr)
    nparr_mean = np.array(nparr.size * [np.mean(nparr)])

    # mean yield
    mean=np.mean(nparr)

    # variation in the yield for PDF error
    # https://arxiv.org/abs/1510.03865
    err=np.sqrt(np.mean((nparr-nparr_mean)**2))
    if nparr.size>0:
        err = err * np.sqrt(nparr.size / (nparr.size - 1))

    return mean, err

def makeplot(yvals, edges, binError, process, masspoint, fpoint, fpoints, yield_frac, signal_peak_frac_mean, signal_peak_frac, starred):
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1,1,1)

    ax.plot(edges, yvals[0], ls = 'steps-mid', lw = 2, label = 'Sample' )
    ax.plot(edges, yvals[0] + binError, ls = 'steps-mid', c = 'r')
    ax.plot(edges, yvals[0] - binError, ls = 'steps-mid', c = 'r')
    ax.fill_between(edges, yvals[0] + binError, yvals[0] - binError, step = 'mid', color = 'r', alpha = 0.6, label = 'PDF unc.')
    ax.legend()
    ax.text(0.03, 0.95, '%s, f = %.1f, M = %d TeV' %(starred, fpoint, masspoint/1000), horizontalalignment='left', verticalalignment='center', transform = ax.transAxes, weight = 'bold')
    ax.text(0.03, 0.9, 'Yield fractional unc. %4.3f%%' %(yield_frac*100), horizontalalignment='left', verticalalignment='center', transform = ax.transAxes)
    ax.text(0.03, 0.85, 'Signal peak fraction and unc. %4.3f +- %4.3f' %(signal_peak_frac_mean ,signal_peak_frac), horizontalalignment='left', verticalalignment='center', transform = ax.transAxes)

    #ax.set_ylim(0, 0.1)
    ax.set_xlabel('m(%s)' %starred)
    fig.savefig('%s_m%d_f%s.pdf' %(process, masspoint, fpoints))


def build_plotpoints(process, masspoint, fpoints):
    process = process
    masspoint = masspoint
    fpoints = fpoints

    tf = ROOT.TFile('histOut_%s_%d_%s.root' %(process, masspoint, fpoints))

    tf.cd("plots")
    tf.ls()

    npdf=100
    th={}
    xsec=[]
    signal_peak_frac=[]
    yvals = [[]]
    binError = []
    meanvals = []
    edges = []
    store = []
    if fpoints == '1p0':
        fpoint = 1.0
    if fpoints == '0p5':
        fpoint = 0.5
    if fpoints == '1p0':
        fpoint = 1.0


    if process == 'bstar':
        starred = 'b*'
    else:
        starred = 'q*'


    mpeak=5000

    for i in range(0, npdf+1):
        th[i] = tf.Get("plots/mass"+str(i))
        if i>=1:
            xsec.append(th[i].GetSum())
        th[i].Scale(1./th[i].GetSum());
        if i != 0:
            signal_peak_frac.append(th[i].Integral(th[i].FindBin(mpeak*0.85),th[i].FindBin(mpeak*1.15)))
    for ibin in range(1,th[0].GetNbinsX()+1):
            bin_center = th[0].GetBinCenter(ibin)
            del store[:]
            for ipdf in range(1, npdf+1):
                store.append(th[ipdf].GetBinContent(ibin))
            binmean, binerr = get_mean_PDFerror(store)
            yvals[0].append(th[0].GetBinContent(ibin))
            binError.append(binerr)
            meanvals.append(binmean)
            edges.append(bin_center)
            #print(bin_center, binmean, binerr)

    binError = np.array(binError)
    meanvals = np.array(meanvals)

    return yvals, edges, binError, xsec, signal_peak_frac, starred, fpoint
# ---


if __name__ == '__main__':

    process = 'bstar'
    masspoint = 7
    fpoint = 1.0

    if process == 'bstar':
        starred = 'b*'
    else:
        starred = 'q*'


    mpeak=5000
    binError = []
    meanvals = []

    for i in range(0, npdf+1):
        th[i] = tf.Get("plots/mass"+str(i))
        if i>=1:
            xsec.append(th[i].GetSum())
        th[i].Scale(1./th[i].GetSum());
        if i != 0:
            signal_peak_frac.append(th[i].Integral(th[i].FindBin(mpeak*0.85),th[i].FindBin(mpeak*1.15)))
    edges = []
    store = []
    for ibin in range(1,th[0].GetNbinsX()+1):
            bin_center = th[0].GetBinCenter(ibin)
            del store[:]
            for ipdf in range(1, npdf+1):
                store.append(th[ipdf].GetBinContent(ibin))
            binmean, binerr = get_mean_PDFerror(store)
            yvals[0].append(th[0].GetBinContent(ibin))
            binError.append(binerr)
            meanvals.append(binmean)
            edges.append(bin_center)
            print(bin_center, binmean, binerr)

    binError = np.array(binError)
    meanvals = np.array(meanvals)

    # ---
    # xsec(yield) array
    #
    print("yields mean and fractional error")

    yield_mean, yield_err = get_mean_PDFerror(xsec)
    print(yield_mean, yield_err/yield_mean)

    # ---
    # mean signal peak fraction
    #

    print("signal_peak_frac (+-15% of the resonance mass) mean and fractional error")

    signal_peak_frac_mean, signal_peak_frac_err = get_mean_PDFerror(signal_peak_frac)
    print(signal_peak_frac_mean, signal_peak_frac_err/signal_peak_frac_mean)

    makeplot(yvals, edges, binError, process, masspoint, fpoint, yield_mean, yield_err/yield_mean, signal_peak_frac_mean, signal_peak_frac_err/signal_peak_frac_mean, starred)
    #print binError

