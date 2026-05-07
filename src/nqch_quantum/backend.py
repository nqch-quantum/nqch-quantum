"""Qibo backend adapter for NQCH Quantum Cloud."""

import os

from qibo.backends import NumpyBackend
from qibo.config import raise_error

from .nqch_client import Client


TOKEN_ENVIRONMENT_VARIABLES = ("NQCH_QUANTUM_TOKEN", "NQCH_TOKEN")


def _resolve_token(token):
    """Return an explicit token or the first configured environment token."""
    if token:
        return token

    for variable in TOKEN_ENVIRONMENT_VARIABLES:
        value = os.getenv(variable)
        if value:
            return value

    return None


class NQCHBackend(NumpyBackend):
    """Qibo backend that submits circuits to the NQCH Quantum Cloud."""

    def __init__(
        self,
        token=None,
        platform=None,
        project="personal",
        verbosity=True,
        client=None,
        dtype="complex128",
    ):
        super().__init__()
        self.name = "nqch-quantum"
        self.set_dtype(dtype=dtype)

        if platform is None:
            raise_error(
                ValueError,
                "The NQCH backend requires a target platform, for example "
                '`qibo.set_backend("nqch-quantum", platform="platform", ...)`.',
            )

        resolved_token = _resolve_token(token)
        if client is None and resolved_token is None:
            raise_error(
                ValueError,
                "The NQCH backend requires a token. Pass `token=...` or set "
                "`NQCH_QUANTUM_TOKEN` or `NQCH_TOKEN`.",
            )

        self.platform = platform
        self.project = project
        self.verbosity = verbosity
        self.client = client if client is not None else Client(token=resolved_token)

    def execute_circuit(
        self,
        circuit,
        initial_state=None,
        nshots=1000,
        verbatim=False,
    ):
        """Execute a Qibo circuit on the configured NQCH platform."""
        if initial_state is not None:
            raise_error(
                ValueError,
                "The NQCH backend does not support `initial_state`; hardware and "
                "cloud executions start from the device default initial state.",
            )

        job = self.client.run_circuit(
            circuit,
            device=self.platform,
            project=self.project,
            nshots=nshots,
            verbatim=verbatim,
        )

        return job.result(verbose=self.verbosity)


class MetaBackend:
    """Qibo provider entry point for ``qibo.set_backend("nqch-quantum")``."""

    @staticmethod
    def load(**kwargs):
        """Load the NQCH Qibo backend."""
        return NQCHBackend(**kwargs)
        
    @staticmethod
    def list_available():
        return True
