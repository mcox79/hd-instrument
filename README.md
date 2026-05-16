# hd-instrument

Observable hyperdimensional computing substrate with neuromodulator-style control and reward-modulated Hebbian learning.

A research instrument for compositional computation: every operation is traceable, every modulator scalar is dial-able, and the substrate is independently certified against closed-form theory.

## Status

Pre-alpha. See [PROGRESS.md](PROGRESS.md) for current phase and [PLAN.md](PLAN.md) for the full build plan.

## Install

```bash
pip install -e ".[dev,dashboard]"
```

## Verify

```bash
pytest verification/
python verification/run_certification.py
```

## Dashboard

```bash
streamlit run hdlab/dashboard/app.py
```

## License

MIT. See [LICENSE](LICENSE).
