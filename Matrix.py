import array
import unittest

class Matrix:
    """
    Clase que representa una matriz.

    Ejemplos:
    >>> matrix = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
    >>> print(matrix)
    1   2   3
    4   5   6
    >>> matrix[1, 1]
    5
    >>> matrix2 = Matrix(2, 3, [[7, 8, 9], [10, 11, 12]])
    >>> print(matrix + matrix2)
    8   10   12
    14   16   18
    >>> print(matrix * 2)
    2   4   6
    8   10   12
    >>> print(Matrix(2, 2, [[1, 2], [10, 20]]).multiply(matrix2))
    27   30   33
    270   300   330
    """

    def __init__(self, rows, cols, elements=None):
        self.rows = rows
        self.cols = cols
        self.elements = array.array('i', [0] * (rows * cols)) if elements is None else array.array('i', [element for row in elements for element in row])

    def __str__(self):
        return '\n'.join(['   '.join(map(str, self.elements[i:i+self.cols])) for i in range(0, len(self.elements), self.cols)])

    def __getitem__(self, index):
        i, j = index
        return self.elements[i * self.cols + j]

    def __add__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Las matrices deben tener las mismas dimensiones para la suma.")
        result = Matrix(self.rows, self.cols)
        result.elements = array.array('i', [a + b for a, b in zip(self.elements, other.elements)])
        return result

    def __mul__(self, scalar):
        result = Matrix(self.rows, self.cols)
        result.elements = array.array('i', [element * scalar for element in self.elements])
        return result

    def tolist(self):
        return [self.elements[i:i + self.cols].tolist() for i in range(0, len(self.elements), self.cols)]


    def multiply(self, other):
        if self.cols != other.rows:
            raise ValueError("El número de columnas de la primera matriz debe ser igual al número de filas de la segunda.")
        result = Matrix(self.rows, other.cols)
        for i in range(self.rows):
            for j in range(other.cols):
                result.elements[i * result.cols + j] = sum(self.elements[i * self.cols + k] * other.elements[k * other.cols + j] for k in range(self.cols))
        return result

    def add_elementwise(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Las matrices deben tener las mismas dimensiones para la suma elemento a elemento.")
        result = Matrix(self.rows, self.cols)
        result.elements = array.array('i', [a + b for a, b in zip(self.elements, other.elements)])
        return result

    def scalar_multiply_elementwise(self, scalar):
        result = Matrix(self.rows, self.cols)
        result.elements = array.array('i', [element * scalar for element in self.elements])
        return result

    def elementwise_multiply(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Las matrices deben tener las mismas dimensiones para la multiplicación elemento a elemento.")
        result = Matrix(self.rows, self.cols)
        result.elements = array.array('i', [a * b for a, b in zip(self.elements, other.elements)])
        return result

class TestMatrixMethods(unittest.TestCase):
    def test_matrix_initialization(self):
        matrix = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        self.assertEqual(matrix.rows, 2)
        self.assertEqual(matrix.cols, 3)
        self.assertEqual(matrix.tolist(), [[1, 2, 3], [4, 5, 6]])

    def test_matrix_addition(self):
        matrix_a = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        matrix_b = Matrix(2, 3, [[7, 8, 9], [10, 11, 12]])
        result = matrix_a + matrix_b
        self.assertEqual(result.tolist(), [[8, 10, 12], [14, 16, 18]])

    def test_scalar_multiplication(self):
        matrix = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        result = matrix * 2
        self.assertEqual(result.tolist(), [[2, 4, 6], [8, 10, 12]])

    def test_matrix_multiplication(self):
        matrix_a = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        matrix_b = Matrix(3, 2, [[7, 8], [9, 10], [11, 12]])
        result = matrix_a.multiply(matrix_b)
        self.assertEqual(result.tolist(), [[58, 64], [139, 154]])

    def test_elementwise_addition(self):
        matrix_a = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        matrix_b = Matrix(2, 3, [[7, 8, 9], [10, 11, 12]])
        result = matrix_a.add_elementwise(matrix_b)
        self.assertEqual(result.tolist(), [[8, 10, 12], [14, 16, 18]])

    def test_scalar_multiply_elementwise(self):
        matrix = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        result = matrix.scalar_multiply_elementwise(2)
        self.assertEqual(result.tolist(), [[2, 4, 6], [8, 10, 12]])

    def test_elementwise_multiply(self):
        matrix_a = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        matrix_b = Matrix(2, 3, [[7, 8, 9], [10, 11, 12]])
        result = matrix_a.elementwise_multiply(matrix_b)
        self.assertEqual(result.tolist(), [[7, 16, 27], [40, 55, 72]])

    def test_tolist(self):
        matrix = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        result = matrix.tolist()
        self.assertEqual(result, [[1, 2, 3], [4, 5, 6]])

if __name__ == '__main__':
    unittest.main()
