import plotnine as p9
from plotnine.data import mtcars

# Example: Scatter plot with cividis color mapping
(
    p9.ggplot(mtcars, p9.aes(x='wt', y='mpg', color='factor(gear)'))
    + p9.geom_point()
    + p9.scale_color_viridis()
    + p9.theme_minimal()
)   
