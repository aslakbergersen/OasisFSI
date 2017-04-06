from dolfin import Constant, inner, inv, dot, grad, det, Identity,\
solve, lhs, rhs, assemble, DirichletBC, div, sym, tr, norm, \
MPI, mpi_comm_world
#from semi_implicit import *


def extrapolate_setup(F_solid_linear, d_, phi, dx_f, **semimp_namespace):

    F_extrapolate =  inner(grad(d_["n"]), grad(phi))*dx_f
    F_solid_linear += F_extrapolate

    return dict(F_solid_linear=F_solid_linear)
