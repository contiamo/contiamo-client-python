import client as contiamo

# Authenticated access
contiamo_client = contiamo.Client('Jvzbw4E9yQ7yzYvow7FU', api_base='http://localhost:3000/api')

# Project methods
print('### Getting project')
project = contiamo_client.Project.retrieve('48590121')

print('### Getting apps')
print(project.App.list())

# Dashboards
print('### Getting dashboards')
dashboards = project.Dashboard.list()
dashboard = project.Dashboard.retrieve(dashboards[0]['id'])
print(dashboard)

# Widgets
# print(dashboard.Widget.list())
