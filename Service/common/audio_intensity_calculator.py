import numpy as np
from Service.config import model_sampling_rate
from Service.logging.logging import *


def filter_high_intensity_segments(audio_array, segment_duration: float, intensity_threshold: float, model_sampling_rate: int  = model_sampling_rate):
    """
    Filter high-intensity audio segments from the given audio array.

    This function divides the audio data into segments of specified duration, calculates the intensity
    of each segment, and retains only those segments whose intensity exceeds a given threshold.

    Parameters:
        audio_array (np.ndarray): The input audio data as a NumPy array.
        segment_duration (float): The duration of each segment in seconds.
        intensity_threshold (float): The intensity threshold for filtering segments.
        model_sampling_rate (int, optional): The sampling rate of the model, defaults to the configured model_sampling_rate.

    Returns:
        List[np.ndarray]: A list of NumPy arrays containing high-intensity audio segments.
    """
    segment_samples = int(segment_duration * model_sampling_rate)  # Number of samples per segment
    high_intensity_segments = []

    # Split audio into segments and process their intensities
    num_segments = len(audio_array) // segment_samples
    for i in range(num_segments):
        start_sample = i * segment_samples
        end_sample = start_sample + segment_samples
        segment = audio_array[start_sample:end_sample]
        
        # Calculate intensity for each segment
        intensity = compute_intensity(segment)
        
        # Only keep the segment if its intensity exceeds the threshold
        if intensity > intensity_threshold:
            # logging.info(f"Keeping high-intensity segment {i+1} with intensity {intensity:.6f}")
            high_intensity_segments.append(segment)
        else:
            # logging.info(f"Skipping low-intensity segment {i+1} with intensity {intensity:.6f}")
            continue

    # If there are remaining samples that don't form a full segment, calculate their intensity
    if len(audio_array) % segment_samples != 0:
        segment = audio_array[num_segments * segment_samples:]
        intensity = compute_intensity(segment)
        if intensity > intensity_threshold:
            # logging.info(f"Keeping last high-intensity segment with intensity {intensity:.6f}")
            high_intensity_segments.append(segment)

    return high_intensity_segments


def compute_intensity(audio_segment: np.ndarray) -> float:
    """
    Calculate the intensity (mean square amplitude) of a given audio segment.

    The intensity is computed as the mean of the square of the absolute values of the audio samples.

    Parameters:
        audio_segment (np.ndarray): The audio segment as a NumPy array.

    Returns:
        float: The calculated intensity of the audio segment.
    """
    """Calculate intensity (mean square amplitude) of a given audio segment."""
    return np.mean(np.abs(audio_segment) ** 2)
