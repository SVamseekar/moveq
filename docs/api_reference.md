# API Reference

Complete Python API and class references for the `moveq` suite.

---

## 1. `moveq_core.equity`

Core population-weighted inequality algorithms.

### `compute_gini(values: np.ndarray, weights: np.ndarray) -> float`
Computes the population-weighted Gini coefficient via numerical integration of the Lorenz curve.

- **Parameters**:
  - `values` (`np.ndarray`): Public transport service levels per areal unit (e.g. departures, seat-km).
  - `weights` (`np.ndarray`): Population count or weight per areal unit.
- **Returns**:
  - `float`: Gini coefficient in \([0, 1]\). \(0\) represents perfect equality, and \(1\) represents maximum inequality. Zero total service returns `0.0`.
- **Raises**:
  - `ValueError`: if inputs are not 1-dimensional, differ in length, are empty, contain non-finite or negative values, or have non-positive total weight.

---

### `compute_palma_ratio(values: np.ndarray, weights: np.ndarray) -> float`
Computes the Palma ratio: the ratio of the mean service level in the top 10% highest-service population to the bottom 40% lowest-service population.

- **Parameters**:
  - `values` (`np.ndarray`): Public transport service levels per areal unit.
  - `weights` (`np.ndarray`): Population weight per unit.
- **Returns**:
  - `float`: Palma ratio. Areas that straddle the 40% / 90% population cuts are split proportionally. Equal service, including all-zero service, returns `1.0`. Returns `float("inf")` if the bottom 40% has zero mean service while the top 10% does not.
- **Raises**:
  - `ValueError`: same input constraints as `compute_gini`.

---

### `compute_concentration_index(service: np.ndarray, rank: np.ndarray, population: np.ndarray) -> float`
Computes the Wagstaff Concentration Index using the fractional rank covariance method.

- **Parameters**:
  - `service` (`np.ndarray`): Service level per areal unit.
  - `rank` (`np.ndarray`): Socioeconomic or deprivation rank per unit (where \(1\) = most deprived, higher numbers = less deprived).
  - `population` (`np.ndarray`): Population weight per unit.
- **Returns**:
  - `float`: Concentration Index. For non-negative service this lies in \([-1, 1]\). Positive values indicate pro-rich concentration; negative values indicate pro-poor concentration. Tied ranks share a group-midpoint fractional rank. Unpopulated units are ignored. Zero mean service returns `0.0`.
- **Raises**:
  - `ValueError`: if any array is not 1-dimensional, lengths differ, inputs are empty or non-finite, or total population is not positive. Negative service is allowed.

---

### `gini_result(values, weights, *, context=None) -> EquityResult`
Same Gini calculation as `compute_gini`, returned as an `EquityResult` (`method="lorenz-trapezoid"`). Zero-weight units are counted in `n_dropped` and excluded from `n_areas` and `total_population`. Zero total service records a warning and sets `value` to `0.0`.

### `palma_result(values, weights, *, context=None) -> EquityResult`
Same Palma calculation as `compute_palma_ratio`, returned as an `EquityResult` (`method="palma-split-40-90"`). `parameters` records the population cuts `bottom_cut=0.40` and `top_cut=0.90`. All-zero service and infinite Palma each record a warning.

### `concentration_index_result(service, rank, population, *, context=None) -> EquityResult`
Same Concentration Index calculation as `compute_concentration_index`, returned as an `EquityResult` (`method="wagstaff-covariance"`). Unpopulated units are dropped (`n_dropped` / `n_areas`). Zero mean service records a warning and sets `value` to `0.0`.

### `EquityResult`
Frozen dataclass analogous to `ScoreResult`. `value` is the same number the corresponding `compute_*` function returns (`inf` is allowed for Palma).

- `metric: "gini" | "palma" | "ci"`
- `value: float`
- `method: str` — documented method id (`lorenz-trapezoid`, `palma-split-40-90`, `wagstaff-covariance`)
- `n_areas: int` — live areal units used
- `n_dropped: int` — units dropped (for example zero-population units)
- `total_population: float` — sum of weights actually used
- `parameters: dict` — method parameters (Palma cuts, and so on)
- `warnings: list[str]` — empty if none
- `note: str | None` — optional explanation of conventions
- `context: dict[str, str]` — free-form metadata, default `{}`
- `to_dict() -> dict` — JSON-serializable copy of the fields

The existing `compute_gini`, `compute_palma_ratio`, and `compute_concentration_index` functions still return `float` (they return `.value` from the corresponding `*_result` function).

---

## 2. `moveq_core.score`

Configurable weighted composite scoring with dynamic missing-term weight renormalization.

### `compute_score(...) -> ScoreResult`
```python
def compute_score(
    terms: dict[str, float | None],
    weights: dict[str, float],
    *,
    labels: dict[str, str] | None = None,
    n_areas: int | None = None,
    context: dict[str, str] | None = None,
    empty_note: str = "No score for this cut — required inputs are missing.",
) -> ScoreResult
```
- **Parameters**:
  - `terms` (`dict[str, float | None]`): Mapping of term IDs to normalized values in \([0, 1]\) (or `None` if missing).
  - `weights` (`dict[str, float]`): Mapping of term IDs to initial design weights (finite and strictly positive).
  - `labels` (`dict[str, str] | None`): Optional human-readable labels for each term.
  - `n_areas` (`int | None`): Optional count of areal units contributing to this score.
  - `context` (`dict[str, str] | None`): Free-form metadata dict preserved in results.
  - `empty_note` (`str`): Informational message returned when all terms are missing.
- **Returns**:
  - `ScoreResult`: Dataclass containing the computed score, component breakdown, list of dropped terms, and audit notes.

### `ScoreResult`
- `score: float | None`: Overall composite score \([0, 100]\), or `None` if all terms were missing.
- `components: list[ScoreComponent]`: Breakdown of individual score components.
- `dropped: list[str]`: Keys of terms that were omitted due to missing data.
- `n_areas: int | None`: Number of units evaluated.
- `note: str | None`: Explanatory notice (e.g. renormalizations).
- `context: dict[str, str]`: Custom contextual metadata.
- `to_dict() -> dict[str, Any]`: Serializes the score result into a JSON-compatible dictionary.

---

## 3. `moveq_core.frames`

Convenience methods for pandas DataFrames (requires `moveq-core[frames]`).

### `compute_vulnerability_index(df: pd.DataFrame, factors: list[str]) -> pd.Series`
Combines multiple deprivation and vulnerability columns into a 0–100 index using min-max scaling followed by row-wise averaging.

### `identify_multiply_deprived(df: pd.DataFrame, factors: list[str], min_factors: int = 3) -> pd.Series`
Returns a boolean pandas Series flagging rows situated in the worst tertile (\(\ge 66.7\%\) quantile) across at least `min_factors` indicators.

---

## 4. `moveq_catalogue.catalogue`

Cross-country methodology harmonization registry.

### `SectionAction` (`Enum`)
- `SectionAction.SAME = "same"`
- `SectionAction.REPLACE = "replace"`
- `SectionAction.OMIT = "omit"`

### `Catalogue(base_sections: list[str], country: str)`
- `register(section_id: str, action: SectionAction, *, note: str | None = None, replacement_title: str | None = None) -> Catalogue`
- `unregistered() -> list[str]`: Lists any base sections that have not yet been assigned a decision.
- `validate() -> list[str]`: Validates completeness. Returns a list of error strings; empty list indicates full specification.
- `summary() -> dict[str, int]`: Returns counts of each action (`same`, `replace`, `omit`).
- `to_dict() -> dict[str, Any]`: Serializes the catalogue into a dictionary.
