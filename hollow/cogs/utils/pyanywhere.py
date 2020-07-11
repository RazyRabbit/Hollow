from .text import replace_escapes
import requests

api_url = 'https://www.pythonanywhere.com/api/v0'

def get(url, token):
    return requests.get(f'{api_url}{url}', headers={'Authorization': f'Token {token}'})

def post(url, token, **data):
    return requests.post(f'{api_url}{url}', data, headers={'Authorization': f'Token {token}'})

class Console:
    def __init__(self, client, name, **about):
        self.client = client
        self.about = about
        self.name = name
    
    def __getattr__(self, name):
        return self.about[name]

    def __repr__(self):
        return f'<{type(self).__name__} {self.name.title()}>'
    
    def send(self, *inputs, end='\n'):
        for input in inputs:
            post(f'/user/{self.client.username}/consoles/{self.id}/send_input/', self.client.token, input=f'{input}{end}')

        return inputs

    @property
    def output(self):
        if (response := get(f'/user/{self.client.username}/consoles/{self.id}/get_latest_output/', self.client.token)).status_code == 200:
            return replace_escapes(response.json()["output"], '\n')

        return

class Client:
    def __init__(self, username, token):
        self.username = username
        self.token = token
    
    @property
    def consoles(self):
        if (response := get(f'/user/{self.username}/consoles/', self.token)).status_code == 200:
            return [Console(self, **about) for about in response.json()]
        
        return []
    
    @property
    def console(self) -> Console:
        if consoles := self.consoles:
            return consoles[0]

        return 
    
    @property
    def usage(self):
        if (response := get(f'/user/{self.username}/cpu/', self.token)).status_code == 200:
            return response.json()["daily_cpu_total_usage_seconds"]
        
        return 0.0