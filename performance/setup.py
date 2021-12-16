
# edit the following parameters which control the benchmark
mincpus = 16
maxcpus = 128
nsteps_cpus = 6

multigpu = (1,2,3,)
multithread = (1,2,4,8)
multithread = (8,)
multithread_gpu = (42,)
if (maxcpus < max(multigpu)):
    raise ValueError('increase the number of processors')

systems = ['interface','lj']
runconfig = ['cpu-opt', 'cpu-omp','cpu-kokkos','cpu-kokkos-omp','cuda-kokkos','cuda-gpu', 'cuda-kokkos-omp', 'cuda-gpu-omp', 'cpu-bare']

excludeSystems = ['interface']
excludeSystemCompilerPairs = []

# this are fixed parameters
singlethread =(1,)
zerogpu = (0,)

threads = {
            'cpu-bare' : singlethread,
            'cpu-opt' : singlethread,
            'cpu-omp' : multithread,
            'cpu-kokkos' : singlethread,
            'cpu-kokkos-omp' : multithread,
            'cuda-gpu' : singlethread,
            'cuda-kokkos' : singlethread,
            'cuda-gpu-omp' : multithread_gpu,
            'cuda-kokkos-omp' : multithread_gpu,
        }
gpus    = {
            'cpu-bare' : zerogpu,
            'cpu-opt' : zerogpu,
            'cpu-omp' : zerogpu,
            'cpu-kokkos' : zerogpu,
            'cpu-kokkos-omp' : zerogpu,
            'cuda-gpu' : multigpu,
            'cuda-kokkos' : multigpu,
            'cuda-gpu-omp' : multigpu,
            'cuda-kokkos-omp' : multigpu,
        }

# list of available versions, toolchan descriptoirs and modules
compilations = {
    '29Sep2021': {
       'foss-2020b-cuda-kokkos'        :'GCC/10.2.0  CUDA/11.1.1  OpenMPI/4.0.5 LAMMPS/29Sep2021-CUDA-11.1.1-kokkos-omp',
       'foss-2020b-cuda-kokkos-omp'    :'GCC/10.2.0  CUDA/11.1.1  OpenMPI/4.0.5 LAMMPS/29Sep2021-CUDA-11.1.1-kokkos-omp',
       'foss-2020b-cuda-gpu'           :'GCC/10.2.0  CUDA/11.1.1  OpenMPI/4.0.5 LAMMPS/29Sep2021-CUDA-11.1.1-gpu',
       'foss-2021b-cuda-kokkos'        :'GCC/11.2.0  OpenMPI/4.1.1 LAMMPS/29Sep2021-CUDA-11.4.1-kokkos-omp',
       'foss-2021b-cuda-kokkos-omp'    :'GCC/11.2.0  OpenMPI/4.1.1 LAMMPS/29Sep2021-CUDA-11.4.1-kokkos-omp',
       'foss-2021b-cuda-gpu'           :'GCC/11.2.0  OpenMPI/4.1.1 LAMMPS/29Sep2021-CUDA-11.4.1-gpu',
       'foss-2020b-kokkos'             :'GCC/10.2.0  OpenMPI/4.0.5 LAMMPS/29Sep2021-kokkos',
       'foss-2021b-kokkos'             :'GCC/11.2.0  OpenMPI/4.1.1 LAMMPS/29Sep2021-kokkos',
       'iomkl-2019b-kokkos'            :'iccifort/2019.5.281  OpenMPI/3.1.4 LAMMPS/29Sep2021-kokkos',
       'foss-2020b-kokkos-omp'         :'GCC/10.2.0  OpenMPI/4.0.5 LAMMPS/29Sep2021-kokkos-omp',
       'foss-2021b-kokkos-omp'         :'GCC/11.2.0  OpenMPI/4.1.1 LAMMPS/29Sep2021-kokkos-omp',
       'iomkl-2019b-kokkos-omp'        :'iccifort/2019.5.281  OpenMPI/3.1.4 LAMMPS/29Sep2021-kokkos-omp'
       },
    '3Mar2020': {
       'foss-2020a-kokkos'     :'GCC/9.3.0  OpenMPI/4.0.3 LAMMPS/3Mar2020-Python-3.8.2-kokkos',
       'foss-2020a-kokkos-omp' :'GCC/9.3.0  OpenMPI/4.0.3 LAMMPS/3Mar2020-Python-3.8.2-kokkos-omp',
       }
}







