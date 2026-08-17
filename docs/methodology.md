# Methodology & Mathematical Foundations

This document outlines the formal mathematical definitions and algorithmic formulations implemented in `moveq-core`.

---

## 1. Population-Weighted Gini Coefficient

The Gini coefficient measures overall inequality in the distribution of a resource (e.g. public transport service capacity, trips per hour) across an areal population.

### Mathematical Formulation

Let areal units be indexed by \(i = 1, \dots, N\).
- Let \(y_i \ge 0\) be the service level (e.g. weekly trips, departures) in areal unit \(i\).
- Let \(w_i > 0\) be the population in areal unit \(i\).

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

Given sorted service levels \(y_{(i)}\) and cumulative population fractions \(p_k\):
1. **Bottom 40% Mean Service**:
   \[
   \bar{y}_{B40} = \frac{\sum_{i: p_i \le 0.40} y_{(i)} w_{(i)}}{\sum_{i: p_i \le 0.40} w_{(i)}}
   \]
2. **Top 10% Mean Service**:
   \[
   \bar{y}_{T10} = \frac{\sum_{i: p_i > 0.90} y_{(i)} w_{(i)}}{\sum_{i: p_i > 0.90} w_{(i)}}
   \]
3. **Palma Ratio**:
   \[
   \text{Palma} = \frac{\bar{y}_{T10}}{\bar{y}_{B40}}
   \]

If \(\bar{y}_{B40} = 0\), the ratio returns \(\infty\) (`float("inf")`).

---

## 3. Wagstaff Concentration Index (CI)

While the Gini coefficient measures pure inequality without regard to socioeconomic status, the **Concentration Index** measures inequality in a service variable \(y\) that is systematically correlated with a socioeconomic ranking variable \(r\) (e.g. index of multiple deprivation or income rank).

### Mathematical Formulation

Let:
- \(y_i\) = transit service in area \(i\)
- \(r_i\) = socioeconomic rank in area \(i\) (where \(r=1\) represents the most deprived/lowest socioeconomic rank, and higher values represent less deprived/wealthier areas)
- \(w_i\) = population of area \(i\)

1. **Ordering**: Sort all units in ascending order of their rank \(r_i\).
2. **Fractional Rank Calculation**:
   Compute the midpoint fractional rank \(R_i\) for each sorted unit:
   \[
   R_i = \frac{\sum_{j=1}^{i-1} w_j + \frac{1}{2} w_i}{\sum_{j=1}^N w_j}
   \]
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

### Interpretation
- \(CI \in [-1, 1]\).
- \(CI > 0\) (**Pro-Rich / Less Deprived**): Public transport service is disproportionately concentrated in less deprived areas.
- \(CI < 0\) (**Pro-Poor / More Deprived**): Public transport service is disproportionately concentrated in more deprived areas.
- \(CI = 0\): Service is uniformly distributed across socioeconomic tiers.

---

## 4. Weighted Composite Scoring with Weight Renormalization

Composite indicators aggregate multiple accessibility and service dimensions \(k \in K\) (each normalized to \([0, 1]\)) into a single \(0\)–\(100\) score using design weights \(w_k\).

### Graceful Handling of Missing Terms

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
