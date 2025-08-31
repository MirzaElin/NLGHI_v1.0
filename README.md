# NLGHI — Newfoundland & Labrador Geriatric Health Index

A PyQt5 desktop application that quantifies the Comprehensive Geriatric Assessment (CGA) for **longitudinal** monitoring of older adults.

- **WHO-aligned domains** with predefined weights
- Fixed **0–5** impairment ratings per domain
- **DSAV = rating × domain weight**, **GHI = ΣDSAV / 27**
- **Charts:** GHI trend line and DSAV heatmap
- Patient workspace (history, notes, symptom checker, future references, attachments)
- Exports (TXT/MD/CSV), backups, and data validation

> Research and education only. Not a medical device; does not provide diagnosis or treatment recommendations.

## Install

```bash
pip install -r requirements.txt
python NLGHI_App_MD.py
```

## Repository layout (suggested)

```
.
├── NLGHI_App_MD.py
├── paper.md
├── paper.bib
├── README.md
├── LICENSE
├── CITATION.cff
├── CONTRIBUTING.md
├── requirements.txt
├── tests/
│   └── test_invariants.py
└── .github/workflows/tests.yml
```

## How it works

- **Inputs:** domain impairment ratings (0–5) on a fixed set of weighted domains.
- **Outputs:** DSAVs per domain, and a single GHI score per visit (`ΣDSAV/27`).
- **Visualization:** longitudinal GHI line chart; DSAV heatmap across sessions.

## Citing

See `CITATION.cff` or cite the JOSS paper once accepted.
