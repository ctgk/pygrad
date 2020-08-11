import numpy as np

from pygrad._core._array import Array
from pygrad._core._operator import _Operator
from pygrad._utils._typecheck import _typecheck
from pygrad._utils._unbroadcast import _unbroadcast_to


class _MatVecMul(_Operator):

    def __init__(self, x, y, name: str = None):
        super().__init__(x, y, name=name)

    @staticmethod
    def _forward_numpy(x, y):
        return x @ y

    @staticmethod
    def _backward_numpy(delta: np.ndarray, x: np.ndarray, y: np.ndarray):
        delta = np.expand_dims(delta, -1)
        delta = np.broadcast_to(delta, x.shape)
        dx = delta * y
        dy = _unbroadcast_to(delta * x, y.shape)
        return dx, dy


class _VecMatMul(_Operator):

    def __init__(self, x, y, name: str = None):
        super().__init__(x, y, name=name)

    @staticmethod
    def _forward_numpy(x, y):
        return x @ y

    @staticmethod
    def _backward_numpy(delta, x, y):
        delta = np.expand_dims(delta, -2)
        delta = np.broadcast_to(delta, y.shape)
        dx = _unbroadcast_to((delta * y).sum(axis=-1), x.shape)
        dy = delta * x[:, None]
        return dx, dy


class _MatMul(_Operator):

    def __init__(self, x, y, name: str = None):
        super().__init__(x, y, name=name)
        if not (self._args[0].ndim == self._args[1].ndim == 2):
            raise ValueError('Arguments of matmul() must be 2-dimensional.')

    @staticmethod
    def _forward_numpy(x, y):
        return x @ y

    @staticmethod
    def _backward_numpy(delta: np.ndarray, x: np.ndarray, y: np.ndarray):
        dx = delta @ y.T
        dy = x.T @ delta
        return dx, dy


class _BatchMatMul(_Operator):

    def __init__(self, x, y, name=None):
        super().__init__(x, y, name=name)

    @staticmethod
    def _forward_numpy(x, y):
        return x @ y

    @staticmethod
    def _backward_numpy(delta, x, y):
        dx = _unbroadcast_to(delta @ np.swapaxes(y, -1, -2), x.shape)
        dy = _unbroadcast_to(np.swapaxes(x, -1, -2) @ delta, y.shape)
        return dx, dy


@_typecheck(exclude=('x', 'y'))
def matmul(x: Array, y: Array, name: str = None) -> Array:
    """Return matrix multiplication of two arrays.

    Parameters
    ----------
    x : Array
        Input array.
    y : Array
        Another input array.
    name : str, optional
        Name of the operation, by default None.

    Returns
    -------
    Array
        matrix multiplication of two arrays.

    Examples
    --------
    >>> import pygrad as pg
    >>> pg.matmul([[1, 2], [2, 3]], [-1, 3])
    array([5, 7])
    >>> pg.matmul([-1, 3], [[1, 2], [2, 3]])
    array([5, 7])
    >>> pg.matmul([[1, 2], [2, 3]], [[-1], [3]])
    array([[5],
           [7]])
    >>> pg.matmul([[[1, 2], [2, 3]], [[-1, 2], [2, -3]]], [[-1], [3]])
    array([[[  5],
            [  7]],
    <BLANKLINE>
           [[  7],
            [-11]]])
    """
    if not isinstance(x, Array):
        x = Array(x)
    if not isinstance(y, Array):
        y = Array(y)
    if y.ndim == 1:
        return _MatVecMul(x, y, name=name).forward()
    if x.ndim == 1:
        return _VecMatMul(x, y, name=name).forward()
    if x.ndim == y.ndim == 2:
        return _MatMul(x, y, name=name).forward()
    return _BatchMatMul(x, y, name=name).forward()
