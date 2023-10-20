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
                          WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN):
    
    # Restriccion VAR: 1, 2, 3
    # Restriccion PROB: 1, 6
    for o in range(data.cantidad_ordenes):
        lhs_var_3 = cplex.SparsePair()
        lhs_problema_1 = cplex.SparsePair()
        
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                lhs_var_1 = cplex.SparsePair()
                lhs_var_2 = cplex.SparsePair()
                lhs_problema_1.ind.append(Delta[(o, h, d)])
                lhs_problema_1.val.append(1)
                lhs_problema_6 = cplex.SparsePair() 
                for t in range(data.cantidad_trabajadores):
                    lhs_var_1.ind.append(X[(t, o, h, d)])
                    lhs_var_1.val.append(1)
                    lhs_var_2.ind.append(X[(t, o, h, d)])
                    lhs_var_2.val.append(1)
                    lhs_var_3.ind.append(X[(t,o, h, d)])
                    lhs_var_3.val.append(1)
                    lhs_problema_6.ind.append(X[(t, o, h, d)])
                    lhs_problema_6.val.append(1)
                lhs_var_1.ind.append(Delta[(o, h, d)])
                lhs_var_1.val.append(-1)
                my_problem.linear_constraints.add(lin_expr=[lhs_var_1], senses=['G'], rhs=[0])
                lhs_var_2.ind.append(Delta[(o, h, d)])
                lhs_var_2.val.append(-data.M)
                my_problem.linear_constraints.add(lin_expr=[lhs_var_2], senses=['L'], rhs=[0])
                #Aplicamos distributiva a (1-delta)*M
                lhs_problema_6.ind.append('CONSTANT1_AUX')
                lhs_problema_6.val.append(data.M)
                lhs_problema_6.ind.append(Delta[(o, h, d)])
                lhs_problema_6.val.append(-data.M)
                lhs_problema_6.ind.append('CONSTANT2_AUX')
                lhs_problema_6.val.append(-data.ordenes[o].trabajadores_necesarios)#To
                my_problem.linear_constraints.add(lin_expr=[lhs_problema_6], senses=['G'], rhs=[0])

        lhs_var_3.ind.append(A[o])
        lhs_var_3.val.append(-1)
        my_problem.linear_constraints.add(lin_expr=[lhs_var_3], senses=['G'], rhs=[0])
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_1], senses=['L'], rhs=[1])                   
                
               

    # Restriccion VAR: 4, 5
    # Restriccion PROB: 3
    for d in range(data.cantidad_dias):
        for t in range(data.cantidad_trabajadores):
            lhs_var_4 = cplex.SparsePair()
            lhs_var_5 = cplex.SparsePair()
            for o in range(data.cantidad_ordenes):
                for h in range(data.cantidad_turnos):
                    lhs_var_4.ind.append(X[(t, o, h, d)])
                    lhs_var_4.val.append(1)
                    lhs_var_5.ind.append(X[(t, o, h, d)])
                    lhs_var_5.val.append(1)
            lhs_var_4.ind.append(E[(t,d)])
            lhs_var_4.val.append(-1)
            my_problem.linear_constraints.add(lin_expr=[lhs_var_4], senses=['G'], rhs=[0])
            lhs_var_5.ind.append(E[(t,d)])
            lhs_var_5.val.append(-data.M)
            my_problem.linear_constraints.add(lin_expr=[lhs_var_5], senses=['L'], rhs=[0])
        
     # Restriccion VAR: 6, 7
    # Restriccion PROB:  
    for t in range(data.cantidad_trabajadores):
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                lhs_var_6 = cplex.SparsePair()
                lhs_var_7 = cplex.SparsePair()
                lhs_problema_2 = cplex.SparsePair()
                for o in range(data.cantidad_ordenes):
                    lhs_var_6.ind.append(X[(t, o, h, d)])
                    lhs_var_6.val.append(1)
                    lhs_var_7.ind.append(X[(t, o, h, d)])
                    lhs_var_7.val.append(1)
                    lhs_problema_2.ind.append(X[(t, o, h, d)])
                    lhs_problema_2.val.append(1)
                lhs_var_6.ind.append(F[(t,h,d)])
                lhs_var_6.val.append(-1)
                my_problem.linear_constraints.add(lin_expr=[lhs_var_6], senses=['G'], rhs=[0])
                lhs_var_7.ind.append(F[(t,h,d)])
                lhs_var_7.val.append(-data.M)
                my_problem.linear_constraints.add(lin_expr=[lhs_var_7], senses=['L'], rhs=[0])   
                my_problem.linear_constraints.add(lin_expr=[lhs_problema_2], senses=['L'], rhs=[1])
                

    # Restriccion PROB: 3, 4
    for t in range(data.cantidad_trabajadores):  
        lhs_problema_3 = cplex.SparsePair()  
        for d in range(data.cantidad_dias):
            lhs_problema_3.ind.append(E[(t,d)])
            lhs_problema_3.val.append(1)
            lhs_problema_4 = cplex.SparsePair()
            for h in range(data.cantidad_turnos):
                lhs_problema_4.ind.append(F[(t,h,d)])
                lhs_problema_4.val.append(1)
            my_problem.linear_constraints.add(lin_expr=[lhs_problema_4], senses=['L'], rhs=[4])
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_3], senses=['L'], rhs=[5])
    
    # Restriccion 5
    for (o1, o2) in data.ordenes_conflictivas:
        for h in range(data.cantidad_turnos):
            if h<4:
                for t in range(data.cantidad_trabajadores):    
                    for d in range(data.cantidad_dias):
                        lhs_problema_5 = cplex.SparsePair()
                        lhs_problema_5.ind.append(X[(t, o1, h, d)])
                        lhs_problema_5.val.append(1)
                        lhs_problema_5.ind.append(X[(t, o2, h+1, d)])
                        lhs_problema_5.val.append(1)
                        lhs_problema_5.ind.append(X[(t, o2, h, d)])
                        lhs_problema_5.val.append(1)
                        lhs_problema_5.ind.append(X[(t, o1, h+1, d)])
                        lhs_problema_5.val.append(1)
                        my_problem.linear_constraints.add(lin_expr=[lhs_problema_5], senses=['L'], rhs=[1])
        
    # Restriccion 7
    for (o1, o2) in data.ordenes_correlativas:
        lhs_problema_7_lesser = cplex.SparsePair() 
        lhs_problema_7_greater = cplex.SparsePair() 
        for h in range(data.cantidad_turnos):
            if h<4:
                for d in range(data.cantidad_dias):
                    lhs_problema_7_lesser.ind.append(Delta[(o1, h, d)])
                    lhs_problema_7_lesser.val.append(1)
                    lhs_problema_7_lesser.ind.append(Delta[(o2, h+1, d)])
                    lhs_problema_7_lesser.val.append(-1)
                    lhs_problema_7_greater.ind.append(Delta[(o1, h, d)])
                    lhs_problema_7_greater.val.append(1)
                    lhs_problema_7_greater.ind.append(Delta[(o2, h+1, d)])
                    lhs_problema_7_greater.val.append(-1)
                    my_problem.linear_constraints.add(lin_expr=[lhs_problema_7_lesser], senses=['L'], rhs=[0])
                    my_problem.linear_constraints.add(lin_expr=[lhs_problema_7_greater], senses=['G'], rhs=[0])

    
    # Restriccion 8 y 9 
    for t in range(data.cantidad_trabajadores):  
        lhs_problema_8_max = cplex.SparsePair()
        lhs_problema_8_min = cplex.SparsePair()
        for d in range(data.cantidad_dias):
            for h in range(data.cantidad_turnos):
                for o in range(data.cantidad_ordenes):
                    lhs_problema_8_max.ind.append(X[(t, o, h, d)])
                    lhs_problema_8_max.val.append(1)
                    lhs_problema_8_min.ind.append(X[(t, o, h, d)])
                    lhs_problema_8_min.val.append(1)
        lhs_problema_8_max.ind.append('MAX_ORDERS')
        lhs_problema_8_max.val.append(-1)
        lhs_problema_8_min.ind.append('MIN_ORDERS')
        lhs_problema_8_min.val.append(-1)
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_8_max], senses=['L'], rhs=[0])
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_8_min], senses=['G'], rhs=[0])


        
        lhs_problema_9 = cplex.SparsePair()
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    lhs_problema_9.ind.append(X[(t, o, h, d)])
                    lhs_problema_9.val.append(1)
        lhs_problema_9.ind.append('CONSTANT1_AUX')
        lhs_problema_9.val.append(data.M)
        lhs_problema_9.ind.append(zMAX[t])
        lhs_problema_9.val.append(-data.M)
        lhs_problema_9.ind.append('MAX_ORDERS')
        lhs_problema_9.val.append(-1)
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_9], senses=['G'], rhs=[0])

        
        lhs_problema_9_b = cplex.SparsePair()
        lhs_problema_9_b.ind.append(zMAX[t])
        lhs_problema_9_b.val.append(1)
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_9_b], senses=['E'], rhs=[1])

        #Link
        lhs_obj_6 = cplex.SparsePair()
        lhs_obj_6.ind.append(WH1[t])
        lhs_obj_6.val.append(1)
        lhs_obj_6.ind.append(WH2[t])
        lhs_obj_6.val.append(1)
        lhs_obj_6.ind.append(WH3[t])
        lhs_obj_6.val.append(1)
        lhs_obj_6.ind.append(WH4[t])
        lhs_obj_6.val.append(1)
        lhs_problema_10 = cplex.SparsePair()
        for o in range(data.cantidad_ordenes):
            for h in range(data.cantidad_turnos):
                for d in range(data.cantidad_dias):
                    lhs_problema_10.ind.append(X[(t, o, h, d)])
                    lhs_problema_10.val.append(1)
                    lhs_obj_6.ind.append(X[(t, o, h, d)])
                    lhs_obj_6.val.append(-1) 
        lhs_problema_10.ind.append('CONSTANT1_AUX')
        lhs_problema_10.val.append(-data.M)
        lhs_problema_10.ind.append(zMIN[t])
        lhs_problema_10.val.append(+data.M)
        lhs_problema_10.ind.append('MIN_ORDERS')
        lhs_problema_10.val.append(-1)
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_10], senses=['L'], rhs=[0])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_6], senses=['G'], rhs=[0])

        lhs_problema_10_b = cplex.SparsePair()
        lhs_problema_10_b.ind.append(zMIN[t])
        lhs_problema_10_b.val.append(1)
        my_problem.linear_constraints.add(lin_expr=[lhs_problema_10_b], senses=['E'], rhs=[1])

        #WH1
        lhs_obj_1 = cplex.SparsePair([S1[t],WH1[t]], [5.0,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_1], senses=['L'], rhs=[0])

        #WH2
        lhs_obj_2 = cplex.SparsePair([S2[t],WH2[t]], [5.0,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_2], senses=['L'], rhs=[0])

        lhs_obj_2_b = cplex.SparsePair([WH2[t],S1[t]], [1,-5.0])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_2_b], senses=['L'], rhs=[0])

        #WH3
        lhs_obj_3 = cplex.SparsePair([S3[t],WH3[t]], [5.0,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_3], senses=['L'], rhs=[0])

        lhs_obj_3_b = cplex.SparsePair([WH3[t],S2[t]], [1,-5.0])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_3_b], senses=['L'], rhs=[0])

        #WH4
        lhs_obj_4 = cplex.SparsePair([WH4[t],S3[t]], [1,-6.0])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_4], senses=['L'], rhs=[0])

        #S1>=S2
        lhs_obj_5 = cplex.SparsePair([S1[t],S2[t]], [1,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_5], senses=['G'], rhs=[0])

        #S2>=S3
        lhs_obj_5_b = cplex.SparsePair([S2[t],S3[t]], [1,-1])
        my_problem.linear_constraints.add(lin_expr=[lhs_obj_5_b], senses=['G'], rhs=[0])

    # Restriccion 10
    lhs_problema_11 = cplex.SparsePair()
    lhs_problema_11.ind.append('MAX_ORDERS')
    lhs_problema_11.val.append(1)
    lhs_problema_11.ind.append('MIN_ORDERS')
    lhs_problema_11.val.append(-1)
    my_problem.linear_constraints.add(lin_expr=[lhs_problema_11], senses=['L'], rhs=[10])

    lhs_problema_11_b = cplex.SparsePair()
    lhs_problema_11_b.ind.append('MAX_ORDERS')
    lhs_problema_11_b.val.append(1)
    lhs_problema_11_b.ind.append('MIN_ORDERS')
    lhs_problema_11_b.val.append(-1)
    my_problem.linear_constraints.add(lin_expr=[lhs_problema_11_b], senses=['G'], rhs=[0])

        


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
    A, X, E, F, Delta, WH1, WH2, WH3, WH4, S1, S2, S3, zMAX, zMIN = {},{},{},{},{},{},{},{},{},{},{},{},{},{} 
    for o in range(data.cantidad_ordenes):
        my_problem.variables.add(obj = [data.ordenes[o].beneficio], 
                                lb = [0], 
                                ub = [1], 
                                types=['B'],
                                names=[f'A_{i}']
                                )
        A[i] = f'A_{i}'
        i+=1
        for t in range(data.cantidad_trabajadores):
            for d in range(data.cantidad_dias):
                my_problem.variables.add(lb = [0], 
                                    ub = [1], 
                                    types=['B'],
                                    names=[f'E_{t}_{d}']
                                    )
                E[(t,d)] = f'E_{t}_{d}'
                for h in range(data.cantidad_turnos):
                    my_problem.variables.add(lb = [0], 
                                             ub = [1], 
                                             types=['B'],
                                             names=[f"X_{t}_{o}_{h}_{d}"]
                                             )
                    X[(t,o,h,d)] = f"X_{t}_{o}_{h}_{d}"

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
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'F_{t}_{h}_{d}']
                                         )
                F[(t,h,d)] = f'F_{t}_{h}_{d}'

    
    for o in range(data.cantidad_ordenes):
        for h in range(data.cantidad_turnos):
            for d in range(data.cantidad_dias):
                my_problem.variables.add(lb = [0], 
                                         ub = [1], 
                                         types=['B'],
                                         names=[f'Delta_{o}_{h}_{d}']
                                         ) 
                Delta[(o,h,d)] = f'Delta_{o}_{h}_{d}'

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
    with open('status.json', 'w') as json_file:
        json.dump(status_json, json_file)

def main():
    
    # Obtenemos los datos de la instancia.
    data = get_instance_data()
    
    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    # prob_lp.parameters.mip.strategy.nodeselect.set(1)
    # prob_lp.parameters.mip.strategy.variableselect.set(1)
    # prob_lp.parameters.mip.strategy.bbinterval.set(1)
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)


if __name__ == '__main__':
    main()
