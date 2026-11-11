# Sector ROCE and Source Comparison Notes

ROCE is computed as EBIT / (equity capital + reserves + borrowings) × 100, per the supplied technical specification. Financial-sector companies are tagged and given within-sector percentile context; their debt/equity values are not used for high-leverage flagging.

The source company-master ROE/ROCE fields are treated as display cross-checks only. They do not override the recomputed analytics. Material differences are recorded in `output/source_ratio_comparison.csv`; known anomalies and missing historical statements are retained for review.
