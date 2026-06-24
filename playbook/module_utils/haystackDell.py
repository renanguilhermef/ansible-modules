##
# This module is used to connect on haystack using pyhaystack
# Class Skyspark EMS to connect on the entrocim application
#!/usr/bin/python3
##
import pyhaystack
import hszinc
import urllib3

class haystackEMS:

    def __init__(self,hostname,project,api_user,api_password):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session = pyhaystack.connect('skyspark', uri='https://' + hostname,
                                project=project,
                                username=api_user,
                                password=api_password,http_args={'debug':True, 'tls_verify':False, 'insecure_requests_warning':False})
                                
    def about(self):
        return self.session.about()

    def eval(self,arg_expr):
        eval_grid = hszinc.Grid()
        eval_grid.column["expr"] = {}
        eval_grid.append({"expr": arg_expr})
        op = self.session._post_grid("eval", grid=eval_grid, callback=lambda *a, **kwa : None)
        return op.result

    def call(self,method,commit_grid):
        op = self.session._post_grid(method, grid=commit_grid, callback=lambda *a, **kwa : None)
        return op.result        
