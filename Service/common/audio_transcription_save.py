import os
import pandas as pd

def audio_transcription_save(temp_file_path, full_transcription, audio_save_path):
    data = {
            "File Path": [temp_file_path],
            "Transcription": [full_transcription]
        }
    excel_file_path = os.path.join(os.path.dirname(audio_save_path), "transcriptions.xlsx")
    if os.path.exists(excel_file_path):
            # Load existing data and append new data
            df = pd.read_excel(excel_file_path)
            new_row = pd.DataFrame(data)
            df = pd.concat([df, new_row], ignore_index=True)
    else:
            # Create a new DataFrame if the file doesn't exist
            df = pd.DataFrame(data)

        # Save the DataFrame to Excel
    df.to_excel(excel_file_path, index=False)
