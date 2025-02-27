import pygame
import sounddevice as sd
import numpy as np
import wave
import os
from pydub import AudioSegment
from pydub.playback import play

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Talking Cat")

# Load cat image
cat_img = pygame.image.load("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4uP9Vk1fLkk67nT9gE8mLIqMMK-tQpWvlPQ&s")  # Add a cat image in the same directory
cat_img = pygame.transform.scale(cat_img, (300, 300))

# Define colors
WHITE = (255, 255, 255)

# Recording settings
RATE = 44100
DURATION = 3


# Function to record audio
def record_audio(filename="voice.wav"):
    print("Recording...")
    recording = sd.rec(int(RATE * DURATION), samplerate=RATE, channels=2, dtype=np.int16)
    sd.wait()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(recording.tobytes())
    print("Recording saved!")


# Function to modify voice (pitch shift)
def modify_voice(filename="voice.wav", output="voice_modified.wav"):
    audio = AudioSegment.from_wav(filename)
    audio = audio.speedup(playback_speed=1.5)  # Increase pitch
    audio.export(output, format="wav")
    return output


# Function to play audio
def play_audio(filename):
    audio = AudioSegment.from_wav(filename)
    play(audio)


# Game loop
running = True
while running:
    screen.fill(WHITE)
    screen.blit(cat_img, (100, 100))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                record_audio()
                mod_file = modify_voice()
                play_audio(mod_file)

pygame.quit()
os.remove("voice.wav")
os.remove("voice_modified.wav")
