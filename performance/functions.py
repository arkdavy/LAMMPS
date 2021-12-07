
def dataSelector(runcfg, threads, gpus):

    """Retruns a simple classification of the data, sets variables which allows for a differentiation of calculation types"""

    suffix, title, collectionSize = '', None, None

    # the following selection of versions/toolchais is used at all non-gpu calculations
    collection = {
        '29Sep2021': ['foss-2020b-kokkos-omp','foss-2021b-kokkos-omp', 'iomkl-2019b-kokkos-omp'],
         '3Mar2020': ['foss-2020a-kokkos-omp']
      }

    # for kokkos
    str_thds, str_gpus = '', ''

    
    if (runcfg.find('omp')>0 or runcfg.find('cuda-kokkos')>=0): str_thds = 't {}'.format(threads)
    #print(runcfg, threads, str_thds)

    if gpus > 0               : str_gpus = 'g {}'.format(gpus)

    if (runcfg == 'cpu-opt'):
        suffix = '-sf opt'
        title = 'MPI (OPT pkg)'
    if (runcfg == 'cpu-bare'):
        suffix = ''
        title = 'MPI (bare LAMMPS)'
    if (runcfg == 'cuda-kokkos'):
        title = 'MPI + cuda (kokkos pkg)'
        suffix = '-k on {} -sf kk'.format(str_gpus)
        collection = { '29Sep2021': ['foss-2020b-cuda-kokkos','foss-2021b-cuda-kokkos'] }
    if (runcfg == 'cuda-kokkos-omp'):
        title = 'MPI + cuda + OpenMP (kokkos pkg)'
        suffix = '-k on {} {} -sf kk'.format(str_gpus, str_thds)
        collection = { '29Sep2021': ['foss-2020b-cuda-kokkos-omp','foss-2021b-cuda-kokkos-omp'] }
    if (runcfg == 'cuda-gpu'):
        title = 'MPI + cuda (GPU pkg)'
        suffix = '-sf gpu -pk gpu {}'.format(gpus)
        collection = { '29Sep2021': ['foss-2020b-cuda-gpu','foss-2021b-cuda-gpu'] }
    if (runcfg == 'cuda-gpu-omp'):
        title = 'MPI + cuda + OpenMP (GPU pkg)'
        suffix = '-sf gpu -pk gpu {}'.format(gpus)
        collection = { '29Sep2021': ['foss-2020b-cuda-gpu','foss-2021b-cuda-gpu'] }
    if (runcfg == 'cpu-kokkos'): 
        title = 'MPI (kokkos)'
        suffix = '-k on {} -sf kk'.format(str_thds)
        collection = {
            '29Sep2021': ['foss-2020b-kokkos','foss-2021b-kokkos', 'iomkl-2019b-kokkos'],
             '3Mar2020': ['foss-2020a-kokkos']
        }
    if (runcfg == 'cpu-kokkos-omp'): 
        title = 'MPI + openMP (kokkos)'
        suffix = '-k on {} -sf kk'.format(str_thds)
    if (runcfg == 'cpu-omp'):
        title = 'MPI + openMP (OMP pkg)'
        suffix = '-sf omp'.format(str_thds)

    collectionSize = 0
    for version, toolchains in collection.items():
       for toolchain in toolchains:
           collectionSize += 1

    return suffix, title, collection, collectionSize


def cpusAtThreads(threads, nsteps, mincpus, maxcpus, rcfg, ngpu):

    mintasks = max(1,int(mincpus/threads))
    maxtasks = int(maxcpus/threads)

#    if (rcfg == 'cuda-kokkos-mpicuda'):
#       step = max(1,int((maxtasks-mintasks)/max(1,nsteps-int(ngpu/2)-2)))
#    else:
    step = max(1,int((maxtasks-mintasks)/nsteps))

    tasks = list(range(mintasks, maxtasks, max(1,step))) 
    try:
      tasks[0] = mintasks
    except:
      tasks = [1]
    if (len(tasks)>1):
        if tasks[0]==tasks[1]: tasks.remove(tasks[0])

    if tasks[-1] != maxtasks:
        tasks.append(maxtasks)

#    if (rcfg == 'cuda-kokkos-mpicuda'):
#        # leave only primes of gpu number in the tasks list
#        new_tasks = []
#        for t in tasks:
#           new_tasks.append(t - t % ngpu)
#        tasks = new_tasks
#        include = list(range(1,ngpu+4))
#        include.extend(tasks)
#        include = set(include)
#        tasks = list(include)
#        tasks.sort()
    if (rcfg.find('cuda-kokkos')>=0):
        tasks = [ngpu]
    elif (rcfg.find('cuda-gpu')>=0):
        tasks = [ngpu]
            
    return tasks



