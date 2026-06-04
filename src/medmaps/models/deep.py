"""Deep forecasters: a GRU and a TCN, behind the same Forecaster interface.

Kept deliberately small. The question is not whether a big network can fit, it is
whether a modest sequence model earns its complexity over persistence. Inputs and
targets are standardised on the training split; predictions are inverse-transformed.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

from .base import Forecaster


class _GRUNet(nn.Module):
    def __init__(self, n_features: int, hidden: int, horizon: int) -> None:
        super().__init__()
        self.gru = nn.GRU(n_features, hidden, batch_first=True)
        self.head = nn.Linear(hidden, horizon)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.gru(x)
        return self.head(out[:, -1, :])


class _TCNNet(nn.Module):
    def __init__(self, n_features: int, hidden: int, horizon: int) -> None:
        super().__init__()
        self.body = nn.Sequential(
            nn.Conv1d(n_features, hidden, kernel_size=3, padding=1, dilation=1),
            nn.ReLU(),
            nn.Conv1d(hidden, hidden, kernel_size=3, padding=2, dilation=2),
            nn.ReLU(),
        )
        self.head = nn.Linear(hidden, horizon)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.body(x.transpose(1, 2))  # (b, t, f) -> (b, f, t)
        return self.head(z[:, :, -1])


class _TorchForecaster(Forecaster):
    def __init__(
        self, epochs: int = 40, lr: float = 1e-3, batch_size: int = 256,
        hidden: int = 64, seed: int = 7,
    ) -> None:
        super().__init__()
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.hidden = hidden
        self.seed = seed
        self.horizon: int | None = None
        self._net: nn.Module | None = None

    def _build(self, n_features: int) -> nn.Module:
        raise NotImplementedError

    def _fit(self, X: np.ndarray, y: np.ndarray) -> None:
        torch.manual_seed(self.seed)
        self.horizon = int(y.shape[1])
        self._x_mu = X.mean(axis=(0, 1))
        self._x_sd = X.std(axis=(0, 1)) + 1e-6
        self._y_mu = float(y.mean())
        self._y_sd = float(y.std()) + 1e-6

        xs = torch.tensor((X - self._x_mu) / self._x_sd, dtype=torch.float32)
        ys = torch.tensor((y - self._y_mu) / self._y_sd, dtype=torch.float32)
        loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(xs, ys), batch_size=self.batch_size, shuffle=True
        )

        net = self._build(X.shape[2])
        opt = torch.optim.Adam(net.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()
        net.train()
        for _ in range(self.epochs):
            for xb, yb in loader:
                opt.zero_grad()
                loss = loss_fn(net(xb), yb)
                loss.backward()
                opt.step()
        net.eval()
        self._net = net

    def predict(self, X: np.ndarray) -> np.ndarray:
        xs = torch.tensor((X - self._x_mu) / self._x_sd, dtype=torch.float32)
        with torch.no_grad():
            out = self._net(xs).numpy()
        return out * self._y_sd + self._y_mu


class GRUForecaster(_TorchForecaster):
    name = "gru"

    def _build(self, n_features: int) -> nn.Module:
        return _GRUNet(n_features, self.hidden, self.horizon)


class TCNForecaster(_TorchForecaster):
    name = "tcn"

    def _build(self, n_features: int) -> nn.Module:
        return _TCNNet(n_features, self.hidden, self.horizon)
