import numpy as np

import pandas as pd

class Graph:
    """
    Graph class for the implementation of the shultze voting method
    Graph.adj_matr is the representation of the graph in matrix form
    """

    def __init__(self, node_list):
        """
        Builder of Graph class
        :param node_list: List[str] with the names of the nodes(or candidates)
        """
        self.adj_matr = np.zeros((len(node_list), len(node_list)))
        self.num_node = len(node_list)
        self.node_dict = {node_list[i]: i for i in range(len(node_list))}
        self.strong = None
        self.best_found = None

    def add_arch(self, node1, node2, weight):
        """
        Method for connecting two nodes, one way
        :param node1: str key for first node
        :param node2: str key for second node
        :param weight: int weight of the arch
        :return: self
        """
        n1, n2 = self.node_dict[node1], self.node_dict[node2]
        self.adj_matr[n1, n2] = weight
        return self

    def decode_pref(self, p_list, n_list=None):
        """
        Creates preferece matrix, matrix[i, j] = the number of entities that prefers i to j
        :param p_list: List[List[str]] matrix with all the preferences
        :param n_list: List[int] list with the number of occurances of the p_list values if none all are considered once
        :return: self
        """
        if n_list is None:
            n_list = list(np.ones(len(p_list)))
        for pref, n in zip(p_list, n_list):
            for i in range(len(pref)):
                for j in range(i, len(pref)):
                    if i != j:
                        x1, x2 = pref[i], pref[j]
                        self.adj_matr[self.node_dict[x1], self.node_dict[x2]] += n
        return self

    def get_strong_matrix(self):
        """
        Computes the widest path for each combination
        matrix[i, j] = width of the widest path
        :return: self
        """
        if self.strong is not None:
            return self.strong
        strong = np.zeros(self.adj_matr.shape)
        n = strong.shape[0]
        for i in range(n):
            for j in range(n):
                if i != j:
                    if self.adj_matr[i, j] > self.adj_matr[j, i]:
                        strong[i, j] = self.adj_matr[i, j]
                    else:
                        strong[i, j] = 0
        for i in range(n):
            for j in range(n):
                if i != j:
                    for k in range(n):
                        if i != k and j != k:
                            strong[j, k] = max(strong[j, k], min(strong[j, i], strong[i, k]))
        self.strong = strong
        return self.strong

    def find_best(self, string_format=False):
        """
        find the best candidate using the shultze method
        https://en.wikipedia.org/wiki/Schulze_method
        :param string_format: Bool specify if you want results in a string or List
        :return: List of the results in order of preference or string if string_format is True
        """
        s = self.get_strong_matrix()
        lis = [[] for x in range(s.shape[0])]
        for i in range(s.shape[0]):
            cont = 0
            for j in range(s.shape[1]):
                if s[i, j] > s[j, i]:
                    cont += 1
            else:
                lis[cont].append(list(self.node_dict)[i])
        fin = []
        for i in lis:
            if i:
                fin.append(i)
        self.best_found = fin
        if string_format:
            return self.__present(fin)
        return fin

    def __present(self, win_list):
        """
        return nicely formatted string to illustrate results
        :param win_list: object graph from find_best
        :return:
        """
        out = ""
        cont = 1
        for place in reversed(win_list):
            if place:
                out += str(cont) + ": " + str(place) + "\n"
                cont += 1
        return out

    @staticmethod
    def read_json(file, vote='Preference', identifier='Email', rank='Position'):
        """
        Static method for decoding json file and returning an instance of the
        Graph class
        :param file: str path to json file
        :param vote: str name of the vote preference column
        :param identifier: str name of the identifier column
        :param rank: str name of the rank column
        :return: Graph object
        """
        data = pd.read_json(file)
        films = data[vote].unique()
        graph = Graph(list(films))
        mat = list(data.sort_values(by=rank).
                   groupby(by=identifier, sort=False)[vote].
                   apply(list))
        graph.decode_pref(mat)
        return graph
