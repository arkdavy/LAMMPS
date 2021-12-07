#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job=my_lammps_calculation
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=4
#SBACTH --mem-per-cpu=3850
#SBATCH --time=24:00:00
#SBATCH --account=su950

# drop all modules
module purge

export ebversion='4.5.0'

export EB_PREFIX=${HOME}/easybuild-$ebversion

# define module paths to look for
export MODULEPATH=${EB_PREFIX}/modules/all:${EB_PREFIX}/modules/Core:${EB_PREFIX}/modules/MPI

# load ones required for the LAMMPS execuation
module load GCC/11.2.0 OpenMPI/4.1.1 LAMMPS/29Sep2021-kokkos-omp

# adjust the number of OpenMP threads automatically
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

# executed command
srun `which lmp` -k on t ${OMP_NUM_THREADS} -sf kk -in in.lammps
