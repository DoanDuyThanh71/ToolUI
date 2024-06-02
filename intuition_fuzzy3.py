""" Read Page 3 """
import numpy as np
import time, os, pickle

from functools import reduce
from tabulate import tabulate
from sklearn import svm, tree
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

class IntuitiveFuzzy(object):


	def __init__(self, data, split_indice, namefile, att_nominal_cate, delta, alpha, B, num_delta, dis_tg_C, dis_tg_B):
		#super(IntuitiveFuzzy, self).__init__()
		# self.data_train = data_train
		self.data = data
		self.split_indice = split_indice
		self.namefile = namefile
		# Including decision. Assume last column is decision values
		self.attributes = range(0, len(self.data[0]))
		self.C = self.attributes[:-1]
		self.B = B
		# self.dis_C = dis_C
		self.dis_tg_C = dis_tg_C
		self.dis_tg_B = dis_tg_B

		# self.W = []
		self.arr_cate = att_nominal_cate
		self.arr_real = [i for i in self.attributes  if i not in att_nominal_cate]

		### For filtering phase ###
		self.num_attr = len(self.attributes)
		self.num_objs = len(self.data[:,0])
		# print("Doi tuong", split_indice)
		# print("num_obj",self.num_objs)
		self.num_delta = num_delta
		# print("doi tuong truoc", self.num_delta)
		self.num_prev = self.num_objs - self.num_delta
		# print("num_prev", self.num_delta)
		# self.num_objs_icr = len(self.data[:,0])
		# self.num_delta = self.num_objs - self.num_prev
		self.num_class = len(set(self.data[:,-1]))
		self.delta = delta
		self.alpha = alpha
		# print("Alpha", self.alpha)

		self.relational_matrices = self._get_single_attr_IFRM(self.data)
		self.IFRM = None
		self.dis_IFRM = None
		self.D = None
		# print(self.num_objs)
		# print(self.num_prev)
		#self.matrix_C = self._get_multiple_attr_IFRM()
		#self.alpha = np.mean(np.sort(list(set(self.matrix_C[0].flatten()))))
		# self.delta = delta
		
		#self.arr_acc = []
		#self.acc = 0.0
		

	def alpha_level(self, IFRM):
		# alpha = self.alpha
		beta = (1 - self.alpha) / (1 + self.alpha)
		# pi = (1.-IFRM[0]- IFRM[1])
		IFRM[0][IFRM[0] < self.alpha] = 0.
		IFRM[0][IFRM[1] > beta] = 0.
		# IFRM[0][pi > self.pi] = 0.
		IFRM[1][IFRM[0] == 0] = 1.

		return IFRM


	def _get_single_attr_IFRM(self, data):
		"""
			This function returns a dictionary of relational matrices corresponding to
			each single attributes
			Params :
				- data : The numpy DataFrame of sample data
			Returns :
				- result : The dictionary of relational matrices corresponding each attribute
		"""
		result = []
		column_d = data[:,-1]
		matrix_D = np.zeros((self.num_objs, self.num_objs), dtype=np.float32)
		matrix_D = 1 - np.abs(np.subtract.outer(column_d, column_d))

		list_index_real = [list(self.attributes).index(i) for i in self.arr_real]
		for k in self.attributes:
			column = data[:,k]
			std = np.std(column, ddof = 1)
			rel_matrix = np.zeros((2, self.num_objs, self.num_objs), np.float32)

			if k in list_index_real:
				rel_matrix[0] = 1 - np.abs(np.subtract.outer(column, column))
				if std == 0.0: lamda = 1.0
				else: lamda = (np.sum(np.minimum(rel_matrix[0], matrix_D))/np.sum(matrix_D))/std
				rel_matrix[1] = ((1.0 - rel_matrix[0]) / (1.0 + lamda * rel_matrix[0]))
				rel_matrix = self.alpha_level(rel_matrix)
			else:
				for i in range(self.num_objs - 1):
					rel_matrix[0,i, i + 1:] = list(map(lambda x: 1.0 if x == column[i] else 0.0, column[i+1:]))
					rel_matrix[0,i + 1:, i] = rel_matrix[0,i, i + 1:]

				rel_matrix[0][np.diag_indices(self.num_objs)] = 1.0
				rel_matrix[1] = 1.0 - rel_matrix[0]
			rel_matrix = np.array(rel_matrix)
			result.append(rel_matrix)
			# result = np.array(result)
		return result

	def _get_union_IFRM(self, IFRM_1, IFRM_2):
		"""
			This function will return the intuitive  relational matrix of P union Q
			where P and Q are two Intuitionistic Matrix.
			Note : in the paper R{P union Q} = R{P} intersect R{Q}
			Params :
				- IFRM_1 : First Intuitionistic Fuzzy Matrix
				- IFRM_2 : Second Intuitionistic Fuzzy Matrix
			Returns :
				- result : The IFRM of P intersect Q
		"""
		# result = np.zeros((2,self.num_objs, self.num_objs),dtype=np.float32)
		# num_objs = IFRM_1[0].shape[0]
		# shape_1, shape_2 = IFRM_1.shape[1], IFRM_1.shape[2]
		result = np.zeros((2, self.num_objs, self.num_objs), dtype=np.float32)

		result[0] = np.minimum(IFRM_1[0], IFRM_2[0])
		result[1] = np.maximum(IFRM_1[1], IFRM_2[1])

		return result

	def _get_cardinality(self, IFRM):
		"""
			Returns the caridnality of a Intuitionistic Matrix
			Params :
				- IFRM : An intuitive fuzzy relational matrix
			Returns :
				- caridnality : The caridnality of that parition
		"""
		# ones = np.ones(IFRM[0].shape,dtype=np.float32)
		#caridnality = round(np.sum((ones + IFRM[0] - IFRM[1])/2),2)
		caridnality = np.sum((1. + IFRM[0] - IFRM[1])) /2
		return caridnality

	def partition_dist_d(self, IFRM): #Tinh tren U + dU
		"""
			This function returns the distance partition to d: D(P_B, P_{B U{d}})
			Params : IFRM is intuitiononstic fuzzy relation matrix
			Returns :
				- result : A scalar representing the distance
		"""
		IFRM_cardinality = self._get_cardinality(IFRM)
		IFRM_d = self._get_union_IFRM(IFRM, self.relational_matrices[self.attributes[-1]])
		IFRM_d_cardinality = self._get_cardinality(IFRM_d)
		dis = (1 / ((self.split_indice)**2)) * (IFRM_cardinality - IFRM_d_cardinality)
		return dis
	

	def incre_distance(self, dis, M):

		tp1 = (self.num_delta)** 2 * dis
		# print("tp1", tp1)
		
		H = self._get_union_IFRM(M, self.relational_matrices[-1])
		
		tp3 = 1/2 * np.sum(- H[0, self.split_indice:self.num_delta, self.split_indice:self.num_delta ] + H[1, self.split_indice:self.num_delta, self.split_indice:self.num_delta] 
					 + M[0, self.split_indice : self.num_delta, self.split_indice:self.num_delta] - M[1, self.split_indice : self.num_delta, self.split_indice : self.num_delta])
		# print("tp3 ", tp3)
		tp2 = self._get_cardinality( M[:, self.split_indice :self.num_delta , :self.num_delta]) - self._get_cardinality(H[:, self.split_indice:self.num_delta, :self.num_delta])
		# print("tp2 ", tp2)
		distance = (tp1 - 2 * tp2 + tp3) / ((self.split_indice)**2)

		return distance

	def sig(self, IFRM, a):
		"""
			This function measures the significance of an attribute a to the set of
			attributes B. This function begin use step 2.
			Params :
				- IFRM : intuitionistic matrix relation
				- a : an attribute in C but not in B
			Returns :
				- sig : significance value of a to B
		"""
		d2 = self.partition_dist_d(self._get_union_IFRM(IFRM,self.relational_matrices[a]))
		sig = d2

		return sig

	def filter(self):
		"""
			The main function for the filter phase
			Params :
				- verbose : Show steps or not
			Returns :
				- W : A list of potential attributes list
		"""
		# initialization
		# self.B = []
		matrix_C = reduce(self._get_union_IFRM, [self.relational_matrices[i] for i in self.attributes[:-1]])
		dis_C = self.partition_dist_d(matrix_C)

		# Filter phase
		start = time.time()
		c_m = min(np.setdiff1d(self.C, self.B), key=lambda x: self.partition_dist_d(self.relational_matrices[x]))
		self.B.append(c_m)
		
		IFRM_TG = self.relational_matrices[c_m]
		d = self.partition_dist_d(IFRM_TG)

		while round(d,3) - round(dis_C, 3) > self.delta :
			li = [[cm, self.partition_dist_d(self._get_union_IFRM(IFRM_TG, self.relational_matrices[cm]))]
              for cm in np.setdiff1d(self.C, self.B)]

			pt = min(li, key=lambda x: x[1])
			IFRM_TG = self._get_union_IFRM(IFRM_TG, self.relational_matrices[pt[0]])
			d = pt[1]
			print("d: ", d)
			self.B.append(pt[0])
		self.dis_tg_C = dis_C
		self.dis_tg_B = d
		# Add reduce one variable step
		finish = time.time() - start
		# self.dis_tg = d
		return self.B, self.dis_tg_C, self.dis_tg_B, finish
	

	# Filter stage when adding object set delta_O = {o4, o5}
	def filter_incre(self):
		matrix_C = reduce(self._get_union_IFRM, [self.relational_matrices[i] for i in self.attributes[:-1]])
		matrix_B = reduce(self._get_union_IFRM, [self.relational_matrices[i] for i in self.B])
		dis_B_incre = self.incre_distance(self.dis_tg_B, matrix_B)
		dis_C_incre = self.incre_distance(self.dis_tg_C, matrix_C)
		# print("dis_B_incre", dis_B_incre)	
		# print("dis_C_incre", dis_C_incre)	
		# dis_C = self.incre_distance(matrix_C)
		# dis_C = self.incre_distance(self.dis_tg_C, matrix_C)
		# print("Dis_B", dis_B)
		# print("Dis_C", dis_C)

		# car_B = self._get_cardinality(matrix_B[:, :self.split_indice, :self.split_indice])
		# IFRM_d = self._get_union_IFRM(matrix_B, self.relational_matrices[self.attributes[-1]])
		# IFRM_d_cardinality = self._get_cardinality(IFRM_d[:, :self.split_indice, :self.split_indice])
		# dis_B = (1 / ((self.split_indice)**2)) * (car_B  - IFRM_d_cardinality)			


		# car_C = self._get_cardinality(matrix_C[:, :self.split_indice, :self.split_indice])
		# IFRM_d_C = self._get_union_IFRM(matrix_C, self.relational_matrices[self.attributes[-1]])
		# IFRM_d_cardinality_C = self._get_cardinality(IFRM_d_C[:, :self.split_indice, :self.split_indice])
		# dis_C = (1 / ((self.split_indice)**2)) * (car_C  - IFRM_d_cardinality_C)		


		# print("Dis_B", dis_B)
		# print("Dis_C", dis_C)
		# print("DTG", dtg)
		start = time.time()
		# if round(dis_B,3) - round(dis_C, 3) > 0.001:
		# 	finish = time.time() - start
		# 	return self.B, self.dis_tg_C, self.dis_tg_B, finish
		# self.dis_tg_B = np.copy(dis_B_incre)
		# B = np.copy(self.B)
		# # Filter attributes
		while round(dis_B_incre,3) - round(dis_C_incre, 3) > 0.001:
			# print("Dis_prev", dis_prev)
			# Sig = dist_B_up - incre_distance -> Choice max Sig
			# new_B = np.setdiff1d(self.B, [c_m]).tolist()
			li = [[cm, self.incre_distance(self.dis_tg_B,reduce(self._get_union_IFRM, [self.relational_matrices[x] for x in np.setdiff1d(self.B, [cm])]))] 
												for cm in self.B]
			# print(li)
			pt = max(li, key=lambda x: x[1])
			# print("PT1", pt[1])
			# self.dis_tg_B = pt[1]
			# print("dis_B", dis_B)
			if pt[1] <= dis_B_incre : 
				# self.dis_tg_B = dis_B
				self.B.remove(pt[0])
				dis_B_incre = pt[1]
				break
			else: 
				self.dis_tg_B = pt[1]
				# self.dis_tg_B = np.copy(dis_B_incre)
				break
			# self.dis_tg_B = dis_B
		# 	# Calculate partition B at next step
		# 	matrix_B = self._get_union_IFRM(matrix_B, self.relational_matrices[pt[0]])
			# if pt[1] <= 0.001:
			# 	dis_B = np.copy(pt[1])
			# 	self.B = np.setdiff1d(self.B, [pt[0]])
			# 	break
				# self.B = np.setdiff1d(self.B, [pt[0]])
				# dis_B = np.copy(pt[1])
		# self.B = np.copy(B)
		# matrix_B_new = reduce(self._get_union_IFRM, [self.relational_matrices[i] for i in self.B])
		# dis_B_incre_new = self.incre_distance(self.dis_tg_B, matrix_B_new)
		# print("New",dis_B_incre_new)

		# car_B = self._get_cardinality(matrix_B_new[:, :self.split_indice, :self.split_indice])
		# IFRM_d = self._get_union_IFRM(matrix_B_new, self.relational_matrices[self.attributes[-1]])
		# IFRM_d_cardinality = self._get_cardinality(IFRM_d[:, :self.split_indice, :self.split_indice])
		# dis_B_new = (1 / ((self.split_indice)**2)) * (car_B  - IFRM_d_cardinality)			

		# print("New2",dis_B_new)
			# max_c = dis_B
			# h = []
			# for x in self.B:
			# 	dis_incre_x = self.partition_dist_d(reduce(self._get_union_IFRM, [self.relational_matrices[x] for x in np.setdiff1d(self.B, [x])]))
			# 	h.append([x,dis_incre_x])
			# pt = max(h, key=lambda h: h[1])
			# self.B.remove(pt[0])
			# self.dis_tg_B = pt[1]
			# break
		self.dis_tg_C = np.copy(dis_C_incre)
		finish = time.time() - start
		return self.B, self.dis_tg_C, self.dis_tg_B, finish

	def scores(self, reduct):
		# y_test = self.data[:,-1]
		# y_test = y_test.astype(int)
		# print(reduct)
		# list_index = [self.attributes[:-1].index(i) for i in reduct]
		# X_test = self.data[:,list_index]
		# print(list_index)

		y_train = self.data[:self.split_indice,-1]
		y_train = y_train.astype(int)
		X_train = self.data[:self.split_indice, reduct]


		#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
		# clf = tree.DecisionTreeClassifier()
		# clf = svm.SVC(kernel='rbf', C=1, random_state=42).fit(X_train, y_train)
		# clf = KNeighborsClassifier(n_neighbors=10).fit(X_train, y_train)
		# clf = svm.SVC(kernel='rbf', C=1, random_state=42)
		clf = KNeighborsClassifier(n_neighbors=5)
		H = cross_val_score(clf, X_train, y_train, cv=10)
		acc = round(H.mean(), 3)
		std = round(np.std(H), 3)
		# scores = round(cross_val_score(clf, X_train, y_train, cv=10).mean(),3)
		# scores = clf.score(X_test, y_test)
		#self.arr_acc.append(scores)

		return acc, std
	
	def update_dataset(self, data):
		'''
			This is a function to update incremental dataset
			Params:
				- data: new dataset
		'''
		self.data = data
		# self.prev = num_prev

	def update_n_objs(self):
		'''
			This is a function to update a new number of objects
		'''
		# self.num_prev += self.num_objs
		# self.num_delta = self.num_objs - self.num_prev
		self.num_objs = len(self.data[:,0])
		# self.dis_tg = self.dis_tg
	
	def update_dis(self, dis):
		self.dis_tg = dis

	def update_n_attribute(self, B):
		'''
			This is a function to update a new list of attributes
			Params:lear
				- B: list of attribute after wrapper phase of previous step.
		'''
		# TODO: save reduct set into self.B
		# self.dis_tg = dis_tg
		self.B = B

	def update_retional_matrices(self):
		'''
			This is a function to update relational_matrices
		'''
		self.relational_matrices = self._get_single_attr_IFRM(self.data)
		

	def evaluate(self, name, reduct_f, time_f):
		# print("reduct_f", reduct_f)
		# cf = tree.DecisionTreeClassifier()
		# cf= svm.SVC(kernel='rbf', C=1, random_state=42)
		cf = KNeighborsClassifier(n_neighbors=5)

		# y_test= self.data[:,-1]
		# y_test = y_test.astype(int)
		y_train = self.data[:self.split_indice,-1]
		y_train = y_train.astype(int)
		
		
		# X_test_o = self.data[:,:-1]
		X_train_o = self.data[:self.split_indice,:-1]


		clf_o = cf.fit(X_train_o, y_train)
		# scores_o = round(clf_o.score(X_test_o, y_test),3)
		#clf = KNeighborsClassifier(n_neighbors=10)
		H_o = cross_val_score(clf_o, X_train_o, y_train, cv=10)
		scores_o = round(H_o.mean(),3)
		std_o = round(np.std(H_o), 3)



		# Calculate Filter
		# reduct_f = reduct_f[-1]
		# X_test = self.data[:, reduct_f]
		X_train = self.data[:self.split_indice, reduct_f]

		clf = cf.fit(X_train, y_train)
		# scores_f = round(clf.score(X_test, y_train),3)
		H_f = cross_val_score(clf, X_train, y_train, cv=10)
		scores_f = round(H_f.mean(),3)
		std_f = round(np.std(H_f), 3)

		return (name,len(self.attributes)-1, len(reduct_f),
			 scores_o, std_o, scores_f, std_f, round(time_f,3), list(self.B), self.alpha)
