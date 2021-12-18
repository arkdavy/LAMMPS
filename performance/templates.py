
def runTemplate(system, version, compiler, module, ntasks_node, threads_adjust, tasks, threads, gpus, suffix, rcfg, envar):
    if gpus > 0:
        accountgpuline="""#SBATCH --account=su950-gpu
#SBATCH --partition=gpu
#SBATCH --gres=gpu:ampere_a100:{}""".format(gpus)
    else:
        accountgpuline="#SBATCH --account=su950"


    header1 = """#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job=lammps-{}-{}-{}-{}-{}-{}
#SBATCH --ntasks-per-node={}
#SBATCH --cpus-per-task={}
#SBACTH --mem-per-cpu=3850
#SBATCH --time=24:00:00
""".format(system, rcfg, version, compiler, threads, gpus, ntasks_node, threads_adjust)

    header2="""
# drop system-wide modules
module purge

export ebversion='4.5.0'

export EB_PREFIX=${{HOME}}/easybuild-$ebversion

# define module paths to look for
export MODULEPATH=${{EB_PREFIX}}/modules/all:${{EB_PREFIX}}/modules/Core:${{EB_PREFIX}}/modules/MPI

module load {}

""".format(module)
    header = header1 + accountgpuline + header2

    footer = """
export OMP_NUM_THREADS={}
{}

export MKL_DEBUG_CPU_TYPE=5
export MKL_CBWR=COMPATIBLE

for ntasks in {}
do

srun --cpu-bind=cores -n ${{ntasks}} -c ${{OMP_NUM_THREADS}} lmp -screen MPIx${{ntasks}}_GPUx{}_THRDSx{} {} -in in.lammps

done
""".format(threads, envar, ' '.join([str(x) for x in tasks]), gpus, threads, suffix)
    
    return header+footer


def lj():
    return """log none

#############################
# P R E L I M I N A R I E S #
#############################

units lj                  # Use reduced LJ style units
atom_style atomic         # Uncharged point particles
atom_modify map hash      # Needed for indexing of clusters etc

# Define a lattice with which to populate the simulation cell. With units
# set to 'lj' the second argument to the lattice command is the reduced
# density rho* and the spacings are multiples of that required to acheive
# that density. Also define a simulation cell called 'box' in lattice units
# and fill it with atoms. Here we're creating a box which is ten lattice
# constants in each direction.
lattice fcc 1.0 spacing 1 1 1
region box block 0 24 0 24 0 24 units lattice
create_box 1 box
create_atoms 1 box


# Set the mass of the first (and only) atom type.
mass 1 1.0

# Lennard-Jones interactions between particles, 3.5 sigma cut-off. Apply
# long range tail corrections to energy and pressure and set all coefficients
# to unity since we work in reduced units here. Note that this doesn't shift
# the potential such that it goes to zero at the cutoff. That would require
# pair_modify('shift', 'yes').
#pair_style lj/cut/gpu  3.5  # GPU version
pair_style lj/cut  3.5      # non-GPU version
pair_modify tail  yes
pair_coeff 1  1  1.0  1.0

#############################
#   M E L T   S Y S T E M   #
#############################
velocity all create 2.4 41787 mom yes dist gaussian # Assign velocities

timestep 0.002   # simulation timestep
thermo 100       # output thermodynamic data every 100 steps

# Define a fix  in this case with index 1 applied to all
# particles in the simulation. This fix is for simulations
# in the anisotropic NPT ensemble. Note that we use the MTK
# correction.
fix 1 all npt temp 2.4 2.4 0.1 iso 5.0 5.0 0.5 mtk yes tchain 5 pchain 5

run 50000         # run for 50000 steps

#############################
# F R E E Z E  S Y S T E M  #
#############################

# Define solid atoms. This closely follows ten Wolde  Ruiz-Montero and Frenkel  Faraday Discuss  1996  104  93-110
# Compute components of the per-atom q6 vector
#compute q6 all orientorder/atom degrees 1 6 components 6 nnn NULL cutoff 1.3

# get number of connections
#compute coord_number all coord/atom orientorder q6 0.5

# An atom is solid if it has 8 or more connections
#variable is_solid atom c_coord_number>=8
#group solid dynamic all var is_solid    # Must be dynamic to update

# do clustering
#compute cluster solid cluster/atom 1.3

# define chunks  one chunk per cluster
#compute clus_chunks solid chunk/atom c_cluster

# count the size of each chunk
#compute size_chunks solid property/chunk clus_chunks count

# Find the maximum entry in the vector of chunk sizes
#variable max_n equal max(c_size_chunks)

# Thermo style which includes this variable
#thermo_style custom step temp pe vol v_max_n

#thermo 1000  # Print the thermo information every 1000 steps

# Reset the npt fix at a lower temperature (below freezing)
#fix 1  all npt temp  0.65  0.65  0.1  iso  5.0  5.0  0.5  mtk yes tchain  5  pchain  5

run 50000  # Run for this many steps"""


def interface():
  return """log none

#############################################
#        Preamble and read structure        #
#############################################

units metal

boundary p  p  p

atom_style full

box tilt large
read_data surface.lmp
#read_restart restart.*

#############################################
#         Atom types and charges            #
#############################################

group Ca type 1
group C4 type 2
group O4 type 3
group O2 type 4
group H2 type 5

set group Ca charge   2.000000
set group C4 charge   1.123285
set group O4 charge  -1.041095
set group O2 charge  -0.820000
set group H2 charge   0.410000


#############################################
#                Bond types                 #
#############################################
# type 1 : carbonate C4-O4 stretch 
# type 2 : water O2-H2 stretch


bond_style harmonic
bond_coeff 1 17.950 1.3130
bond_coeff 2 22.965   1.0120

#############################################
#               Angle types                 #
#############################################
# Type 1 : carbonate O4-C4-O4 angle 
# Type 2 : water     H2-O2-H2 angle


angle_style hybrid class2 harmonic

angle_coeff 1 class2       120.     6.617   0. 0.
angle_coeff 1 class2   bb  12.818   1.3042  1.3042
angle_coeff 1 class2   ba  1.53319  1.53319 1.3042 1.3042 

angle_coeff 2 harmonic 1.63068 113.24


#############################################
#             Improper types                #
#############################################
# Type 1 : carbonate   out-of-plane potential

improper_style distance
improper_coeff 1 20.796 360.00

#############################################
#            Pair potentials                #
#############################################
pair_style hybrid/overlay coul/long 9. lj/cut 9. table linear 200001
pair_coeff * * coul/long

pair_coeff 1 2 table ../../../../surfaceInput/caco3.pot buck_ca_c4 9.
pair_coeff 1 3 table ../../../../surfaceInput/caco3.pot buck_ca_o4 9.
pair_coeff 3 3 table ../../../../surfaceInput/caco3.pot buck_o4_o4 9.

# Calcium water
pair_coeff 1 4 table ../../../../surfaceInput/caco3.pot lj_ca_o2  9.

# Carbonate oxygen - water oxygen
pair_coeff 3 4 table ../../../../surfaceInput/caco3.pot buck_o4_o2 9.

# Carbonate oxygen - water hydrogen
pair_coeff 3 5 table ../../../../surfaceInput/caco3.pot buck_o4_h2 9.

# Water oxygen/water oxygen
pair_coeff 4 4 lj/cut   0.0067400000   3.165492
pair_modify tail yes

# Parameters for reciprocal space long-range electrostatics
kspace_style pppm 1.0e-4

velocity all create 300.0 30446 mom yes dist gaussian

thermo_style custom step temp pe ke etotal enthalpy press vol spcpu

thermo 100    
timestep 0.001

fix 1 all npt aniso 1.0 1.0 1.0 temp 300. 300. 0.1 tchain 5 pchain 5 mtk yes 

# Run for 20000 steps 
run 20000
"""
