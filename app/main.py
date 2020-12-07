from __future__ import print_function
from ortools.linear_solver import pywraplp
import pandas as pd


def create_complete_data(csv_path : str = 'data/retention_pc.csv'):
    df = pd.read_csv(csv_path, sep=",")
    return df.values, df.columns.to_list(), df

def read_product_name(csv_path: str = 'data/product_names.csv'):
    df = pd.read_csv(csv_path, sep=",")
    return df.columns.to_list()

def create_data_model(full_matrix, full_product_name_list, list_name):
    """Stores the data for the problem."""
    list_index = []
    for name in list_name:
        index = 0
        found_product = False
        for i, prod in enumerate(full_product_name_list):
            if full_product_name_list[i] == name:
                index = i
                found_product = True
        if not found_product:
            print("Wrong product name - {0} - Problem might not be solvable \n".format(name))
        else:
            list_index.append(index)

    # Creating the matrix used to solve the problem
    matrix = []
    for i in range(len(list_index)):
        matrix.append([])
        for j in range(len(list_index)):
            matrix[i].append(full_matrix[list_index[i]][list_index[j]])

    data = {
        "comp_matrix": matrix,
        "num_product": len(matrix),
        'name_product': list_name
    }
    # Si aucun nom, on met juste des numéros de produits
    if len(data['name_product']) == 0:
        data['name_product'] = range(data['num_product'])
    return data

def verify_data_model(data):
  """Verifies the shape of the input"""
  right_input = True
  for i in range(data['num_product']):
    matrix_line = data['comp_matrix'][i]
    if len(matrix_line) != data['num_product']:
      print("len(comp_matrix[{0}]) = {1} while there is {2} lines in the matrix.\n".format(i, len(matrix_line), data['num_product']))
      right_input = False

  if len(data['name_product']) != data['num_product']:
    print("There is {0} names of products and {1} products.\n".format(len(data['name_product']), data['num_product']))
    right_input = False
  if not right_input:
    print("WRONG INPUT: problem will not be solved.\n")

  return right_input

def process_result(solver, status, data, comp_var, group):
  """Process the result"""
  if status == pywraplp.Solver.OPTIMAL:

    min_index_group = 0
    for i in range(data['num_product']):
      if group[i].solution_value() == 1:
        min_index_group = i
        break

    print('\nNumber of groups = %d' % solver.Objective().Value())
    pair_product_group_list = []
    for i in range(data['num_product']):
      for j in range(data['num_product']):
          if comp_var[i][j].solution_value() == 1:
            pair_product_group_list.append([i,j - min_index_group])

    print_group(pair_product_group_list, data)

    print('\n------------Resolution information-------------\n')
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes\n' % solver.nodes())
  else:
    print('The problem does not have an optimal solution.')
  return

def print_group(pair_product_group_list, data):
  """Print the group"""

  print('\n---------------------Groups--------------------')
  pair_product_group_list = sorted(pair_product_group_list, key = lambda x: x[1])
  group_index = -1
  for pair_product_group in pair_product_group_list:
    if group_index != pair_product_group[1]:
      group_index = pair_product_group[1]
      print("\nGroup {0} contains : {1}".format(group_index, data['name_product'][pair_product_group[0]]))
    else:
      print("{0}                  {1}".format(" "*len(str(group_index)),data['name_product'][pair_product_group[0]]))


def main():
    print('\n\n----------Creating data and variables----------\n')
    full_matrix, full_product_name_list, _ = create_complete_data()
    list_product_name = read_product_name()
    data = create_data_model(full_matrix, full_product_name_list, list_product_name)

    if not verify_data_model(data):
        return

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Creating group variables
    group = {}
    for i in range(data['num_product']):
        group[i] = solver.IntVar(0, 1, 'group[%d]' % i)
    print('Maximal number of groups =', solver.NumVariables())

    # Creating compatibility variables
    comp_var = []
    for i in range(data['num_product']):
        comp_var.append([])
        for j in range(data['num_product']):
            comp_var[i].append(solver.IntVar(0, 1, "comp_var[{0}][{1}]".format(i, j)))
    print('Number of compatibility variables =', solver.NumVariables() - data['num_product'])

    # Contraintes de choix de groupe
    for i in range(data['num_product']):
        constraint_expr = \
            [data['comp_matrix'][i][j] * comp_var[i][j] for j in range(data['num_product'])]
        solver.Add(sum(constraint_expr) == 1)

    # Contraintes d'incompatibilite
    for i in range(data['num_product']):
        for j in range(data['num_product']):
            for k in range(data['num_product']):
                if (data['comp_matrix'][i][k] == 1 and data['comp_matrix'][j][k] == 1 and data['comp_matrix'][i][
                    j] == 0):
                    solver.Add(comp_var[i][k] + comp_var[j][k] <= 1)

    # Contraintes pour la création d'un groupe
    for i in range(data['num_product']):
        constraint_expr = \
            [data['comp_matrix'][j][i] * comp_var[j][i] for j in range(data['num_product'])]
        solver.Add(sum(constraint_expr) <= data['num_product'] * group[i])

    print('Number of constraints =', solver.NumConstraints())

    objective = solver.Objective()
    for j in range(data['num_product']):
        objective.SetCoefficient(group[j], 1)
    objective.SetMinimization()

    print('\n\n--------------------Solving--------------------')
    status = solver.Solve()
    process_result(solver, status, data, comp_var, group)

if __name__ == '__main__':
    main()
