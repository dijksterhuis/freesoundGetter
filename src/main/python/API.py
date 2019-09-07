import freesound
import requests
import datetime
import sys
import os
import string

class OAuth:
    def __init__(self, client_id, client_secret):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__auth_url = "https://freesound.org/apiv2/oauth2/authorize/?client_id={}&response_type=code".format(client_id)
        self.__auth_code = None
        self.access_token = None
        self.token_type = None
        
    def oauth(self):
        self.token_type = "oauth"
        self._get_auth_code()
        self._get_oauth_token()
        return self
        
    def _get_auth_code(self):
        terminal_printout = "-" * 30
        terminal_printout += "\nPlease visit: {}".format(self.__auth_url)
        terminal_printout += " \n ... Then follow the instruction to get an authorization code..."
        terminal_printout += " \n ... Then paste it here: "
        self.__auth_code = input(terminal_printout)
        return self
    
    def _get_oauth_token(self, auth_code=None):
        post_data = {
            "client_id" : self.__client_id,
            "client_secret" : self.__client_secret,
            "grant_type" : "authorization_code",
            "code": auth_code if auth_code else self.__auth_code
        }
        r = requests.post("https://freesound.org/apiv2/oauth2/access_token/", data = post_data)
        self.access_token = access_token = r.json()['access_token']
        return self


class ThrottlingException(Exception):
    pass

class Throttling:
    def __init__(self, daily_limit=None, hourly_limit=None, minute_limit=None, rate_buffer=5):
        
        self.limit_daily = daily_limit - rate_buffer
        self.limit_hourly = hourly_limit - rate_buffer
        self.limit_minute = minute_limit - rate_buffer
        
        self.count_daily = 0
        self.count_hourly = 0
        self.count_minute = 0
        
        self.last_check = datetime.datetime.now()
    
    def add_one(self):
        
        self.last_check = datetime.datetime.now()
        
        self.count_daily += 1
        self.count_hourly += 1
        self.count_minute += 1
        
        self.__check_rates()
        
        if self.count_daily == self.limit_daily: return ThrottlingException("Daily limit reached.")
        if self.count_hourly == self.limit_hourly: return ThrottlingException("Hourly limit reached.")
        if self.count_minute == self.limit_minute: return ThrottlingException("Minute limit reached.")
    
    def __check_rates(self):
        pass

class FreesoundWrapper:
    def __init__(self, auth):
        self.cli = freesound.FreesoundClient()
        self.__results_pager = None
        self.cli.set_token(auth.access_token, auth.token_type)
    
    def search(self, query):
        if query.text and query.filters:
            self.__results_pager = self.cli.text_search(
                query = query.text,
                filter = query.filters,
                fields = query.fields,
                sort = query.sort,
                group_by_pack = query.group_packs
            )
        elif query.text:
            self.__results_pager = self.cli.text_search(
                query = query.text,
                fields = query.fields,
                sort = query.sort,
                group_by_pack = query.group_packs
            )
        elif query.filters:
            self.__results_pager = self.cli.text_search(
                filter = query.filters,
                fields = query.fields,
                sort = query.sort,
                group_by_pack = query.group_packs
            )
        else:
            self.__results_pager = self.cli.text_search(
                fields = query.fields,
                sort = query.sort,
                group_by_pack = query.group_packs
            )
        return self
    
    def get_all(self, dl_dir):
        
        total_results = self.__results_pager.count
        page_count, sounds_count = (total_results // 15) + 1, 0
        
        check_string = "There are {a} total results to download...".format(a=total_results)
        check_string += "\nAre you sure you want to continue? [Y/N]: "
        check = input(check_string)
        
        if check == "N": return False
        
        print(
            "{a} total results to get.\n{b} total pages.\nStarting download run...\n{c}\n".format(
                a=total_results, 
                b=page_count, 
                c="-"*50
            )
        )
        
        for page_idx in range(page_count):
            
            for sound in self.__results_pager:
                
                sys.stdout.write(
                    "\rGetting sound {a} of {b}... Sound ID: {c} Sound name: {d}{e}".format(
                        a = sounds_count, 
                        b = total_results,
                        c = sound.id,
                        d = sound.name,
                        e = " "*30
                    )
                )
                sys.stdout.flush()
                self.get_sound(sound, dl_dir)
                sounds_count += 1
                
            self.__results_pager = self.__results_pager.next_page()
    
    def get_sound(self, sound, path_name):
        if not os.path.exists(path_name):
            raise Exception("\nDownload directory not found: {}".format(dl_dir))
        
        sound_name = self.__clean_name(sound.name, sound.type)
        filename = "{a}___{b}.{c}".format(
            a = sound_name,
            b = sound.id, 
            c = sound.type
        )
        
        if filename not in os.listdir(path_name):
            sound.retrieve(path_name, filename)
    
    @staticmethod
    def __clean_name(name, filetype):
        
        for s in string.punctuation.replace(".", "").replace("_", ""):
            name = name.replace(s, "")
            
        name = name.replace(" - ", "_").\
                    replace(" ","_").\
                    replace("-","_")
        
        name = name.rstrip(".{}".format(filetype))
        name = name.rstrip(".{}".format(filetype.upper()))
        
        return name
 