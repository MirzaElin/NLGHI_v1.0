# Contributing

Thank you for the interest in improving NLGHI.

## How to contribute
- Open an issue to discuss bugs or feature ideas.
- Fork the repo, create a feature branch, and open a pull request.

## Development setup
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Code style
- Keep the **domains, weights, rating scale (0–5), DSAV, and GHI** logic intact.
- Add features in separate dialogs/windows when possible.
- Document public functions and keep methods focused.
