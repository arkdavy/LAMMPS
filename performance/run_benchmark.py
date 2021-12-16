import sys
import os
from pathlib import Path
from templates import runTemplate, lj, interface
from functions import dataSelector, cpusAtThreads
from setup import *

exclusive = False

submit = True

# overwrite the default setup variables here (for shorted execution)
systems = ['lj']
runconfig = ['cpu-bare','cpu-omp','cpu-opt','cpu-kokkos','cpu-kokkos-omp']
runconfig = ['cpu-omp']

countJobs = 0
for rcfg in runconfig:

    _,_,collection,_ = dataSelector(rcfg, 1, 1)

    print('running task: ', rcfg)
    print('running thrugh the following compilations: ')

    for system in systems:

        for version, compilerModulePair in compilations.items():

          if version not in collection.keys(): continue

          # initial path
          p_init = Path.cwd()
        
          if (exclusive):
            prefix = system + 'exclusive/' + rcfg + '/'
          else:
            prefix = system + '/' + rcfg + '/'

        
          p = Path(prefix+version); p.mkdir(exist_ok=True, parents=True)
        
          for compiler, module in compilerModulePair.items():

            if compiler not in collection[version]: continue

            print(compiler)

            envar = ""
            if (rcfg.find('kokkos')>0):
                # these options are advised by Kokkos, but do not currently work on Sulis
                #if (compiler == 'iomkl-2019b'):
                #       envar = "export OMP_PROC_BIND=true"
                #else:
                #       envar = """export OMP_PROC_BIND=spread\nexport OMP_PLACES=threads"""
                #    pass
                # so passing them out
                pass

            # path where calculations will be running
            p_run = Path(prefix+version+"/"+compiler); p_run.mkdir(exist_ok=True)
        
            # write input file
            p = p_run / "in.lammps"
            with p.open('w') as f:
                if (system=='lj'):
                    f.write(lj())
                elif (system=='interface'):
                    f.write(interface())
                else:
                    raise ValueError("unknown system")
        
            os.chdir(p_run)
            print(Path.cwd())
            if (submit):
 #              os.system('rm run-*')
             #  os.system('rm MPIx*')
               os.system('rm slurm*')
            os.chdir(p_init)
            print(Path.cwd())

            # loop over various GPU and OpenMP settings
            for thrds in threads[rcfg]:
              for gps in gpus[rcfg]:

                tasks = cpusAtThreads(thrds, nsteps_cpus, mincpus, maxcpus, rcfg, gps)

                if (exclusive):
                
                   countJobs += 1
                   run_name = "run-{}_t{}_g{}.sh".format(rcfg, thrds, gps)
                   p = p_run / run_name
                   
                   with p.open('w') as f:
                   
                     suffix,_,_,_ = dataSelector(rcfg, thrds, gps)
                     runtext = runTemplate(system, version, compiler, module, maxcpus, 1, tasks, thrds, gps, suffix, rcfg, envar)
                     f.write(runtext)
                   
                     print ("system, version, compiler | ntasks | nthreads, ngpus: ", 
                             system, version, compiler, "|", " ".join([str(x) for x in tasks]), "|", thrds, gps)
                   
                   # run the calculation
                   os.chdir(p_run)
                   print(thrds, gps, run_name)
                   if (system=='interface'): os.system('cp ../../../../surfaceInput/surfbench/surface.lmp .')
                   if (submit):
                       os.system('sbatch '+run_name)
                   os.chdir(p_init)

                else:

                   for tsk in tasks:
                     countJobs += 1
                     run_name = "run-{}_n{}_t{}_g{}.sh".format(rcfg, tsk, thrds, gps)
                     p = p_run / run_name
                     
                     with p.open('w') as f:
                     
                       suffix,_,_,_ = dataSelector(rcfg, thrds, gps)
                       runtext = runTemplate(system, version, compiler, module, tsk, thrds, [tsk], thrds, gps, suffix, rcfg, envar)
                       f.write(runtext)
                     
                       print ("system, version, compiler | ntasks | nthreads, ngpus: ", 
                               system, version, compiler, "|", " ".join([str(x) for x in [tsk]]), "|", thrds, gps)
                     
                     # run the calculation
                     os.chdir(p_run)
                     print(thrds, gps, run_name)
                     if (system=='interface'): os.system('cp ../../../../surfaceInput/surfbench/surface.lmp .')
                     if (submit):
                         os.system('sbatch '+run_name)
                     os.chdir(p_init)
           
                print()
           
        
print("total Jobs: ", countJobs)
