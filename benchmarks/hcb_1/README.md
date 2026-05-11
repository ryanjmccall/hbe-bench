# HCB-1: Hypometabolic Crash Benchmark

HCB-1 generates a synthetic cortical-column network under progressive energy
starvation. The dataset input is the pair `[Connectivity_Graph,
Energy_Scalar_t]`; the target label is `crash_timestamp`, the first time the
smoothed synchrony order parameter crosses the bifurcation threshold.

The default verifier compares a small-world topology with a random topology
using the same node count, degree, and deterministic seeds. The small-world
graph is expected to retain synchrony longer because its local clustering and
shortcuts provide greater allostatic reserve under declining ATP flux.

```bash
python benchmarks/hcb_1/generator.py --verify
python benchmarks/hcb_1/generator.py --topology small_world --output-dir artifacts/hcb_1
python benchmarks/hcb_1/generator.py --topology random --output-dir artifacts/hcb_1
```

Artifacts are written as compressed NumPy datasets plus a PNG plot showing ATP
flux, mean neural activity/synchrony, and the critical-slowing lag-1
autocorrelation around the crash point.

