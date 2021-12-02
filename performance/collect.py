import os, re, sys
import subprocess
import datetime
import glob
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from functions import dataSelector
from functionsPlot import *
from setup import *

def adjustLegend(legend, figure):
   renderer = figure.canvas.get_renderer()
   shift = max([t.get_window_extent(renderer).width for t in legend.get_texts()])
   for t in legend.get_texts():
        t.set_ha('right') # ha is alias for horizontalalignment
        t.set_position((shift,0))

# overwrite the default setup variables here (for shorted execution)
systems = ['lj','lj-shared']
#runconfig = ['cpu-opt', 'cpu-kokkos','cpu-omp','cpu-kokkos-omp']

print("*** COLLECTING ***")

timing = {}
for system in systems:

    for rcfg in runconfig:

        print("system, rcfg: ", system, rcfg)

        _,title,collection,_ = dataSelector(rcfg, 1, 1)

        for version, compilers in collection.items():

            for compiler in compilers:

                  # initial path
                  p_init = Path.cwd()
                  
                  prefix = system + '/' + rcfg + '/'
                  
                  p = Path(prefix+version)
  
                  # path where calculations will be running
                  p_run = Path(prefix+version+"/"+compiler)

                  print("path: ", p_run)
  
                  tkey = '{}+{}+{}+{}'.format(system,rcfg,version,compiler)
                  timing[tkey] = []
  
                  fileList = glob.glob(prefix+version+"/"+compiler+'/MPI*')
                  for fle in fileList:

                       line = subprocess.check_output(['tail', '-2', fle]).decode()
                       try:
                         strTime = line.strip().split()[-1]
                       except:
                         strTime = line.strip().split()[-2]


                       [hours, minutes, seconds] = [int(x) for x in strTime.split(':')]
                       x = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

                       m = re.search('MPIx(\d+)_GPUx(\d+)_THRDSx(\d+)',fle)
                       tasks, gpus, threads = int(m.group(1)), int(m.group(2)), int(m.group(3))
                       timing[tkey].append([threads*tasks, x.seconds, gpus, threads, tasks])


print(timing)

print("*** PLOTTING ***")

xlimcpu = (10.5, 132.5)
ylimcpu = (85, 560.0)


for system in systems:

  # cuda pictures
  figcuda, axcuda = initFigure(6, 4, maxcpus, 'CUDA (Kokkos & GPU pkgs)')
  axcuda.set_xlabel('GPUs')
  axcuda_idx = -1

  for rcfg in runconfig:

        print("system, rcfg: ", system, rcfg)

        _,title,collection,_ = dataSelector(rcfg, 1, 1)

        axs = None
        if (rcfg in ('cpu-omp','cpu-kokkos-omp')):
           fig, ax0, axs = initFigureRow(6, 6, 2, 2, maxcpus, title)
        else:
           # cpu-kokkos,  
           fig, ax0 = initFigure(6, 2.5, maxcpus, title)

        axs_idx = -1
        for version, compilers in collection.items():

            for compiler in compilers:

                axs_idx += 1

                tkey = '{}+{}+{}+{}'.format(system,rcfg,version,compiler)

                infoLine = "\n {}+{}+{}+{}".format(system,rcfg,version,compiler)
                try:
                  timing_vc = np.array(timing[tkey])
                except:
                  excLine = "It seems that the following "+infoLine+"key does not exsit in the 'timing' dictionary"
                  raise Exception()

                infoLine = "system, runconfig, version, compiler: \n {}, {}, {}, {}".format(system,rcfg,version,compiler)
                try:
                   gpus    = timing_vc[:,2]
                   threads = timing_vc[:,3]
                   tasks   = timing_vc[:,4]
                except:
                  excLine = "It seems that the 'timing dictionary' at "+infoLine+"\n is empty"
                  raise Exception(excLine)
                uniqueThreads = np.unique(threads)
                uniqueTasks   = np.unique(tasks  )
                uniqueGpus    = np.unique(gpus   )

                if (rcfg in ('cpu-omp','cpu-kokkos-omp')):

                    axs[axs_idx].set_title(version + "-" + compiler, fontsize = 8)
                    axs[axs_idx].set_xlim(xlimcpu)
                    axs[axs_idx].set_ylim(ylimcpu)
                    ax0.set_xlim(xlimcpu)
                    ax0.set_ylim(ylimcpu)

                    for thrd in uniqueThreads:

                       idx_threads = np.where(timing_vc[:,3]==thrd)[0]
                       dat = timing_vc[idx_threads,:]
                       x, y = dat[:,0], dat[:,1]
                       idx = np.argsort(x)

                       firsty, lasty = y[idx[0]], y[idx[-1]]
                       lammps_label = "LAMMPS-{}-{} ({}|{})".format(version, compiler, firsty, lasty)
                       thread_label = "thrds={} ({}|{})".format(thrd, firsty, lasty)


                       if (thrd == 1):  plotxy(x[idx], y[idx], '-*', ax0, color = lineBaseColors[axs_idx], 
                                                                markersize = markersize, label = lammps_label)

                       mixedColor = colorFader(lineBaseColors[axs_idx],  lineFadeColors[axs_idx], (thrd-1)/np.amax(uniqueThreads), power=0.5)
                       plotxy(x[idx], y[idx], '-*', axs[axs_idx], color = mixedColor, 
                                               markersize = markersize, label = thread_label)



                else:

                    data = timing_vc
                    x, y = data[:,0], data[:,1]
                    idx = np.argsort(x)

                    firsty, lasty = y[idx[0]], y[idx[-1]]
                    lammps_label = "LAMMPS-{}-{} ({}|{})".format(version, compiler, firsty, lasty)

                    lineBaseColors[axs_idx]
                    plotxy(x[idx], y[idx], '-*', ax0, color = lineBaseColors[axs_idx], 
                                            markersize = markersize, label = lammps_label)

                    if rcfg == 'cuda-gpu' or rcfg == 'cuda-kokkos':

                        axcuda_idx += 1

                        ax0.set_xlim([0.8,3.2])

                        axcuda.set_xlim([0.8,3.2])

                        plotxy(x[idx], y[idx], '-*', axcuda, color = lineBaseColors[axcuda_idx], 
                                                markersize = markersize, label = lammps_label)

                    if (rcfg.find('cpu') >=0):
                          ax0.set_xlim(xlimcpu)
                          ax0.set_ylim(ylimcpu)



        ax0.legend(fontsize=9)
 #       adjustLegend(ax0.get_legend(), fig)
        if (axs):
           for ax in axs:  ax.legend(fontsize=9)

        fig.savefig("pictures/"+system+"_"+rcfg+'.pdf')
        fig.savefig("pictures/"+system+"_"+rcfg+'.png')
        plt.clf()


  axcuda.legend(fontsize=9)
  figcuda.savefig("pictures/"+system+'-cuda.pdf')
  figcuda.savefig("pictures/"+system+'-cuda.png')
  plt.clf()
  

