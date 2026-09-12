# T1.6 — Missing-term reweighting (DEMONSTRATED)

Constructed composite: `access=0.8`, `frequency=0.6`, `climate` missing, design weights 0.50 / 0.25 / 0.25.

The independent oracle (`composite_score` in `oracles.py`) gives **73.33333333333333** under `reweight`. Treating the missing term as zero gives **55.0**. That 18-point swing is the example; it is not a finding about a named NUTS2 region.

`as_zero` is documented here as the contrast, not as a second badge. One case, one badge, one expected value (`reweight`).
