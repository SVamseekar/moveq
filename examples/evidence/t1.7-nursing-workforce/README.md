# T1.7 — Global nursing workforce (BLOCKED)

Kharazmi, Bordbar and Bordbar, *Distribution of nursing workforce in the world using Gini coefficient*, BMC Nursing 22:151 (2023). CC BY 4.0.

The paper reports a global Gini of **0.667**, between-HDI-group Gini **0.467**, and within-group values **0.217–0.283**, over 189 countries.

This case does **not** compute a Gini. Three independent defects, verified from the article:

1. **Formula.** Methods state `Gini = 1 − Σ(Xi × Yi)` with `Xi` / `Yi` as cumulative percentages of population and nurses. That is not moveq's trapezoid Lorenz form, and it is incomplete as written.
2. **No per-country table.** Table 1 is four HDI-group aggregates (population totals, nurse totals, age and sex shares). The 189-country series is not published. Data are "available from the corresponding author on reasonable request".
3. **Weighting undisclosed.** Country-equal and population-weighted Ginis are different numbers; the paper does not say which it used.

The four-row table, were it scored, is the *between-group* comparison (published 0.467), not a route to 0.667. A WHO NHWA + UN rebuild would be a **separate RECOMPUTED** case and must never be labelled a reproduction of 0.667.
