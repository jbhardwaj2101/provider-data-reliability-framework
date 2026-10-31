# Reproducibility notes

- Random generator: `random.Random(seed)` from the Python standard library.
- Replications: seeds 0 through 99 inclusive.
- Event count: 1,000 per replication.
- Synthetic inputs: 80% evidence flag probability, 12% downstream failure flag probability, uniform event kinds.
- Generate outputs: `python pdrf_benchmark.py --output results`.
- Unit tests: `python -m unittest discover -p 'test_*.py' -v`.
- No actual provider identity resolution, verified attestations, real downstream publication acknowledgments, or observational patient/provider data.
