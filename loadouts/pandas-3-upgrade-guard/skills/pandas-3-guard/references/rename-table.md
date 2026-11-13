# pandas 1/2 → pandas 3 table

From the pandas 3.0.0 release notes (https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) and the copy-on-write
guide (https://pandas.pydata.org/docs/user_guide/copy_on_write.html). Checked against pandas 3.1.0.

## Removed: raises in pandas 3

| Old | pandas 3 |
|---|---|
| `df.applymap(f)` | `df.map(f)` |
| `df.append(other)` (removed in 2.0) | `pd.concat([df, other], ignore_index=True)` |
| `df.iteritems()` (removed in 2.0) | `df.items()` |
| `df.fillna(method="ffill")` | `df.ffill()` |
| `df.replace(x, method="pad")` | `df.replace(x, np.nan).ffill()` |
| `s.interpolate("pad")` | `s.ffill()` |
| `freq="H"`, `"BH"`, `"T"`, `"L"`, `"U"`, `"N"` | `"h"`, `"bh"`, `"min"`, `"ms"`, `"us"`, `"ns"` |
| `freq="M"`, `"Q"`, `"Y"`, `"A"` (ends) | `"ME"`, `"QE"`, `"YE"` |
| `read_csv(delim_whitespace=True)` | `read_csv(sep=r"\s+")` |
| `read_csv(date_parser=f)` | `read_csv(date_format="...")` or `pd.to_datetime` afterwards |
| `read_csv(infer_datetime_format=True)` | drop it; strict inference is the default |
| `df.swapaxes(0, 1)` | `df.T` |
| `s.view("int64")` | `s.astype("int64")` |
| `df.groupby("k", axis=1)` | `df.T.groupby("k")` |
| `df.first("3D")` / `df.last("3D")` | `df.loc[df.index < df.index[0] + pd.Timedelta("3D")]` |
| `pd.to_numeric(s, errors="ignore")` | `pd.to_numeric(s, errors="coerce")` |
| `s.bool()` | `bool(s.item())` |
| `pd.set_option("mode.use_inf_as_na", True)` | `df.replace([np.inf, -np.inf], np.nan)` |
| `pd.read_json('[{"a": 1}]')` | `pd.read_json(io.StringIO(text))` (same for read_html, read_xml) |

## Copy-on-write: writes that are silently lost

| Old | pandas 3 |
|---|---|
| `df["v"][0] = 1` | `df.loc[0, "v"] = 1` |
| `df[df.a > 0]["b"] = 0` | `df.loc[df.a > 0, "b"] = 0` |
| `df["v"].fillna(0, inplace=True)` | `df["v"] = df["v"].fillna(0)` |
| `sub = df[cols]; sub["x"] = 1` expecting `df` to change | change `df` itself |
| defensive `.copy()` to silence SettingWithCopyWarning | not needed; the warning is gone |

## Changed meaning: same code, different answer

| Change | What to do |
|---|---|
| String columns are dtype `str`, not `object` | `pd.api.types.is_string_dtype(s)`; `select_dtypes(include=["str"])` |
| A `str` column refuses non-strings | convert on purpose if mixed values are wanted |
| Missing strings are `NaN` | test with `isna()`, not `is None` |
| `groupby(...)` on categoricals defaults to `observed=True` | pass `observed=False` to keep empty categories |
| `agg(np.sum)` is no longer swapped for pandas' sum | `agg("sum")` |
| `Series[int]` always means a label, never a position | `s.iloc[i]` for positions |
| `mode.copy_on_write` option does nothing | remove it |
