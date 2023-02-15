# Data Science in Material Science

## About the dataset
Here we have two datasets: 1. a periodic table dataset with the names of elements and its atomic weight; 2. a table containing different combinations of certain elements. Each row is a combination of elements in different percentages. All the percentages in one row sum up to 1. 

Here our GOAL is to compute the atomic weight percentage of each element in each combination. 

## How to analyze them in Python

First, identify the data type you need to contain those data. Here a pandas DataFrame is our best choice. I believe you can use other data types but for beginners it is easier to understand. It is good for computing based on columns and individual values.

```{python}
import pandas as pd

periodic_table = pd.read_csv("atomic_weight.csv", header=None)

periodic_table.columns = ['elements', 'atomic_weight']

example = pd.read_csv("at.csv", header=0)

element = example.columns
print(element)

```

The calculation is quite simple. Let p be the percentage of one element, w be its atomic weight, and we are tring to get wp: its weight percentage.
$$
\begin
wp_i = (w_i*p_i)/sum_k(w_k*p_k), for k  = 1, 2, ..., n
\end
$$
Now we need to manipulate the combo element order so that the elements selected are in an order according to the periodic table (it is just better for later iterations). 
All we need in the end are the two tables: 1. the periodic table of the needed elements; 2. the element percentage table.
An important reminder is that you need to store some interval data such as the partial atomic weight values. After several experiments, we decided to store them in a new dataframe and thus the establishment of a new dataframe. 
Another trick here when generating new columns in a dataframe is that you take the original column name, add a suffix and there you have a new column name. It is better to create a new column than assigning values to an existing column. You will get it once you try it all.

```{python}
elemental_table = periodic_table[[x in element for x in periodic_table["elements"]]].reset_index()
print(elemental_table)
ordered_example = example[elemental_table['elements']]
ordered_example_2 = pd.DataFrame()

#iterate through each column of elements to obtain the total atomic weight of each element in one combo
for i in range(len(element)):
    weight = float(elemental_table['atomic_weight'][i])
    name = elemental_table['elements'][i]
    col_name = name + '_weight'
    ordered_example_2[col_name] = ordered_example[name]*weight
#sum up all the atomic weight and divide it with each atomic weight to get the weight percentage;
for j in range(len(ordered_example_2)):
    a = sum(ordered_example_2.iloc[j])
    ordered_example_2.iloc[j] = ordered_example_2.iloc[j]/a
#outout the result.
ordered_example_2.to_csv('result.csv', mode="w+")
```
