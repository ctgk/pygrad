import numpy as np
import pytest

import pygrad as pg


@pytest.mark.parametrize('parameters, learning_rate, error', [
    (
        [
            pg.Array(1., is_variable=True),
            pg.Array([1., -1.], is_variable=True),
        ],
        1e-3, 'NoError'
    ),
    (
        [
            pg.Array(1., is_variable=True),
            pg.Array([1., -1.], is_variable=True),
        ],
        -1e-3, ValueError
    ),
])
def test_init_error(parameters, learning_rate, error):
    if error == 'NoError':
        pg.optimizers.Gradient(parameters, learning_rate)
    else:
        with pytest.raises(error):
            pg.optimizers.Gradient(parameters, learning_rate)


def test_minimize():
    theta = pg.Array([10, -20], dtype=pg.Float64, is_variable=True)
    optimizer = pg.optimizers.Gradient([theta], learning_rate=0.1)
    for _ in range(100):
        d = theta - [-2, 4]
        loss = pg.square(d).sum()
        expected = theta.data - 0.1 * 2 * d.data
        optimizer.minimize(loss)
        assert np.allclose(theta.data, expected)
    assert np.allclose(theta.data, [-2, 4])


def test_maximize():
    theta = pg.Array([10, -20], dtype=pg.Float64, is_variable=True)
    optimizer = pg.optimizers.Gradient([theta], learning_rate=0.1)
    for _ in range(100):
        d = theta - [-2, 4]
        score = -pg.square(d).sum()
        expected = theta.data - 0.1 * 2 * d.data
        score.backward()
        optimizer.maximize(clear_grad=False)
        theta.clear_grad()
        assert np.allclose(theta.data, expected)
    assert np.allclose(theta.data, [-2, 4])


if __name__ == "__main__":
    pytest.main([__file__])
