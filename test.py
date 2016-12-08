import contiamo

# import contiamo.resources
# import contiamo.public
# import contiamo.data

# Authenticated access
contiamo_client = contiamo.resources.Client('Jvzbw4E9yQ7yzYvow7FU', api_base='http://localhost:3000/api')

# Instantiate project
project = contiamo_client.Project('48590121')

# # Apps
# print('### Getting apps')
# apps = project.App.list(instantiate=False)
# print(apps[:2])
# apps = project.App.list(instantiate=True)
# print(type(apps[0]))
# print(apps[:2])

# # Dashboards
# print('### Getting dashboards')
# dashboards = project.Dashboard.list()
# print(dashboards[0]['id'])
# dashboard = project.Dashboard.retrieve(dashboards[0]['id'])
# print(dashboard)

# print('### Getting query data')
# print(contiamo.public.query('query:olap:48590121:25612:FL2fmx8_XJ_Rx6EbZvoq2s6bPzTXaxPTMWKxSs_A8Bk'))

# print('### Sending data to contract')
# contract_id = 'contract:48590121:666570779:test4'
# token = 'x2w54rto4kqj4me3zeyp56d2nhslqns5'
# data_client = contiamo.data.DataClient(contract_id, token)
# import pandas as pd
# df = pd.DataFrame({'a': [1,2,3,4], 'b': [5,6,7,8]})
# print(data_client.discover(df))
# print(data_client.upload(df))
# df.to_csv('test.csv')
# print(data_client.upload(filename='test.csv'))
# print(data_client.purge())

# Widgets
# print(dashboard.Widget.list())

print('### Testing errors')
# # connection error
# contiamo_client = contiamo.resources.Client('accesstoken', api_base='http://api.some-name.com')
# project = contiamo_client.Project('48590121')
# dashboard = project.Dashboard.retrieve('345')
# # auth error
# contiamo_client = contiamo.resources.Client('wrongaccesstoken', api_base='http://localhost:3000/api')
# project = contiamo_client.Project('48590121')
# dashboard = project.Dashboard.retrieve('345')
# not found error
contiamo_client = contiamo.resources.Client('Jvzbw4E9yQ7yzYvow7FU', api_base='http://localhost:3000/api')
project = contiamo_client.Project('48590121')
dashboard = project.Dashboard.retrieve('345')
dashboard = project.Dashboard.retrieve('123456789')