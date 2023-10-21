from scipy.stats import norm
import numpy as np
import sys

if __name__=='__main__':
    """
    Recibe 5 argumentos:
    1) cantidad de órdenes
    2) cantidad de trabajadores
    3) cantdidad de pares de órdenes conflictivas
    4) cantidad de pares de órdenes con conflicto
    5) nombre del file a guardar
    """

    n_orders = int(sys.argv[1].strip())
    n_workers = int(sys.argv[2].strip())
    n_conflicts = int(sys.argv[3].strip())
    n_consecutives = int(sys.argv[4].strip())
    
    n = norm.rvs(loc=5000, scale=4500, size=n_orders, random_state=1)
    workers = [*range(1,n_workers+1)]
    
    with open(sys.argv[5].strip(), "w") as file:
        file.write(f"{n_workers}\n")
        file.write(f"{n_orders}\n")
        for i in range(n_orders):
            file.write(f"{i} {abs(int(n[i]))} {np.random.choice(workers,1)[0]}\n")
    
        file.write("0\n")
            
        file.write(f"{n_conflicts}\n")
        for i in range(n_conflicts): 
            first_order = np.random.choice(workers,1)[0]
            second_order = np.random.choice(workers,1)[0]
            while first_order==second_order:
                first_order = np.random.choice(workers,1)[0]
                second_order = np.random.choice(workers,1)[0]
            file.write(f"{first_order} {second_order}\n")
        
    
        file.write(f"{n_consecutives}\n")
        for i in range(n_consecutives):
            first_order = np.random.choice(workers,1)[0]
            second_order = np.random.choice(workers,1)[0]
            while first_order==second_order:
                first_order = np.random.choice(workers,1)[0]
                second_order = np.random.choice(workers,1)[0]
            file.write(f"{first_order} {second_order}\n")
    
        file.write("0\n")