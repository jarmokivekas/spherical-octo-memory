import numpy as np
import pygame

def combine_waves(*waves):
    return sum(waves).astype(np.int16)

def combine_waves_scaled(*waves):
    num_waves = len(waves)
    
    # Sum the waves and scale them down by the number of waves to prevent clipping
    combined_wave = sum(wave / num_waves for wave in waves)
    
    return combined_wave.astype(np.int16)

def combine_waves_normalized(*waves):
    combined_wave = sum(waves)
    
    # Find the maximum absolute value in the combined waveform
    max_val = np.max(np.abs(combined_wave))
    
    # If the maximum value exceeds the allowable range, normalize the waveform
    if max_val > 0:
        combined_wave = combined_wave * (32767 / max_val)
    
    return combined_wave.astype(np.int16)

def play_sound(waveform, sample_rate=44100):
    """Plays a sound from a NumPy array using Pygame"""
    sound = pygame.sndarray.make_sound(waveform)
    sound.play()


def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=32767):
    """
    Generates a sine wave of a specific frequency and duration.
    - frequency: Frequency of the sine wave in Hertz
    - duration: Duration of the sound in seconds
    - sample_rate: Number of samples per second (44.1kHz default)
    - amplitude: Max amplitude (32767 for 16-bit audio)
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave.astype(np.int16)  # Convert to 16-bit data



def generate_modulated_sine_wave(frequency_start, frequency_end, duration, sample_rate=44100, amplitude=32767):
    """
    Generates a sine wave with frequency modulation (linear rise).
    - frequency_start: Initial frequency of the sine wave (Hz)
    - frequency_end: Final frequency of the sine wave (Hz)
    - duration: Duration of the sound (seconds)
    - sample_rate: Number of samples per second (44.1kHz default)
    - amplitude: Max amplitude (32767 for 16-bit audio)
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Linearly interpolate frequency from start to end over time
    frequencies = np.linspace(frequency_start, frequency_end, int(sample_rate * duration))

    # Generate sine wave with the changing frequency
    wave = amplitude * np.sin(2 * np.pi * frequencies * t)

    return wave.astype(np.int16)

def apply_amplitude_envelope(wave, attack_time, decay_time, sample_rate=44100):
    num_samples = len(wave)
    envelope = np.ones(num_samples)

    # Attack phase (fade in)
    attack_samples = int(attack_time * sample_rate)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay phase (fade out)
    decay_samples = int(decay_time * sample_rate)
    envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)

    return (wave * envelope).astype(np.int16)

def generate_white_noise(duration, sample_rate=44100, amplitude=32767):
    num_samples = int(sample_rate * duration)
    wave = np.random.uniform(-amplitude, amplitude, num_samples)
    return wave.astype(np.int16)