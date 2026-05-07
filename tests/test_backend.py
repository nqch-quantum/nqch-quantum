import pytest
import qibo
from qibo import Circuit, gates

import nqch_quantum
from nqch_quantum.backend import NQCHBackend


class FakeJob:
    def __init__(self, result):
        self._result = result
        self.verbose = None

    def result(self, verbose=True):
        self.verbose = verbose
        return self._result


class FakeClient:
    token = "fake-token"

    def __init__(self):
        self.calls = []
        self.job = FakeJob("fake-result")

    def run_circuit(self, circuit, device, project, nshots=None, verbatim=False):
        self.calls.append(
            {
                "circuit": circuit,
                "device": device,
                "project": project,
                "nshots": nshots,
                "verbatim": verbatim,
            }
        )
        return self.job


@pytest.fixture(autouse=True)
def restore_qibo_backend():
    yield
    qibo.set_backend("numpy")


class TestNQCHBackend:
    def test_metabackend_loads_backend_with_token(self):
        backend = nqch_quantum.MetaBackend.load(
            token="test-token",
            platform="test-platform",
            project="test-project",
            verbosity=False,
        )

        assert isinstance(backend, NQCHBackend)
        assert backend.name == "nqch-quantum"
        assert backend.client.token == "test-token"
        assert backend.platform == "test-platform"
        assert backend.project == "test-project"
        assert backend.verbosity is False

    def test_metabackend_reads_token_from_environment(self, monkeypatch):
        monkeypatch.delenv("NQCH_TOKEN", raising=False)
        monkeypatch.setenv("NQCH_QUANTUM_TOKEN", "env-token")

        backend = nqch_quantum.MetaBackend.load(platform="test-platform")

        assert backend.client.token == "env-token"

    def test_load_rejects_missing_platform(self):
        with pytest.raises(ValueError, match="requires a target platform"):
            nqch_quantum.MetaBackend.load(token="test-token")

    def test_load_rejects_missing_token(self, monkeypatch):
        monkeypatch.delenv("NQCH_QUANTUM_TOKEN", raising=False)
        monkeypatch.delenv("NQCH_TOKEN", raising=False)

        with pytest.raises(ValueError, match="requires a token"):
            nqch_quantum.MetaBackend.load(platform="test-platform")

    def test_execute_circuit_submits_to_configured_platform(self):
        client = FakeClient()
        backend = NQCHBackend(
            platform="test-platform",
            project="test-project",
            verbosity=False,
            client=client,
        )
        circuit = object()

        result = backend.execute_circuit(circuit, nshots=123, verbatim=True)

        assert result == "fake-result"
        assert client.calls == [
            {
                "circuit": circuit,
                "device": "test-platform",
                "project": "test-project",
                "nshots": 123,
                "verbatim": True,
            }
        ]
        assert client.job.verbose is False

    def test_execute_circuit_rejects_initial_state(self):
        client = FakeClient()
        backend = NQCHBackend(platform="test-platform", client=client)

        with pytest.raises(ValueError, match="does not support `initial_state`"):
            backend.execute_circuit(object(), initial_state=object())

        assert client.calls == []

    def test_qibo_set_backend_and_circuit_call_submit_shots(self):
        client = FakeClient()
        qibo.set_backend(
            "nqch-quantum",
            platform="test-platform",
            project="test-project",
            verbosity=False,
            client=client,
        )
        circuit = Circuit(1)
        circuit.add(gates.M(0))

        result = circuit(nshots=321)

        assert result == "fake-result"
        assert client.calls[0]["device"] == "test-platform"
        assert client.calls[0]["project"] == "test-project"
        assert client.calls[0]["nshots"] == 321
        assert client.calls[0]["verbatim"] is False
        assert client.job.verbose is False
