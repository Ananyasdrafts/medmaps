"""Data layer.

Responsibilities:
    - generate realistic CGM traces with simglucose for a simulated cohort
    - inject medication-adherence scenarios through the insulin control channel
      (missed and mistimed meal boluses)
    - window the streams into supervised (history -> future) examples with
      strictly temporal, leakage-free splits

Kept signal-agnostic so a second vital (phase 2) is a config change, not a rewrite.
"""
