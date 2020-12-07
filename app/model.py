from __future__ import print_function
from ortools.linear_solver import pywraplp

class AppModel:
	def __init__(self, full_matrix, full_product_name_list):
		self.full_matrix = full_matrix
		self.full_product_name_list = full_product_name_list
		self.solver = pywraplp.Solver.CreateSolver('SCIP')

	def create_data_model(self, list_name):
		"""Stores the data for the problem."""
		full_matrix = self.full_matrix
		full_product_name_list = self.full_product_name_list
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

	def verify_data_model(self, data):
		"""Verifies the shape of the input"""
		right_input = True
		for i in range(data['num_product']):
			matrix_line = data['comp_matrix'][i]
			if len(matrix_line) != data['num_product']:
				print(
					"len(comp_matrix[{0}]) = {1} while there is {2} lines in the matrix.\n".format(i, len(matrix_line),
					                                                                               data['num_product']))
				right_input = False

		if len(data['name_product']) != data['num_product']:
			print("There is {0} names of products and {1} products.\n".format(len(data['name_product']),
			                                                                  data['num_product']))
			right_input = False
		if not right_input:
			print("WRONG INPUT: problem will not be solved.\n")

		return right_input

	def process_result(self, status, data, comp_var, group):
		"""Process the result"""
		pair_product_group_list = None
		if status == pywraplp.Solver.OPTIMAL:
			min_index_group = 0
			for i in range(data['num_product']):
				if group[i].solution_value() == 1:
					min_index_group = i
					break
			pair_product_group_list = []
			for i in range(data['num_product']):
				for j in range(data['num_product']):
					if comp_var[i][j].solution_value() == 1:
						pair_product_group_list.append([i, j - min_index_group])
		return pair_product_group_list

	def run(self, list_name):
		self.solver = pywraplp.Solver.CreateSolver('SCIP')
		data = self.create_data_model(list_name)
		if not  self.verify_data_model(data):
			return

		# Creating group variables
		group = {}
		for i in range(data['num_product']):
			group[i] = self.solver.IntVar(0, 1, 'group[%d]' % i)
		num_group = self.solver.NumVariables()

		# Creating compatibility variables
		comp_var = []
		for i in range(data['num_product']):
			comp_var.append([])
			for j in range(data['num_product']):
				comp_var[i].append(self.solver.IntVar(0, 1, "comp_var[{0}][{1}]".format(i, j)))
		num_compat_var = self.solver.NumVariables() - data['num_product']

		# Contraintes de choix de groupe
		for i in range(data['num_product']):
			constraint_expr = \
				[data['comp_matrix'][i][j] * comp_var[i][j] for j in range(data['num_product'])]
			self.solver.Add(sum(constraint_expr) == 1)

		# Contraintes d'incompatibilite
		for i in range(data['num_product']):
			for j in range(data['num_product']):
				for k in range(data['num_product']):
					if (data['comp_matrix'][i][k] == 1 and data['comp_matrix'][j][k] == 1 and data['comp_matrix'][i][
						j] == 0):
						self.solver.Add(comp_var[i][k] + comp_var[j][k] <= 1)

		# Contraintes pour la création d'un groupe
		for i in range(data['num_product']):
			constraint_expr = [data['comp_matrix'][j][i] * comp_var[j][i] for j in range(data['num_product'])]
			self.solver.Add(sum(constraint_expr) <= data['num_product'] * group[i])

		num_constraints = self.solver.NumConstraints()

		objective = self.solver.Objective()
		for j in range(data['num_product']):
			objective.SetCoefficient(group[j], 1)
		objective.SetMinimization()

		var_count = {
			'num_group': num_group,
			'num_compat_var': num_compat_var,
			'num_constraints': num_constraints
		}
		status = self.solver.Solve()
		pair_product_group_list = self.process_result(status, data, comp_var, group)
		pair_product_group_list = sorted(pair_product_group_list, key=lambda x: x[1])
		return self.solver, pair_product_group_list, data, var_count
