# NQCH Quantum Cloud Client

## Install

Install first the package dependencies with the following commands.

We recommend to start with a fresh virtual environment to avoid dependencies
conflicts with previously installed packages.

```bash
python -m venv ./env
source activate ./env/bin/activate
```

The `nqch-quantum` package can be installed through `pip`:

```bash
pip install nqch-quantum
```

## Quick start

Once installed, the provider allows to run quantum circuit computations on NQCH CQT's labs.

:warning: Note: to run jobs on the remote cluster it is mandatory to own a
validated account.
Please, sign up to your preferred institution to
obtain the needed token to run computations on the cluster.

The following snippet provides a basic usage example.
Replace the `your-token` string with your user token received during the
registration process. To check which devices are available with your account
please visit the dashboard at your institution.

```python
import qibo
import nqch_quantum

# create the circuit you want to run
circuit = qibo.models.QFT(5)

# authenticate to server through the client instance
token = "your-token"
client = nqch_quantum.Client(token)

# run the circuit
device = "device_name"
project = "project_name"
job = client.run_circuit(circuit, device=device, project=project, nshots=1024)
result = job.result()
print(result)
```

The `device` name indicates the specific system or machine that will process the
job. The `project` name corresponds to the project or group to which the user
belongs and which will be charged for the service usage.

## Qibo backend

The package also exposes a Qibo backend provider, so circuits can be submitted
using Qibo's backend API.

```python
import qibo
from qibo import Circuit, gates

qibo.set_backend(
    "nqch-quantum",
    token="your-token",
    platform="selected_platform",
    project="project_name",
    verbosity=False,
)

circuit = Circuit(2)
circuit.add(gates.H(0))
circuit.add(gates.CNOT(0, 1))
circuit.add(gates.M(0, 1))

result = circuit(nshots=1024)
print(result.frequencies())
```

Direct backend execution is also supported when a per-call `verbatim` flag is
needed.

```python
backend = qibo.get_backend()
result = backend.execute_circuit(circuit, nshots=1024, verbatim=True)
```

### Backend limitations

The NQCH backend submits circuits to remote hardware or cloud systems. Execution
is shot-based and starts from the device default initial state, so
`initial_state` is not supported. Exact statevector workflows, gradients,
autodiff, and local statevector expectations are not generally supported by this
backend.
