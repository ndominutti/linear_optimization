import sys
import cplex
import json
import time


TOLERANCE =10e-6 

class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])
        

class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        self.cantidad_turnos     = 5
        self.cantidad_dias     = 6
        self.M = 1_000_000
        

    def load(self,filename):
        # Abrimos el archivo.
        f = open(filename)

        # Leemos la cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Leemos la cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Leemos cada una de las ordenes.
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            row = f.readline().split(' ')
            orden = Orden()
            orden.load(row)
            self.ordenes.append(orden)
        
        # Leemos la cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Leemos los conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            row = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Leemos las ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            row = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Leemos las ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            row = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,row)))
        
        
        # Leemos la cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Leemos las ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            row = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,row)))
        
        # Cerramos el archivo.
        f.close()


def get_instance_data():
    file_location = sys.argv[1].strip()
    instance = FieldWorkAssignment()
    instance.load(file_location)
    return instance
    

def add_constraint_matrix(my_problem, data, A, X, E, F, Delta,
                          WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN):
    
    # Restriccion 1
    restriccion = []
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(-1)
                restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['G']*len(restriccion), rhs=[0]*len(restriccion))

    # Restriccion 2
    restriccion = []
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(-data.M)
                restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[0]*len(restriccion))

    # Restriccion 3
    restriccion = []
    for o in range(data.cantidad_ordenes):
        lhs = cplex.SparsePair()
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_trabajadores):
                    lhs.ind.append(X[(t,o, h, d)])
                    lhs.val.append(1)
        lhs.ind.append(A[o])
        lhs.val.append(-1)
        restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['G']*len(restriccion), rhs=[0]*len(restriccion))

    # Restriccion 4
    restriccion = []
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
            lhs.ind.append(E[(t,d)])
            lhs.val.append(-1)
            restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['G']*len(restriccion), rhs=[0]*len(restriccion))
        
    # Restriccion 5
    restriccion = []
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
            lhs.ind.append(E[(t,d)])
            lhs.val.append(-data.M)
            restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[0]*len(restriccion))

    # Restriccion 6
    restriccion = []
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(F[(t,h,d)])
                lhs.val.append(-1)
                restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['G']*len(restriccion), rhs=[0]*len(restriccion))

    # Restriccion 7
    restriccion = []
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(F[(t,h,d)])
                lhs.val.append(-data.M)
                restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[0]*len(restriccion))

    #----------------- RESTRICCIONES DEL PROBLEMA
    # Restriccion 1
    restriccion = []
    for o in range(data.cantidad_ordenes):
        lhs = cplex.SparsePair()
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(1)
        restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[1]*len(restriccion))

    # Restriccion 2
    restriccion = []
    for t in range(data.cantidad_trabajadores):    
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[1]*len(restriccion))

    # Restriccion 3
    restriccion = []
    for t in range(data.cantidad_trabajadores):  
        lhs = cplex.SparsePair()  
        for d in range(data.cantidad_dias):
            lhs.ind.append(E[(t,d)])
            lhs.val.append(1)
        restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[5]*len(restriccion))

    # Restriccion 4
    restriccion = []
    for t in range(data.cantidad_trabajadores):  
        for d in range(data.cantidad_dias):
            lhs = cplex.SparsePair()  
            for h in range(data.cantidad_turnos):
                lhs.ind.append(F[(t,h,d)])
                lhs.val.append(1)
                restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[4]*len(restriccion))
    
    # Restriccion 5
    restriccion = []
    for (o1, o2) in data.ordenes_conflictivas:
        for h in range(data.cantidad_turnos):
            if h<4:
                for t in range(data.cantidad_trabajadores):    
                    for d in range(data.cantidad_dias):
                        lhs = cplex.SparsePair()
                        lhs.ind.append(X[(t, o1, h, d)])
                        lhs.val.append(1)
                        lhs.ind.append(X[(t, o2, h+1, d)])
                        lhs.val.append(1)
                        lhs.ind.append(X[(t, o2, h, d)])
                        lhs.val.append(1)
                        lhs.ind.append(X[(t, o1, h+1, d)])
                        lhs.val.append(1)
                        restriccion.append(lhs)
    my_problem.linear_constraints.add(lin_expr=restriccion, senses=['L']*len(restriccion), rhs=[1]*len(restriccion))
        
    # Restriccion 6 y 6b
    restriccion_6   = []
    restriccion_6_b = []
    for d in range(data.cantidad_dias):
        for h in range(data.cantidad_turnos):
            for o in range(data.cantidad_ordenes):
                lhs   = cplex.SparsePair() 
                lhs_b = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):  
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                    lhs_b.ind.append(X[(t, o, h, d)])
                    lhs_b.val.append(1)
                #Aplicamos distributiva a (1-delta)*M
                lhs.ind.append('CONSTANT1_AUX')
                lhs.val.append(data.M)
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(-data.M)
                lhs.ind.append('CONSTANT2_AUX')
                lhs.val.append(-data.ordenes[o].trabajadores_necesarios)#To
                lhs_b.ind.append('CONSTANT2_AUX')
                lhs_b.val.append(-data.ordenes[o].trabajadores_necesarios)
                restriccion_6.append(lhs)
                restriccion_6_b.append(lhs_b)
    my_problem.linear_constraints.add(lin_expr=restriccion_6, senses=['G']*len(restriccion_6), rhs=[0]*len(restriccion_6))
    my_problem.linear_constraints.add(lin_expr=restriccion_6_b, senses=['L']*len(restriccion_6_b), rhs=[0]*len(restriccion_6_b))

    # Restriccion 7
    restriccion_lesser = []
    restriccion_greater = []
    for (o1, o2) in data.ordenes_correlativas:
        lhs_lesser = cplex.SparsePair() 
        lhs_greater = cplex.SparsePair() 
        for h in range(data.cantidad_turnos):
            if h<4:
                for d in range(data.cantidad_dias):
                    lhs_lesser.ind.append(Delta[(o1, h, d)])
                    lhs_lesser.val.append(1)
                    lhs_lesser.ind.append(Delta[(o2, h+1, d)])
                    lhs_lesser.val.append(-1)
                    lhs_greater.ind.append(Delta[(o1, h, d)])
                    lhs_greater.val.append(1)
                    lhs_greater.ind.append(Delta[(o2, h+1, d)])
                    lhs_greater.val.append(-1)
                    restriccion_lesser.append(lhs_lesser)
                    restriccion_greater.append(lhs_greater)
    my_problem.linear_constraints.add(lin_expr=restriccion_lesser, senses=['L']*len(restriccion_lesser), rhs=[0]*len(restriccion_lesser))
    my_problem.linear_constraints.add(lin_expr=restriccion_greater, senses=['G']*len(restriccion_greater), rhs=[0]*len(restriccion_greater))

    
    # Restriccion 8 y 9 
    restriccion_max = []
    restriccion_min = []
    restriccion_zMAX = []
    restriccion_zMAX_sum = []
    restriccion_zMIN = []
    restriccion_zMIN_sum = []
    for t in range(data.cantidad_trabajadores):  
        lhs_max = cplex.SparsePair()
        lhs_min = cplex.SparsePair()
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                for o in range(data.cantidad_ordenes):
                    lhs_max.ind.append(X[(t, o, h, d)])
                    lhs_max.val.append(1)
                    lhs_min.ind.append(X[(t, o, h, d)])
                    lhs_min.val.append(1)
        lhs_max.ind.append('MAX_ORDERS')
        lhs_max.val.append(-1)
        lhs_min.ind.append('MIN_ORDERS')
        lhs_min.val.append(-1)
        restriccion_min.append(lhs_min)
        restriccion_max.append(lhs_max)
          
        lhs = cplex.SparsePair()
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
        lhs.ind.append('CONSTANT1_AUX')
        lhs.val.append(data.M)
        lhs.ind.append(zMAX[t])
        lhs.val.append(-data.M)
        lhs.ind.append('MAX_ORDERS')
        lhs.val.append(-1)
        restriccion_zMAX.append(lhs)
        

        
        lhs = cplex.SparsePair()
        lhs.ind.append(zMAX[t])
        lhs.val.append(1)
        restriccion_zMAX_sum.append(lhs)

    
        lhs = cplex.SparsePair()
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
        lhs.ind.append('CONSTANT1_AUX')
        lhs.val.append(-data.M)
        lhs.ind.append(zMIN[t])
        lhs.val.append(+data.M)
        lhs.ind.append('MIN_ORDERS')
        lhs.val.append(-1)
        restriccion_zMIN.append(lhs)

        lhs = cplex.SparsePair()
        lhs.ind.append(zMIN[t])
        lhs.val.append(1)
        restriccion_zMIN_sum.append(lhs)

    
    my_problem.linear_constraints.add(lin_expr=restriccion_zMAX, senses=['G']*len(restriccion_zMAX), rhs=[0]*len(restriccion_zMAX))
    my_problem.linear_constraints.add(lin_expr=restriccion_zMAX_sum, senses=['E']*len(restriccion_zMAX_sum), rhs=[1]*len(restriccion_zMAX_sum))
    my_problem.linear_constraints.add(lin_expr=restriccion_zMIN, senses=['L']*len(restriccion_zMIN), rhs=[0]*len(restriccion_zMIN))
    my_problem.linear_constraints.add(lin_expr=restriccion_zMIN_sum, senses=['E']*len(restriccion_zMIN_sum), rhs=[1]*len(restriccion_zMIN_sum))
    my_problem.linear_constraints.add(lin_expr=restriccion_max, senses=['L']*len(restriccion_max), rhs=[0]*len(restriccion_max))
    my_problem.linear_constraints.add(lin_expr=restriccion_min, senses=['G']*len(restriccion_min), rhs=[0]*len(restriccion_min))

    # Restriccion 10
    lhs = cplex.SparsePair()
    lhs.ind.append('MAX_ORDERS')
    lhs.val.append(1)
    lhs.ind.append('MIN_ORDERS')
    lhs.val.append(-1)
    my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[10])

    lhs = cplex.SparsePair()
    lhs.ind.append('MAX_ORDERS')
    lhs.val.append(1)
    lhs.ind.append('MIN_ORDERS')
    lhs.val.append(-1)
    my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])
    
    

    #Restricciones función objetivo
    wh1   = []
    wh2_left   = []
    wh2_right   = []
    wh3_left   = []
    wh3_right   = []
    wh4   = []
    s1_s2    = []
    s2_s3    = []
    link  = []
    for t in range(data.cantidad_trabajadores):
        #WH1
        lhs = cplex.SparsePair([S1[t],WH1[t]], [5.0,-1])
        wh1.append(lhs)
        

        #WH2
        lhs = cplex.SparsePair([S2[t],WH2[t]], [5.0,-1])
        wh2_left.append(lhs)

        lhs = cplex.SparsePair([WH2[t],S1[t]], [1,-5.0])
        wh2_right.append(lhs)

        #WH3
        lhs = cplex.SparsePair([S3[t],WH3[t]], [5.0,-1])
        wh3_left.append(lhs)

        lhs = cplex.SparsePair([WH3[t],S2[t]], [1,-5.0])
        wh3_right.append(lhs)

        #WH4
        lhs = cplex.SparsePair([WH4[t],S3[t]], [1,-6.0])
        wh4.append(lhs)

        #S1>=S2
        lhs = cplex.SparsePair([S1[t],S2[t]], [1,-1])
        s1_s2.append(lhs)

        #S2>=S3
        lhs = cplex.SparsePair([S2[t],S3[t]], [1,-1])
        s2_s3.append(lhs)

        #Link
        lhs = cplex.SparsePair()
        lhs.ind.append(WH1[t])
        lhs.val.append(1)
        lhs.ind.append(WH2[t])
        lhs.val.append(1)
        lhs.ind.append(WH3[t])
        lhs.val.append(1)
        lhs.ind.append(WH4[t])
        lhs.val.append(1)
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(-1)  
        link.append(lhs)
    my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])
    my_problem.linear_constraints.add(lin_expr=wh2_left, senses=['L']*len(wh2_left), rhs=[0]*len(wh2_left))
    my_problem.linear_constraints.add(lin_expr=wh2_right, senses=['L']*len(wh2_right), rhs=[0]*len(wh2_right))
    my_problem.linear_constraints.add(lin_expr=wh3_left, senses=['L']*len(wh3_left), rhs=[0]*len(wh3_left))
    my_problem.linear_constraints.add(lin_expr=wh3_right, senses=['L']*len(wh3_right), rhs=[0]*len(wh3_right))
    my_problem.linear_constraints.add(lin_expr=wh4, senses=['L']*len(wh4), rhs=[0]*len(wh4))
    my_problem.linear_constraints.add(lin_expr=s1_s2, senses=['G']*len(s1_s2), rhs=[0]*len(s1_s2))
    my_problem.linear_constraints.add(lin_expr=s2_s3, senses=['G']*len(s2_s3), rhs=[0]*len(s2_s3))
    my_problem.linear_constraints.add(lin_expr=link, senses=['G']*len(link), rhs=[0]*len(link))

        


def add_variables(my_problem, data):
    #Constantes necesarias para las restricciones
    my_problem.variables.add(lb = [1], 
                             ub = [1], 
                             types=['B'],
                             names=['CONSTANT1_AUX']
                             )
    my_problem.variables.add(lb = [1], 
                             ub = [1], 
                             types=['B'],
                             names=['CONSTANT2_AUX']
                             )
    # Variables binarias que representan a Ao y, al agregarle el beneficio de la orden
    # como peso en la función objetivo, también representa a SUM(Bo*Ao)
    i=0
    A = {}
    for orden in data.ordenes:
        my_problem.variables.add(obj = [orden.beneficio], 
                                lb = [0], 
                                ub = [1], 
                                types=['B'],
                                names=[f'A_{i}']
                                )
        A[i] = f'A_{i}'
        i+=1
    
    X = {}
    for t in range(data.cantidad_trabajadores):
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    my_problem.variables.add(lb = [0], 
                                             ub = [1], 
                                             types=['B'],
                                             names=[f"X_{t}_{o}_{h}_{d}"]
                                             )
                    X[(t,o,h,d)] = f"X_{t}_{o}_{h}_{d}"
    
    E = {}
    for t in range(data.cantidad_trabajadores):
        for d in range(data.cantidad_dias):
            my_problem.variables.add(lb = [0], 
                                    ub = [1], 
                                    types=['B'],
                                    names=[f'E_{t}_{d}']
                                    )
            E[(t,d)] = f'E_{t}_{d}'
    
    F = {}
    for t in range(data.cantidad_trabajadores):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'F_{t}_{h}_{d}']
                                         )
                F[(t,h,d)] = f'F_{t}_{h}_{d}'
    
    Delta = {}
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'Delta_{o}_{h}_{d}']
                                         ) 
                Delta[(o,h,d)] = f'Delta_{o}_{h}_{d}'
    
    WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN = {},{},{},{},{},{},{},{},{}      
    for t in range(data.cantidad_trabajadores):
        my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'S1_{t}']
                                         )
        S1[t] = f'S1_{t}'
        my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'S2_{t}']
                                         )
        S2[t] = f'S2_{t}'
        my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'S3_{t}']
                                         )
        S3[t] = f'S3_{t}'
        my_problem.variables.add(obj = [-1000],
                                         lb = [0], 
                                         ub = [5], 
                                         types=['I'],
                                         names=[f'WH1_{t}']
                                         ) 
        WH1[t] = f'WH1_{t}'
        my_problem.variables.add(obj = [-1200],
                                         lb = [0], 
                                         ub = [5], 
                                         types=['I'],
                                         names=[f'WH2_{t}']
                                         ) 
        WH2[t] = f'WH2_{t}'
        my_problem.variables.add(obj = [-1400],
                                         lb = [0], 
                                         ub = [5], 
                                         types=['I'],
                                         names=[f'WH3_{t}']
                                         ) 
        WH3[t] = f'WH3_{t}'
        my_problem.variables.add(obj = [-1500],
                                         lb = [0], 
                                         ub = [6], 
                                         types=['I'],
                                         names=[f'WH4_{t}']
                                         )
        WH4[t] = f'WH4_{t}'
        
        my_problem.variables.add(
                                 lb = [0], 
                                 ub = [1], 
                                 types=['B'],
                                 names=[f'zMAX_{t}']
                                 )
        zMAX[t] = f'zMAX_{t}'

        my_problem.variables.add(
                                     lb = [0], 
                                     ub = [1], 
                                     types=['B'],
                                     names=[f'zMIN_{t}']
                                     )
        zMIN[t] = f'zMIN_{t}'


    #Variables MIN Y MAX de órdenes
    my_problem.variables.add(lb = [1], 
                             ub = [data.cantidad_ordenes], 
                             types=['I'],
                             names=['MAX_ORDERS']
                             )
    my_problem.variables.add(lb = [1], 
                             ub = [data.cantidad_ordenes], 
                             types=['I'],
                             names=['MIN_ORDERS']
                             )

    

    return A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN


def populate_by_row(my_problem, data):

    A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN = add_variables(my_problem, data)

    # Seteamos direccion del problema
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.minimize)

    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion. 
    add_constraint_matrix(my_problem, data, A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN)

    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('balanced_assignment.lp')

def solve_lp(my_problem, data):
    
    # Resolvemos el ILP.
    start_time = time.time()
    my_problem.solve()
    end_time = time.time()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    variables_name = my_problem.variables.get_names()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ',objective_value)
    print('Status solucion: ',status_string,'(' + str(status) + ')')

    status_json = {
        'TIME':[round(end_time - start_time,2)],
        'A':{'VAR':[],'VAL':[]},
        'X':{'VAR':[],'VAL':[]},
        'D':{'VAR':[],'VAL':[]},
        'E':{'VAR':[],'VAL':[]},
        'F':{'VAR':[],'VAL':[]},
        'S':{'VAR':[],'VAL':[]},
        'W':{'VAR':[],'VAL':[]},
        'M':{'VAR':[],'VAL':[]},
        'RESULT':[],
        'zMAX':{'VAR':[],'VAL':[]},
        'zMIN':{'VAR':[],'VAL':[]}
    }
        
    for i in range(len(x_variables)):
        # Tomamos esto como valor de tolerancia, por cuestiones numericas.
        if x_variables[i] > TOLERANCE:
            if variables_name[i][0] not in ('z','C','S'):
                print(variables_name[i] + ':' , x_variables[i])
                status_json[variables_name[i][0]]['VAR'].append(variables_name[i])
                status_json[variables_name[i][0]]['VAL'].append(x_variables[i])
    status_json['RESULT'] = objective_value
    with open(f'../data/output/status_{sys.argv[2].strip()}.json', 'w') as json_file:
        json.dump(status_json, json_file)

def main():
    
    # Obtenemos los datos de la instancia.
    data = get_instance_data()
    
    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    nodeselect_strategy = {'df':0,'bb':1}
    prob_lp.parameters.mip.strategy.nodeselect.set(nodeselect_strategy[sys.argv[3].strip()])
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)


if __name__ == '__main__':
    #Must give as arguments:
    #1) data path
    #2) problem name
    #3) nodeselect strategy = df or bb
    #EXAMPLE: python3 field_service.py ../data/new_week_1000.txt 1000_orders_df df
    main()
