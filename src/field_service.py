import sys
import cplex

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
    

def add_constraint_matrix(my_problem, data, A, X, E, F, Delta):
    
    # Restriccion 1
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):
                    lhs.add(X[(t, o, h, d)], 1.0)
                lhs.add(Delta[(o, h, d)], -1.0)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=0)

    # Restriccion 2
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs = cplex.SparsePair()
                for t in range(data.cantidad_trabajadores):
                    lhs.add(X[(t, o, h, d)], 1.0)
                lhs.add(Delta[(o, h, d)], -data.M)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=0)

    # Restriccion 3
    for o in range(data.cantidad_ordenes):
        lhs = cplex.SparsePair()
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                for t in range(data.cantidad_trabajadores):
                    lhs.add(X[(t, o, h, d)], 1.0)
        lhs.add(A[o], -1)
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=0)

    # Restriccion 4
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs.add(X[(t, o, h, d)], 1.0)
            lhs.add(E[(d,t)], -1)
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=0)
        
    # Restriccion 5
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs.add(X[(t, o, h, d)], 1.0)
            lhs.add(E[(t,d)], -data.M)
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=0)

    # Restriccion 6
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.add(X[(t, o, h, d)], 1.0)
                lhs.add(F[(t,h,d)], -1)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=0)

    # Restriccion 7
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.add(X[(t, o, h, d)], 1.0)
                lhs.add(F[(t,h,d)], -data.M)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=0)

    #----------------- RESTRICCIONES DEL PROBLEMA
    # Restriccion 1
    for o in range(data.cantidad_ordenes):
        lhs = cplex.SparsePair()
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs.add(Delta[(o, h, d)], 1.0)
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=1)

    # Restriccion 2
    for t in range(data.cantidad_trabajadores):    
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs.add(X[(t, o, h, d)], 1.0)
                my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=1)

    # Restriccion 3
    for t in range(data.cantidad_trabajadores):  
        lhs = cplex.SparsePair()  
        for d in range(data.cantidad_dias):
            lhs.add(E[(d,t)], 1.0)
        my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=5)

    # Restriccion 4
    for t in range(data.cantidad_trabajadores):  
        for d in range(data.cantidad_dias):
            lhs = cplex.SparsePair()  
            for h in range(data.cantidad_turnos):
                lhs.add(F[(t,h,d)], 1.0)
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['L'], rhs=4)
    
    # Restriccion 5
    ...

    # Restriccion 6
    for d in range(data.cantidad_dias):
        for h in range(data.cantidad_turnos):
            for o in range(data.cantidad_ordenes):
                lhs = cplex.SparsePair() 
                for t in range(data.cantidad_trabajadores):  
                    lhs.add(X[(t, o, h, d)], 1.0)
                #Aplicamos distributiva a (1-delta)*M
                lhs.add_constant(data.M)
                lhs.add(Delta[o, h, d], -data.M)
                lhs.add(data.trabajadores_necesarios[o]) #To
            my_problem.linear_constraints.add(lin_expr=[lhs], senses=['G'], rhs=0)


def add_variables(my_problem, data):
    # Variables binarias que representan a Ao y, al agregarle el beneficio de la orden
    # como peso en la función objetivo, también representa a SUM(Bo*Ao)

    i=0
    A = {}
    for orden in data.ordenes:
        A[i] = my_problem.variables.add(obj = orden.beneficio, 
                                lb = [0], 
                                ub = [1], 
                                types=['B'],
                                names=[f'A_{i}']
                                )
        i+=1
    
    X = {}
    for t in range(data.cantidad_trabajadores):
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    X[(t,o,h,d)] = my_problem.variables.add(lb = [0], 
                                            ub = [1], 
                                            types=['B'],
                                            names=[f'X_{t}_{o}_{h}_{d}']
                                            )
    
    E = {}
    for t in range(data.cantidad_trabajadores):
        for d in range(data.cantidad_dias):
            E[(t,d)] = my_problem.variables.add(lb = [0], 
                                    ub = [1], 
                                    types=['B'],
                                    names=[f'E_{t}_{d}']
                                    )
    
    F = {}
    for t in range(data.cantidad_trabajadores):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                F[(t,h,d)] = my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'F_{t}_{h}_{d}']
                                         )
    
    Delta = {}
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                Delta[(o,h,d)] = my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'Delta_{o}_{h}_{d}']
                                         ) 
                
    return A, X, E, F, Delta


def populate_by_row(my_problem, data):

    A, X, E, F, Delta = add_variables(my_problem, data)

    # Seteamos direccion del problema
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.minimize)

    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion. 
    add_constraint_matrix(my_problem, data, A, X, E, F, Delta)

    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('balanced_assignment.lp')

def solve_lp(my_problem, data):
    
    # Resolvemos el ILP.
    
    my_problem.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ',objective_value)
    print('Status solucion: ',status_string,'(' + str(status) + ')')

    # Imprimimos las variables usadas.
    for i in range(len(x_variables)):
        # Tomamos esto como valor de tolerancia, por cuestiones numericas.
        if x_variables[i] > TOLERANCE:
            print('x_' + str(data.items[i].index) + ':' , x_variables[i])

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
