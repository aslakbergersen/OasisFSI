from dolfin import *


def solver_setup(F_solid_linear, F_solid_nonlinear, VV, dv_, dv_sol, **monolithic):

    F = F_solid_nonlinear + F_solid_linear

    chi = TrialFunction(VV)
    J_linear    = derivative(F_solid_linear, dv_["n"], chi)
    J_nonlinear = derivative(F_solid_nonlinear, dv_["n"], chi)

    A_pre = assemble(J_linear)#, form_compiler_parameters = {"quadrature_degree": 4})
    A = Matrix(A_pre)
    b = None

    dv_sol.parameters['reuse_factorization'] = True

    return dict(F=F, J_nonlinear=J_nonlinear, J_linear=J_linear, \
                A_pre=A_pre, A=A, b=b, dv_sol=dv_sol)


def newtonsolver(F, J_nonlinear, J_linear, A_pre, A, b, bcs, \
                dv_, dv_sol, dv_res, rtol, atol, max_it, T, t, **monolithic):
    Iter      = 0
    residual   = 10**8
    rel_res    = 10**8
    lmbda = 1
    last_rel_res = residual #Capture if residual increases from last iteration
    last_residual = rel_res

    while rel_res > rtol and residual > atol and Iter < max_it:

        if Iter % 1  == 0 or (last_rel_res < rel_res and last_residual < residual):
            print "assebmling new JAC"
            A = assemble(J_nonlinear, tensor=A, \
            form_compiler_parameters = {"quadrature_degree": 4}, \
            keep_diagonal = True)
            # FIX ASSEMBLE MED HEL JACOBI
            #A = assemble(J_nonlinear, tensor=A, keep_diagonal = True)

            A.axpy(1.0, A_pre, True)
            A.ident_zeros()
            [bc.apply(A) for bc in bcs]
            dv_sol.set_operator(A)


        b = assemble(-F, tensor=b)

        last_rel_res = rel_res #Capture if residual increases from last iteration
        last_residual = residual

        [bc.apply(b, dv_["n"].vector()) for bc in bcs]
        #[bc.apply(A, b, dv_["n"].vector()) for bc in bcs]
        dv_sol.solve(dv_res.vector(), b)
        dv_["n"].vector().axpy(lmbda, dv_res.vector())
        [bc.apply(dv_["n"].vector()) for bc in bcs]
        rel_res = norm(dv_res, 'l2')
        residual = b.norm('l2')
        if rel_res > 1E20 or residual > 1E20:
            print "IN IF TEST"
            t = T + 1
            break


        if MPI.rank(mpi_comm_world()) == 0:
            print "Newton iteration %d: r (atol) = %.3e (tol = %.3e), r (rel) = %.3e (tol = %.3e) " \
        % (Iter, residual, atol, rel_res, rtol)
        Iter += 1

    return dict(t=t)
