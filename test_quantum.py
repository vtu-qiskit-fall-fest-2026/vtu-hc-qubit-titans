"""
Test Quantum Core Setup (Member 1 Test Script as described in Starter Handbook Section 6).
Verifies Qiskit and Qiskit-Aer simulator installation and execution.
"""

import sys
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Ensure safe UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_test():
    circuit = QuantumCircuit(1, 1)
    circuit.x(0)
    circuit.measure(0, 0)

    backend = AerSimulator()
    result = backend.run(circuit, shots=100).result()
    counts = result.get_counts()
    print("Quantum Circuit Verification:")
    print("Counts:", counts)
    try:
        print("Circuit Diagram:")
        print(circuit.draw(output="text"))
    except Exception:
        pass
    assert counts.get('1') == 100, "Expected {'1': 100}"
    print("STATUS: PASS (Qiskit and AerSimulator operational!)")

if __name__ == "__main__":
    run_test()
