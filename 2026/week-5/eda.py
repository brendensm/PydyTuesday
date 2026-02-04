import textwrap
import pandas as pd
import pydytuesday
from plotnine import (
    ggplot, aes, geom_col, geom_text, coord_flip, labs,
    theme_minimal, theme, element_rect, element_blank,
    scale_y_continuous, scale_fill_manual, guides, guide_legend
)

# =============================================================================
# Load data
# =============================================================================
pydytuesday.get_date('2026-02-03')
ep = pd.read_csv('edible_plants.csv')

# =============================================================================
# Clean data
# =============================================================================
water_levels = ["Very Low", "Low", "Medium", "High", "Very High"]

ep['cultivation'] = ep['cultivation'].replace('Brassicas', 'Brassica')
ep['water'] = pd.Categorical(
    ep['water'].str.lower().str.title(),
    categories=water_levels,
    ordered=True
)

# =============================================================================
# Aggregate: percent of each water level by cultivation class
# =============================================================================
cult_wat = (
    ep
    .groupby(["cultivation", "water"], observed=False)  # include all categorical levels
    .size()
    .reset_index(name="count")
    .fillna(0)  # just in case
    .assign(
        percent=lambda x: x.groupby("cultivation")["count"]
                          .transform(lambda y: y / y.sum() * 100)
    )
)

# Sample size labels
cult_totals = (
    cult_wat
    .groupby("cultivation")["count"]
    .sum()
    .reset_index(name="total_n")
)

cult_wat = cult_wat.merge(cult_totals, on="cultivation")

# =============================================================================
# Sort cultivation classes by water intensity (High + Very High %)
# =============================================================================
cultivation_order = (
    cult_wat[cult_wat['water'].isin(['Very High', 'High'])]
    .groupby('cultivation')['percent']
    .sum()
    .sort_values(ascending=True)
    .index
    .tolist()
)

cult_wat['cultivation'] = pd.Categorical(
    cult_wat['cultivation'], 
    categories=cultivation_order, 
    ordered=True
)

cult_totals['cultivation'] = pd.Categorical(
    cult_totals['cultivation'],
    categories=cultivation_order,
    ordered=True
)

# =============================================================================
# Plot
# =============================================================================
likert_colors = [
    "#8c510a",  # Very Low (brown)
    "#d8b365",  # Low
    "#b8b8b8",  # Medium (gray)
    "#5ab4ac",  # High
    "#01665e"   # Very High (dark teal)
]

subtitle_text = (
    "Among 146 edible plant species from the Edible Plant Database, "
    "created by the European Citizen Science GROW Observatory."
)

cult_wat2 = cult_wat[cult_wat["count"] > 0]

fig = (
    ggplot(cult_wat2, aes(x="cultivation", y="percent", fill="water"))
    + geom_col()
    + geom_text(
        data=cult_totals,
        mapping=aes(x="cultivation", y=-4, label="total_n"),
        inherit_aes=False,
        size=8,
        ha="left"
    )
    + coord_flip()
    + scale_y_continuous(
        labels=lambda l: [f"{int(v)}%" for v in l]
    )
    + scale_fill_manual(values=likert_colors)
    + guides(fill=guide_legend(reverse=True))
    + labs(
        title="Plant water needs by cultivation class",
        subtitle=textwrap.fill(subtitle_text, width=75),
        caption="TidyTuesday 2026, Week 5",
        fill=""
    )
    + theme_minimal()
    + theme(
        legend_position="bottom",
        axis_title=element_blank(),
        plot_title_position="plot",
        plot_background=element_rect(fill="#FAF9F6", color="#FAF9F6"),
        panel_background=element_rect(fill="#FAF9F6"),
        panel_grid_major=element_blank()
    )
)

fig.save("output.png", dpi=300)
