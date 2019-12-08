from azureml.core import Workspace

ws = Workspace.from_config()
print(ws.webservices['tt-seer'].get_logs())