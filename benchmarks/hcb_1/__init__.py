"""HCB-1 hypometabolic crash benchmark."""

from .generator import (
    HCBConfig,
    HCBResult,
    generate_hcb_dataset,
    verify_bifurcation,
)

__all__ = [
    "HCBConfig",
    "HCBResult",
    "generate_hcb_dataset",
    "verify_bifurcation",
]
