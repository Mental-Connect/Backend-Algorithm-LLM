import json

with open("./config.json", encoding = "utf-8") as f:
    confrigations = json.load(f)


chatbot_confrigations = confrigations['chatbot_confrigations']
audio_to_text_transcriber = confrigations['audio_to_text_transcriber']

chatbot_model = chatbot_confrigations['model']
temprature = chatbot_confrigations['temprature']
session_keywords = chatbot_confrigations['session_keywords']
session_specific_prompt = chatbot_confrigations['session_specific_prompt']
generic_non_session_prompt = chatbot_confrigations['generic_non_session_prompt']

audio_text_model = audio_to_text_transcriber['model']
model_sampling_rate = audio_to_text_transcriber['model_sampling_rate']
kwargs = audio_to_text_transcriber['kwargs']
