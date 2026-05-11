from benchmarks.hcb_1.generator import verify_bifurcation


def test_verify_bifurcation():
    report = verify_bifurcation()
    assert report["passed"], report

