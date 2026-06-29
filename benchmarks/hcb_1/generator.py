"""Dataset generator for HCB-1: the hypometabolic crash benchmark.

The benchmark simulates a coupled neural population under progressive energy
starvation. The target label is the first sustained collapse point after the
network crosses its topology-dependent bifurcation threshold.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class HCBConfig:
    n_nodes: int = 32
    steps: int = 500
    duration: float = 50.0
    seed: int = 42
    topology: str = "small_world"
    mean_degree: int = 4
    rewire_probability: float = 0.06
    random_edge_probability: float = 0.08
    collapse_fraction: float = 0.55
    sustain_steps: int = 8


@dataclass(frozen=True)
class HCBResult:
    config: HCBConfig
    connectivity_graph: np.ndarray
    energy_scalar_t: np.ndarray
    activity: np.ndarray
    slowing_signal: np.ndarray
    synchrony: np.ndarray
    crash_index: int
    t_crash: float
    critical_energy: float
    topology_resilience: float

    @property
    def input_tensor(self) -> dict[str, np.ndarray]:
        return {
            "connectivity_graph": self.connectivity_graph,
            "energy_scalar_t": self.energy_scalar_t,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "topology": self.config.topology,
            "seed": self.config.seed,
            "n_nodes": self.config.n_nodes,
            "steps": self.config.steps,
            "t_crash": self.t_crash,
            "crash_index": self.crash_index,
            "critical_energy": self.critical_energy,
            "topology_resilience": self.topology_resilience,
            "input_tensor": {
                "connectivity_graph_shape": list(self.connectivity_graph.shape),
                "energy_scalar_t_shape": list(self.energy_scalar_t.shape),
            },
        }


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    rowsum = matrix.sum(axis=1, keepdims=True)
    return np.divide(matrix, rowsum, out=np.zeros_like(matrix), where=rowsum > 0)


def make_connectivity_graph(config: HCBConfig) -> np.ndarray:
    """Create a deterministic graph for the requested topology."""
    rng = np.random.default_rng(config.seed)
    n = config.n_nodes
    if n < 8:
        raise ValueError("HCB-1 needs at least 8 nodes to expose topology shifts.")

    if config.topology == "small_world":
        degree = max(2, min(config.mean_degree, n - 1))
        if degree % 2:
            degree += 1
        graph = np.zeros((n, n), dtype=float)
        half_degree = degree // 2
        for node in range(n):
            for offset in range(1, half_degree + 1):
                neighbor = (node + offset) % n
                graph[node, neighbor] = 1.0
                graph[neighbor, node] = 1.0

        upper_edges = np.argwhere(np.triu(graph, k=1) > 0)
        for source, target in upper_edges:
            if rng.random() >= config.rewire_probability:
                continue
            graph[source, target] = 0.0
            graph[target, source] = 0.0
            forbidden = set(np.flatnonzero(graph[source] > 0))
            forbidden.add(source)
            candidates = [idx for idx in range(n) if idx not in forbidden]
            if not candidates:
                graph[source, target] = 1.0
                graph[target, source] = 1.0
                continue
            new_target = int(rng.choice(candidates))
            graph[source, new_target] = 1.0
            graph[new_target, source] = 1.0
        return _normalize_rows(graph)

    if config.topology == "random":
        p = config.random_edge_probability
        graph = rng.random((n, n)) < p
        graph = np.triu(graph, k=1)
        graph = graph + graph.T
        graph = graph.astype(float)
        for node in range(n):
            if graph[node].sum() == 0:
                target = int(rng.integers(0, n - 1))
                if target >= node:
                    target += 1
                graph[node, target] = 1.0
                graph[target, node] = 1.0
        return _normalize_rows(graph)

    if config.topology == "lattice":
        return make_connectivity_graph(
            HCBConfig(**{**asdict(config), "topology": "small_world", "rewire_probability": 0.0})
        )

    raise ValueError(f"Unknown HCB topology: {config.topology}")


def _average_clustering(row_normalized_graph: np.ndarray) -> float:
    graph = row_normalized_graph > 0
    clustering = []
    for node in range(graph.shape[0]):
        neighbors = np.flatnonzero(graph[node])
        degree = len(neighbors)
        if degree < 2:
            clustering.append(0.0)
            continue
        subgraph = graph[np.ix_(neighbors, neighbors)]
        edge_count = subgraph.sum() / 2.0
        possible_edges = degree * (degree - 1) / 2.0
        clustering.append(edge_count / possible_edges)
    return float(np.mean(clustering))


def _degree_regularity(row_normalized_graph: np.ndarray) -> float:
    degrees = (row_normalized_graph > 0).sum(axis=1).astype(float)
    mean_degree = degrees.mean()
    if mean_degree == 0:
        return 0.0
    return float(1.0 / (1.0 + degrees.std() / mean_degree))


def topology_resilience(row_normalized_graph: np.ndarray) -> float:
    """Return a 0..1 survivability score from local clustering and regularity."""
    clustering = _average_clustering(row_normalized_graph)
    regularity = _degree_regularity(row_normalized_graph)
    return float(np.clip(0.75 * clustering + 0.25 * regularity, 0.0, 1.0))


def critical_energy_for_graph(row_normalized_graph: np.ndarray) -> float:
    """Lower critical energy means the network remains stable longer."""
    resilience = topology_resilience(row_normalized_graph)
    return float(np.clip(0.42 - 0.26 * resilience, 0.12, 0.42))


def _detect_crash(
    activity: np.ndarray,
    energy: np.ndarray,
    critical_energy: float,
    collapse_fraction: float,
    sustain_steps: int,
) -> int:
    baseline = float(activity[: max(5, activity.shape[0] // 10)].mean())
    threshold = baseline * collapse_fraction
    mean_activity = activity.mean(axis=1)
    below = (mean_activity < threshold) & (energy < critical_energy)
    for idx in range(0, len(below) - sustain_steps + 1):
        if np.all(below[idx : idx + sustain_steps]):
            return idx
    return int(np.argmin(np.abs(energy - critical_energy)))


def generate_hcb_dataset(config: HCBConfig | None = None) -> HCBResult:
    """Generate the HCB-1 tensors and deterministic crash label."""
    config = config or HCBConfig()
    rng = np.random.default_rng(config.seed)
    graph = make_connectivity_graph(config)
    resilience = topology_resilience(graph)
    critical_energy = critical_energy_for_graph(graph)

    t = np.linspace(0.0, config.duration, config.steps)
    energy = np.linspace(1.0, 0.0, config.steps)
    activity = np.zeros((config.steps, config.n_nodes), dtype=float)
    slowing_signal = np.zeros(config.steps, dtype=float)
    synchrony = np.zeros(config.steps, dtype=float)

    state = 0.62 + 0.025 * rng.standard_normal(config.n_nodes)
    node_phase = rng.uniform(0.0, 2.0 * np.pi, config.n_nodes)

    for idx, current_energy in enumerate(energy):
        margin = current_energy - critical_energy
        coupled = graph @ state
        network_pull = coupled - state

        slowing = 1.0 / (abs(margin) + 0.045)
        slowing_signal[idx] = slowing
        wobble = 0.004 * slowing * np.sin(0.85 * t[idx] + node_phase)

        if margin >= 0.0:
            drive = 2.2 * current_energy + 1.4 * coupled - 1.05
            target = 0.18 + 0.72 * _sigmoid(drive)
            relaxation = 0.018 + 0.24 * abs(margin)
        else:
            target = 0.03 + 0.08 * current_energy + 0.03 * coupled
            relaxation = 0.20 + 0.55 * abs(margin)

        diffusion = 0.06 * (0.5 + resilience) * network_pull
        state = state + relaxation * (target - state) + diffusion + wobble
        state = np.clip(state, 0.0, 1.0)

        activity[idx] = state
        synchrony[idx] = float(np.abs(np.mean(np.exp(1j * 2.0 * np.pi * state))))

    crash_index = _detect_crash(
        activity,
        energy,
        critical_energy,
        config.collapse_fraction,
        config.sustain_steps,
    )

    return HCBResult(
        config=config,
        connectivity_graph=graph,
        energy_scalar_t=energy,
        activity=activity,
        slowing_signal=slowing_signal,
        synchrony=synchrony,
        crash_index=crash_index,
        t_crash=float(t[crash_index]),
        critical_energy=critical_energy,
        topology_resilience=resilience,
    )


def render_timeseries_plot(result: HCBResult, path: str | Path) -> Path:
    """Write the required time-series plot when Matplotlib is available."""
    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    x_axis = np.linspace(0.0, result.config.duration, result.config.steps)
    mean_activity = result.activity.mean(axis=1)

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(x_axis, mean_activity, color="#1f77b4", label="mean activity")
    axes[0].axvline(result.t_crash, color="#d62728", linestyle="--", label="t_crash")
    axes[0].set_ylabel("activity")
    axes[0].legend(loc="best")

    axes[1].plot(x_axis, result.energy_scalar_t, color="#2ca02c", label="energy")
    axes[1].axhline(result.critical_energy, color="#d62728", linestyle="--", label="critical energy")
    axes[1].set_ylabel("energy")
    axes[1].legend(loc="best")

    axes[2].plot(x_axis, result.slowing_signal, color="#9467bd", label="critical slowing")
    axes[2].set_xlabel("time")
    axes[2].set_ylabel("slowing")
    axes[2].legend(loc="best")

    fig.suptitle(f"HCB-1 hypometabolic crash: {result.config.topology}")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def write_dataset(result: HCBResult, output_dir: str | Path, make_plot: bool = True) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"hcb_1_{result.config.topology}_seed_{result.config.seed}"

    npz_path = output_dir / f"{stem}.npz"
    np.savez_compressed(
        npz_path,
        connectivity_graph=result.connectivity_graph,
        energy_scalar_t=result.energy_scalar_t,
        activity=result.activity,
        slowing_signal=result.slowing_signal,
        synchrony=result.synchrony,
        crash_index=result.crash_index,
        t_crash=result.t_crash,
        critical_energy=result.critical_energy,
    )

    summary_path = output_dir / f"{stem}.json"
    summary_path.write_text(json.dumps(result.summary(), indent=2) + "\n", encoding="utf-8")

    csv_path = output_dir / f"{stem}_series.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["step", "time", "energy", "mean_activity", "slowing_signal", "synchrony"])
        for idx, energy_value in enumerate(result.energy_scalar_t):
            writer.writerow(
                [
                    idx,
                    idx * result.config.duration / (result.config.steps - 1),
                    energy_value,
                    float(result.activity[idx].mean()),
                    result.slowing_signal[idx],
                    result.synchrony[idx],
                ]
            )

    files = {"npz": str(npz_path), "summary": str(summary_path), "series_csv": str(csv_path)}
    if make_plot:
        plot_path = output_dir / f"{stem}.png"
        try:
            files["plot"] = str(render_timeseries_plot(result, plot_path))
        except ImportError:
            files["plot_skipped"] = "matplotlib is not installed"
    return files


def verify_bifurcation() -> tuple[bool, str]:
    """CI-safe HCB-1 verification using only NumPy."""
    base = HCBConfig(seed=7, n_nodes=32, steps=420)
    small_world = generate_hcb_dataset(base)
    small_world_repeat = generate_hcb_dataset(base)
    random_graph = generate_hcb_dataset(HCBConfig(**{**asdict(base), "topology": "random"}))

    if small_world.connectivity_graph.shape != (base.n_nodes, base.n_nodes):
        return False, "connectivity graph shape mismatch"
    if small_world.energy_scalar_t.shape != (base.steps,):
        return False, "energy scalar timeline shape mismatch"
    if small_world.crash_index != small_world_repeat.crash_index:
        return False, "crash point is not deterministic for a fixed seed"
    if not small_world.crash_index > random_graph.crash_index:
        return (
            False,
            "topology shift failed: expected small_world to survive longer "
            f"than random ({small_world.crash_index} <= {random_graph.crash_index})",
        )

    early = small_world.slowing_signal[: base.steps // 5].mean()
    near_crash = small_world.slowing_signal[
        max(0, small_world.crash_index - base.steps // 10) : small_world.crash_index
    ].mean()
    if not near_crash > early:
        return False, "critical slowing signal did not increase before crash"

    return (
        True,
        "HCB-1 verified: "
        f"small_world t_crash={small_world.t_crash:.2f}, "
        f"random t_crash={random_graph.t_crash:.2f}, "
        f"critical_energy={small_world.critical_energy:.3f}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or verify the HCB-1 benchmark dataset.")
    parser.add_argument("--topology", choices=["small_world", "random", "lattice"], default="small_world")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--nodes", type=int, default=32)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--output", type=Path, default=Path("artifacts/hcb_1"))
    parser.add_argument("--no-plot", action="store_true", help="Skip PNG plot generation.")
    parser.add_argument("--verify", action="store_true", help="Run deterministic bifurcation verification.")
    args = parser.parse_args()

    if args.verify:
        passed, message = verify_bifurcation()
        print(message)
        raise SystemExit(0 if passed else 1)

    result = generate_hcb_dataset(
        HCBConfig(topology=args.topology, seed=args.seed, n_nodes=args.nodes, steps=args.steps)
    )
    files = write_dataset(result, args.output, make_plot=not args.no_plot)
    print(json.dumps({"summary": result.summary(), "files": files}, indent=2))


if __name__ == "__main__":
    main()
