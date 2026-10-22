"""
Test suite validating Member 3's integration contract for QShield.
Ensures simulate_bb84 returns the exact keys, types, and expected bounds.
"""

import sys
import os
import importlib.util
import pytest

# Explicitly load local app.py to avoid collisions with site-packages 'app'
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

app_spec = importlib.util.spec_from_file_location("qshield_app", os.path.join(repo_root, "app.py"))
qshield_app = importlib.util.module_from_spec(app_spec)
app_spec.loader.exec_module(qshield_app)

simulate_bb84 = qshield_app.simulate_bb84
make_circuit = qshield_app.make_circuit
measure_qubits = qshield_app.measure_qubits


def test_contract_keys_and_types():
    """Verify that simulate_bb84 returns the exact agreed dictionary contract."""
    res = simulate_bb84(n_bits=64, eve=False, noise=0.0, sample_fraction=0.25, seed=42)

    required_keys = ["n_bits", "sifted_bits", "sampled_bits", "sample_errors", "qber", "remaining_bits", "status"]
    for key in required_keys:
        assert key in res, f"Missing key in simulation output: {key}"

    assert isinstance(res["n_bits"], int)
    assert isinstance(res["sifted_bits"], int)
    assert isinstance(res["sampled_bits"], int)
    assert isinstance(res["sample_errors"], int)
    assert isinstance(res["qber"], float)
    assert isinstance(res["remaining_bits"], int)
    assert isinstance(res["status"], str)


def test_clean_channel_qber_zero():
    """In ideal conditions (no Eve, no noise), QBER must be 0.0%."""
    res = simulate_bb84(n_bits=128, eve=False, noise=0.0, sample_fraction=0.25, seed=42)
    assert res["qber"] == 0.0
    assert res["sample_errors"] == 0
    assert res["remaining_bits"] == res["sifted_bits"] - res["sampled_bits"]


def test_eve_attack_qber_elevation():
    """With Eve intercept-resend enabled, QBER should be substantially higher (~25%)."""
    res = simulate_bb84(n_bits=512, eve=True, noise=0.0, sample_fraction=0.3, seed=42)
    assert res["qber"] > 0.15, f"Expected QBER > 15% with Eve active, got {res['qber']}"
    assert "High errors" in res["status"]


def test_sifting_conservation():
    """Sifted bits must equal sampled bits plus remaining bits."""
    res = simulate_bb84(n_bits=256, eve=False, noise=0.05, sample_fraction=0.25, seed=123)
    assert res["remaining_bits"] + res["sampled_bits"] == res["sifted_bits"]


def test_input_validation():
    """Ensure invalid parameters raise ValueErrors as per specification."""
    with pytest.raises(ValueError):
        simulate_bb84(n_bits=4)

    with pytest.raises(ValueError):
        simulate_bb84(noise=-0.1)

    with pytest.raises(ValueError):
        simulate_bb84(sample_fraction=0.0)
