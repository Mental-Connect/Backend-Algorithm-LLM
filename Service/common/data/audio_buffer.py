class AudioBuffer:
    def __init__(self):
        self.audio_for_context_store: bytearray = bytearray()
        self.transcription_correction_audio_store: bytearray = bytearray()
        self.saved_audio_data: list = []

        
audio_buffer_instance = AudioBuffer()
