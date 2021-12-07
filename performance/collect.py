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
systems = ['lj-shared']
#runconfig = ['cpu-bare','cpu-opt']

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

  timing2Table = {}
  

  # cuda pictures
  figcuda, axcuda = initFigure(6, 4, maxcpus, 'CUDA (Kokkos & GPU pkgs)')
  axcuda.set_xlabel('GPUs')
  axcuda_idx = -1

  # cuda pictures
  figcuda_omp, axcuda_omp = initFigure(6, 4, maxcpus, 'CUDA + OpenMP (Kokkos & GPU pkgs)')
  axcuda_omp.set_xlabel('GPUs')
  axcuda_omp_idx = -1

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

        timing2Table[rcfg] = {}
        for version, compilers in collection.items():

            for compiler in compilers:


                timing2Table[rcfg][compiler]={}

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

                       timing2Table[rcfg][compiler][thrd] = y[idx[-1]]

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

                        # for the last ran I have used '-omp' kokkos module, re-write the corresponding label
                        if (rcfg.find('kokkos')>0): lammps_label = "LAMMPS-{}-{} ({}|{})".format(version+'-omp', compiler+'-omp', firsty, lasty)

                        axcuda_idx += 1

                        ax0.set_xlim([0.8,3.2])

                        axcuda.set_xlim([0.8,3.2])

                        plotxy(x[idx], y[idx], '-*', axcuda, color = lineBaseColors[axcuda_idx], 
                                                markersize = markersize, label = lammps_label)

                        for xx, yy  in zip(x[idx], y[idx]):
                          timing2Table[rcfg][compiler][xx] = yy

                    if rcfg == 'cuda-gpu-omp' or rcfg == 'cuda-kokkos-omp':

                        axcuda_omp_idx += 1

                        ax0.set_xlim([0.8,3.2])

                        axcuda.set_xlim([0.8,3.2])

                        plotxy(x[idx], y[idx], '-*', axcuda_omp, color = lineBaseColors[axcuda_omp_idx], 
                                                markersize = markersize, label = lammps_label)

                        for xx, yy  in zip(x[idx], y[idx]):
                          timing2Table[rcfg][compiler][xx] = yy

                    if (rcfg.find('cpu') >=0):
                          ax0.set_xlim(xlimcpu)
                          ax0.set_ylim(ylimcpu)
                          timing2Table[rcfg][compiler][1] = y[idx[-1]]



        ax0.legend(fontsize=9)
 #       adjustLegend(ax0.get_legend(), fig)
        if (axs):
           for ax in axs:  ax.legend(fontsize=9)

        #fig.savefig("pictures/"+system+"_"+rcfg+'.pdf')
        fig.savefig("pictures/"+system+"_"+rcfg+'.png')
        plt.clf()

  axcuda.legend(fontsize=9)
  #figcuda.savefig("pictures/"+system+'-cuda.pdf')
  figcuda.savefig("pictures/"+system+'-cuda.png')
  axcuda_omp.legend(fontsize=9)
  #figcuda_omp.savefig("pictures/"+system+'-cuda-omp.pdf')
  figcuda_omp.savefig("pictures/"+system+'-cuda-omp.png')
  plt.clf()

linebreak = "|:---:|:---:|:---:|:---:|:---:|"



print("\nCPU timing (MPI)\n")
printConfigs =  { 'cpu-bare': 'bare LAMMPS', 'cpu-opt': 'OPT package',}
#print(compilers)
items = timing2Table['cpu-bare'].keys()
toolchains = []
for item in items:
       compiler_arr = item.split('-')
       toolchain = '-'.join(compiler_arr[0:2])
       toolchains.append(toolchain)

print("| {} | {} |".format('toolchain',' | '.join(toolchains)))
print(linebreak)
   
for rcfg, name in printConfigs.items():
    compilerthreadsTime = timing2Table[rcfg]
    time_row = [ str(x[1]) for x in compilerthreadsTime.values() ]
    print("| {} | {} |".format(name, ' | '.join(time_row)))

     
print("\nCPU timing (MPI + OpenMP)\n")
printConfigs =  {'cpu-omp': 'OMP package', 'cpu-kokkos-omp':'Kokkos package'}
print("| {} | {} |".format('toolchain'," number of threads "))
print(linebreak)
print("| {} | {} |".format('         '," | ".join(['1','4','8','16'])))
for rcfg, name in printConfigs.items():
    compilerthreadsTime = timing2Table[rcfg]
    print("| {} |".format(name))
    print(linebreak)
    for compiler, threadsTime in  compilerthreadsTime.items():
        compiler_arr = compiler.split('-')
        toolchain = '-'.join(compiler_arr[0:2])
        threads_row, time_row = [], []
        for threads, time in threadsTime.items():
           threads_row.append(threads)
           time_row.append(str(time))
        print("| `{}` | {} |".format(toolchain," | ".join(time_row)))


print("\nGPU timing\n")
printConfigs = {'cuda-kokkos':'Kokkos package', 'cuda-gpu': 'GPU package'}

print("| {} | {} |".format('toolchain'," number of gpus "))
print(linebreak)
print("| {} | {} |".format('         '," | ".join(['1','2','3'])))
for rcfg, name in printConfigs.items():
    compilerthreadsTime = timing2Table[rcfg]
    print("| {} |".format(name))
    print(linebreak)
    for compiler, threadsTime in  compilerthreadsTime.items():
        compiler_arr = compiler.split('-')
        toolchain = '-'.join(compiler_arr[0:2])
        threads_row, time_row = [], []
        for threads, time in threadsTime.items():
           threads_row.append(threads)
           time_row.append(str(time))
        print("| `{}` | {} |".format(toolchain," | ".join(time_row)))


