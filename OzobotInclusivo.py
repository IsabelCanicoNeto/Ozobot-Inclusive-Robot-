# import ButtonStuff.fliclib as fliclib

import asyncio
import struct
from bleak import BleakScanner
from bleak import BleakClient
import time
import simpleaudio as sa
import datetime
import logging
from os import listdir
import sys
from Ozobotcode import *


#UUID = "001"
# p = True
# comportamento = False


class ozoRobot():
	def __init__(self, start_time = datetime.datetime.now(), condition="inclusive", behavior_cond = "explicit", speakerID1 = 1, speakerID2 = 2, speakerID3 = 3, name1 = "nome", name2 = "nome", name3 = "nome", state="empty", p = True):

		# pace
		self.condition = condition
		self.startTime = start_time
		self.behavior_cond = behavior_cond

		# robot ozo Evo
		self.ozoAddress ="MM:MM:MM:MM:MM:MM"
		loop = asyncio.get_event_loop()
		#discover do address do ozobot
		loop.run_until_complete(self.discover())
		#referencia para o cliente a.k.a. ozobot
		self.ozobotClient = BleakClient(self.ozoAddress)

		# colours
		self.speakerID1 = speakerID1
		self.speakerID2 = speakerID2
		self.speakerID3 = speakerID3

		# PARAM espaço
		self.spinAngle = 500
		self.spinTime = 1
		self.driveDist = 800
		self.driveTime = 2
		self.slowPace = False

		self.p = p # print flag

		if p:
			print("inicio")
			print(self.ozobotClient)

		loop.run_until_complete(self.connectRobot())
		# loop.stop()

#===============================================================================
#
#                              ROBOT CONNECTION
#
#===============================================================================

	async def discover(self):
		devices = await BleakScanner.discover()
		# search for robot Evo bluethooth
		for d in devices:
			if "Ozo" in d.name:
				print(d.address)
				print(d.name)
				self.ozoAddress = d.address
			print("dentro do discover: " + d.address)

	async def connectRobot(self):
		try:
			await self.ozobotClient.connect()
			#print(client.is_connected)

			#blocks random behaviors
			initialCommand = b"\x50\x02\x01"
			await self.ozobotClient.write_gatt_char("8903136c-5f13-4548-a885-c58779136703", initialCommand, response=False)
			reset = struct.pack('<BHBBB', 68, 255, 0, 0, 0)
			await self.ozobotClient.write_gatt_char("8903136c-5f13-4548-a885-c58779136703", reset, response=False)

		except Exception as e:
			print("EXCEPTIONNN")
			print(e)


	def closeRobot(self): # validar com erros

		endingLoop = asyncio.new_event_loop()
		battery = endingLoop.run_until_complete(checkBattery(self.ozobotClient))
		#ozobotClient.disconnect()




#===============================================================================
#
#                              ROBOT EXPRESSIONS
#
#===============================================================================

	def checkColour(self, speaker):
		if speaker == self.speakerID1: # red
			return 255, 0, 0
		if speaker == self.speakerID2: # blue
			return 0, 0, 127
		if speaker == self.speakerID3: # white
			return 255, 255, 255

#===============================================================================
#
#                              ROBOT EXPRESSIONS
#
#===============================================================================

	def executeExpression(self, expression, actualSpeaker, actualSpeakerName, nextSpeaker, nextSpeakerName, otherSpeaker, otherSpeakerName, movePace):

		# adicionar a condição inclusive and control
		loop = asyncio.new_event_loop()


		if expression == "greetings" : self.greetings(loop)
		if expression == "firstspeaker" : self.firstspeaker(loop, actualSpeaker, actualSpeakerName)
		if expression == "changespeaker" : self.changespeaker(loop, actualSpeaker, nextSpeaker, nextSpeakerName)
		if expression == "turnexchange" : self.turnexchange(loop, actualSpeaker, nextSpeaker, nextSpeakerName, movePace)
		if expression == "hearing" : self.hearing(loop)
		if expression == "tewarning" : self.tewarning(loop, actualSpeaker, nextSpeaker, nextSpeakerName)
		if expression == "engaging" : self.engaging(loop)
		if expression == "praising" : self.praising(loop, actualSpeakerName)
		if expression == "mixedup" : self.mixedup(loop, actualSpeaker, nextSpeaker, otherSpeaker)
		if expression == "confused" : self.confused(loop, actualSpeaker, nextSpeaker, otherSpeaker)
		if expression == "endwarning" : self.endwarning(loop, actualSpeaker)
		if expression == "goodbye" : self.goodbye(loop)
		if expression == "end" : self.end(loop)




	def greetings(self, loop):
		playSound("begin") #1
		self.greetings_lights(loop, True)
		time.sleep(2)
		self.greetings_mov(loop)
		time.sleep(2)
		self.greetings_lights(loop, False)
		time.sleep(1)

	def greetings_lights(self, loop, firstTime):
		ozobotClient = self.ozobotClient
		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			time.sleep(0.5)
		loop.run_until_complete(changeAllLights(ozobotClient,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))


		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))



		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))



		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))


		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
		time.sleep(0.05)

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))
		time.sleep(0.05)

		if not firstTime:
			loop.stop()

	def greetings_mov(self, loop):
		loop.run_until_complete(spin_left(self.ozobotClient,1000,1.4))
		playSound("hi") #1
		time.sleep(2)



	'''
	************************************ First speaker  **************************************
	'''

	def firstspeaker(self, loop, actualSpeaker, nameSpeaker):
		playSound("warning2") # 5 em movimento - validar se faz sentido que já temos as rodas
		time.sleep(0.5)
		self.firstspeaker_lights(loop, True, actualSpeaker)
		time.sleep(0.5)
		self.firstspeaker_mov(loop, nameSpeaker)
		time.sleep(1)
		self.firstspeaker_lights(loop, False, actualSpeaker)

	def firstspeaker_lights(self, loop, firstTime, actualSpeaker):
		ozobotClient = self.ozobotClient
		c1,c2,c3 = self.checkColour(actualSpeaker)

		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.5)
		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))
		time.sleep(1)

		if not firstTime:
			loop.stop()

	def firstspeaker_mov(self, loop, name):
		ozobotClient = self.ozobotClient
		# playSound("move") # 5 validar se justifica que já temos as rodas
		loop.run_until_complete(drive(ozobotClient,self.driveDist,self.driveDist,self.driveTime))

		playSound("speaker") # 5 em movimento - validar se faz sentido que já temos as rodas
		time.sleep(0.5)
		playSound(name) # 5
		time.sleep(1)


	'''
	******************************** turnexchange **************************************
	'''


	def turnexchange(self, loop, actualSpeaker, nextSpeaker, nextSpeakerName, slowPace):

		playSound("warning2") # 5 em movimento - validar se faz sentido que já temos as rodas
		self.turnexchange_lights(loop, True, actualSpeaker, nextSpeaker)
		time.sleep(1)
		slowPace = False
		self.turnexchange_mov(loop, actualSpeaker, nextSpeaker, nextSpeakerName, slowPace, False)
		time.sleep(2)
		self.turnexchange_lights(loop, False, actualSpeaker, nextSpeaker)

	def turnexchange_lights(self, loop, firstTime, actualSpeaker, nextSpeaker):
		ozobotClient = self.ozobotClient
		c1,c2,c3 = self.checkColour(actualSpeaker)
		c4, c5, c6 = self.checkColour(nextSpeaker)
		loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))

		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.5)

			loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))

			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,0,0,0))

			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,0,0,0))


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,0,0,0))

			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


		if not firstTime:
			loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))
			time.sleep (5)
			loop.stop()


	def turnexchange_mov(self, loop, actualSpeaker, nextSpeaker, name, slowPace, Organic):
		ozobotClient = self.ozobotClient

		if slowPace :  # slower pace, inclusive configuration
			driveDist = int ( self.driveDist / 2)
			driveTime = self.driveTime * 2
		else :
			driveDist = self.driveDist
			driveTime = self.driveTime

		loop.run_until_complete(drive(ozobotClient,-driveDist,-driveDist,driveTime))
		time.sleep(2)

		if (actualSpeaker == self.speakerID1) :
			if (nextSpeaker == self.speakerID3): loop.run_until_complete(spin_left(ozobotClient, self.spinAngle,self.spinTime))
			else:  loop.run_until_complete(spin_right(ozobotClient, self.spinAngle,self.spinTime))
		if (actualSpeaker == self.speakerID2) :
			if (nextSpeaker == self.speakerID1): loop.run_until_complete(spin_left(ozobotClient, self.spinAngle,self.spinTime))
			else: loop.run_until_complete(spin_right(ozobotClient, self.spinAngle,self.spinTime))
		if (actualSpeaker == self.speakerID3) :
			if (nextSpeaker == self.speakerID2): loop.run_until_complete(spin_left(ozobotClient, self.spinAngle,self.spinTime))
			else: loop.run_until_complete(spin_right(ozobotClient, self.spinAngle,self.spinTime))

		time.sleep(2)
		loop.run_until_complete(drive(ozobotClient,self.driveDist,self.driveDist,self.driveTime))
		if not Organic :
			playSound("speaker") # 5 em movimento - validar se faz sentido que já temos as rodas
			time.sleep(2)
			playSound(name) # 5 em movimento - validar se faz sentido que já temos as rodas
			time.sleep(3)


	'''
	******************************** changespeaker **************************************
	'''


	def changespeaker(self, loop, actualSpeaker, nextSpeaker, nextSpeakerName):

		#playSound("warning2") # 5 em movimento - validar se faz sentido que já temos as rodas
		# print(" DEBUG Speaker 1: " + str(actualSpeaker) + " next Speaker : " + str(nextSpeaker) )
		self.changespeaker_lights(loop, True, actualSpeaker, nextSpeaker)
		self.turnexchange_mov(loop, actualSpeaker, nextSpeaker, nextSpeakerName, False, False)
		#self.changespeaker_mov(loop, actualSpeaker, nextSpeaker, nextSpeakerName)
		self.changespeaker_lights(loop, False, actualSpeaker, nextSpeaker)
		time.sleep(1)


	def changespeaker_lights(self, loop, firstTime, actualSpeaker, nextSpeaker):
		ozobotClient = self.ozobotClient
		c1,c2,c3 = self.checkColour(actualSpeaker)
		c4, c5, c6 = self.checkColour(nextSpeaker)
		loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))

		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.5)

			loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))

			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,0,0,0))

			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,0,0,0))


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,0,0,0))

			time.sleep(0.1)
			loop.run_until_complete(changeLight(ozobotClient,128,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,2,c4,c5,c6))
			time.sleep(0.05)
			loop.run_until_complete(changeLight(ozobotClient,1,c4,c5,c6))
			time.sleep(0.1)


		if not firstTime:
			loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))
			time.sleep (1)
			loop.stop()


	def changespeaker_mov(self, loop, actualSpeaker, nextSpeaker, name):
		ozobotClient = self.ozobotClient

		#loop.run_until_complete(drive(ozobotClient,-self.driveDist,-self.driveDist,self.driveTime))
		#time.sleep(10)

		stime = self.spinTime
		stime2 = self.spinTime / 2
		sspeed = int (self.spinAngle  * 2)
		sspeed2 = self.spinAngle
		dist = self.driveDist * 2
		dtime = self.driveTime * 10

		# loop.run_until_complete(spin_left(ozobotClient, self.spinAngle,self.spinTime))
		# loop.run_until_complete(drive(ozobotClient,self.driveDist,self.driveDist,self.driveTime))

		if (actualSpeaker == self.speakerID1) :
			if (nextSpeaker == self.speakerID3):
				loop.run_until_complete(spin_left(ozobotClient, sspeed, stime))
				time.sleep(0.5)
				loop.run_until_complete(drive(ozobotClient,dist, dist,dtime))
				time.sleep(0.5)
				loop.run_until_complete(spin_right(ozobotClient, sspeed2, stime2))
				time.sleep(0.5)
			else:
				loop.run_until_complete(spin_right(ozobotClient, sspeed, stime))
				time.sleep(0.5)
				loop.run_until_complete(drive(ozobotClient,dist, dist,dtime))
				time.sleep(0.5)
				loop.run_until_complete(spin_left(ozobotClient, sspeed2, stime2))
				time.sleep(0.5)
		if (actualSpeaker == self.speakerID2) :
			if (nextSpeaker == self.speakerID1):
				loop.run_until_complete(spin_left(ozobotClient, sspeed, stime))
				time.sleep(0.5)
				loop.run_until_complete(drive(ozobotClient,dist, dist,dtime))
				time.sleep(0.5)
				loop.run_until_complete(spin_right(ozobotClient, sspeed2, stime2))
				time.sleep(0.5)
			else:
				loop.run_until_complete(spin_right(ozobotClient, sspeed, stime))
				time.sleep(0.5)
				loop.run_until_complete(drive(ozobotClient,dist, dist,dtime))
				time.sleep(0.5)
				loop.run_until_complete(spin_left(ozobotClient, sspeed2, stime2))
				time.sleep(0.5)

		if (actualSpeaker == self.speakerID3) :
			if (nextSpeaker == self.speakerID2):
				loop.run_until_complete(spin_left(ozobotClient, sspeed, stime))
				time.sleep(0.5)
				loop.run_until_complete(drive(ozobotClient,dist, dist,dtime))
				time.sleep(0.5)
				loop.run_until_complete(spin_right(ozobotClient, sspeed2, stime2))
				time.sleep(0.5)
			else:
				loop.run_until_complete(spin_right(ozobotClient, sspeed, stime))
				time.sleep(0.5)
				loop.run_until_complete(drive(ozobotClient,dist, dist,dtime))
				time.sleep(0.5)
				loop.run_until_complete(spin_left(ozobotClient, sspeed2, stime2))
				time.sleep(0.5)


		time.sleep(1)

		# playSound("speaker") # 5 em movimento - validar se faz sentido que já temos as rodas
		# time.sleep(2)

		# playSound(name) # 5 em movimento - validar se faz sentido que já temos as rodas
		# time.sleep(3)

	'''
	******************************** hearing **************************************
	'''

	def hearing(self, loop):

		self.hearing_mov(loop)
		time.sleep(3)


	def hearing_lights(self, loop, firstTime):
		ozobotClient = self.ozobotClient
		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(1)

		loop.run_until_complete(changeAllLights(ozobotClient,6,100,127))
		loop.run_until_complete(changeLight(ozobotClient,128,0,0,0))

		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))

		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,32,6,100,127))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,16,6,100,127))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,8,6,100,127))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,4,6,100,127))
		time.sleep(1.5)
		loop.run_until_complete(changeLight(ozobotClient,2,6,100,127))

		if not firstTime:
			loop.stop()

	def hearing_mov(self, loop):
		ozobotClient = self.ozobotClient
		loop.run_until_complete(drive(ozobotClient,100,100,2))
		time.sleep(2)
		loop.run_until_complete(drive(ozobotClient,-100,-100,2))
		time.sleep(2)
		loop.run_until_complete(stop(ozobotClient))

	'''
	******************************** tewarning **************************************
	'''

	def tewarning(self, loop, actualSpeaker, nextSpeaker, nextSpeakerName):

		playSound("warning2") # 5 em movimento - validar se faz sentido que já temos as rodas
		self.tewarning_lights(loop, True, actualSpeaker, nextSpeaker)
		time.sleep(1)
		self.tewarning_mov(loop, nextSpeakerName)
		time.sleep(2)
		self.tewarning_lights(loop, False, actualSpeaker, nextSpeaker)

	def tewarning_lights(self, loop, firstTime, actualSpeaker, nextSpeaker):
		ozobotClient = self.ozobotClient
		c1,c2,c3 = self.checkColour(actualSpeaker)
		c4,c5,c6 = self.checkColour(nextSpeaker)

		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.1)

		loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))
		loop.run_until_complete(changeLight(ozobotClient,128,c4,0,0))

		time.sleep(0.5)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))

		time.sleep(0.5)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))

		time.sleep(0.5)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))

		time.sleep(0.5)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c4,c5,c6))

		time.sleep(0.5)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))
		time.sleep(0.5)
		if not firstTime :
			loop.stop()

	def tewarning_mov(self, loop, name):

		time.sleep(0.1)
		playSound("warning2") #10 tewarn, ALERTA avaliar se colocamos o nome ou nao
		time.sleep(2)
		#name = self.checkName(self.nextSpeaker)
		playSound(name) # 5 em movimento - validar se faz sentido que já temos as rodas
		time.sleep(1)

	'''
	******************************** engaging **************************************
	'''

	def engaging(self, loop):
		ozobotClient = self.ozobotClient
		# self.engaging_lights(ozobotClient, loop, True)
		time.sleep(1)
		self.engaging_mov(loop)
		#time.sleep(2)
		#self.engaging_lights(ozobotClient, loop, False)

	def engaging_lights(self, loop):

		time.sleep(0.1)

	def engaging_mov(self, loop):
		ozobotClient = self.ozobotClient
		time.sleep(1.5)
		playSound("backchanneling2") #11 bc
		loop.run_until_complete(drive(ozobotClient,100,100,2))
		time.sleep(2)
		loop.run_until_complete(drive(ozobotClient,-100,-100,2))
		time.sleep(2)
		loop.run_until_complete(stop(ozobotClient))

		time.sleep(1)

	'''
	******************************** praising **************************************
	'''

	def praising(self, loop, actualSpeakername):
		ozobotClient = self.ozobotClient
		#self.praising_lights(ozobotClient, loop, True, spID1, spID2, spID3)
		time.sleep(1)
		self.praising_mov(loop, actualSpeakername)
		time.sleep(2)
		# self.praising_lights(ozobotClient, loop, False, spID1, spID2, spID3)

	def praising_lights(self, loop):

		time.sleep(0.1)


	def praising_mov(self, loop, name):
		ozobotClient = self.ozobotClient

		time.sleep(1.5)
		playSound("praising") #12 bc praise
		# name = self.checkName(self.actualSpeaker)
		playSound (name)
		time.sleep(2)
		loop.run_until_complete(drive(ozobotClient,100,100,2))
		time.sleep(2)
		loop.run_until_complete(drive(ozobotClient,-100,-100,2))
		time.sleep(2)
		loop.run_until_complete(stop(ozobotClient))

		time.sleep(1)

	'''
	******************************** mixedup **************************************
	'''

	def mixedup(self, loop, actualSpeaker, nextSpeaker, otherSpeaker):

		self.mixedup_lights(loop, True, actualSpeaker, nextSpeaker, otherSpeaker)
		#time.sleep(1)
		self.mixedup_mov(loop)
		time.sleep(2)
		#mixedup_lights(ozobotClient, loop, False, spID1, spID2, spID3)

	def mixedup_lights(self, loop, firstTime, actualSpeaker, nextSpeaker, otherSpeaker):
		ozobotClient = self.ozobotClient
		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
		time.sleep(0.1)
		c1,c2,c3 = self.checkColour(actualSpeaker)
		c4, c5, c6 = self.checkColour(nextSpeaker)
		c7, c8, c9 = self.checkColour(otherSpeaker)

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,c7,c8,c9))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,1,c7,c8,c9))

		time.sleep(0.1)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,c7,c8,c9))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,1,c7,c8,c9))

		time.sleep(0.1)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,c7,c8,c9))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,32,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,1,c7,c8,c9))

		if not firstTime :
			loop.stop()

	def mixedup_mov(self, loop):

		time.sleep(1.5)
		playSound("mixedup") # 14 clear sound confused
		time.sleep(3)



	'''
	******************************** confused **************************************
	'''

	def confused(self, loop, actualSpeaker, nextSpeaker, otherSpeaker):
		self.confused_lights(loop, True, actualSpeaker, nextSpeaker, otherSpeaker)
		time.sleep(1)
		self.confused_mov(loop)
		time.sleep(2)
		self.confused_lights(loop, False, actualSpeaker, nextSpeaker, otherSpeaker)

	def confused_lights(self, loop, firstTime, actualSpeaker, nextSpeaker, otherSpeaker):
		ozobotClient = self.ozobotClient
		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.1)
		c1,c2,c3 = self.checkColour(actualSpeaker)
		c4, c5, c6 = self.checkColour(nextSpeaker)
		c7, c8, c9 = self.checkColour(otherSpeaker)

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,c7,c8,c9))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,1,c7,c8,c9))

		time.sleep(0.1)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,32,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,c7,c8,c9))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,1,c7,c8,c9))

		time.sleep(0.1)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,c7,c8,c9))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,c1,c2,c3))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,32,c4,c5,c6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,1,c7,c8,c9))

		if not firstTime :
			loop.stop()

	def confused_mov(self, loop):
		ozobotClient = self.ozobotClient
		loop.run_until_complete(spin_left(ozobotClient,2000,2))

		loop.run_until_complete(spin_right(ozobotClient,2000,2))

		time.sleep(1.5)
		playSound("confused2") #16

		time.sleep(1.3)

	'''
	******************************** endwarning **************************************
	'''

	def endwarning(self, loop, actualSpeaker):

		playSound("warning2") # 18
		self.endwarning_lights(loop, True, actualSpeaker)
		time.sleep(1)
		self.endwarning_mov(loop)
		time.sleep(2)
		self.endwarning_lights(loop, False, actualSpeaker)

	def endwarning_lights(self, loop, firstTime, actualSpeaker):
		ozobotClient = self.ozobotClient
		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.1)
		loop.run_until_complete(changeAllLights(ozobotClient,0,0,0))

		c1,c2,c3 = self.checkColour(actualSpeaker)

		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))
		loop.run_until_complete(turnOffAllLights(ozobotClient))

		time.sleep(0.1)

		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))
		loop.run_until_complete(turnOffAllLights(ozobotClient))

		time.sleep(0.1)

		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))
		loop.run_until_complete(turnOffAllLights(ozobotClient))

		time.sleep(0.1)
		loop.run_until_complete(changeAllLights(ozobotClient,123,70,6))
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))

		time.sleep(0.1)
		loop.run_until_complete(changeAllLights(ozobotClient,123,70,6))
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(changeAllLights(ozobotClient,c1,c2,c3))
		time.sleep(1)

		if not firstTime :
			loop.stop()

	def endwarning_mov(self, loop):

		time.sleep(1.5)
		playSound("ewarningfinal") # 18
		time.sleep(1.3)
		time.sleep(1)

	'''
	******************************** goodbye **************************************
	'''

	def goodbye(self, loop):
		playSound("begin") #20
		time.sleep(2)
		self.goodbye_lights(loop, True)
		time.sleep(1)
		self.goodbye_mov(loop)
		time.sleep(2)
		self.goodbye_lights(loop, False)

	def goodbye_lights(self, loop, firstTime):
		ozobotClient = self.ozobotClient
		if firstTime :
			loop.run_until_complete(turnOffAllLights(ozobotClient))
			loop.run_until_complete(changeLight(ozobotClient,128, 0, 0,0))
			time.sleep(0.5)
		loop.run_until_complete(changeAllLights(ozobotClient,123,70,6))
		loop.run_until_complete(changeLight(ozobotClient,128,0,0,0))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))


		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))


		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))


		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,0,0,0))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,0,0,0))

		time.sleep(0.1)
		loop.run_until_complete(changeLight(ozobotClient,32,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,16,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,8,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,4,123,70,6))
		time.sleep(0.05)
		loop.run_until_complete(changeLight(ozobotClient,2,123,70,6))

		if not firstTime:
			loop.stop()

	def goodbye_mov(self, loop):
		ozobotClient = self.ozobotClient
		loop.run_until_complete(spin_left(ozobotClient,2000,2))
		playSound("bye") #20
		time.sleep(6)
		loop.run_until_complete(turnOffAllLights(ozobotClient))
		loop.run_until_complete(stop(ozobotClient))

	'''
	******************************** END  **************************************
	'''
	def end(self, loop):
		print("end") #20
		loop.run_until_complete(turnOffAllLights(self.ozobotClient))
		loop.run_until_complete(stop(self.ozobotClient))
	'''
	******************************** NEUTRAL **************************************
	'''
	def neutral(self, loop ):
		ozobotClient = self.ozobotClient
		loop.run_until_complete(changeLight(ozobotClient,1,255,255,255))
		loop.run_until_complete(changeLight(ozobotClient,2,255,255,255))
		loop.run_until_complete(changeLight(ozobotClient,4,255,255,255))
		loop.run_until_complete(changeLight(ozobotClient,8,255,255,255))
		loop.run_until_complete(changeLight(ozobotClient,16,255,255,255))
		loop.run_until_complete(changeLight(ozobotClient,32,255,255,255))
		time.sleep(1)
		if count%4 == 1:
			loop.run_until_complete(spin_left(ozobotClient,700,2))
		elif count%4 == 2:
			loop.run_until_complete(spin_left(ozobotClient,700,2))
		elif count%4 == 3:
			loop.run_until_complete(spin_left(ozobotClient,700,2))
		loop.run_until_complete(drive(ozobotClient, 700, 700,3))


#===============================================================================
#
#                                   SOUND
#
#===============================================================================

def playSound(expression):
	pathToFile = "Sounds/" + expression + ".wav"
	wave_obj = sa.WaveObject.from_wave_file(pathToFile)
	play_obj = wave_obj.play()

