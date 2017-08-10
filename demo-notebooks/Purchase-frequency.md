
# Purchase frequency

In this notebook you will see how to create a table grouping transactions information by customers’ purchase frequency. This is possible thanks to functions functions from the pandas librairie such as df.groupby() and df.cut().


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

### Selecting data from march 2017


```python
transactions = transactions.loc[transactions['Field transaction date date'] >= 20170301]
transactions = transactions.loc[transactions['Field transaction date date'] <= 20170331]

```


```python
df = pd.DataFrame({
        'customer_id' : transactions['Field customer id'],
        'revenue' : pd.to_numeric(transactions['Field app price']),
        'n_of_purchases' : [1]*len(transactions)
    })
df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>customer_id</th>
      <th>n_of_purchases</th>
      <th>revenue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2F65fA7Cd10cbFFD</td>
      <td>1</td>
      <td>4.99</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2F65fA7Cd10cbFFD</td>
      <td>1</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2F65fA7Cd10cbFFD</td>
      <td>1</td>
      <td>0.99</td>
    </tr>
    <tr>
      <th>5</th>
      <td>44dEeeb9eEF3ff64</td>
      <td>1</td>
      <td>14.99</td>
    </tr>
    <tr>
      <th>8</th>
      <td>7FeFbCBe6147a9ff</td>
      <td>1</td>
      <td>0.19</td>
    </tr>
  </tbody>
</table>
</div>



### Creation of an intermediate table



```python
total_users = df['customer_id'].nunique()

#CREATION OF AN INTERMEDIATE TABLE

#Grouping by customer id
pf = df.groupby('customer_id').agg({
        'revenue' : 'sum',
        'n_of_purchases' : 'sum'
    }).reset_index()

#Selection of data to create 'No. of Purchases', 'No. of UAUs'and 'Total Revenue'columns 
x = pf.groupby('n_of_purchases').agg({
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
      <td>13656</td>
      <td>108827.53</td>
      <td>45.504832</td>
      <td>13656</td>
    </tr>
    <tr>
      <th>1</th>
      <td>(1, 2]</td>
      <td>4848</td>
      <td>67683.44</td>
      <td>16.154615</td>
      <td>9696</td>
    </tr>
    <tr>
      <th>2</th>
      <td>(2, 3]</td>
      <td>2697</td>
      <td>60800.95</td>
      <td>8.987004</td>
      <td>8091</td>
    </tr>
    <tr>
      <th>3</th>
      <td>(3, 5]</td>
      <td>1734</td>
      <td>40058.73</td>
      <td>5.778074</td>
      <td>6936</td>
    </tr>
    <tr>
      <th>4</th>
      <td>(3, 5]</td>
      <td>1621</td>
      <td>47674.62</td>
      <td>5.401533</td>
      <td>8105</td>
    </tr>
  </tbody>
</table>
</div>



### Creation of final table


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

y
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>n_of_purchases</th>
      <th>n_of_users</th>
      <th>percentage_of_users</th>
      <th>revenue</th>
      <th>average_revenue_per_user</th>
      <th>total_transactions</th>
      <th>average_transaction_price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>13656</td>
      <td>45.504832</td>
      <td>108827.53</td>
      <td>7.969210</td>
      <td>13656</td>
      <td>7.969210</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>4848</td>
      <td>16.154615</td>
      <td>67683.44</td>
      <td>13.961106</td>
      <td>9696</td>
      <td>6.980553</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2697</td>
      <td>8.987004</td>
      <td>60800.95</td>
      <td>22.543919</td>
      <td>8091</td>
      <td>7.514640</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4-5</td>
      <td>3355</td>
      <td>11.179607</td>
      <td>87733.35</td>
      <td>26.150030</td>
      <td>15041</td>
      <td>5.832947</td>
    </tr>
    <tr>
      <th>4</th>
      <td>6-8</td>
      <td>2160</td>
      <td>7.197601</td>
      <td>67805.61</td>
      <td>31.391486</td>
      <td>15094</td>
      <td>4.492223</td>
    </tr>
    <tr>
      <th>5</th>
      <td>9-13</td>
      <td>1501</td>
      <td>5.001666</td>
      <td>52535.05</td>
      <td>35.000033</td>
      <td>16605</td>
      <td>3.163809</td>
    </tr>
    <tr>
      <th>6</th>
      <td>14-21</td>
      <td>927</td>
      <td>3.088970</td>
      <td>43901.67</td>
      <td>47.358867</td>
      <td>16169</td>
      <td>2.715175</td>
    </tr>
    <tr>
      <th>7</th>
      <td>22-34</td>
      <td>575</td>
      <td>1.916028</td>
      <td>41079.43</td>
      <td>71.442487</td>
      <td>15946</td>
      <td>2.576159</td>
    </tr>
    <tr>
      <th>8</th>
      <td>35-55</td>
      <td>200</td>
      <td>0.666445</td>
      <td>23325.54</td>
      <td>116.627700</td>
      <td>9070</td>
      <td>2.571724</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Above 55</td>
      <td>91</td>
      <td>0.303232</td>
      <td>43065.94</td>
      <td>473.252088</td>
      <td>20571</td>
      <td>2.093527</td>
    </tr>
  </tbody>
</table>
</div>



We can thus observe that the maximum revenue is generated by people buying apps only once a month (low frequency buyers). We can now identify buying behaviours according to purchase frequency. 
