import os
import json

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.json')

with open(config_path, encoding = "utf-8") as f:
    configuration = json.load(f)


# Chatbot configuration
chatbot_configuration = configuration['chatbot_configuration']
chatbot_model = chatbot_configuration['model'] # Name code for other models: glm-4-plus, glm-4-0520, glm-4, glm-4-air, glm-4-airx, glm-4-long, glm-4-flash
chatbot_temperature = chatbot_configuration['temperature']
