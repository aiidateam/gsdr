"""Pure Gray-Scott reaction-diffusion logic. No I/O, no printing, no sys.exit."""
# ruff: noqa: N803, N806

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypedDict

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from typing import NotRequired


class SimParams(TypedDict):
    grid_size: int
    du: float
    dv: float
    F: float
    k: float
    dt: float
    n_steps: int
    seed: "NotRequired[int]"


REQUIRED_KEYS: list[str] = ["grid_size", "du", "dv", "F", "k", "dt", "n_steps"]


class SimError(Exception):
    """Base class for simulation errors."""


class DiffusionError(SimError):
    """Raised when du or dv is not positive."""


class TimeStepError(SimError):
    """Raised when dt is not positive."""


class InstabilityError(SimError):
    """Raised when NaN/Inf appears during integration, or initial-field shapes mismatch."""


class TrivialStateError(SimError):
    """Raised when the final variance of V is below threshold."""


def laplacian(Z: NDArray[np.floating]) -> NDArray[np.floating]:
    return (
        -4 * Z
        + np.roll(Z, 1, axis=0)
        + np.roll(Z, -1, axis=0)
        + np.roll(Z, 1, axis=1)
        + np.roll(Z, -1, axis=1)
    )


def simulate(
    params: SimParams,
    progress: Callable[[int, int], None] | None = None,
    u_init: NDArray[np.floating] | None = None,
    v_init: NDArray[np.floating] | None = None,
) -> tuple[NDArray[np.floating], NDArray[np.floating], float, float]:
    n: int = params["grid_size"]
    du: float = params["du"]
    dv: float = params["dv"]
    F: float = params["F"]
    k: float = params["k"]
    dt: float = params["dt"]
    steps: int = params["n_steps"]
    seed: int | None = params.get("seed", None)

    if du <= 0 or dv <= 0:
        raise DiffusionError("Diffusion constants must be positive")

    if dt <= 0:
        raise TimeStepError("Time step must be positive")

    if seed is not None:
        np.random.seed(seed)

    if u_init is not None and v_init is not None:
        if u_init.shape != (n, n) or v_init.shape != (n, n):
            raise InstabilityError(f"Initial field shape mismatch for grid_size={n}")
        U = u_init.astype(float, copy=True)
        V = v_init.astype(float, copy=True)
    else:
        U = np.ones((n, n))
        V = np.zeros((n, n))
        r: int = n // 10
        c: int = n // 2
        U[c - r : c + r, c - r : c + r] = 0.50
        V[c - r : c + r, c - r : c + r] = 0.25

    report_every: int = max(1, steps // 20)
    for step in range(steps):
        Lu = laplacian(U)
        Lv = laplacian(V)
        uvv = U * V * V
        U += dt * (du * Lu - uvv + F * (1 - U))
        V += dt * (dv * Lv + uvv - (F + k) * V)

        if not np.all(np.isfinite(U)) or not np.all(np.isfinite(V)):
            raise InstabilityError(f"Numerical instability detected at step {step}")

        if progress is not None and (step + 1) % report_every == 0:
            progress(step + 1, steps)

    var_v: float = float(np.var(V))
    mean_v: float = float(np.mean(V))

    if var_v < 1e-8:
        raise TrivialStateError("Trivial steady state (no pattern formed)")

    return U, V, var_v, mean_v
