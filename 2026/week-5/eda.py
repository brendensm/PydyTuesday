import pandas as pd
import pydytuesday

# Download files from the week, which you can then read in locally
pydytuesday.get_date('2026-02-03')

ep = pd.read_csv('edible_plants.csv')

ep
