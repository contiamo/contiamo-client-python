
# Purchase frequency

_In this notebook you will see how to create a table grouping transactions information by customers’ purchase frequency. This is possible thanks to functions functions from the pandas librairie such as df.groupby() and df.cut()._ 


```python
import pandas as pd
import contiamo
```

### Query data into Contiamo


```python
transactions = %contiamo query query:sql:48590597:411:g71GXzJjsx4Uvad11ouKjoYbQUNNPy-qRMKkBNZfyx4
customers = %contiamo query query:sql:48590597:441:MG5W2dMjXzYgsHsgdQYzmhv44dxEQX2Lodu5Uh2Hx_s
applications = %contiamo query query:sql:48590597:442:-gz3nbw1fdmtSXkD4zGNA-cVa7s6sQtRn8upCSn6uys            
```


```python
df = pd.DataFrame({
        'customer_id' : transactions['Field customer id'],
        'revenue' : pd.to_numeric(transactions['Field app price']),
        'n_of_purchases' : [1]*len(df['customer_id'])
    })
```

## Purchase frequency table

### Creation of an intermediate table



```python
total_users = df['customer_id'].nunique()

#CREATION OF AN INTERMEDIATE TABLE

#Selection of data to create 'No. of Purchases', 'No. of UAUs'and 'Total Revenue'columns 
x = df.groupby('n_of_purchases').agg({
    'customer_id': 'size',
    'revenue' : 'sum',
})

x = x.reset_index()

#Renaming columns
x.rename(columns = {'customer_id': 'n_of_users'}, inplace=True)

#Creation of '% of Total UAUs' and 'Total transations'columns
x['percentage_of_users'] = 100 * x['n_of_users'] / total_users

x['total_transactions'] = x['n_of_purchases'] * x['n_of_users']

#Creation of 'No. of Purchases' buckets 
x['n_of_purchases'] = pd.cut(x['n_of_purchases'], bins=[0,1,2,3,5,8,13,21,34,55,float('inf')]) 


x.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>n_of_purchases</th>
      <th>n_of_users</th>
      <th>revenue</th>
      <th>percentage_of_users</th>
      <th>total_transactions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>(0, 1]</td>
      <td>416878</td>
      <td>1.799473e+06</td>
      <td>1389.13029</td>
      <td>416878</td>
    </tr>
  </tbody>
</table>
</div>




```python
#CREATION OF FINAL TABLE

#Grouping data by 'No. of Purchases' buckets
y = x.groupby('n_of_purchases').agg({
    'revenue': 'sum',
    'n_of_users': 'sum',
    'percentage_of_users' : 'sum',
    'total_transactions': 'sum',
})

y = y.reset_index()


#Creation of 'Average revenue per user' and 'Average transaction price' colums
y['average_revenue_per_user'] = y['revenue'] / y['n_of_users']
y['average_transaction_price'] = y['revenue'] / y['total_transactions']


#Putting the colums in the right order
cols = ['n_of_purchases','n_of_users', 'percentage_of_users', 'revenue', 'average_revenue_per_user', 'total_transactions', 'average_transaction_price']
y = y[cols]

#Renaming the 'No. of Purchases' buckets
y['n_of_purchases']=y['n_of_purchases'].astype(str)
y = y.replace({'n_of_purchases': {
            '(0, 1]': '1',
            '(1, 2]' : '2',
            '(2, 3]' : '3', 
            '(3, 5]' : '4-5',
            '(5, 8]' : '6-8',
            '(8, 13]' : '9-13',
            '(13, 21]' : '14-21',
            '(21, 34]' : '22-34',
            '(34, 55]' : '35-55',
            '(55, inf]' : 'Above 55',
        }})
```
