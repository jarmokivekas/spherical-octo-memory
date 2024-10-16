import numpy as np
import pygame
import random

def combine_waves_scaled(*waves):
    num_waves = len(waves)
    
    # Sum the waves and scale them down by the number of waves to prevent clipping
    combined_wave = sum(wave / num_waves for wave in waves)
    
    return combined_wave.astype(np.int16)

def apply_adsr(wave, sample_rate, attack=0.3, decay=0.5, sustain_level=0.3, release=0.5):
    length = len(wave)
    adsr = np.ones(length)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    
    # Attack phase (fade in)
    adsr[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay phase
    adsr[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain_level, decay_samples)
    
    # Release phase (fade out)
    adsr[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
    
    # Apply envelope to the wave
    return wave * adsr

def apply_echo(wave, delay, decay, sample_rate):
    echo_samples = int(delay * sample_rate)
    echoed_wave = np.zeros(len(wave) + echo_samples)
    echoed_wave[:len(wave)] += wave
    echoed_wave[echo_samples:] += decay * wave
    return echoed_wave[:len(wave)] *0.5 # Ensure it's the original length

def generate_layered_tone(base_freq, sample_rate, duration, detune=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave1 = np.sin(2 * np.pi * base_freq * t)
    wave2 = np.sin(2 * np.pi * (base_freq + detune) * t)  # Detuned wave
    return (wave1 + wave2) * 0.5  # Normalize to avoid clipping

def low_pass_filter(wave, cutoff_freq, sample_rate):
    rc = 1 / (2 * np.pi * cutoff_freq)
    alpha = sample_rate * rc / (sample_rate * rc + 1)
    filtered_wave = np.zeros_like(wave)
    for i in range(1, len(wave)):
        filtered_wave[i] = alpha * wave[i] + (1 - alpha) * filtered_wave[i - 1]
    return filtered_wave

def vary_amplitude(wave, variation_factor=0.1):
    # Apply random amplitude variations
    amp_variation = 1 + variation_factor * (2 * np.random.rand(len(wave)) - 1)
    return wave * amp_variation

def apply_tremolo(wave, mod_freq, sample_rate):
    t = np.linspace(0, len(wave) / sample_rate, len(wave), False)
    tremolo = 0.5 * (1 + np.sin(2 * np.pi * mod_freq * t))  # Modulate amplitude
    return wave * tremolo

def generate_sine_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)
    return wave

def combine_waves(*waves):
    return sum(waves) * 0.5  # Normalize

def generate_ambient_music(frequencies, sample_rate, duration):
    waves = []
    for i in range(10):
        freq = random.choice(frequencies)
        note_duration = np.random.uniform(1, 3)  # Randomize note lengths
        # wave = generate_sine_wave(freq, note_duration, sample_rate)
        wave = generate_layered_tone(freq, duration=note_duration, sample_rate=sample_rate)
        # wave = apply_adsr(wave, sample_rate)
        # wave = low_pass_filter(wave, cutoff_freq=500, sample_rate=sample_rate)
        # wave = apply_echo(wave, delay= 0.01, decay=0.2, sample_rate=sample_rate)
        waves.append(wave)

    return np.concatenate(waves)

# Parameters
sample_rate = 44100
frequencies = [392, 440, 493.88, 587.33, 659.25]  # G Major Pentatonic

# Generate music and output
ambient_music = generate_ambient_music(frequencies, sample_rate, duration=60)

# Convert to int16 for pygame
sound_data = np.int16(ambient_music * 32767)

# Output using pygame
pygame.mixer.init(frequency=sample_rate, channels=1)
sound = pygame.sndarray.make_sound(sound_data)
sound.play()

pygame.time.wait(int(60 * 1000))
pygame.mixer.quit()