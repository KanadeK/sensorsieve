# Example flat-field sessions

These small deterministic PNGs exercise SensorSieve without using a real photographer's images or metadata.

- `before/`: two persistent dark spots plus one mark present in only one frame. The transient mark must be excluded.
- `after/`: one prior spot remains, one prior spot is gone, and one new spot appears.
- `clean/`: smooth illumination plus deterministic low-level pixel variation, with no persistent spot.
- `invalid-too-few/`: only two frames, used to demonstrate the input failure and exit code `2`.

Regenerate the files with:

```powershell
uv run python scripts/build_examples.py
```

The images are synthetic evidence fixtures, not examples of how to clean a physical sensor.

