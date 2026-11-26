import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

VERSION = '0.26.4'
WHEEL = 'scipy-1.12.0-cp312-cp312-pyodide_2024_0_wasm32.whl'
SHA = '1a081410432367ee43f52a280961df4ba7e9bb65d8b9862b3cd2e3727e84d873'
CHUNK = 2 * 1024 * 1024

with tempfile.TemporaryDirectory() as tmp:
    wheel = pathlib.Path(tmp) / WHEEL
    subprocess.run(['curl', '-fsSL', '--retry', '2', '--max-time', '90', '-o', str(wheel),
                    f'https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/{WHEEL}'], check=True)
    data = wheel.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('Unexpected SciPy wheel SHA-256')
    out = pathlib.Path(sys.argv[1]) / 'mirrors' / VERSION / SHA
    out.mkdir(parents=True, exist_ok=True)
    for n, offset in enumerate(range(0, len(data), CHUNK)):
        (out / f'{n}.bin').write_bytes(data[offset:offset + CHUNK])
    (out / 'size.json').write_text(json.dumps(len(data)), encoding='utf-8')
