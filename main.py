import json
import os
import queue
import random
import struct
import subprocess
import sys
import time
from ctypes import POINTER, cast

import pvporcupine
import pygame
import vosk
import yaml
from fuzzywuzzy import fuzz
from pvrecorder import PvRecorder
from rich import print


import config
import tts
import face


class VoiceAssistant:
    def __init__(self, porcupine, vosk_model, recorder, gpt_interface, audio_player, face_display, cmd_list_yaml):
        self.porcupine = porcupine
        self.recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
        self.recorder = recorder
        self.gpt_interface = gpt_interface
        self.audio_player = audio_player
        self.face_display = face_display
        self.cmd_list_yaml = cmd_list_yaml

    def start(self):
        print('\n\n')
        print('Using device: %s' % recorder.selected_device)
        print(f"Валли (v1.0) начал свою работу ...")
        self.audio_player.play("run")
        time.sleep(0.5)

        self.recorder.start()
        self.ltc = time.time() - 1000
        while True:
            try:
                self.face_display.show_emotion()
                pcm = self.recorder.read()
                if self.porcupine.process(pcm) >= 0:
                    self._on_wake_word()
                    self.ltc = time.time()

                while time.time() - self.ltc <= 10:
                    pcm = self.recorder.read()
                    sp = struct.pack("h" * len(pcm), *pcm)
                    if self.recognizer.AcceptWaveform(sp):
                        if self._process_voice(json.loads(self.recognizer.Result())["text"]):
                            self.ltc = time.time()

            except Exception as err:
                print(f"Uexpected {err=}, {type(err)=}")
                raise

    def _on_wake_word(self):
        self.recorder.stop()
        self.audio_player.play("greet")
        print("Yes, sir.")
        self.recorder.start()

    def _process_voice(self, voice_text):
        cmd = self.recognize_cmd(self.filter_cmd(voice_text))
        print(voice_text)
        print(cmd)
        if len(cmd['cmd'].strip()) <= 0:
            return False
        elif cmd['percent'] < 70 or cmd['cmd'] not in self.cmd_list_yaml.keys():
            self._ask_gpt(voice_text)

            self.audio_player.play("ok")
            self._execute_command(cmd['cmd'], voice_text)

    def filter_cmd(self, raw_voice: str):
        cmd = raw_voice

        for x in config.VA_ALIAS:
            cmd = cmd.replace(x, "").strip()

        for x in config.VA_TBR:
            cmd = cmd.replace(x, "").strip()

        return cmd

    def recognize_cmd(self, cmd: str):
        rc = {'cmd': '', 'percent': 0}
        for c, v in self.cmd_list_yaml.items():

            for x in v:
                vrt = fuzz.ratio(cmd, x)
                if vrt > rc['percent']:
                    rc['cmd'] = c
                    rc['percent'] = vrt

        return rc


    def _execute_command(self, cmd, voice_text):
        CommandExecutor.execute(cmd, voice_text)
    
    def _ask_gpt(self, voice_text):
        response = self.gpt_interface.get_response(voice_text)
        self.audio_player.play_response(response)


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        CDIR = os.getcwd()
        self.sound_path = os.path.join(CDIR, "audio")
    
    def play(self, phrase):
        sound_map = {
            "greet": f"greet{random.choice([1, 2, 3])}.wav",
            "ok": f"ok{random.choice([1, 2, 3])}.wav",
            "not_found": "not_found.wav",
            "thanks": "thanks.wav",
            "run": "run.wav",
            "stupid": "stupid.wav",
            "ready": "ready.wav",
            "off": "off.wav",
        }
        filename = os.path.join(self.sound_path, sound_map[phrase])
        sound = pygame.mixer.Sound(filename)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)

    def play_response(self, response):
        tts.va_speak(response)


class FaceDisplay:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.face = face.Face(self.WIDTH, self.HEIGHT)
        self.emotion = 'default'
    
    def show_emotion(self, emotion_type=False):
        # Show emotion on the screen
        if not emotion_type:
            self.default()

    def default(self):
        if not self.face.blinking:
            self.face.blink()


class CommandExecutor:
    @staticmethod
    def execute(cmd, voice_text):
        if cmd == 'music':
            print('music')
            # subprocess.Popen([f'{CDIR}\\custom-commands\\Run music.exe'])
        elif cmd == 'off':
            porcupine.delete()
            sys.exit(0)
        # Add more commands here


if __name__ == "__main__":
    width, height = 160, 128  # Adjust to your LCD screen size

    # Initialize required components
    audio_player = AudioPlayer()
    face_display = FaceDisplay(width, height)
    cmd_list_yaml = yaml.safe_load(
        open('commands.yaml', 'rt', encoding='utf8'),
    )

    vosk_model = vosk.Model("model_small")
    porcupine = pvporcupine.create(
        access_key=config.PICOVOICE_TOKEN,
        keyword_paths=[config.path_wake_word],
        model_path='porcupine_params_ru.pv',
        sensitivities=[1]
    )

    recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)

    assistant = VoiceAssistant(porcupine, vosk_model, recorder, gpt_interface, audio_player, face_display, cmd_list_yaml)
    assistant.start()
