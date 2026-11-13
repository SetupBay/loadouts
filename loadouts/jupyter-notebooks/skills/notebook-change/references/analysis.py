# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Weekly orders: example analysis
# Parameters first, a data check, then the result. Runs top to bottom from a fresh kernel.

# %% tags=["parameters"]
SEED = 42
N_ORDERS = 500
WEEKS = 8

# %%
import random
import statistics

rng = random.Random(SEED)
orders = [{"week": rng.randrange(WEEKS), "pence": rng.randint(200, 5000)} for _ in range(N_ORDERS)]

# %% [markdown]
# ## Data check
# Shape, missing values and ranges that the rest of the notebook relies on.

# %%
assert len(orders) == N_ORDERS, "unexpected row count"
assert all(o["pence"] is not None for o in orders), "missing values"
assert all(0 <= o["week"] < WEEKS for o in orders), "week out of range"
print(f"rows: {len(orders)}, weeks: {len({o['week'] for o in orders})}")

# %%
by_week = {w: [o["pence"] for o in orders if o["week"] == w] for w in range(WEEKS)}
summary = {w: (len(v), statistics.median(v)) for w, v in by_week.items()}
busiest = max(summary, key=lambda w: summary[w][0])
print(f"busiest week: {busiest} with {summary[busiest][0]} orders, median £{summary[busiest][1] / 100:.2f}")
