#import speech_recognition as sr
# Sarah code
# inspired by https://github.com/wangshub/python-vad/blob/master/vad.py and Sarah Gillet code

import pyaudio
import time



import datetime

import webrtcvad
import collections
import sys
import signal

from array import array
from struct import pack

import time

import threading

import wave

import numpy as np

import struct

import math

import logging
from os import listdir



# linux command line: arecord -l

class vadSpeech():
    def __init__(self, device_id, micID, start_time, sample_rate=16000, chunk_duration_ms=30, padding_duration_ms=1000,
                 vad_critic=3, filename_wave="test", speakersfile_wave = "nome", silenceDb=50.0, activity = None, condition= "inclusive") :
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.device_id = device_id
        self.RATE = sample_rate
        self.CHUNK_DURATION_MS = chunk_duration_ms  # supports 10, 20 and 30 (ms)
        self.PADDING_DURATION_MS = padding_duration_ms  # 1500 , 1 sec judgement (Sarah had 1000)
        self.CHUNK_SIZE = int(self.RATE * self.CHUNK_DURATION_MS / 1000)  # chunk to read
        self.CHUNK_BYTES = self.CHUNK_SIZE * 2  # 16bit = 2 bytes, PCM
        self.NUM_PADDING_CHUNKS = int(self.PADDING_DURATION_MS / self.CHUNK_DURATION_MS)
        # NUM_WINDOW_CHUNKS = int(240 / CHUNK_DURATION_MS)
        self.NUM_WINDOW_CHUNKS = int(400 / self.CHUNK_DURATION_MS)  # 400 ms/ 30ms  - 13ms
        self.NUM_WINDOW_CHUNKS_END = self.NUM_WINDOW_CHUNKS * 2 # 26 ms

        self.START_OFFSET = int(self.NUM_WINDOW_CHUNKS * self.CHUNK_DURATION_MS * 0.5 * self.RATE)
        self.valueAccessLock = threading.Lock()
        self.first_triggered = start_time
        self.vad_criticality_level = vad_critic # default 1 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive.
        self.pa = pyaudio.PyAudio()
        self.confirm_input_device(self.device_id)
        self.list_speak_durations = []
        self.time_of_speech = []
        self.running_index = 0
        self.time_window_minutes = 1
        self.leave = False
        self.endOfLastSpeech = -1
        self.start_time = -1
        self.triggered = False
        self.frames = []
        self.filename_wave = filename_wave
        self.lock_db = threading.Lock()
        self.energy = -1
        self.speakersfile_wave = speakersfile_wave
        self.silenceDb = silenceDb

        # robot conf and condition
        self.activity = activity
        self.condition = condition
        # microphone IDs configuration
        self.micID = micID
        self.other_mic1ID = 0
        self.other_mic2ID = 0

        self.other_mic1 = None
        self.other_mic2 = None

        self.idle = True
        self.VADminoverlap = 3.0 # number of seconds to consider an overlap
        self.VADminidle = 3.0 # number of seconds to consider idle
        self.start_idle = -1


    def confirm_input_device(self, device_id):
        try:
            dev = self.pa.get_device_info_by_index(device_id)
            print("vad: device {} - name: {} - maxInputChannels: {} ".format(device_id, dev['name'],
                                                                             dev['maxInputChannels']))
        except:
            print("\nERROR: No input device with id {}. Choose one from below:\n".format(device_id))

    def detect_background(self):
        self.stream = self.pa.open(format=self.FORMAT,
                                   channels=self.CHANNELS,
                                   rate=self.RATE,
                                   input=True,
                                   start=False,
                                   input_device_index=self.device_id,
                                   frames_per_buffer=self.CHUNK_SIZE)
        dev = self.pa.get_device_info_by_index(self.device_id)
        print("vad_detect_backgound: device {} - name: {} - maxInputChannels: {} ".format(self.device_id, dev['name'],
                                                                 dev['maxInputChannels']))


        self.got_a_sentence = False
        # self.activity.func("firstspeaker")
        #self.activity_callback = activity_callback

        self.start_time = time.time() # IN
        self.endOfLastSpeech = time.time() #IN

        self.threadDetecting = threading.Thread(target=self._detectThread)
        self.threadDetecting.start()

    def rms(self, frame):
        count = len(frame) / 2.0
        format = "%dh" % (count)
        # short is 16 bit int
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * (1.0/32768.0)
            sum_squares += n * n
        # compute the rms
        rms = math.pow(sum_squares / count, 0.5);
        return rms * 1000


    def set_dB(self, value):
        with self.lock_db:
            self.energy = value

    def get_dB(self):
        with self.lock_db:
            return self.energy

    def _detectThread(self):
        vad = webrtcvad.Vad(self.vad_criticality_level)
        while not self.leave:
            ring_buffer = collections.deque(maxlen=self.NUM_PADDING_CHUNKS)
            self.triggered = False
            voiced_frames = []
            ring_buffer_flags = [0] * self.NUM_WINDOW_CHUNKS
            ring_buffer_index = 0

            ring_buffer_flags_end = [0] * self.NUM_WINDOW_CHUNKS_END
            ring_buffer_index_end = 0
            buffer_in = ''
            # WangS
            raw_data = array('h')
            index = 0
            start_point = 0
            self.stream.start_stream()
            StartTime = time.time()
            # print("* recording: ")
            self.got_a_sentence = False
            while not self.got_a_sentence and not self.leave:
                try:
                    chunk = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                except Exception as e:
                    print(e)
                    continue
                # add WangS
                self.frames.append(chunk)
                #calculation of current decibel

                currdB = 20*math.log(self.rms(chunk),10)
                # controlar se recebe
                #if currdB > 30:
                # print("Speak " + str(self.device_id))
                # print (currdB)
                self.set_dB(currdB)
                raw_data.extend(array('h', chunk))
                index += self.CHUNK_SIZE

                active = vad.is_speech(chunk, self.RATE)

                # check silence per child  IN toDo overlap
                currdB1 =  self.other_mic1.get_dB()
                currdB2 = self.other_mic2.get_dB()
                if ((currdB1 - currdB) > 10.0): active = 0
                if ((currdB2 - currdB) >  10.0): active = 0
                if currdB < self.silenceDb : active = 0

                # sys.stdout.write('1' if active else '_')
                ring_buffer_flags[ring_buffer_index] = 1 if active else 0
                ring_buffer_index += 1
                ring_buffer_index %= self.NUM_WINDOW_CHUNKS

                ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
                ring_buffer_index_end += 1
                ring_buffer_index_end %= self.NUM_WINDOW_CHUNKS_END


                # start point detection
                if not self.triggered:
                    ring_buffer.append(chunk)
                    num_voiced = sum(ring_buffer_flags)
                    if num_voiced > 0.8 * self.NUM_WINDOW_CHUNKS:
                        self.triggered = True
                        if (self.first_triggered == -1):
                            self.first_triggered = time.time() - (
                                        self.CHUNK_DURATION_MS * self.NUM_WINDOW_CHUNKS) / 1000.0
                        #start_point = index - self.CHUNK_SIZE * self.NUM_WINDOW_CHUNKS  # start point
                        # self.endOfLastSpeech = time.time() erro
                        if self.idle : # IN
                            self.start_time = time.time() #- (self.CHUNK_DURATION_MS * self.NUM_WINDOW_CHUNKS) / 1000.0
                            # (self.CHUNK_DURATION_MS * self.NUM_WINDOW_CHUNKS) / 1000.0
                        self.list_speak_durations.append(0.0)
                        self.time_of_speech.append(time.time())
                        print (f"VAD : start device id :  {self.device_id} db {str(currdB)}")

                        voiced_frames.extend(ring_buffer)
                        ring_buffer.clear()

                       # new IN  mark beginning of talking
                        self.idle = False # IN
                        self.start_idle = -1
                    # end point detection
                    else:

                        # validate if every mic is idle
                        if (self.idle == False) and (self.start_idle != -1) :
                            duration_idle = time.time() - self.start_idle
                            if duration_idle >= self.VADminidle :
                                self.idle = True
                                print (f"VAD : start idle device id :  {self.device_id} pause duration {str(duration_idle)} db {str(currdB)}")
                            # else: print (f"breath pause device id :  {self.device_id} pause duration {str(duration_idle)} db {str(currdB)}")

                        if self.idle and self.other_mic1.idle and self.other_mic2.idle:

                            endOfLastSpeech = max(self.endOfLastSpeech, self.other_mic1.endOfLastSpeech, self.other_mic2.endOfLastSpeech) #IN
                            duration_time = time.time() - endOfLastSpeech
                            overlap = False

                            # print(f"idle all devices duration_time {str(duration_time)} end of last speech {endOfLastSpeech}, device {self.micID}")
                            mic_speakingTime = self.getSpeakingTime() #IN
                            othermicID1_speakingTime = self.other_mic1.getSpeakingTime() #IN
                            othermicID2_speakingTime = self.other_mic2.getSpeakingTime() #IN
                            self.activity.checknextactivity("idle",  endOfLastSpeech, overlap, self.micID, self.other_mic1ID, self.other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime,duration_time)
                        # end IN

                else:
                    voiced_frames.append(chunk)
                    ring_buffer.append(chunk)
                    num_unvoiced = self.NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)
                    duration_time = time.time() - self.start_time
                    self.list_speak_durations[-1] = duration_time
                    # print(f"keep talking device id  {self.device_id} duration_time {str(duration_time) } db {str(currdB)}")
                    # end point detection
                    if num_unvoiced > 0.90 * self.NUM_WINDOW_CHUNKS_END:
                        self.triggered = False
                        self.got_a_sentence = True
                        self.endOfLastSpeech = time.time()
                        print(f"VAD : stop talking device id  {self.device_id} duration {duration_time}")
                        self.start_idle = self.endOfLastSpeech
                        # end IN
                    else:
                        # keep talking
                        overlap = False
                        if (duration_time >= self.VADminoverlap) and (self.other_mic1.idle == False) or (self.other_mic2.idle == False) : # só reage overlap se for maior 3s
                            overlap = True
                        # TOdo validar se é preciso dar mais margem

                        # check robot expression based on duration of speech IN
                        mic_speakingTime = self.getSpeakingTime() #IN
                        othermicID1_speakingTime = self.other_mic1.getSpeakingTime() #IN
                        othermicID2_speakingTime = self.other_mic2.getSpeakingTime() #IN

                        self.activity.checknextactivity("talking", self.start_time, overlap, self.micID, self.other_mic1ID, self.other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime,duration_time)
                        # end IN


    def stop_detecting(self):
        self.leave = True
        try:
            self.threadDetecting.join(0.5)
        except Exception as e:
            print("Exception while joining", e)
        self.stream.stop_stream()
        self.stream.close()
        # Terminate the PortAudio interface
        self.pa.terminate()
        wf = wave.open(self.filename_wave+str(self.device_id)+".wav", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.pa.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()


    def getSpeakingTime(self):
        return sum(self.list_speak_durations)

    def getSpeakingRatioWithOwn(self):
        return sum(self.list_speak_durations) / (time.time() - self.first_triggered)


    def getTimeOfFirstUtterance(self):
        return self.first_triggered

    def getEndTimeOfLastUtterance(self):
        return (not self.triggered), self.endOfLastSpeech

    def getTimeLastUttLength(self):
        if len(self.list_speak_durations) > 0:
            return self.list_speak_durations[-1]
        else:
            return 0.0

    def getSpeechActive(self):
        return self.triggered

    def getStartOfPause(self):
        return self.endOfLastSpeech

    def getSpeakingRatioWindow(self):
        if time.time() - self.first_triggered > self.time_window_minutes*60:
            return self.getSpeakingTimeWindow()/self.time_window_minutes*60
        else:
            return self.getSpeakingRatioWithOwn()

    def getSpeakingTimeWindow(self):
        if len(self.time_of_speech) > 0:
            time_stamp_window_ago = time.time() - self.time_window_minutes * 60
            while len(self.time_of_speech) > self.running_index + 1 and \
                    self.time_of_speech[self.running_index + 1] < time_stamp_window_ago:
                self.running_index += 1
            if self.running_index == len(self.time_of_speech) - 1 and \
                    self.time_of_speech[self.running_index] < time_stamp_window_ago:
                # if the last present time stamp is more than three minutes
                return max(0,
                           self.time_of_speech[self.running_index] + self.list_speak_durations[
                               self.running_index] - time_stamp_window_ago)
            sumOfSpeech = sum(self.list_speak_durations[self.running_index + 1:])
            sumOfSpeech += max(0,
                               self.time_of_speech[self.running_index] + self.list_speak_durations[
                                   self.running_index] - time_stamp_window_ago)
            return sumOfSpeech
        else:
            return 0

    def printMicMetrics(self):
        print("Microphone metrics")
        print("microphone device_id {}".format(self.device_id))
        print("speaking time {}".format(self.getSpeakingTime()))
        # print("speaking time window {}".format(self.getSpeakingTimeWindow()))
        # print("speaking ratio with own {}".format(self.getSpeakingRatioWithOwn()))
        # print("speaking ratio window {}".format(self.getSpeakingRatioWindow()))
        print(f"speaking started {self.getTimeOfFirstUtterance()}")
        print(f"speaking end {self.getEndTimeOfLastUtterance()}")

        print(f"speak durations ")
        print(self.list_speak_durations)
        print(f"time of starting speech ")
        print(self.time_of_speech)

    def logMicMetrics(self):

        mic_logs = []
        name = str(self.start_time)
        file = "Logs\\" + "MIC" + name + ".log"
        logging.basicConfig(filename=file, level=logging.DEBUG)
        logging.info("======MICROPHONE VAD ======")
        logging.info(str(self.device_id))
        logging.info("======Speaking Time ======")
        logging.info(str(self.getSpeakingTime()))
        logging.info("======First Soeak======")
        logging.info(self.getTimeOfFirstUtterance())
        logging.info("======Last Soeech======")
        logging.info(self.getEndTimeOfLastUtterance())
        # VALIDAR TEMPOS POR SPEAKER, STATE ....
        logging.info("======Speak duration ======")
        logging.info(self.list_speak_durations)
        logging.info("======time of starting speech======")
        logging.info(self.time_of_speech)

        mic_logs.append(str(self.device_id))
        mic_logs.append(str(self.getSpeakingTime()))
        mic_logs.append(self.getTimeOfFirstUtterance())
        mic_logs.append(self.getEndTimeOfLastUtterance())
        mic_logs.append(self.list_speak_durations)
        mic_logs.append(self.time_of_speech)

        return mic_logs
    #logging.info("======ROOM TOTAL TIMES======")
    #logging.info(logTotalTimePerRoom)


