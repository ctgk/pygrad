import numpy as np
import pytest

import pygrad as pg
from pygrad._utils._numerical_grad import _numerical_grad


@pytest.mark.parametrize('x, name, expected', [
    ([1, -1, 5], 'relu', [1, 0, 5]),
])
def test_forward(x, name, expected):
    actual = pg.nn.relu(x, name=name)
    assert np.allclose(actual.data, expected)
    assert actual.name == name + '.out'


@pytest.mark.parametrize('x', [
    pg.Array(np.random.rand(2, 3), is_variable=True),
    pg.Array(np.random.rand(4, 2, 3), is_variable=True),
])
def test_backward(x):
    pg.nn.relu(x).backward()
    dx = x.data > 0
    assert np.allclose(dx, x.grad, rtol=0, atol=1e-2)


@pytest.mark.parametrize('x', [
    pg.Array(np.random.rand(2, 3), is_variable=True),
    pg.Array(np.random.rand(4, 2, 3), is_variable=True),
])
def test_numerical_grad(x):
    pg.nn.relu(x).backward()
    dx = _numerical_grad(pg.nn.relu, x)[0]
    assert np.allclose(dx, x.grad, rtol=0, atol=1e-2)


if __name__ == "__main__":
    pytest.main([__file__])
