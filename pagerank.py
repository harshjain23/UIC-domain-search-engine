import math
import numpy
import pandas


def ensure_positive(matrix):
    matrix = matrix.T
    for colKey in matrix:
        if matrix[colKey].sum() == 0.0:
            matrix[colKey] = pandas.Series(numpy.ones(len(matrix[colKey])), index=matrix.index)
    return matrix.T


def extract_nodes(matrix):
    nodes = set()
    for colKey in matrix:
        nodes.add(colKey)
    for rowKey in matrix.T:
        nodes.add(rowKey)
    return nodes


def start(nodes):
    if len(nodes) == 0: raise ValueError("There must be at least one node.")
    startProb = 1.0 / float(len(nodes))
    return pandas.Series({node : startProb for node in nodes})


def make_square(matrix, keys, default=0.0):
    matrix = matrix.copy()

    def insert_missing_columns(matrix):
        for key in keys:
            if not key in matrix:
                matrix[key] = pandas.Series(default, index=matrix.index)
        return matrix
    matrix = insert_missing_columns(matrix)
    matrix = insert_missing_columns(matrix.T).T
    return matrix.fillna(default)


def apply_p_rank(weights):
    rsp = 0.15
    weights = pandas.DataFrame(weights)
    nodes = extract_nodes(weights)
    weights = make_square(weights, nodes, default=0.0)
    weights = ensure_positive(weights)
    curr = start(nodes)
    probabilities = weights.div(weights.sum(axis=1), axis=0)
    alpha = 1.0 / float(len(nodes)) * rsp
    probabilities = probabilities.copy().multiply(1.0 - rsp) + alpha
    for iteration in range(1000):
        temp = curr.copy()
        curr = curr.dot(probabilities)
        delta = curr - temp
        if (math.sqrt(delta.dot(delta))) < 0.00001:
            break
    return curr
