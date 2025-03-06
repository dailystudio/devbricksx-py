from dataclasses import dataclass

from devbricksx.common.json_convert import JsonConvert
from devbricksx.development.log import debug

DEFAULT_AI_SETTINGS_FILE = "private/ai.json"

@dataclass
class AISettings:
    open_ai_apikey: str
    open_ai_model: str
    dall_e_model: str
    sd_apikey: str
    bard_apikey: str
    bard_model: str
    reddit_client_id: str
    reddit_client_secret: str
    firebase_service_account_key: str
    firebase_storage_bucket: str

    def __str__(self):
        print_str = 'AI settings:\n' \
                    'OPEN.AI API Key: [%s]\nOPEN.AI Model: [%s]\nDALL·E Model: [%s]' \
                    'SD API Key: [%s]\n' \
                    'Bard API Key: [%s]\nBard Model: [%s]\n' \
                    'Firebase Service Account Key: [%s]\nFirebase Storage Bucket; [%s]'

        return print_str % (self.open_ai_apikey,
                            self.open_ai_model,
                            self.dall_e_model,
                            self.sd_apikey,
                            self.bard_apikey,
                            self.bard_model,
                            self.firebase_service_account_key,
                            self.firebase_storage_bucket)

aiSettings = {}

def init_ai_settings(ai_settings_file):
    global aiSettings
    debug(f"Loading AI settings from[{ai_settings_file}] ... ")
    aiSettings = JsonConvert.from_file(ai_settings_file, AISettings)
    debug("Loaded AI settings: {}".format(aiSettings))

def get_ai_settings():
    return aiSettings