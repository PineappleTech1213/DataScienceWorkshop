# Calculate Element's Atomic Weight Percentage in Alloy.

This is a little practice in using Python for data engineering in material science. The goal is to calculate the atomic weight percentages of elemtns in alloy according to the periodic table.

First let's read in the data:

```{python}
import pandas as pd
#read in a period table
periodic_table = pd.read_csv("atomic_weight.csv", header=None)

periodic_table.columns = ['elements', 'atomic_weight']
#have a look at it
print(periodic_table.head(10))
#read in a table of alloy's element percentage
example = pd.read_csv("at.csv", header=0)

```
Now we need to know, what elements are in the alloy combo? So we extract them from the example dataset.
This is a good coding practice coz you never know when the element combos are gonna change right? So you just take them out of the original data.

```{python}
element = example.columns

elemental_table = periodic_table[[x in element for x in periodic_table["elements"]]].reset_index()
print(elemental_table)
#order the elemtns according to the periodic table selection
ordered_example = example[elemental_table['elements']]
ordered_example_2 = pd.DataFrame()
```
Even the student in material science knows that he needs to write a loop to do it efficiently, and this is how we do it. 
First, we calculated each element's atomic weight according to its percentage
Second, we calculated the sum of those weighted weights.
Lastly, we calculated the weight percentage.
```{python}
for i in range(len(element)):
    weight = float(elemental_table['atomic_weight'][i])
    name = elemental_table['elements'][i]
    col_name = name + '_weight'
    ordered_example_2[col_name] = ordered_example[name]*weight

for j in range(len(ordered_example_2)):
    a = sum(ordered_example_2.iloc[j])
    ordered_example_2.iloc[j] = ordered_example_2.iloc[j]/a
 # store the data
ordered_example_2.to_csv('result.csv', mode="w+")
```
This is an example of a complete ETL (extract, transform, load) process, but in a simple and elegant way.

### END
