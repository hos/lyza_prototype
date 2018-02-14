import numpy as np
from math import log
from lyza_prototype.scalar_interface import ScalarInterface
import itertools

class AbsoluteErrorScalarInterface(ScalarInterface):
    def __init__(self, function, exact, p):
        self.function = function
        self.exact = exact
        self.p = p # Lp error

    def calculate(self, elem):
        result = 0.
        n_node = len(elem.nodes)

        coefficients = [self.function.vector[i,0] for i in elem.dofmap]

        for n in range(elem.n_quad_point):
            u_h = [0. for i in range(elem.function_dimension)]

            for I, i in itertools.product(range(n_node), range(elem.function_dimension)):
                u_h[i] += elem.quad_N[n][I]*coefficients[I*elem.function_dimension+i]

            exact_val = self.exact(elem.quad_points_global[n])

            inner_product = 0.
            for i in range(elem.function_dimension):
                inner_product += (exact_val[i] - u_h[i])**2

            result += pow(inner_product, self.p/2.)*elem.quad_points[n].weight*elem.quad_det_jac[n]

        return result


class DerivativeAbsoluteErrorScalarInterface(ScalarInterface):
    def __init__(self, function, exact_deriv, p):
        self.function = function
        self.exact_deriv = exact_deriv
        self.p = p # Lp error

    def calculate(self, elem):
        result = 0.
        n_node = len(elem.nodes)

        coefficients = [self.function.vector[i,0] for i in elem.dofmap]

        for n in range(elem.n_quad_point):
            u_h = np.zeros((elem.function_dimension, elem.physical_dimension))

            for I, i, j in itertools.product(range(n_node), range(elem.function_dimension), range(elem.physical_dimension)):
                u_h[i][j] += elem.quad_B[n][I][j]*coefficients[I*elem.function_dimension+i]

            exact_val = np.array(self.exact_deriv(elem.quad_points_global[n]))

            inner_product = 0.
            for i in range(elem.function_dimension):
                for j in range(elem.physical_dimension):
                    inner_product += (exact_val[i,j] - u_h[i,j])**2


            result += pow(inner_product, self.p/2.)*elem.quad_points[n].weight*elem.quad_det_jac[n]

        return result


def get_exact_solution_vector(function_space, exact):
    exact_solution_vector = np.zeros((function_space.get_system_size(), 1))

    for n in function_space.mesh.nodes:
        exact_val = exact(n.coor)
        for n, dof in enumerate(function_space.node_dofs[n.idx]):
            exact_solution_vector[dof] = exact_val[n]

    return exact_solution_vector


def absolute_error(function, exact, exact_deriv, quadrature_degree, error='l2'):

    if error == 'l2':
        result = absolute_error_lp(function, exact, 2, quadrature_degree)
    elif error == 'linf':
        result = abs(function.vector - get_exact_solution_vector(function.function_space, exact)).max()
    elif error == 'h1':
        l2 = absolute_error_lp(function, exact, 2, quadrature_degree)
        l2d = absolute_error_deriv_lp(function, exact_deriv, 2, quadrature_degree)
        result = pow(pow(l2,2.) + pow(l2d,2.), .5)
    else:
        raise Exception('Invalid error specification: %s'%error)

    return result


def absolute_error_lp(function, exact, p, quadrature_degree):
    result = 0.

    assembly = function.function_space.get_assembly(quadrature_degree)
    interface = AbsoluteErrorScalarInterface(function, exact, p)

    for e in assembly.elems:
        result += interface.calculate(e)

    result = pow(result, 1./p)

    return result


def absolute_error_deriv_lp(function, exact_deriv, p, quadrature_degree):
    result = 0.

    assembly = function.function_space.get_assembly(quadrature_degree)
    interface = DerivativeAbsoluteErrorScalarInterface(function, exact_deriv, p)

    for e in assembly.elems:
        result += interface.calculate(e)

    result = pow(result, 1./p)

    return result


def plot_convergence_rates(path, h_max_array, l2_array, linf_array, h1_array):
    import pylab as pl

    pl.figure()

    linf_convergence_array = [float('nan')]
    l2_convergence_array = [float('nan')]
    h1_convergence_array = [float('nan')]

    for i in range(len(h_max_array)):
        if i >= 1:
            base = h_max_array[i-1]/h_max_array[i]
            # import ipdb; ipdb.set_trace()
            l2_convergence_array.append(log(l2_array[i-1]/l2_array[i])/log(base))
            linf_convergence_array.append(log(linf_array[i-1]/linf_array[i])/log(base))
            h1_convergence_array.append(log(h1_array[i-1]/h1_array[i])/log(base))

    # print(l2_convergence_array)
    pl.semilogx(h_max_array, l2_convergence_array, '-o', label='$L^2$ Convergence rate')
    pl.semilogx(h_max_array, linf_convergence_array, '-o', label='$L^\infty$ Convergence rate')
    pl.semilogx(h_max_array, h1_convergence_array, '-o', label='$H^1$ Convergence rate')

    pl.xlabel('$h_{max}$')
    pl.ylabel('$\log(\epsilon_{n-1}-\epsilon_{n})/\log(h_{max,n-1}-h_{max,n})$')
    pl.grid(b=True, which='minor', color='gray', linestyle='--')
    pl.grid(b=True, which='major', color='gray', linestyle='-')
    pl.title('Convergence rates')
    pl.legend()

    pl.savefig(path)


def plot_errors(path, h_max_array, l2_array, linf_array, h1_array):
    import pylab as pl

    pl.figure()

    # Error figure
    pl.loglog(h_max_array, l2_array, '-o', label='$L^2$ Error')
    pl.loglog(h_max_array, linf_array, '-o', label='$L^\infty$ Error')
    pl.loglog(h_max_array, h1_array, '-o', label='$H^1$ Error')


    # pl.minorticks_on()
    pl.xlabel('$h_{max}$')
    pl.ylabel('$\epsilon_{a}$')
    pl.grid(b=True, which='minor', color='gray', linestyle='--')
    pl.grid(b=True, which='major', color='gray', linestyle='-')
    pl.title('Errors')
    pl.legend()

    pl.savefig(path)


