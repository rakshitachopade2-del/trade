# Synthetic intake example

Every price, volume, membership record, filing figure and publication record here is invented for engineering tests. Even the NIFTY50 mapping is exercised with fictional values. This is not historical exchange data or a successful real-data trial.

Run `.venv/bin/python -m backend.app.intake data/intake-example` from the repository root. The expected result is **coverage_complete / synthetic_test**, with 36 unique in-sample bars, one extra 10:00-start bar, and one duplicate stock-list entry. Review references explicitly refer only to these fictional fixtures. Nothing is fetched from the example.invalid URL.

See [the exact schema](../../docs/MILESTONE_2A.md). Generated reports/original copies belong only in ignored private-data/.
