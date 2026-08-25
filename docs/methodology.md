# Methodology & Mathematical Foundations

This document outlines the formal mathematical definitions and algorithmic formulations implemented in `moveq-core`.

---

## 1. Population-Weighted Gini Coefficient

The Gini coefficient measures overall inequality in the distribution of a resource (e.g. public transport service capacity, trips per hour) across an areal population.

### Mathematical Formulation

Let areal units be indexed by \(i = 1, \dots, N\).
- Let \(y_i \ge 0\) be the service level (e.g. weekly trips, departures) in areal unit \(i\).
- Let \(w_i \ge 0\) be the population in areal unit \(i\), with \(\sum_i w_i > 0\). Individual unpopulated units (\(w_i = 0\)) are allowed; they contribute nothing.

Inputs are 1-dimensional. Non-finite values are rejected.

If total service \(\sum_i y_i w_i = 0\) (nothing to distribute), \(G = 0\) by convention.

1. **Ordering**: Sort all units by non-decreasing service level:
   \[
   y_{(1)} \le y_{(2)} \le \dots \le y_{(N)}
   \]
2. **Cumulative Population Share**:
   \[
   p_k = \frac{\sum_{j=1}^k w_{(j)}}{\sum_{j=1}^N w_j}, \quad p_0 = 0
   \]
3. **Cumulative Service Share**:
   \[
   s_k = \frac{\sum_{j=1}^k y_{(j)} w_{(j)}}{\sum_{j=1}^N y_j w_j}, \quad s_0 = 0
   \]
4. **Lorenz Area Integration**:
   The Lorenz curve plots \(s_k\) against \(p_k\). The area under the Lorenz curve \(L\) is computed via trapezoidal numerical integration:
   \[
   L = \int_0^1 s(p) \, dp \approx \sum_{k=1}^N \frac{s_{k-1} + s_k}{2} (p_k - p_{k-1})
   \]
5. **Gini Coefficient**:
   \[
   G = 1 - 2L
   \]

### Interpretation
- \(G = 0\): Perfect equality (every individual receives identical transit service).
- \(G = 1\): Maximum inequality (one person receives all transit service).

---

## 2. Palma Ratio

The Palma ratio focuses specifically on the distributional extremes: the top 10% highest-service population relative to the bottom 40% lowest-service population.

### Mathematical Formulation

Sort units by non-decreasing service. Let \(W = \sum_i w_i\), and write \(W_{(k)}^{\text{before}}\) for the population strictly below unit \(k\) in that order.

An areal unit that straddles a cut is **split**: only the share of its population that falls inside the bottom 40% or top 10% is counted. Whole-unit inclusion/exclusion would make the ratio depend on how the map is partitioned.

1. **Overlap weights**:
   \[
   \omega_k^{B40} = \max\bigl(0,\; \min(W_{(k)}^{\text{before}} + w_{(k)},\; 0.40 W) - W_{(k)}^{\text{before}}\bigr)
   \]
   \[
   \omega_k^{T10} = \max\bigl(0,\; (W_{(k)}^{\text{before}} + w_{(k)}) - \max(W_{(k)}^{\text{before}},\; 0.90 W)\bigr)
   \]
2. **Means and ratio**:
   \[
   \bar{y}_{B40} = \frac{\sum_k y_{(k)}\,\omega_k^{B40}}{\sum_k \omega_k^{B40}}, \qquad
   \bar{y}_{T10} = \frac{\sum_k y_{(k)}\,\omega_k^{T10}}{\sum_k \omega_k^{T10}}, \qquad
   \text{Palma} = \frac{\bar{y}_{T10}}{\bar{y}_{B40}}
   \]

If both means are zero (all-zero service), Palma is \(1\) by the same equality convention as Gini. If only \(\bar{y}_{B40} = 0\), the ratio returns \(\infty\) (`float("inf")`). Because units are sorted ascending and values are non-negative, Palma is otherwise at least \(1\).

---

## 3. Wagstaff Concentration Index (CI)

While the Gini coefficient measures pure inequality without regard to socioeconomic status, the **Concentration Index** measures inequality in a service variable \(y\) that is systematically correlated with a socioeconomic ranking variable \(r\) (e.g. index of multiple deprivation or income rank).

### Mathematical Formulation

Let:
- \(y_i\) = transit service in area \(i\)
- \(r_i\) = socioeconomic rank in area \(i\) (where \(r=1\) represents the most deprived/lowest socioeconomic rank, and higher values represent less deprived/wealthier areas)
- \(w_i\) = population of area \(i\)

Unpopulated units (\(w_i = 0\)) are dropped before ranking. Service may be negative (e.g. a residual); Gini and Palma reject negatives.

1. **Ordering**: Sort remaining units in ascending order of rank \(r_i\).
2. **Tied ranks**: Consecutive units with the same \(r\) form a group \(g\) with mass \(W_g\). Every unit in the group shares the group's midpoint fractional rank, so the result does not depend on input order among ties:
   \[
   R_g = \frac{W_{<g} + \tfrac{1}{2} W_g}{W}
   \]
   where \(W_{<g}\) is the population strictly poorer (lower rank) than group \(g\).
3. **Weighted Covariance & Mean**:
   \[
   \mu = \frac{\sum_{i=1}^N w_i y_i}{\sum_{i=1}^N w_i}
   \]
   \[
   \text{Cov}_w(y, R) = \frac{\sum_{i=1}^N w_i (y_i - \mu)(R_i - 0.5)}{\sum_{i=1}^N w_i}
   \]
4. **Concentration Index**:
   \[
   CI = \frac{2 \cdot \text{Cov}_w(y, R)}{\mu}
   \]
   If \(\mu = 0\), \(CI = 0\) by convention.

### Interpretation
- For non-negative service, \(CI \in [-1, 1]\).
- \(CI > 0\) (**Pro-Rich / Less Deprived**): Public transport service is disproportionately concentrated in less deprived areas.
- \(CI < 0\) (**Pro-Poor / More Deprived**): Public transport service is disproportionately concentrated in more deprived areas.
- \(CI = 0\): Service is uniformly distributed across socioeconomic tiers (or mean service is zero).

---

## 4. Weighted Composite Scoring with Weight Renormalization

Composite indicators aggregate multiple accessibility and service dimensions \(k \in K\) (each normalized to \([0, 1]\)) into a single \(0\)–\(100\) score using design weights \(w_k\).

### Graceful Handling of Missing Terms

Design weights \(w_k\) must be finite and strictly positive. Term values must be finite (`NaN` / `inf` are rejected, not clipped). Values outside \([0, 1]\) are clipped after that check.

When a subset of indicators \(M \subset K\) is unavailable (i.e. \(y_k = \text{None}\)), `moveq` drops \(M\) and renormalizes the weights of the available indicators \(P = K \setminus M\):

1. **Effective Weights**:
   \[
   w_k' = \frac{w_k}{\sum_{j \in P} w_j} \quad \forall k \in P
   \]
2. **Composite Score**:
   \[
   S = 100 \times \sum_{k \in P} w_k' \cdot \text{clip}_{0,1}(y_k)
   \]
3. If all indicators are missing (\(P = \emptyset\)), \(S = \text{None}\) and an explanatory note is recorded.

---

## 5. Multidimensional Vulnerability & Deprivation Indices

In [`moveq_core.frames`](file:///Users/souravamseekarmarti/Projects/moveq/reference/python/moveq-core/src/moveq_core/frames.py):

- **Vulnerability Index**: Combines \(M\) deprivation factors (e.g. unemployment, zero-car households, elderly population) by min-max scaling each factor column to \([0, 100]\) and computing the row-wise mean:
  \[
  V_i = \frac{100}{M} \sum_{m=1}^M \frac{x_{im} - \min(x_m)}{\max(x_m) - \min(x_m)}
  \]
- **Multiply-Deprived Areas**: Identifies areal units in the worst tertile (\(\ge 66.7\%\) quantile) across at least \(k\) indicators simultaneously.
