import os
import json

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.json')

with open(config_path, encoding = "utf-8") as f:
    confrigations = json.load(f)


chatbot_confrigations = confrigations['chatbot_confrigations']
audio_to_text_transcriber = confrigations['audio_to_text_transcriber']
database_information = confrigations['database_information']

chatbot_model = chatbot_confrigations['model'] # Name code for other models: glm-4-plus, glm-4-0520, glm-4, glm-4-air, glm-4-airx, glm-4-long, glm-4-flash
temprature = chatbot_confrigations['temprature']
session_keywords = chatbot_confrigations['session_keywords']
session_specific_prompt = chatbot_confrigations['session_specific_prompt']
generic_non_session_prompt = chatbot_confrigations['generic_non_session_prompt']

audio_text_model = audio_to_text_transcriber['model']
model_sampling_rate = audio_to_text_transcriber['model_sampling_rate']
kwargs = audio_to_text_transcriber['kwargs']

client_uri = database_information['client_uri']
database_name = database_information['database_name']
collection = database_information['collection']