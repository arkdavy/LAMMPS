#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job=my_lammps_calculation-gpu
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=42
#SBACTH --mem-per-cpu=3850
#SBATCH --time=24:00:00
#SBATCH --account=su950-gpu
#SBATCH --partition=gpu
#SBATCH --gres=gpu:ampere_a100:1

# drop all modules
module purge

export ebversion='4.5.0'

export EB_PREFIX=${HOME}/easybuild-$ebversion

# define module paths to look for
export MODULEPATH=${EB_PREFIX}/modules/all:${EB_PREFIX}/modules/Core:${EB_PREFIX}/modules/MPI

# load ones required for the LAMMPS execuation
module load GCC/11.2.0 OpenMPI/4.1.1 LAMMPS/29Sep2021-CUDA-11.4.1-kokkos-omp

# re-adjust the number of OpenMP threads
export OMP_NUM_THREADS=1

# executed command
srun `which lmp` -k on g 1 -sf kk -in in.lammps
