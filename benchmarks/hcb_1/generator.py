"""HCB-1: Hypometabolic Crash Benchmark dataset generator.

This module simulates a phase-reduced neural mass network under progressive
ATP starvation. The generated input contract is:

    [Connectivity_Graph, Energy_Scalar_t]

and the target is the first timestamp where network synchrony drops below the
bifurcation threshold.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class HCB1Config:
    nodes: int = 64
    degree: int = 6
    duration: float = 120.0
    dt: float = 0.05
    seed: int = 42
    simulation_seed: int = 123
    rewiring_probability: float = 0.08
    synchrony_threshold: float = 0.55
    burn_in_seconds: float = 5.0


def make_small_world_graph(config: HCB1Config) -> np.ndarray:
    """Create a Watts-Strogatz style ring lattice with deterministic shortcuts."""
    if config.degree % 2:
        raise ValueError("degree must be even for the ring lattice")
    if config.degree >= config.nodes:
        raise ValueError("degree must be smaller than nodes")

    rng = np.random.default_rng(config.seed)
    graph = np.zeros((config.nodes, config.nodes), dtype=float)

    half_degree = config.degree // 2
    for i in range(config.nodes):
        for offset in range(1, half_degree + 1):
            j = (i + offset) % config.nodes
            graph[i, j] = 1.0
            graph[j, i] = 1.0

    original_edges = [
        (i, j)
        for i in range(config.nodes)
        for j in range(i + 1, config.nodes)
        if graph[i, j] > 0.0
    ]
    for i, j in original_edges:
        if rng.random() >= config.rewiring_probability:
            continue
        candidates = np.flatnonzero((np.arange(config.nodes) != i) & (graph[i] == 0.0))
        if len(candidates) == 0:
            continue
        new_j = int(rng.choice(candidates))
        graph[i, j] = 0.0
        graph[j, i] = 0.0
        graph[i, new_j] = 1.0
        graph[new_j, i] = 1.0

    return graph


def make_random_graph(config: HCB1Config) -> np.ndarray:
    """Create a deterministic Erdos-Renyi style graph with matched edge budget."""
    rng = np.random.default_rng(config.seed)
    graph = np.zeros((config.nodes, config.nodes), dtype=float)
    target_edges = config.nodes * config.degree // 2
    pairs = np.array(
        [(i, j) for i in range(config.nodes) for j in range(i + 1, config.nodes)]
    )
    selected = rng.choice(len(pairs), size=target_edges, replace=False)

    for i, j in pairs[selected]:
        graph[i, j] = 1.0
        graph[j, i] = 1.0

    degrees = graph.sum(axis=1)
    for i in np.flatnonzero(degrees == 0.0):
        j = int(rng.integers(0, config.nodes - 1))
        if j >= i:
            j += 1
        graph[i, j] = 1.0
        graph[j, i] = 1.0

    return graph


def clustering_coefficient(graph: np.ndarray) -> float:
    degrees = graph.sum(axis=1)
    triangles = np.diag(graph @ graph @ graph) / 2.0
    triples = degrees * (degrees - 1.0) / 2.0
    local = np.divide(
        triangles,
        triples,
        out=np.zeros_like(triangles, dtype=float),
        where=triples > 0.0,
    )
    return float(local.mean())


def locality_score(graph: np.ndarray) -> float:
    n = graph.shape[0]
    edge_i, edge_j = np.where(np.triu(graph, 1) > 0.0)
    if len(edge_i) == 0:
        return 0.0
    circular_distance = np.minimum(np.abs(edge_i - edge_j), n - np.abs(edge_i - edge_j))
    return float(np.mean(1.0 - circular_distance / (n / 2.0)))


def topology_resilience(graph: np.ndarray) -> float:
    """Estimate allostatic reserve from clustering, locality, and degree balance."""
    degrees = graph.sum(axis=1)
    degree_balance = 1.0 / (1.0 + degrees.std() / (degrees.mean() + 1e-9))
    return float(
        0.45 * clustering_coefficient(graph)
        + 0.35 * locality_score(graph)
        + 0.20 * degree_balance
    )


def normalize_graph(graph: np.ndarray) -> np.ndarray:
    degrees = graph.sum(axis=1)
    return np.divide(
        graph,
        degrees[:, None],
        out=np.zeros_like(graph, dtype=float),
        where=degrees[:, None] > 0.0,
    )


def energy_schedule(config: HCB1Config) -> tuple[np.ndarray, np.ndarray]:
    steps = int(config.duration / config.dt) + 1
    timestamps = np.arange(steps, dtype=float) * config.dt
    energy = np.maximum(0.0, 1.0 - (timestamps / config.duration) ** 1.1)
    return timestamps, energy


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    pad = window // 2
    padded = np.pad(values, (pad, pad), mode="edge")
    smoothed = np.convolve(padded, np.ones(window) / window, mode="valid")
    return smoothed[: len(values)]


def rolling_lag1_autocorrelation(values: np.ndarray, window: int) -> np.ndarray:
    result = np.zeros_like(values, dtype=float)
    for idx in range(len(values)):
        start = max(0, idx - window + 1)
        segment = values[start : idx + 1]
        if len(segment) < 3:
            result[idx] = 0.0
            continue
        left = segment[:-1] - segment[:-1].mean()
        right = segment[1:] - segment[1:].mean()
        denom = np.linalg.norm(left) * np.linalg.norm(right)
        result[idx] = float(np.dot(left, right) / denom) if denom > 1e-12 else 0.0
    return result


def simulate_network(
    graph: np.ndarray, config: HCB1Config, topology: str = "custom"
) -> dict[str, Any]:
    """Run a deterministic hypometabolic crash simulation."""
    rng = np.random.default_rng(config.simulation_seed)
    timestamps, energy = energy_schedule(config)
    weights = normalize_graph(graph)
    resilience = topology_resilience(graph)

    node_index = np.arange(config.nodes, dtype=float)
    intrinsic_frequency = (
        1.0
        + 0.06 * np.sin(2.0 * np.pi * node_index / config.nodes)
        + 0.015 * rng.normal(size=config.nodes)
    )
    stress_axis = rng.normal(size=config.nodes)
    stress_axis = (stress_axis - stress_axis.mean()) / (stress_axis.std() + 1e-9)
    phase = rng.normal(loc=0.0, scale=0.08, size=config.nodes)

    synchrony = np.zeros_like(timestamps)
    mean_activity = np.zeros_like(timestamps)
    neural_activity = np.zeros((len(timestamps), config.nodes), dtype=float)

    for step, available_energy in enumerate(energy):
        allostatic_coupling = 2.20 * resilience * available_energy * (1.0 - available_energy)
        basal_coupling = 1.25 * available_energy + 0.22 * resilience
        coupling_gain = basal_coupling + allostatic_coupling
        metabolic_stress = 1.80 * (1.0 - available_energy) ** 2 * (1.15 - resilience)

        phase_pull = np.sum(weights * np.sin(phase[None, :] - phase[:, None]), axis=1)
        d_phase = intrinsic_frequency + coupling_gain * phase_pull + metabolic_stress * stress_axis
        phase = phase + config.dt * d_phase

        amplitude = max(0.05, float(available_energy)) ** 0.55
        activity = amplitude * np.sin(phase)
        neural_activity[step] = activity
        mean_activity[step] = float(activity.mean())
        synchrony[step] = float(np.abs(np.exp(1j * phase).mean()))

    smooth_window = max(3, int(1.0 / config.dt))
    smoothed_synchrony = moving_average(synchrony, smooth_window)
    first_allowed_idx = int(config.burn_in_seconds / config.dt)
    candidate_indices = np.flatnonzero(
        (smoothed_synchrony < config.synchrony_threshold)
        & (np.arange(len(timestamps)) >= first_allowed_idx)
    )
    crash_idx = int(candidate_indices[0]) if len(candidate_indices) else len(timestamps) - 1
    slowing_window = max(5, int(5.0 / config.dt))
    critical_slowing = rolling_lag1_autocorrelation(mean_activity, slowing_window)

    return {
        "topology": topology,
        "config": asdict(config),
        "input_tensor": {
            "connectivity_graph": graph,
            "energy_scalar_t": energy,
        },
        "neural_activity": neural_activity,
        "mean_activity": mean_activity,
        "synchrony": synchrony,
        "smoothed_synchrony": smoothed_synchrony,
        "critical_slowing": critical_slowing,
        "crash_index": crash_idx,
        "crash_timestamp": float(timestamps[crash_idx]),
        "timestamps": timestamps,
        "topology_resilience": resilience,
    }


def generate_dataset(topology: str, config: HCB1Config) -> dict[str, Any]:
    if topology == "small_world":
        graph = make_small_world_graph(config)
    elif topology == "random":
        graph = make_random_graph(config)
    else:
        raise ValueError("topology must be 'small_world' or 'random'")
    return simulate_network(graph, config, topology=topology)


def verify_bifurcation(config: HCB1Config | None = None) -> dict[str, Any]:
    """Acceptance verifier: topology deterministically shifts the crash point."""
    config = config or HCB1Config()
    small_world = generate_dataset("small_world", config)
    random = generate_dataset("random", config)
    small_world_repeat = generate_dataset("small_world", config)
    random_repeat = generate_dataset("random", config)

    crash_delta = small_world["crash_timestamp"] - random["crash_timestamp"]
    deterministic = (
        small_world["crash_timestamp"] == small_world_repeat["crash_timestamp"]
        and random["crash_timestamp"] == random_repeat["crash_timestamp"]
    )
    valid_window = (
        config.burn_in_seconds < random["crash_timestamp"] < config.duration
        and config.burn_in_seconds < small_world["crash_timestamp"] < config.duration
    )
    slowing_rises = _critical_slowing_rises(small_world) and _critical_slowing_rises(random)
    passed = bool(deterministic and valid_window and slowing_rises and crash_delta >= 8.0)

    return {
        "passed": passed,
        "small_world_crash_timestamp": small_world["crash_timestamp"],
        "random_crash_timestamp": random["crash_timestamp"],
        "crash_delta_seconds": crash_delta,
        "small_world_resilience": small_world["topology_resilience"],
        "random_resilience": random["topology_resilience"],
        "deterministic": deterministic,
        "valid_window": valid_window,
        "critical_slowing_rises": slowing_rises,
    }


def _critical_slowing_rises(dataset: dict[str, Any]) -> bool:
    crash_idx = int(dataset["crash_index"])
    critical_slowing = dataset["critical_slowing"]
    early_end = max(5, min(crash_idx // 3, len(critical_slowing)))
    late_start = max(0, crash_idx - max(5, int(10.0 / dataset["config"]["dt"])))
    early = critical_slowing[:early_end]
    late = critical_slowing[late_start:crash_idx]
    if len(early) == 0 or len(late) == 0:
        return False
    return float(np.nanmean(late)) > float(np.nanmean(early))


def write_artifacts(dataset: dict[str, Any], output_dir: Path, make_plot: bool = True) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_dir / f"hcb_1_{dataset['topology']}.npz",
        connectivity_graph=dataset["input_tensor"]["connectivity_graph"],
        energy_scalar_t=dataset["input_tensor"]["energy_scalar_t"],
        neural_activity=dataset["neural_activity"],
        mean_activity=dataset["mean_activity"],
        synchrony=dataset["synchrony"],
        critical_slowing=dataset["critical_slowing"],
        crash_timestamp=np.array(dataset["crash_timestamp"]),
    )
    metadata = {
        "topology": dataset["topology"],
        "config": dataset["config"],
        "crash_timestamp": dataset["crash_timestamp"],
        "topology_resilience": dataset["topology_resilience"],
    }
    (output_dir / f"hcb_1_{dataset['topology']}.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    if make_plot:
        write_plot(dataset, output_dir / f"hcb_1_{dataset['topology']}.png")


def write_plot(dataset: dict[str, Any], path: Path) -> None:
    import matplotlib.pyplot as plt

    timestamps = dataset["timestamps"]
    energy = dataset["input_tensor"]["energy_scalar_t"]
    crash_timestamp = dataset["crash_timestamp"]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(timestamps, energy, color="black", linewidth=2)
    axes[0].set_ylabel("ATP flux")
    axes[0].set_ylim(-0.05, 1.05)

    axes[1].plot(timestamps, dataset["mean_activity"], color="#3366aa", linewidth=1.2)
    axes[1].plot(timestamps, dataset["synchrony"], color="#aa6633", linewidth=1.0, alpha=0.75)
    axes[1].axhline(
        dataset["config"]["synchrony_threshold"],
        color="gray",
        linewidth=1.0,
        linestyle="--",
    )
    axes[1].set_ylabel("activity / R")

    axes[2].plot(timestamps, dataset["critical_slowing"], color="#7a3db8", linewidth=1.2)
    axes[2].set_ylabel("lag-1 autocorr.")
    axes[2].set_xlabel("time")

    for axis in axes:
        axis.axvline(crash_timestamp, color="#cc2222", linewidth=1.5)
        axis.grid(True, alpha=0.25)

    title = (
        f"HCB-1 {dataset['topology']} crash at t={crash_timestamp:.2f} "
        f"(resilience={dataset['topology_resilience']:.3f})"
    )
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or verify HCB-1 datasets.")
    parser.add_argument("--topology", choices=("small_world", "random"), default="small_world")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/hcb_1"))
    parser.add_argument("--no-plot", action="store_true", help="Skip PNG plot generation.")
    parser.add_argument("--verify", action="store_true", help="Run deterministic bifurcation test.")
    parser.add_argument("--seed", type=int, default=HCB1Config.seed)
    parser.add_argument("--simulation-seed", type=int, default=HCB1Config.simulation_seed)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = HCB1Config(seed=args.seed, simulation_seed=args.simulation_seed)

    if args.verify:
        report = verify_bifurcation(config)
        print(json.dumps(report, indent=2))
        return 0 if report["passed"] else 1

    dataset = generate_dataset(args.topology, config)
    write_artifacts(dataset, args.output_dir, make_plot=not args.no_plot)
    print(
        json.dumps(
            {
                "topology": dataset["topology"],
                "crash_timestamp": dataset["crash_timestamp"],
                "topology_resilience": dataset["topology_resilience"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

