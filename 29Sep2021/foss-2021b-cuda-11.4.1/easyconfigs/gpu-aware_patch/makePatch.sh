echo "This is a checksum fix for building LAMMPS-29Sep2021 documentation and cuda-aware problem" > LAMMPS-29Sep2021-fixdoc.patch
diff -ruN lammps-stable_29Sep2021/cmake/Modules/Documentation.cmake.orig lammps-stable_29Sep2021/cmake/Modules/Documentation.cmake >> LAMMPS-29Sep2021-fixdoc.patch
diff -ruN lammps-stable_29Sep2021/src/KOKKOS/kokkos_old.cpp lammps-stable_29Sep2021/src/KOKKOS/kokkos.cpp >> LAMMPS-29Sep2021-fixdoc.patch

