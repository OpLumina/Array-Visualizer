# Array Space Explorer (array_visualizer.py)

A lightweight, single-file browser UI for exploring **N-dimensional arrays** in a visual representation, make pipelines, and view the actual code you can use to replicate it (with NumPy). It starts a tiny local HTTP server and serves an embedded HTML/JS app (no external assets).

## Requirements

- Python 3.8+ (uses only the standard library)
- A modern web browser (Chrome/Edge/Firefox)

## Run

```bash
python array_visualizer.py
```

By default it binds to `127.0.0.1` on an available port (starting at `8765`) and opens a browser tab automatically.

### CLI options

```bash
python array_visualizer.py --host 127.0.0.1 --port 8765
python array_visualizer.py --no-browser
```

- `--host` (default `127.0.0.1`): address to bind the server to
- `--port` (default `0`): port to bind (`0` = auto-pick a free port)
- `--no-browser`: don’t auto-open a browser tab

Stop the server with `Ctrl+C`.

## Controls

- `WASD` or arrow keys: move
- `Q / E`: up / down
- Mouse drag: orbit camera
- `Shift` + drag: move selected array
- Mouse wheel: zoom
- Click a cell: select it (then edit in the cell input)

## UI overview

- **Arrays** tab: add 1D–5D arrays, fill, snap, delete (per-row `x`)
- **Pipeline** tab: build operations like snap-to, align, copy-data, fill, reshape, move, scale, delete
- **Info** tab: camera + selected array stats


## Tests

Run the small unit test suite (covers port selection):

```bash
python -m unittest -v test_array_visualizer.py
```
