
# Heatmap of revenue depending on application type and customer age

_This is a demo notebook that can be used to explore Contiamo Labs. It uses a demo databases created by Contiamo and representating transaction information for a mobile app retailer_


```python
import pandas as pd
import contiamo

import seaborn as sns
import numpy as np
```

### Query data into Contiamo


```python
transactions = %contiamo query query:sql:48590597:411:g71GXzJjsx4Uvad11ouKjoYbQUNNPy-qRMKkBNZfyx4
customers = %contiamo query query:sql:48590597:441:MG5W2dMjXzYgsHsgdQYzmhv44dxEQX2Lodu5Uh2Hx_s
applications = %contiamo query query:sql:48590597:442:-gz3nbw1fdmtSXkD4zGNA-cVa7s6sQtRn8upCSn6uys            
```

### Selecting data from the customers table


```python
df1 = pd.DataFrame ({
        'Age' : customers['Field age'],
        'Customer id' : customers['Field customer id']
    })
```

### Selecting data from the transactions table


```python
df2 = pd.DataFrame ({
        'Revenue' : transactions['Field app price'],
        'Application type' : transactions['Field app type'],
        'Customer id' : transactions['Field customer id']
        })
```

### Merging tables, correcting types, group by Application type and Age 


```python
df = df2.set_index('Customer id').join(df1.set_index('Customer id'))
df['Revenue']=pd.to_numeric(df['Revenue'])
df = df.groupby(['Application type','Age'], as_index=False).sum()
```

### Convert table into matrix


```python
df = df.pivot_table('Revenue', 'Application type', 'Age', fill_value=0)
```




### Display heatmap


```python
sns.set_context("poster")  # display large charts
sns.heatmap(table, annot=True)
```

