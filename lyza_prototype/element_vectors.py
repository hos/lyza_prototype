from lyza_prototype.element_interface import ElementInterface
import numpy as np
import itertools

class FunctionElementVector(ElementInterface):

    def __init__(self, function):
        self.function = function

    def linear_form_vector(self, elem):
        n_node = len(elem.nodes)
        n_dof = n_node*elem.function_dimension

        f = np.zeros((n_dof,1))

        for q in elem.quad_points:
            f_cont = np.zeros((n_dof,1))

            for I, i in itertools.product(range(n_node), range(elem.function_dimension)):
                alpha = I*elem.function_dimension + i
                f_val = self.function(q.global_coor)
                f[alpha] += f_val[i]*q.N[I]*q.det_jac*q.weight


        return f