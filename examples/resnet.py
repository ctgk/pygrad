import argparse

import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from tqdm import trange

import pygrad as gd


class ResidualBlock(gd.Module):

    def __init__(self, num_ch):
        super().__init__()
        self.layers = gd.nn.Sequential(
            gd.nn.BatchNormalization(num_ch),
            gd.nn.ReLU(),
            gd.nn.Conv2D(num_ch, num_ch, 3, pad=1, bias=False),
            gd.nn.BatchNormalization(num_ch),
            gd.nn.ReLU(),
            gd.nn.Conv2D(num_ch, num_ch, 3, pad=1, bias=False),
        )

    def __call__(self, x, *, update_bn: bool = False):
        return self.layers(x, update_bn=update_bn) + x


class ResNet(gd.Module):

    def __init__(self):
        super().__init__()
        self.layers = gd.nn.Sequential(
            gd.nn.Conv2D(3, 16, 3),
            gd.nn.MaxPool2D(2),
            gd.nn.ReLU(),
            gd.nn.BatchNormalization(16),
            gd.nn.Conv2D(16, 32, 3),
            gd.nn.MaxPool2D(2),
            ResidualBlock(32),
            ResidualBlock(32),
            ResidualBlock(32),
        )
        self.d = gd.nn.Dense(32, 10)

    def __call__(self, x, *, update_bn: bool = False):
        h = self.layers(x, update_bn=update_bn)
        h = h.mean(axis=(1, 2))
        return self.d(h)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--epoch', type=int, default=5)
    parser.add_argument('-b', '--batch', type=int, default=50)
    args = parser.parse_args()

    gd.config.dtype = gd.Float32
    x, y = fetch_openml('CIFAR_10', return_X_y=True)
    x = x.astype(np.float32).reshape(-1, 32, 32, 3)
    x /= x.max(axis=(1, 2), keepdims=True)
    y = y.astype(np.int)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=10000, stratify=y)
    resnet = ResNet()
    optimizer = gd.optimizers.Adam(resnet)
    x = gd.Array(np.zeros((args.batch, 32, 32, 3), dtype=np.float32))
    y = gd.Array(np.zeros(args.batch, dtype=np.int))
    with gd.Graph() as g:
        logits = resnet(x)
        loss = gd.stats.sparse_softmax_cross_entropy(y, logits).mean()
    for e in range(1, args.epoch + 1):
        pbar = trange(0, len(x_train), args.batch)
        tp = 0
        total = 0
        for i in pbar:
            x.data = x_train[i: i + args.batch]
            y.data = y_train[i: i + args.batch]
            g.forward()
            optimizer.minimize(g)
            if optimizer.n_iter % 10 == 0:
                tp += np.sum(y.data == np.argmax(logits.data, -1))
                total += args.batch
                pbar.set_description(
                    f'Epoch={e}, Accuracy={int(100 * tp / total)}%')
        indices = np.random.permutation(len(x_train))
        x_train = x_train[indices]
        y_train = y_train[indices]

    y_pred = np.argmax(resnet(x_test).data, -1)
    print(confusion_matrix(y_test, y_pred))