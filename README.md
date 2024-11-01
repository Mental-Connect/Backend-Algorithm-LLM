# Backend-Algorithm-LLM

Python version: Python 3.12.2

There are Two main Models Running
1) Audio Transcription
2) Text Generation

1) Audio Transcritption Model
   a) Paraformer-zh (Non Streaming) --> Correction and offline Subject Identification. 
   b) Parafomer-zh (Streaming) --> Real Time Transcription

Download Link: https://huggingface.co/funasr/paraformer-zh

2) Text Generation Model(Question answering Chatbot):

 Zhipu AI: [ZHIPU AI OPEN PLATFORM (bigmodel.cn)](https://bigmodel.cn/dev/howuse/model)

How to Run Fast Api Service (DEMO):
   uvicorn Service.main:app --reload


Confrigation Settings:

1) ChatBot Confrigations:

   a) Model: Model used for question answering
   b) Temprature: Tell how much model deviate from original question context, 1 mean greater deviation while 0 is no deviation
   c) session_kwargs: Those words which if present in the context provided to model than it will answer the question if not present then it will not response
   d) session_specific_prompt, generic_non_session_prompt, text_speaker_identification: These are the prompt according to which model can behave 

2) Audio Transcriber Settings:
   a) streaming_model, non_streaming_model: Names of main model used to transcription
   b)streaming_model_revision: The version of model used, change if new version come
   c)streaming_configrations: Model standard confrigations, for these detailed analysis visit website: https://modelscope.cn/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online/summary
   d) kwargs: device: cpu or cuda
   e)vad_model: To identify the starting and ending point of audio and also give time stamps
   f)vad_kwargs: max_single_segment_time: it tells how much audio can be given to paraformer at one time
   g) punc_model: correct the punctuation
   h)spk_model: Subject Identification
   I)Audio_transcription_files, online_streaming_files, online_correction_files: Files to store the temporary audio files
   j) model_sampling_rate: Model accepted Sampling rate 

3) Docker Uploading Issue:
When uploading on docker usually soundfile or librosa give error of ffmpeg, this is due to missing library which cannot be installed through docker-requirement file. After creating the docker image and running container, following linux commands are used to download

docker exec -it <container_id_or_name> /bin/bash

After entering the container, write following command

apt-get update && \
apt-get install -y ffmpeg && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*
