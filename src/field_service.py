import sys
import cplex
import json

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
                          WH1, WH2, WH3, WH4, S1, S2, S3):
    
    # Restriccion 1
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(-1)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])

    # Restriccion 2
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(-data.M)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

    # Restriccion 3
    for o in range(data.cantidad_ordenes):
        lhs = cplex.SparsePair()
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_trabajadores):
                    lhs.ind.append(X[(t,o, h, d)])
                    lhs.val.append(1)
        lhs.ind.append(A[o])
        lhs.val.append(-1)
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])

    # Restriccion 4
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
            lhs.ind.append(E[(t,d)])
            lhs.val.append(-1)
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])
        
    # Restriccion 5
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
            lhs.ind.append(E[(t,d)])
            lhs.val.append(-data.M)
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

    # Restriccion 6
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(F[(t,h,d)])
                lhs.val.append(-1)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])

    # Restriccion 7
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                lhs.ind.append(F[(t,h,d)])
                lhs.val.append(-data.M)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

    #----------------- RESTRICCIONES DEL PROBLEMA
    # Restriccion 1
    for o in range(data.cantidad_ordenes):
        lhs = cplex.SparsePair()
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(1)
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[1])

    # Restriccion 2
    for t in range(data.cantidad_trabajadores):    
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[1])

    # Restriccion 3
    for t in range(data.cantidad_trabajadores):  
        lhs = cplex.SparsePair()  
        for d in range(data.cantidad_dias):
            lhs.ind.append(E[(t,d)])
            lhs.val.append(1)
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[5])

    # Restriccion 4
    for t in range(data.cantidad_trabajadores):  
        for d in range(data.cantidad_dias):
            lhs = cplex.SparsePair()  
            for h in range(data.cantidad_turnos):
                lhs.ind.append(F[(t,h,d)])
                lhs.val.append(1)
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[4])
    
    # Restriccion 5
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
                        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[1])
        
    # Restriccion 6
    for d in range(data.cantidad_dias):
        for h in range(data.cantidad_turnos):
            for o in range(data.cantidad_ordenes):
                lhs = cplex.SparsePair() 
                for t in range(data.cantidad_trabajadores):  
                    lhs.ind.append(X[(t, o, h, d)])
                    lhs.val.append(1)
                #Aplicamos distributiva a (1-delta)*M
                lhs.ind.append('AUX_CONSTANT1')
                lhs.val.append(data.M)
                lhs.ind.append(Delta[(o, h, d)])
                lhs.val.append(-data.M)
                lhs.ind.append('AUX_CONSTANT2')
                lhs.val.append(-data.ordenes[o].trabajadores_necesarios)#To
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])

    # Restriccion 7
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
                    my_problem.linear_constraints.add(lin_expr=[lhs_lesser], senses=['L'], rhs=[0])
                    my_problem.linear_constraints.add(lin_expr=[lhs_greater], senses=['G'], rhs=[0])

    # Restriccion 8 y 9
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
        my_problem.linear_constraints.add(lin_expr=[lhs_max], senses=['L'], rhs=[0])
        my_problem.linear_constraints.add(lin_expr=[lhs_min], senses=['G'], rhs=[0])

    # Restriccion 10
    lhs = cplex.SparsePair()
    lhs.ind.append('MAX_ORDERS')
    lhs.val.append(1)
    lhs.ind.append('MIN_ORDERS')
    lhs.val.append(-1)
    my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[10])

    #Restricciones función objetivo
    for t in range(data.cantidad_trabajadores):
        #WH1
        lhs = cplex.SparsePair([S1[t],WH1[t]], [5.0,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

        #WH2
        lhs = cplex.SparsePair([S2[t],WH2[t]], [5.0,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

        lhs = cplex.SparsePair([WH2[t],S1[t]], [1,-5.0])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

        #WH3
        lhs = cplex.SparsePair([S3[t],WH3[t]], [5.0,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

        lhs = cplex.SparsePair([WH3[t],S2[t]], [1,-5.0])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

        #WH4
        lhs = cplex.SparsePair([WH4[t],S3[t]], [1,-6.0])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=[0])

        #S1>=S2
        lhs = cplex.SparsePair([S1[t],S2[t]], [1,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])

        #S2>=S3
        lhs = cplex.SparsePair([S2[t],S3[t]], [1,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])

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
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=[0])


def add_variables(my_problem, data):
    #Constantes necesarias para las restricciones
    my_problem.variables.add(lb = [1], 
                             ub = [1], 
                             types=['B'],
                             names=['AUX_CONSTANT1']
                             )
    my_problem.variables.add(lb = [1], 
                             ub = [1], 
                             types=['B'],
                             names=['AUX_CONSTANT2']
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
    
    WH1, WH2, WH3, WH4, S1, S2, S3 = {},{},{},{},{},{},{}      
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
    return A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3


def populate_by_row(my_problem, data):

    A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3 = add_variables(my_problem, data)

    # Seteamos direccion del problema
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.minimize)

    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion. 
    add_constraint_matrix(my_problem, data, A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3)

    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('balanced_assignment.lp')

def solve_lp(my_problem, data):
    
    # Resolvemos el ILP.
    
    my_problem.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    variables_name = my_problem.variables.get_names()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ',objective_value)
    print('Status solucion: ',status_string,'(' + str(status) + ')')

    status_json = {
        'A':{'VAR':[],'VAL':[]},
        'X':{'VAR':[],'VAL':[]},
        'D':{'VAR':[],'VAL':[]},
        'E':{'VAR':[],'VAL':[]},
        'F':{'VAR':[],'VAL':[]},
        'S':{'VAR':[],'VAL':[]},
        'W':{'VAR':[],'VAL':[]},
        'M':{'VAR':[],'VAL':[]},
    }
        # Imprimimos las variables usadas.
    for i in range(len(x_variables)):
        # Tomamos esto como valor de tolerancia, por cuestiones numericas.
        if x_variables[i] > TOLERANCE:
            print(variables_name[i] + ':' , x_variables[i])
            status_json[variables_name[i][0]]['VAR'].append(variables_name[i])
            status_json[variables_name[i][0]]['VAL'].append(x_variables[i])
    with open('status.json', 'w') as json_file:
        json.dump(status_json, json_file)

def main():
    
    # Obtenemos los datos de la instancia.
    data = get_instance_data()
    
    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)


if __name__ == '__main__':
    main()
