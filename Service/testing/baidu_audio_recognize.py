import threading
import time
import pyaudio
import websocket
import json
import logging
import uuid
import wave
import numpy as np

from scipy.io import wavfile
from scipy.signal import resample


# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# WebSocket 配置
uri = "ws://vop.baidu.com/realtime_asr" + "?sn=" + str(uuid.uuid1())


# WebSocket 回调函数
def on_open(ws):
    """
    连接后发送数据帧
    :param websocket.WebSocket ws:
    :return:
    """
    def run(*args):
        """
        发送数据帧
        :param args:
        :return:
        """
        send_start_params(ws)
        send_audio(ws)
        send_finish(ws)
        logger.debug("thread terminating")

    threading.Thread(target=run).start()

def on_message(ws, message):
    logger.info(f"Received message: {message}")

def on_error(ws, error):
    logger.error(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.info(f"Closed connection with status code {close_status_code}")



# 发送开始参数
def send_start_params(ws):
    """
    开始参数帧
    :param websocket.WebSocket ws:
    :return:
    """
    req = {
        "type": "START",
        "data": {
            "appid": 116386783,
            "appkey": "u2vZBUqEDbl8u22HxWLZAksQ",
            "dev_pid": 15372,
            "cuid": "yourself_defined_user_id",
            "sample": 16000,
            "format": "pcm"
        }
    }
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)
    logger.info("send START frame with params:" + body)


# 发送音频数据
def send_audio(ws):
    """
    发送二进制音频数据，注意每个帧之间需要有间隔时间
    :param websocket.WebSocket ws:
    :return:
    """
    chunk_ms = 160  # 每个数据帧的时间长度，单位为毫秒
    chunk_len = int(16000 * 2 / 1000 * chunk_ms)  # 16000Hz采样率，每帧160ms的音频数据

    # 初始化PyAudio
    p = pyaudio.PyAudio()

    # 打开麦克风流
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=chunk_len)

    logger.info("开始读取麦克风并发送音频数据...")

    try:
        while True:
            # 从麦克风读取音频数据
            data = stream.read(chunk_len)

            # 直接发送音频数据（pcm格式）
            ws.send(data, websocket.ABNF.OPCODE_BINARY)
            logger.debug(f"发送音频数据帧，长度: {len(data)}")

            time.sleep(chunk_ms / 1000.0)  # 控制发送间隔时间，避免发送过快

    except Exception as e:
        logger.error(f"音频发送发生错误: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()



# 发送结束参数
def send_finish(ws):
    """
    结束参数帧
    :param websocket.WebSocket ws:
    :return:
    """
    req = {
        "type": "FINISH"
    }
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)
    logger.info("send FINISH frame")


def send_cancel(ws):
    """
    发送取消帧
    :param websocket.WebSocket ws:
    :return:
    """
    req = {
        "type": "CANCEL"
    }
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)
    logger.info("send Cancel frame")



# 数据类型转化，将wav文件转化为PCM
# 读取原始 WAV 文件
def read_wav(filename):
    sample_rate, data = wavfile.read(filename)
    return sample_rate, data

# 修改采样频率
def change_sample_rate(data, original_rate, target_rate):
    # 计算目标数据的长度
    target_length = int(len(data) * target_rate / original_rate)
    # 通过重采样来改变采样频率
    return resample(data, target_length).astype(np.int16)

# 转换为单通道
def convert_to_mono(data):
    if data.ndim == 2:  # 双通道
        return np.mean(data, axis=1).astype(np.int16)  # 取平均值转为单通道
    return data  # 已经是单通道

# 设置为 PCM 格式（简单存储为 16-bit 小端字节）
def convert_to_pcm(data):
    return data.tobytes()

# 主过程
def process_wav_and_stream(filename, target_sample_rate=16000):
    # 1. 读取原始文件
    original_rate, data = read_wav(filename)
    print("original_rate: ", original_rate)
    print(np.shape(data))
    print(data[0:10000])
    
    # 2. 修改采样频率
    data_resampled = change_sample_rate(data, original_rate, target_sample_rate)
    
    # 3. 转为单通道
    data_mono = convert_to_mono(data_resampled)
    
    # 4. 转为 PCM 格式
    pcm_data = convert_to_pcm(data_mono)
    # print(pcm_data[10000:20000])
    return pcm_data





# WebSocket 连接
def start_ws():
    ws_app = websocket.WebSocketApp(uri,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
    ws_app.run_forever()


# 启动WebSocket连接
# CMD: python C:\Users\Administrator\Desktop\Backend-Algorithm-LLM\Service\testing\baidu_audio_recognize.py

if __name__ == "__main__":
    start_ws()
