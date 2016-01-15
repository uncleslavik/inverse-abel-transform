import numpy as np
import scipy as sp

class Abel:

    @staticmethod
    def diff(F):
       res = np.zeros(len(F))
       diff=np.diff(F)
       res[0:len(F)-1]=diff[:]
       return res

    @staticmethod
    def transform(F):
        diff=Abel.diff(F)
        nx = len(F)
        x=np.arange(nx)

        integral = sp.zeros(nx, dtype=float)

        for i in range(0, nx-1):
            divisor = sp.sqrt(x[i:nx]**2 - x[i]**2)
            integrand = diff[i:nx] / divisor
            integrand[0] = integrand[1] # deal with the singularity at x=r
            integral[i] = - sp.trapz(integrand, x[i:nx]) / sp.pi

        return(integral)


