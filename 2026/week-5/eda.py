import textwrap
import pandas as pd
import pydytuesday
from plotnine import (
    ggplot, aes, geom_col, coord_flip, labs,
    theme_minimal, theme, element_rect, element_blank, element_text,
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

# =============================================================================
# Create new cultivation labels with (N=X) format
# =============================================================================
cult_totals['cultivation_label'] = (
    cult_totals['cultivation'] + ' (N=' + cult_totals['total_n'].astype(str) + ')'
)

# Create mapping from original cultivation to new label
label_map = dict(zip(cult_totals['cultivation'], cult_totals['cultivation_label']))

# Apply to cult_wat
cult_wat['cultivation_label'] = cult_wat['cultivation'].map(label_map)

# Create ordered categories for the new labels (matching original order)
cultivation_label_order = [label_map[c] for c in cultivation_order]

cult_wat['cultivation_label'] = pd.Categorical(
    cult_wat['cultivation_label'], 
    categories=cultivation_label_order, 
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
    ggplot(cult_wat2, aes(x="cultivation_label", y="percent", fill="water"))
    + geom_col()
    + coord_flip()
    + scale_y_continuous(
        labels=lambda l: [f"{int(v)}%" for v in l]
    )
    + scale_fill_manual(values=likert_colors)
    + guides(fill=guide_legend(reverse=True))
    + labs(
        title="Plant water needs by cultivation class",
        subtitle=textwrap.fill(subtitle_text, width=65),
        caption="Brenden Smith | TidyTuesday 2026, Week 5",
        fill=""
    )
    + theme_minimal(base_size = 14, base_family="Georgia")
    + theme(
        plot_subtitle = element_text(lineheight = 1),
        plot_title = element_text(fontweight = "bold"),
        legend_position="bottom",
        axis_title=element_blank(),
        plot_title_position="plot",
        plot_background=element_rect(fill="#FAF9F6", color="#FAF9F6"),
        panel_background=element_rect(fill="#FAF9F6"),
        panel_grid_major=element_blank()
    )
)

fig.save("output.png", dpi=300)
