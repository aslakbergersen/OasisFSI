from dolfin import Constant, inner, inv, dot, grad, det, Identity,\
solve, lhs, rhs, assemble, DirichletBC, div, sym, nabla_grad


def F_(U):
	return (Identity(len(U)) + grad(U))

def J_(U):
	return det(F_(U))

def sigma_f_new(u,p,d,mu_f):
	return -p*Identity(len(u)) + mu_f*(grad(u)*inv(F_(d)) + inv(F_(d)).T*grad(u).T)


def fluid_setup(v_, p_, d_, n, psi, gamma, dx_f, ds, mu_f, rho_f, k, v_deg, **semimp_namespace):
    F_fluid_linear = (rho_f/k)*inner(J_(d_["n"]) * (3./2.*v_["n"] - 2*v_["n-1"] + 1./2.*v_["n-2"]), psi)*dx_f
    F_fluid_linear += rho_f*inner(J_(d_["n"]) * grad(v_["n"]) * inv(F_(d_["n"])) * ((2*v_["n-1"]-v_["n-2"]) - ((d_["n"]-d_["n-1"])/k)), psi)*dx_f
    F_fluid_linear += rho_f*inner(1./2.*div(J_(d_["n"])*inv(F_(d_["n"]))*(2*v_["n-1"]-v_["n-2"])) * v_["n"], psi)*dx_f

    F_fluid_linear -= inner(div(J_(d_["n"])*inv(F_(d_["n"]))*v_["n"]), gamma)*dx_f
    F_fluid_linear += inner(J_(d_["n"])*sigma_f_new(v_["n"], p_["n"], d_["n"], mu_f)*inv(F_(d_["n"])).T, grad(psi))*dx_f
    F_fluid_nonlinear = inner(Constant(("0","0")),psi)*dx_f
    if v_deg == 1:
        F_fluid -= beta*h*h*inner(J_(d_["n"])*inv(F_(d_["n"]).T)*grad(p), grad(gamma))*dx_f

        print "v_deg",v_deg

    return dict(F_fluid_linear = F_fluid_linear, F_fluid_nonlinear = F_fluid_nonlinear)
