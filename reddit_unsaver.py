import argparse
import random
import time

import requests


class RedditUnsaver:
    '''Class used to unsave all saved posts from a Reddit account.
    Use method `unsave` and provide your `username` and `password` to remove all saved posts.
    '''

    def __init__(self) -> None:

        self.session = requests.session()
        self.retries = 5
        self.headers = {
            "headers_login": {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en;q=0.5",
                "Connection": "keep-alive",
                "Content-Length": "",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "DNT": "1",
                "Host": "old.reddit.com",
                "Origin": "https://old.reddit.com",
                "Referer": "https://old.reddit.com/r/gaming/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-GPC": "1",
                "TE": "trailers",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            },
            "headers_saved": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en;q=0.5",
                "Connection": "keep-alive",
                "DNT": "1",
                "Host": "old.reddit.com",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "TE": "trailers",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            },
            "headers_unsave": {
                "Host": "old.reddit.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Accept": "*/*",
                "Accept-Language": "en-GB,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://old.reddit.com/user/hp_analyst/saved",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Content-Length": "",
                "Origin": "https://old.reddit.com",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",
                "X-Modhash": "zrdaxgbn46e0a6a338979ca2b41d9011da4d811d9143823a57"
            }
        }


    def _get_request_with_retries(self, url: str, headers: dict[str,str], acceptable_codes: list) -> requests.Response | None:
        '''Perform request with retries if the request status code is not in the provided list and return the response.'''

        retries = self.retries
        r = self.session.get(url, headers=headers, stream=True)
        while retries and r.status_code not in acceptable_codes:
            retries -= 1
            time.sleep(2 - random.random())
            r = self.session.get(url, headers=headers, stream=True)
        if r.status_code not in acceptable_codes:
            raise ConnectionError("Response status code not in list.")
        return r


    def _login(self, username: str, password: str) -> requests.Response:
        '''Logs in the user on Reddit for the session and returns the response.'''

        self.headers["headers_login"]["Content-Length"] = str(41 + len(username) + len(password))
        payload_login = {
            "op" : "login-main",
            "user" : f'{username}',
            "passwd" : f'{password}',
            "api_type" : "json"
        }
        login_url = f'https://old.reddit.com/api/login/{username}'

        return self.session.post(login_url, data=payload_login, headers=self.headers["headers_login"])
    

    def unsave(self, username: str, password: str) -> None:
        '''Unsaves all saved posts from Reddit account with provided credentials.'''

        login_response = self._login(username, password)
        if login_response.status_code != 200:
            print("Error logging in! Please check provided credentials. Exiting...")
            return

        unsave_url = "https://old.reddit.com/api/unsave"
        finished = False
        after = ""

        while not finished:
            saved_url = f'https://old.reddit.com/user/{username}/saved.json'
            try:
                saved_res = self._get_request_with_retries(saved_url, self.headers["headers_saved"], [200]).json()
            except ConnectionError:
                print("Connection error getting the saved list, please try again later.")
                return
            
            self.headers["headers_unsave"]["X-Modhash"] = saved_res["data"]["modhash"]

            for post in saved_res["data"]["children"]:
                id = post["data"]["name"]
                payload_unsave = {"id": f"{id}"}
                self.headers["headers_unsave"]["Content-Length"] = f'{len(id) + 3}'

                unsave_response = self.session.post(unsave_url, data=payload_unsave, headers=self.headers["headers_unsave"])
                
                try:
                    title = post["data"]["title"]
                except KeyError:  # Comment
                    title = post["data"]["link_title"]
                if unsave_response.status_code == 200:
                    print(f'Unsaved "{title}".')
                else:
                    print(f'Unable to unsave "{title}".')
                
                time.sleep(2 - random.random())

            after = saved_res["data"]["after"]           
            if after is None:
                finished = True

if __name__ == "__main__":
    
    unsaver = RedditUnsaver()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", type=str, help="Reddit username.", required=True)
    parser.add_argument("-p", "--password", type=str, help="Reddit password.", required=True)
    args = parser.parse_args()
    
    username = args.username
    password = args.password

    unsaver.unsave(username, password)