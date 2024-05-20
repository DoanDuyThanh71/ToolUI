""" Read Page 3 """
import numpy as np
import time, os, pickle

from functools import reduce
from tabulate import tabulate
from sklearn import svm, tree
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

class IntuitiveFuzzy(object):


	def __init__(self, data, namefile, att_nominal_cate, delta, alpha, B, num_delta, dis_tg):
		#super(IntuitiveFuzzy, self).__init__()
		# self.data_train = data_train
		self.data = data
		# print(self.data)
		self.namefile = namefile
		# Including decision. Assume last column is decision values
		self.attributes = range(0, len(self.data[0]))
		self.C = self.attributes[:-1]
		self.B = B
		# self.dis_C = dis_C
		self.dis_tg = dis_tg
		# self.W = []
		self.arr_cate = att_nominal_cate
		self.arr_real = [i for i in self.attributes  if i not in att_nominal_cate]


		### For filtering phase ###
		self.num_attr = len(self.attributes)
		self.num_objs = len(self.data[:,0])
		# print("Doi tuong", self.num_objs)
		# print("num_obj",self.num_objs)
		self.num_delta = num_delta
		self.num_prev = self.num_objs - self.num_delta
		# print("num_prev", self.num_delta)
		# self.num_objs_icr = len(self.data[:,0])
		# self.num_delta = self.num_objs - self.num_prev
		self.num_class = len(set(self.data[:,-1]))
		self.delta = delta
		self.alpha = alpha

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
		shape_1, shape_2 = IFRM_1.shape[1], IFRM_1.shape[2]
		result = np.zeros((2, shape_1, shape_2), dtype=np.float32)

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
		ones = np.ones(IFRM[0].shape,dtype=np.float32)
		#caridnality = round(np.sum((ones + IFRM[0] - IFRM[1])/2),2)
		caridnality = np.sum((ones + IFRM[0] - IFRM[1])/2)
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
		dis = (1 / ((self.num_objs)**2)) * (IFRM_cardinality - IFRM_d_cardinality)
		return dis
	
	def incre_distance(self, M):
		tp1 = (self.num_prev)** 2 * self.dis_tg
		
		H = self._get_union_IFRM(M[:, self.num_prev:, :], self.relational_matrices[-1][:, self.num_prev:, :])
		
		tp3 = 1/2 * np.sum(- H[0, :, self.num_prev: ] + H[1, :, self.num_prev:] + M[0, self.num_prev:, self.num_prev:] - M[1, self.num_prev:, self.num_prev:])

		tp2 = ( self._get_cardinality( M[:, self.num_prev:, :]) - self._get_cardinality(H) )
	#     print("tp2 ", tp2)
		distance = (tp1 + 2 * tp2 - tp3) / ((self.num_objs)**2)
		# print("ABCD", distance)
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
		# print("dis_B", d)
		# print("dis_C", dis_C)
		while round(d,3) - round(dis_C, 3) > self.delta :
			li = [[cm, d - self.partition_dist_d(self._get_union_IFRM(IFRM_TG, self.relational_matrices[cm]))]
              for cm in np.setdiff1d(self.C, self.B)]
			# print("li",li)
			pt = max(li, key=lambda x: x[1])
			IFRM_TG = self._get_union_IFRM(IFRM_TG, self.relational_matrices[pt[0]])
			d = d - pt[1]
			self.B.append(pt[0])
		# Add reduce one variable step
		finish = time.time() - start
		# print("dis_B", d)
		# print("dis_C", dis_C)
		self.dis_tg = d
		return self.B, self.dis_tg, finish
	
	# dist_C_up = incre_distance(dist_C, M_C_up)
	# dist_B_up = incre_distance(dist_B, M_B_up)

	# Filter stage when adding object set delta_O = {o4, o5}
	def filter_incre(self):
		matrix_C = reduce(self._get_union_IFRM, [self.relational_matrices[i] for i in self.attributes[:-1]])
		matrix_B = reduce(self._get_union_IFRM, [self.relational_matrices[i] for i in self.B])

		dis_C = self.incre_distance(matrix_C)
		dis_B = self.incre_distance(matrix_B)
		# if round(dis_B, 4) - round(dis_C, 4) > 0.001: delta = 0.001
		# else: delta = self.delta
		# print("dis_C", round(dis_C,3))
		# print("dis_B", round(dis_B,3))
		# dis_prev = np.copy(self.dis_tg)
		start = time.time()
		# Filter attributes
		while round(dis_B - dis_C, 3) > 0.001 :
			# print("Dis_prev", dis_prev)
			# Sig = dist_B_up - incre_distance -> Choice max Sig
			li = [[cm, dis_B - self.incre_distance(self._get_union_IFRM(matrix_B, self.relational_matrices[cm]))] 
												for cm in np.setdiff1d(self.C, self.B)]
			pt = max(li, key=lambda x: x[1])
			
			# Calculate partition B at next step
			matrix_B = self._get_union_IFRM(matrix_B, self.relational_matrices[pt[0]])
			if pt[1] <= 0.001: break
			dis_B = dis_B - pt[1]
			self.B.append(pt[0])
			# if pt[1] <= 0.001: break
		self.dis_tg = dis_B
		finish = time.time() - start
		if len(self.B) <= 1: return self.B, self.dis_tg, finish
		for c_m in self.B:
			# remove one variable
			new_B = np.setdiff1d(self.B, [c_m]).tolist()
			# recalculate the d(P(B), P(B u {d}))
			matrix_B = reduce(self._get_union_IFRM, [self.relational_matrices[c_m] for c_m in new_B])
			dis_remove_cm = self.partition_dist_d(matrix_B)
			if round(dis_remove_cm - dis_B, 3) <= 0.001 :
				# if len(self.B) == 1: return self.B, self.dis_tg, finish
				# print("Loai bo c_M ",c_m)
				self.B = new_B
		finish = time.time() - start
		return self.B, self.dis_tg, finish

	def scores(self, reduct):
		# y_test = self.data[:,-1]
		# y_test = y_test.astype(int)
		# print(reduct)
		# list_index = [self.attributes[:-1].index(i) for i in reduct]
		# X_test = self.data[:,list_index]
		# print(list_index)

		y_train = self.data[:,-1]
		y_train = y_train.astype(int)
		X_train = self.data[:, reduct]


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
		y_train = self.data[:,-1]
		y_train = y_train.astype(int)
		
		
		# X_test_o = self.data[:,:-1]
		X_train_o = self.data[:,:-1]


		clf_o = cf.fit(X_train_o, y_train)
		# scores_o = round(clf_o.score(X_test_o, y_test),3)
		#clf = KNeighborsClassifier(n_neighbors=10)
		H_o = cross_val_score(clf_o, X_train_o, y_train, cv=10)
		scores_o = round(H_o.mean(),3)
		std_o = round(np.std(H_o), 3)



		# Calculate Filter
		# reduct_f = reduct_f[-1]
		# X_test = self.data[:, reduct_f]
		X_train = self.data[:, reduct_f]

		clf = cf.fit(X_train, y_train)
		# scores_f = round(clf.score(X_test, y_train),3)
		H_f = cross_val_score(clf, X_train, y_train, cv=10)
		scores_f = round(H_f.mean(),3)
		std_f = round(np.std(H_f), 3)

		return (name,len(self.attributes)-1, len(reduct_f),
			 scores_o, std_o, scores_f, std_f, round(time_f,3), list(self.B), self.alpha)

  

