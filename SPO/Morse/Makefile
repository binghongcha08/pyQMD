# Simple makefile
.SUFFIXES: .f .x
.f.x:
	$(FC) $(Flags) $(LIB) $< -o $*.x $(SRC)
  
   FC = gfortran
#  FC = /opt/intel/composer_xe_2011_sp1.8.273/bin/ia32/ifort

#  Flags =  -O0 -ffixed-line-length-none 
   Flags = -w -llapack 

#  LIB = /opt/intel/composer_xe_2011_sp1.8.273/mkl/interfaces/lapack95
#   LIB = /usr/lib/atlas/liblapack.so.3
    SRC = xav.f xav2.f cor.f
#   SRC = gasdev.f ran1.f quantum_potential.f random.f
