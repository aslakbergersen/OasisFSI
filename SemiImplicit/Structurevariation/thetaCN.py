from dolfin import Constant, inner, inv, dot, grad, det, Identity,\
solve, lhs, rhs, assemble, DirichletBC, div, sym, tr, norm, \
MPI, mpi_comm_world
#from semi_implicit import *

def F_(U):
	return Identity(len(U)) + grad(U)

def J_(U):
	return det(F_(U))

def E(U):
	return 0.5*(F_(U).T*F_(U) - Identity(len(U)))

def S(U,lamda_s,mu_s):
    I = Identity(len(U))
    return 2*mu_s*E(U) + lamda_s*tr(E(U))*I

def Piola1(U,lamda_s,mu_s):
	return F_(U)*S(U,lamda_s,mu_s)

def sigma_f(p, u, d, mu_f):
    return  -p*Identity(len(u)) +\
	        mu_f*(grad(u)*inv(F_(d)) + inv(F_(d)).T*grad(u).T)

def Structure_setup(d_, w_, v_, p_, phi, gamma, dS, n, mu_f, \
            vp_, dx_s, mu_s, rho_s, lamda_s, k, mesh_file, theta, **semimp_namespace):

	delta = 1E10
	theta = 1.0


	F_solid_linear = rho_s/k*inner(w_["n"] - w_["n-1"], phi)*dx_s \
	               + delta*(1./k)*inner(d_["n"] - d_["n-1"], gamma)*dx_s \
   				   - delta*inner(Constant(theta)*w_["n"] \
				   + Constant(1 - theta)*w_["n-1"], gamma)*dx_s

	F_solid_nonlinear = inner(Piola1(Constant(theta)*d_["n"] \
	                  + Constant(1 - theta)*d_["n-1"], lamda_s, mu_s), grad(phi))*dx_s

	#F_solid_nonlinear -= inner(J_(d_["n"]("+")) * \
    #3sigma_f(p_["n"]("+"),v_["tilde"]("+"), d_["n"]("+"), mu_f) \
	#*inv(F_(d_["n"]("+"))).T*n("+"), phi("+"))*dS(5)

	#org
	F_solid_nonlinear -= inner(J_(d_["tilde"]("+")) * \
	sigma_f(p_["n"]("+"),v_["tilde"]("+"), d_["tilde"]("+"), mu_f) \
	*inv(F_(d_["tilde"]("+"))).T*n("+"), phi("-"))*dS(5)


	return dict(F_solid_linear = F_solid_linear, F_solid_nonlinear = F_solid_nonlinear)
