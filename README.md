# Contiamo API library

[![Build Status](https://travis-ci.org/contiamo/contiamo-client-python.svg?branch=master)](https://travis-ci.org/contiamo/contiamo-client-python)

The `contiamo` API library in Python provides access to Contiamo's API functionality through a simple interface.

_In order to run the examples below, you need to get the API key and resource tokens from the project._

### Installation

```
pip install contiamo
```

### Using the contiamo client

The contiamo client gives authenticated access to a project's resources. You can view and modify existing resources, and create new ones.

```python
import contiamo

# Client with authenticated access
contiamo_client = contiamo.resources.Client(api_key)

# Instantiate project
project = contiamo_client.Project('48590558')

# Get apps
apps = project.App.list()
print(apps)

# Get dashboard
dashboards = project.Dashboard.list()
dashboard = project.Dashboard.retrieve(dashboards[0]['id'])
print(dashboard)
# Get widgets
widgets = dashboard.Widget.list(instantiate=True)
print(widgets)

# Execute SQL query
df = project.query_sql(666571902, 'select * from contract_contract limit 1;')
print(df)
```

### Using the public and data modules

The public and data modules let you execute published queries and upload data to data contracts.

```python
# Execute published query
query_id = 'query:olap:48590558:34368:' + query_token
print(contiamo.public.query(query_id))

# Use data client
contract_id = 'contract:48590558:666571902:experimental'
data_client = contiamo.data.DataClient(contract_id, contract_token)
# df = {'a': [1,2,3,4], 'b': [5,6,7,8]}
import pandas as pd
df = pd.DataFrame({'a': [1,2,3,4], 'b': [5,6,7,8]})
print(data_client.purge())
print(data_client.discover(df))
print(data_client.upload(df))
# df.to_csv('test.csv')
# print(data_client.upload(filename='test.csv'))
```

Possible alternatives not using the `pandas` library are commented out above.

### Available operations

| Resource  | Create | List | Fetch / Retrieve | Modify | Destroy | Other actions | Child Resources |
| --------- | ------ | ---- | ---------------- | ------ | ------- | ------------- | --------------- |
| client    |        |      |                  |        |         |               | project         |
| project   |        |      |                  |        |         | query_sql     | app, dashboard  |
| dashboard | x      | x    | x                | x      |         |               | widget          |
| widget    | x      | x    | x                | x      |         |               |                 |
| app       |        | x    | x                |        |         |               | contract        |
| contract  | x      | x    | x                | x      | x       |               |                 |

### Support

support@contiamo.com
