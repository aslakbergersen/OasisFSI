from fenics import *
import mshr
import numpy as np
set_log_active(False)
import argparse
from argparse import RawTextHelpFormatter

def parse():
    parser = argparse.ArgumentParser(description="MMS of ALE\n",\
     formatter_class=RawTextHelpFormatter, \
      epilog="############################################################################\n"
      "Example --> python ALE_MMS.py -source_term 0 -var_form 1\n"
      "############################################################################")
    group = parser.add_argument_group('Parameters')
    group.add_argument("-var_form",  type=int, help="Which form to use  --> Default=0, no mapping", default=0)
    group.add_argument("-source_term",  type=int, help="Which source_term to use  --> Default=0, no mapping", default=0)

    return parser.parse_args()
args = parse()
var_form = args.var_form
source_term = args.source_term

I = Identity(2)
def F_(U):
	return (Identity(2) + grad(U))

def J_(U):
	return det(F_(U))
def E(U):
	return 0.5*(F_(U).T*F_(U)-I)

def S(U,lamda_s,mu_s):
	return (2*mu_s*E(U) + lamda_s*tr(E(U))*I)

def P1(U,lamda_s,mu_s):
	return F_(U)*S(U,lamda_s,mu_s)

def solver(N, dt, T):
    mesh = UnitSquareMesh(N, N)

    x = SpatialCoordinate(mesh)

    V = VectorFunctionSpace(mesh, "CG", 1)
    W = V*V
    n = FacetNormal(mesh)

    ud = Function(W)
    u, d = split(ud)

    phi, psi = TestFunctions(W)
    ud0 = Function(W)
    u0, d0 = split(ud0)

    k = Constant(dt)
    t_step = dt
    t = Constant(dt)
    mu_s = 1
    rho_s = 1
    lamda_s = 1

    d_x = "cos(x[1])*sin(t)"
    d_y = "cos(x[0])*sin(t)"

    u_x = "cos(x[1])*cos(t)"
    u_y = "cos(x[0])*cos(t)"

    d_e = Expression((d_x, d_y), degree = 3, t = 0)
    u_e = Expression((u_x, u_y), degree = 3, t = 0)
    
    #assign(ud0.sub(1), project(d_e, V))
    #assign(ud0.sub(0), project(u_e, V))

    u0 = interpolate(u_e, V)
    d0 = interpolate(d_e,V)

    exec("d_x = " + d_x)
    exec("d_y = " + d_y)
    exec("u_x = " + u_x)
    exec("u_y = " + u_y)

    u_vec = as_vector([u_x, u_y])
    d_vec = as_vector([d_x, d_y])
    
    # Create right hand side f
    f1 =rho_s*diff(u_vec, t) - div(P1(d_vec,lamda_s,mu_s))
    #f2 = diff(d_vec, t) - u_vec # is zero when d and u is created to be zero

    delta = 1E10
    F_lin = (rho_s/k)*inner(u-u0,phi)*dx
    F_lin += delta*((1.0/k)*inner(d-d0,psi)*dx - inner(u,psi)*dx)
    F_lin -= inner(f1, phi)*dx #+ inner(f2, psi)*dx

    F_nonlin = -inner(div(P1(d,lamda_s,mu_s)), phi)*dx

    bcs = [DirichletBC(W.sub(0), u_e, "on_boundary"), \
           DirichletBC(W.sub(1), d_e, "on_boundary")]

    L2_u = []
    L2_d = []

    u_file = XDMFFile(mpi_comm_world(), "Structure_MMS_results/velocity.xdmf")
    d_file = XDMFFile(mpi_comm_world(), "Structure_MMS_results/d.xdmf")

    for tmp_t in [u_file, d_file]:
        tmp_t.parameters["flush_output"] = True
        tmp_t.parameters["multi_file"] = 1
        tmp_t.parameters["rewrite_function_mesh"] = False

    d_diff = Function(V)
    u_diff = Function(V)


    F = F_lin + F_nonlin

    chi = TrialFunction(W)
    J_linear    = derivative(F_lin, ud, chi)
    J_nonlinear = derivative(F_nonlin, ud, chi)
    J = derivative(F, ud, chi)

    A_pre = assemble(J_linear)#, form_compiler_parameters = {"quadrature_degree": 4})
    A = Matrix(A_pre)
    b = None

    for i in ["mumps", "superlu_dist", "default"]:
        if has_lu_solver_method(i):
            solver_method = i

    up_sol = LUSolver(solver_method)
    up_sol.parameters['reuse_factorization'] = True
    ud_tent = Function(W)
    rtol = 1e-8
    atol = 1e-8
    max_it = 100

    while t_step <= T:
        u_e.t = t_step
        d_e.t = t_step
        t.assign(t_step)

        Iter      = 0
        residual   = 10**8
        rel_res    = 10**8
        lmbda = 1.0
        last_rel_res = residual #Capture if residual increases from last iteration
        last_residual = rel_res

        while rel_res > rtol and residual > atol and Iter < max_it:

            if Iter % 3  == 0 or (last_rel_res < rel_res and last_residual < residual):
            #    print "assebmling new JAC"
                #A = assemble(J_nonlinear, tensor=A, \
                #form_compiler_parameters = {"quadrature_degree": 4}, \
                #keep_diagonal = True)

                A = assemble(J, keep_diagonal = True)

                #A.axpy(1.0, A_pre, True)
                A.ident_zeros()
                [bc.apply(A) for bc in bcs]
                up_sol.set_operator(A)


            b = assemble(-F, tensor=b)

            last_rel_res = rel_res #Capture if residual increases from last iteration
            last_residual = residual

            [bc.apply(b, ud.vector()) for bc in bcs]
            #[bc.apply(A, b, dvp_["n"].vector()) for bc in bcs]
            up_sol.solve(ud_tent.vector(), b)
            ud.vector().axpy(lmbda, ud_tent.vector())
            [bc.apply(ud.vector()) for bc in bcs]
            rel_res = norm(ud_tent, 'l2')
            residual = b.norm('l2')
            if rel_res > 1E20 or residual > 1E20:
                print "IN IF TEST"
                t = T + 1
                break

            if MPI.rank(mpi_comm_world()) == 0:
                print "Newton iteration %d: r (atol) = %.3e (tol = %.3e), r (rel) = %.3e (tol = %.3e) " \
            % (Iter, residual, atol, rel_res, rtol)
            Iter += 1
        
        #ud0.assign(ud)
        u_, d_ = ud.split(True)
        u0.assign(u_); d0.assign(d_)

        L2_u.append(errornorm(u_e, u_, norm_type="l2", degree_rise = 3))
        L2_d.append(errornorm(d_e, d_, norm_type="l2", degree_rise = 3))
        print "Time ", t_step
        t_step += dt

    E_u.append(np.mean(L2_u))
    E_d.append(np.mean(L2_d))
    h.append(mesh.hmin())

test = "time"
#Space
if test == "space":
    #N = [4,8,16,32,64]
    N = [4,8,16]
    dt = [1.0E-6]
    T = 1.0E-5

else:
    test = "time"
    N = [100]
    dt = [0.04, 0.02, 0.01]
    T = 0.08

E_u = [];  E_d = []; h = []

for n in N:
    for t in dt:
        print "Solving for t = %g, N = %d" % (t, n)
        solver(n, t, T)

print "Checking Convergence in Space P2-P1"

for i in E_u:
    print "Errornorm Velocity L2", i

print

for i in range(len(E_u) - 1):
    if test == "space":
        r_u = np.log(E_u[i+1]/E_u[i]) / np.log(h[i+1]/h[i])
    if test == "time":
        r_u = np.log(E_u[i+1]/E_u[i]) / np.log(dt[i+1]/dt[i])
    print "Convergence Velocity", r_u

print

for i in E_d:
    print "Errornorm Deformation L2", i

print

for i in range(len(E_d) - 1):
    if test == "space":
        r_d = np.log(E_d[i+1]/E_d[i]) / np.log(h[i+1]/h[i])
    if test == "time":
        r_d = np.log(E_d[i+1]/E_d[i]) / np.log(dt[i+1]/dt[i])
    print "Convergence Velocity", r_u

"""
print "Checking Convergence in time"

N = [64]
dt = [8.0E-4, 4E-4, 2E-4, 1E-4, 0.5E-4]
T = 1.0E-2
E_u = [];  E_d = []; h = []
for n in N:
    for t in dt:
        print "Solving for t = %g, N = %d" % (t, n)
        solver(n, t, T)

for i in E_u:
    print "Errornorm Velocity L2", i

print

for i in range(len(E_u) - 1):
    r_u = np.log(E_u[i+1]/E_u[i]) / np.log(dt[i+1]/dt[i])
    print "Convergence Velocity", r_u

print

for i in E_d:
    print "Errornorm Deformation L2", i

print

for i in range(len(E_d) - 1):
    r_d = np.log(E_d[i+1]/E_d[i]) / np.log(dt[i+1]/dt[i])

    print "Convergence Deformation", r_d"""
