from bs4 import BeautifulSoup
import argparse
import requests
import json
import os

splunk_host = os.getenv('SPLUNK_HOST')
service_username = os.getenv('SPLUNK_USERNAME')
service_password = os.getenv('SPLUNK_PASSWORD')

class Splunk:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()

    def init_login(self, endpoint):
        get_session = self.session.get(endpoint)
        soup = BeautifulSoup(get_session.text, 'html.parser')
        get_partials = soup.find(id='splunkd-partials',  type='text/json').contents[0]
        cval = json.loads(get_partials.strip())['/services/session']['entry'][0]['content']['cval']
        return cval

    def login(self):
        endpoint = f'{self.host}/en-US/account/login'
        header = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        login_form = { 'username': self.username, 
            'password': self.password, 'cval': self.init_login(endpoint) }
        self.session.post(endpoint, data=login_form, headers=header)
  
    def init_upload(self, endpoint):
        get_upload = self.session.get(endpoint)
        soup = BeautifulSoup(get_upload.text, 'html.parser')
        form_key = soup.find('input', {'name': 'splunk_form_key'}).get('value')
        form_state = soup.find('input', {'name': 'state'}).get('value')
        return form_key, form_state

    def upload(self, app_path):
        endpoint = f'{self.host}/en-US/manager/appinstall/_upload'
        form_key, form_state = self.init_upload(endpoint)
        base_filename = os.path.basename(app_path)
        multipart_upload = {
            'state': (None, form_state),
            'splunk_form_key': (None, form_key),
            'appfile': (base_filename, open(app_path, 'rb'), 'application/x-gzip')
        }
        upload_app = self.session.post(endpoint, files=multipart_upload)
        print(upload_app)

    def __enter__(self):
        self.login()
        return self
    
    def __exit__(self ,type, value, traceback):
        self.session.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload Splunk app')
    parser.add_argument('--path', type=str, help='Path to compressed Splunk app')
    args = parser.parse_args()
  
    with Splunk(splunk_host, service_username, service_password) as splunk:
        splunk.upload(args.path)
