from ortools.linear_solver import pywraplp
import pandas as pd
from typing import List, Dict
import argparse

class ProductOptimizer:
	"""
	Add Doc Here
	"""
	def __init__(self, retention_csv: str):
		"""
		Read data from csv path
		:param retention_csv: Path to csv containing data
		"""
		self.retention_csv = retention_csv
		self.data_df = pd.read_csv(retention_csv, sep=",")
		self.solver = pywraplp.Solver.CreateSolver('SCIP')

	def create_data_model(self, list_name: List) -> Dict:
		"""
		Read data from CSV file and return a matrix with all needed data
		:param list_name: List of products to use
		:return: Data needed for computation
		"""
		product_list = self.get_product_list(list_name)
		data_matrix = self.create_data_matrix(product_list, list_name)
		return data_matrix

	def get_product_list(self, list_name: List) -> List:
		"""
		Search need product from given matrix
		:param list_name: List of products to extract
		:return: List of found products
		"""
		list_index = []
		for name in list_name:
			index = 0
			found_product = False
			for i, prod in enumerate(self.data_df.columns.to_list()):
				if self.data_df.columns.to_list()[i] == name:
					index = i
					found_product = True
			if not found_product:
				print("Wrong product name - {0} - Problem might not be solvable \n".format(name))
			else:
				list_index.append(index)
		return list_index

	def create_data_matrix(self, product_list: List, list_name: List) -> Dict:
		"""
		Creating the matrix used to solve the problem
		:param product_list: List of found prodicts
		:param list_name: List of products to use
		:return: Matrix contraining all data needed for computation
		"""
		matrix = []
		# TODO: Replace double for loop
		for i in range(len(product_list)):
			matrix.append([])
			for j in range(len(product_list)):
				matrix[i].append(self.data_df.values[product_list[i]][product_list[j]])

		data = {
			"comp_matrix": matrix,
			"num_product": len(matrix),
			'name_product': list_name
		}
		# Si aucun nom, on met juste des numéros de produits
		if len(data['name_product']) == 0:
			data['name_product'] = range(data['num_product'])
		return data

	@staticmethod
	def verify_data_model(data: Dict) -> bool:
		"""
		Verifiy input data
		:param data: Data Matrix
		:return: Whether if matrix is right or not
		"""
		right_input = True
		for i in range(data['num_product']):
			matrix_line = data['comp_matrix'][i]
			if len(matrix_line) != data['num_product']:
				print("len(comp_matrix[{0}]) = {1} while there is {2} lines in the matrix.\n".format(i, len(matrix_line),
					                                                                               data['num_product']))
				right_input = False
		if len(data['name_product']) != data['num_product']:
			print("There is {0} names of products and {1} products.\n".format(len(data['name_product']),
			                                                                  data['num_product']))
			right_input = False
		if not right_input:
			print("WRONG INPUT: problem will not be solved.\n")
		return right_input

	@staticmethod
	def process_result(status, data, comp_var, group) -> List:
		"""
		Resolve optimization problem
		:param status: Solver Status
		:param data: Data matrix
		:param comp_var: Matrice X
		:param group: Matrice Y
		:return: Liste des groupes avec les produits associés
		"""
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

	def run_simulation(self, list_name):
		"""
		Run Main
		:param list_name: List of products to use
		:return:
		"""
		data = self.create_data_model(list_name)
		assert self.verify_data_model(data)

		#########################
		# Creation des matrices #
		#########################

		# Creating group variables, with 0 product each (Y)
		# Crée la matrice Y avec une colonne par produit (liste), remplie de 0
		group = {}
		for i in range(data['num_product']):
			group[i] = self.solver.IntVar(0, 1, 'group[%d]' % i)
		num_group = self.solver.NumVariables()

		# Creating compatibility variables (X)
		# Crée la matrice X, avec une ligne par produit et une colone par groupe, remplie de 0
		comp_var = []
		for i in range(data['num_product']):
			comp_var.append([])
			for j in range(data['num_product']):
				comp_var[i].append(self.solver.IntVar(0, 1, "comp_var[{0}][{1}]".format(i, j)))
		num_compat_var = self.solver.NumVariables() - data['num_product']

		############################
		# Creation des contraintes #
		############################

		# Contraintes de choix de groupe
		# Assure qu'un produit n'est attribué qu'a un seul groupe
		for i in range(data['num_product']):
			constraint_expr = \
				[data['comp_matrix'][i][j] * comp_var[i][j] for j in range(data['num_product'])]
			self.solver.Add(sum(constraint_expr) == 1)

		# Contraintes d'incompatibilite
		# Assure que deux produits icompatibles ne sont pas associés au même groupe.
		for i in range(data['num_product']):
			for j in range(data['num_product']):
				for k in range(data['num_product']):
					if (data['comp_matrix'][i][k] == 1 and data['comp_matrix'][j][k] == 1 and data['comp_matrix'][i][
						j] == 0):
						self.solver.Add(comp_var[i][k] + comp_var[j][k] <= 1)

		# Contraintes pour la création d'un groupe
		# Assure de ne pas associé trop de produits dans chaque groupe
		# Quand on associe un produit à un nouveau groupe dans la matrice X, crée le groupe dans la matrice Y (0->1)
		for i in range(data['num_product']):
			constraint_expr = [data['comp_matrix'][j][i] * comp_var[j][i] for j in range(data['num_product'])]
			self.solver.Add(sum(constraint_expr) <= data['num_product'] * group[i])

		# Coef 1 pour chaque produit
		num_constraints = self.solver.NumConstraints()
		objective = self.solver.Objective()
		for j in range(data['num_product']):
			objective.SetCoefficient(group[j], 1)
		objective.SetMinimization()

		# Variables
		var_count = {
			'num_group': num_group,
			'num_compat_var': num_compat_var,
			'num_constraints': num_constraints
		}

		#################
		# Solve problem #
		#################

		status = self.solver.Solve()
		pair_product_group_list = self.process_result(status, data, comp_var, group)
		pair_product_group_list = sorted(pair_product_group_list, key=lambda x: x[1])
		return self.solver, pair_product_group_list, data, var_count

	@staticmethod
	def print_group(pair_product_group_list, data):
		"""Print the group"""
		print('\n---------------------Groups--------------------')
		pair_product_group_list = sorted(pair_product_group_list, key=lambda x: x[1])
		group_index = -1
		for pair_product_group in pair_product_group_list:
			if group_index != pair_product_group[1]:
				group_index = pair_product_group[1]
				print("\nGroup {0} contains : {1}".format(group_index, data['name_product'][pair_product_group[0]]))
			else:
				print("{0}                  {1}".format(" " * len(str(group_index)),
				                                        data['name_product'][pair_product_group[0]]))

if __name__== '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('products', metavar='P', type=str, nargs='+',
	                    help='Liste des produits pour optimization')
	parser.add_argument('-C','--csv_path', type=str, default='app/data/retention_pc.csv',
	                    help="Chemin vers le fichier CSV contenant la matrice de compatibilité")
	args = parser.parse_args()
	po = ProductOptimizer(args.csv_path)
	solver, pair_product_group_list, data, var_count = po.run_simulation(args.products)
	po.print_group(pair_product_group_list, data)
