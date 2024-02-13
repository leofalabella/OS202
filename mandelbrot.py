# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
from mpi4py import MPI
import matplotlib.cm


@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Sinon on itère
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

def calculate_mandelbrot_row(start, end, mandelbrot_set, scaleX, scaleY, height):
    row_result = np.empty((end - start, height), dtype=np.double)
    for y in range(start, end):
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            row_result[y-start, x] = mandelbrot_set.convergence(c, smooth=True)
    
    return row_result

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # On peut changer les paramètres des deux prochaines lignes
    mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
    width, height = 1024, 1024

    scaleX = 3./width
    scaleY = 2.25/height

    convergence = np.empty((width, height), dtype=np.double)

    rows_per_process = height // size
    start_row = rank * rows_per_process
    end_row = start_row + rows_per_process

    if rank == size - 1:
        end_row = height

    # Calcul de l'ensemble de mandelbrot :
    deb = time()
    local_result = calculate_mandelbrot_row(start_row, end_row, mandelbrot_set, scaleX, scaleY, height)
    fin = time()
    print(f"Temps du calcul du process {rank} : {fin-deb}")

    max_time = comm.reduce(fin - deb, op=MPI.MAX, root=0)

    # Constitution de l'image résultante :
    if rank == 0:
        result = np.empty((height, width), dtype=np.double)
    else:
        result = None
    
    comm.Gather(local_result, result, root=0)

    if rank == 0:
        deb = time()
        image = Image.fromarray(np.uint8(matplotlib.cm.plasma(result)*255))
        fin = time()

        print(f"Temps de constitution de l'image : {fin-deb}")
        print(f"Temps total: {fin-deb+max_time}")
        # image.show()
        image.save("output_mpi.png")


#mpirun -n 4.mandelbrot.py