import unittest
import numpy as np

import sys
import os
current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
sys.path.append("src/")


from src.kernel import RadialBasisFunction
from src.filter_layer import FilterLayer

class LayerTest(unittest.TestCase):
    @staticmethod
    def random_filter_matrix(shape):
        filter_mx = np.random.rand(shape[0], shape[1])
        norms = np.linalg.norm(filter_mx, axis = 0)
        return filter_mx * (1 / norms)

    def setUp(self):
        self.filter_mx_1x1x1 = LayerTest.random_filter_matrix((1*1*1, 2))
        self.filter_mx_3x3x1 = LayerTest.random_filter_matrix((3*3*1, 2))
        self.filter_mx_3x3x2 = LayerTest.random_filter_matrix((3*3*2, 2))

    def test_extract_patches_without_zero_padding(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=2, filter_size=(3, 3), 
            dp_kernel=RadialBasisFunction(1), filter_matrix=self.filter_mx_3x3x2,
            zero_padding=(0, 0)
        )
        input = np.array([
            [11, 12], [13, 14], [15, 16], 
            [21, 22], [23, 24], [25, 26], 
            [31, 32], [33, 34], [35, 36]
        ]).transpose()
        patched = l._extract_patches(input)

        self.assertEqual(patched.shape, (2 * l.filter_size[0] * l.filter_size[1], 1))
        expectedPatched = np.array([
            [
                11, 12, 13, 14, 15, 16,
                21, 22, 23, 24, 25, 26,
                31, 32, 33, 34, 35, 36,
            ]
        ]).transpose()
        self.assertTrue((patched == expectedPatched).all())

    def test_extract_patches_zero_padding(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=2, filter_size=(3, 3), 
            dp_kernel=RadialBasisFunction(1), filter_matrix=self.filter_mx_3x3x2,
            zero_padding=(1, 1)
        )
        input = np.array([
            [11, 12], [13, 14], [15, 16], 
            [21, 22], [23, 24], [25, 26], 
            [31, 32], [33, 34], [35, 36]
        ]).transpose()
        patched = l._extract_patches(input)

        self.assertEqual(patched.shape, (2 * l.filter_size[0] * l.filter_size[1], l.input_size[0] * l.input_size[1]))
        expectedPatched = np.array([
            [ 0, 0,   0, 0,   0, 0,     0, 0,   11, 12, 13, 14,     0, 0,   21, 22, 23, 24, ], 
            [ 0, 0,   0, 0,   0, 0,     11, 12, 13, 14, 15, 16,     21, 22, 23, 24, 25, 26, ], 
            [ 0, 0,   0, 0,   0, 0,     13, 14, 15, 16, 0, 0,       23, 24, 25, 26, 0, 0,   ], 
            [ 0, 0,   11, 12, 13, 14,   0, 0,   21, 22, 23, 24,     0, 0,   31, 32, 33, 34, ], 
            [ 11, 12, 13, 14, 15, 16,   21, 22, 23, 24, 25, 26,     31, 32, 33, 34, 35, 36, ], 
            [ 13, 14, 15, 16, 0, 0,     23, 24, 25, 26, 0, 0,       33, 34, 35, 36, 0, 0,   ], 
            [ 0, 0,   21, 22, 23, 24,   0, 0,   31, 32, 33, 34,     0, 0,   0, 0,   0, 0,   ], 
            [ 21, 22, 23, 24, 25, 26,   31, 32, 33, 34, 35, 36,     0, 0,   0, 0,   0, 0,   ], 
            [ 23, 24, 25, 26, 0, 0,     33, 34, 35, 36, 0, 0,       0, 0,   0, 0,   0, 0,   ]
        ]).transpose()

        self.assertTrue((patched == expectedPatched).all())

    def test_extract_patches_adj_without_zero_padding(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=2, filter_size=(3, 3), 
            dp_kernel=RadialBasisFunction(1), filter_matrix=self.filter_mx_3x3x2,
            zero_padding=(0, 0)
        )

        patched = l._extract_patches(np.array([
            [1, 0],     [1, 3],     [1, 0], 
            [1, 3],     [1, 0],     [1, 3], 
            [1, 0],     [1, 3],     [1, 0]
        ]).transpose())

        adj = l._extract_patches_adj(patched)
        self.assertEqual(adj.shape, (2, 9))

        expectedAdj = np.array([
            [1, 0],     [1, 3],     [1, 0], 
            [1, 3],     [1, 0],     [1, 3], 
            [1, 0],     [1, 3],     [1, 0]
        ]).transpose()

        self.assertTrue((adj == expectedAdj).all())

    def test_extract_patches_adj_with_zero_padding(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=2, filter_size=(3, 3), 
            dp_kernel=RadialBasisFunction(1), filter_matrix=self.filter_mx_3x3x2,
            zero_padding=(1, 1)
        )

        patched = l._extract_patches(np.array([
            [1, 3],     [1, 2],     [1, 1], 
            [1, 2],     [1, 1],     [1, 0], 
            [1, 1],     [1, 0],     [1, 0]
        ]).transpose())

        adj = l._extract_patches_adj(patched)
        self.assertEqual(adj.shape, (2, 9))

        expectedAdj = np.array([
            [4, 12],    [6, 12],    [4, 4], 
            [6, 12],    [9, 9],     [6, 0], 
            [4, 4],     [6, 0],     [4, 0]
        ]).transpose()
        
        self.assertTrue((adj == expectedAdj).all())



    def test_forward_doesnt_crash(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=1, filter_size=(3, 3), 
             dp_kernel=RadialBasisFunction(1), 
            filter_matrix=self.filter_mx_3x3x1,
            zero_padding=(0, 0)
        )
        l.forward(np.array([[1, 1, 1, 1, 0, 1, 1, 1, 1]]))

    def test_g_doesnt_crash(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=1, filter_size=(3, 3), 
            dp_kernel=RadialBasisFunction(1), 
            filter_matrix=self.filter_mx_3x3x1,
            zero_padding=(1, 1)
        )
        output = l.forward(np.array([[1, 1, 1, 1, 0, 1, 1, 1, 1]]))
        U = np.array([
            [0.5, 0.5], [0.7, 0.9], [0.3, 0.7],
            [0.2, 0.1], [0.1, 0.3], [0.6, 0.4],
            [0.5, 0.9], [0.2, 0.1], [0.1, 0.8],
        ]).transpose()
        B = l._calculate_B(U)
        C = l._calculate_C(U, output)
        l._g(B, C)

    def test_h_doesnt_crash(self):
        l = FilterLayer(
            input_size=(3, 3), in_channels=1, filter_size=(3, 3), 
            dp_kernel=RadialBasisFunction(1), 
            filter_matrix=self.filter_mx_3x3x1,
            zero_padding=(1, 1)
        )
        output = l.forward(np.array([[1, 1, 1, 1, 0, 1, 1, 1, 1]]))
        U = np.array([
            [0.5, 0.5], [0.7, 0.9], [0.3, 0.7],
            [0.2, 0.1], [0.1, 0.3], [0.6, 0.4],
            [0.5, 0.9], [0.2, 0.1], [0.1, 0.8],
        ]).transpose()
        B = l._calculate_B(U)
        l._h(U, B)


if __name__ == '__main__':
    unittest.main()