---
title: "The Newfoundland & Labrador Geriatric Health Index (NLGHI): A WHO-aligned, weighted multi-domain metric for longitudinal monitoring of geriatric health"
tags:
  - Python
  - Geriatrics
  - Health informatics
  - Clinical research
  - Public health
authors:
  - name: Mirza Niaz Zaman Elin
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 2025-08-31
bibliography: paper.bib
---

# Summary

The Newfoundland & Labrador Geriatric Health Index (NLGHI) converts the traditionally narrative Comprehensive Geriatric Assessment (CGA) into a quantitative, longitudinal measure aligned with the World Health Organization’s (WHO) holistic definition of health. The software provides a PyQt5 desktop interface for entering per-domain impairment ratings (fixed 0–5 scale), automatically computing domain-specific aggregate values (DSAVs = rating × domain weight) and an overall Geriatric Health Index (GHI = ΣDSAV/27). Built-in charts visualize GHI trajectories and DSAV heatmaps across visits; a patient workspace supports clinical notes, history, symptom snapshots, follow-ups, attachments, and reports. The design preserves clinical nuance while enabling early signal detection, standardized comparison across services, and reproducible analytics for clinical and public health research [@palmer2018cga; @Sum2022cga].

# Statement of need

Comprehensive Geriatric Assessment (CGA) is the current standard for evaluating older adults, yet it remains largely qualitative and narrative. While CGA’s multidimensional scope is indispensable, its outputs are not typically expressed as standardized, reproducible, and sensitive metrics. As a result, clinicians and researchers struggle to detect small but clinically meaningful changes over time, to compare outcomes across services, or to aggregate data for study and policy [@palmer2018cga; @Sum2022cga]. This absence of quantification constrains timely recognition of deterioration, delays early intervention, and limits the ability to evaluate the effectiveness of individualized care plans. A computable, transparent, and longitudinally sensitive measure is therefore needed to complement CGA and unlock its full value in both clinical and population settings.

NLGHI addresses this gap by providing a structured, quantitative framework that preserves CGA’s holistic intent while producing standardized scores amenable to longitudinal tracking. Its domains were selected to align with the WHO definition of health as encompassing physical, mental, and social well-being, not merely the absence of disease. Accordingly, the instrument spans biomedical conditions, functional status and disability, mental and behavioral health, and key social determinants. This breadth ensures the index captures the complex interplay of multimorbidity, function, cognition, and context that characterizes geriatric health.

A population-agnostic tool is insufficient here: the health of older adults is distinct from that of other age groups. Multimorbidity, polypharmacy, frailty, atypical presentations, and reduced physiological reserve make single-disease indicators or general adult measures poor proxies for health status in later life. Outcomes that matter to older adults—maintenance of independence, preservation of cognition, avoidance of functional decline—often shift the clinical focus from disease control to capability and participation. By integrating domains tailored to these priorities, the NLGHI offers a customized approach that is more responsive to geriatric realities than generic indices.

Quantification adds practical advantages that qualitative CGA lacks. First, it increases sensitivity to gradual change: small domain-level shifts can be summarized and visualized, enabling clinicians to detect emerging risk and act before crises occur. Second, standardized scoring improves comparability across episodes of care, clinicians, and sites, supporting coordinated transitions and clearer communication. Third, quantification enables decision support: thresholds can trigger review when risk accumulates. Finally, computable scores create analytic artifacts—time series, group summaries, and risk strata—that are essential for quality improvement and rigorous evaluation.

Implications extend beyond individual care. For clinical research, a transparent multi-domain metric offers a consistent outcome for trials and observational studies, allowing investigators to quantify functional and psychosocial benefits that traditional disease-centric endpoints may miss. Because NLGHI is constructed for repeated use, it suits longitudinal cohorts, pragmatic trials embedded in care pathways, and health-services research assessing models of geriatric care, rehabilitation, and community support. For public health, aggregated scores enable surveillance and planning: identifying communities with rising risk, revealing disparities linked to deprivation or access barriers, and evaluating programs such as falls prevention or cognitive health initiatives.

# Design and implementation

NLGHI implements a fixed list of domains with predefined weights reflecting clinical salience. At each visit, the clinician selects an impairment rating per domain on a 0–5 scale. DSAVs are computed as rating × domain weight. The overall GHI is calculated as ΣDSAV / 27, a normalized index designed for sensitive longitudinal comparison. The application is implemented in Python with PyQt5, NumPy, and Matplotlib. Core features include DSAV heatmaps, GHI trend charts, a patient workspace (history, notes, symptom checker, future references, attachments), backup/restore, export utilities, and data validation.

# Quality control

Automated tests verify constants (domain count and weights) and the GHI calculation invariant. The repository includes instructions and a minimal CI workflow to run tests on pushes and pull requests. Manual quality checks include exercising the GUI to ensure charts render and scroll correctly for long longitudinal series.

# Acknowledgements

Thanks to the community of clinicians and developers who provided feedback during iterations of the interface and data model.

# References
