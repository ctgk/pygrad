import numpy as np
import pytest

import pygrad as pg
from pygrad._utils._numerical_grad import _numerical_grad


@pytest.mark.parametrize('x, expected', [
    ([1, -1, 5], np.exp([1, -1, 5])),
])
def test_forward(x, expected):
    actual = pg.exp(x)
    assert np.allclose(actual.data, expected)


@pytest.mark.parametrize('x, dy, expected', [
    (pg.Array([1., -1, 5], is_variable=True), None, np.exp([1, -1, 5])),
    (
        pg.Array([-7., 3], is_variable=True), [1, -2],
        np.array([1, -2]) * np.exp([-7, 3])
    ),
])
def test_backward(x, dy, expected):
    if dy is None:
        pg.exp(x).backward()
    else:
        pg.exp(x).backward(_grad=dy)
    assert np.allclose(x.grad, expected)


@pytest.mark.parametrize('x', [
    pg.Array(np.random.rand(2, 3), is_variable=True),
    pg.Array(np.random.rand(4, 2, 3), is_variable=True),
])
def test_numerical_grad(x):
    pg.exp(x).backward()
    dx = _numerical_grad(pg.exp, x)[0]
    assert np.allclose(dx, x.grad, rtol=0, atol=1e-2)


if __name__ == "__main__":
    pytest.main([__file__])
