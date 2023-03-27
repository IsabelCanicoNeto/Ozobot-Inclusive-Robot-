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
import random
from OzobotInclusivo import *



#UUID = "001"
# p = True
# comportamento = False





class activityRobot():
	def __init__(self, start_time = datetime.datetime.now(), condition="inclusive", behavior_cond="explicit", speakerID1 = 1, speakerID2 = 2, speakerID3 = 3, name1 = "nome", name2 = "nome", name3 = "nome", state="empty", p = True):

		# condition
		self.condition = condition
		self.startTime = start_time
		self.behavior_cond = behavior_cond

		# robot ozo Evo

		if self.condition == "baseline":
			self.robot = -1
		else:
			self.robot = ozoRobot(start_time, condition, behavior_cond, speakerID1, speakerID2, speakerID3, p)
		self.robot_log = []

		# speakers information

		self.speakerID1 = speakerID1
		self.speakerID2 = speakerID2
		self.speakerID3 = speakerID3
		self.name1 = name1
		self.name2 = name2
		self.name3 = name3

		# conversation information
		self.actualSpeaker = speakerID1
		self.nextSpeaker = speakerID2
		self.otherSpeaker = speakerID3
		self.newSpeaker = 0



		# inclusion metrica
		self.belonginessID1 = 0.0
		self.belonginessID2 = 0.0
		self.belonginessID3 = 0.0

		self.speakingTimeID1 = 0.0
		self.speakingTimeID2 = 0.0
		self.speakingTimeID3 = 0.0

		self.speakingInterruptTimeID1 = 0.0 # time ID1 interrupt
		self.speakingInterruptTimeID2 = 0.0 # time ID2 interrupt
		self.speakingInterruptTimeID3 = 0.0 # time ID3 interrupt

		self.speakingInterruptedbyTimeID1 = 0.0 # time ID1  was interrupted by others
		self.speakingInterruptedbyTimeID2 = 0.0 # time ID2 was interrupted by others
		self.speakingInterruptedbyTimeID3 = 0.0 # time ID3 was interrupted by others

		# state
		self.state = state
		self.previousState="empty"
		self.startState = time.time()


		# logging values
		self.activatedExpression = {}
		self.logExpression = []
		self.logStates = []
		self.logTimePerExpression = []
		self.count = 0
		self.p = p # print flag

		print("inicio")
		print(self.robot)

		# configuration values
		self.minspeech = 1.0 # number of seconds to evaluate new expression
		self.minspeech2move = 3.0 # number of seconds to evaluate a move in talking state ( organic speaker change or hearing, praising , TE or mixed-up)
		self.minhearing = 10.0 # number of speaking seconds to evaluate hearing expression
		self.minpraising = 15.0 # number of speaking seconds to evaluate praising expression
		self.minWTE = 90.0 # number of speaking seconds to evaluate warning to TE
		self.minTE = 105.0 # number of speaking seconds to evaluate TE
		self.minoverlap = 2* self.minspeech2move # number of seconds to evaluate overlap in talking state
		self.minWoverlap = self.minspeech2move # number of seconds to evaluate overlap in talking state

		self.minidle = 5.0 # number of seconds to evaluate new expression after idle
		self.minidlehearing = 10.0 # number of seconds to evaluate hearing in idle state
		self.minidleWTE = 15.0 # number of seconds to evaluate warning to TE in idle state
		self.minidleTE = 20.0 # number of seconds to evaluate warning to TE in idle state


		self.slowpace = False
	# loop.run_until_complete(self.connectRobot())
		# loop.stop()


	def finishActivity(self): # validar com erros

		logTotalTimePerExpression = {}

		if self.condition != "baseline" : self.robot.closeRobot()

		for (e,d) in self.logTimePerExpression:
			if e not in logTotalTimePerExpression.keys():
				logTotalTimePerExpression[e] = d
			else:
				logTotalTimePerExpression[e] = logTotalTimePerExpression[e] + d

		name = str(self.startTime)

		file = "Logs\\" + "ACT" + name + ".log"
		logging.basicConfig(filename=file, level=logging.DEBUG)
		logging.info("======CONDITION======")
		logging.info(self.condition)
		logging.info("======Behaviour======")
		logging.info(self.behavior_cond)
		logging.info("======Expressions ======")
		logging.info(self.logExpression)
		#logging.info("======ROOM CHANGES======")
		# logging.info(logRoomEntrances)
		# VALIDAR TEMPOS POR SPEAKER, STATE ....
		logging.info("======Expressions TIMES======")
		logging.info(self.logTimePerExpression)
		#logging.info("======ROOM TOTAL TIMES======")
		#logging.info(logTotalTimePerRoom)

		self.robot_log = []
		self.robot_log.append(self.condition)
		self.robot_log.append(self.behavior_cond)
		self.robot_log.append(self.logExpression)
		self.robot_log.append(self.logTimePerExpression)




	def checkFileName(self):
		files = listdir('Logs')

		if len(files) == 0:
			return "1"
		else:
			splitedFiles = []
			for f in files:
				name = f.split('.')[0]
				splitedFiles.append(name)
			splitedFiles.sort()
			numberPart = splitedFiles[-1]
			#numberPart = files[-1].split('.')[0]
			number = int(numberPart) + 1
			return str(number)

#===============================================================================
#
#                              Situation analysis
#
#===============================================================================


	def checknextactivity(self, statusSpeech, startState, overlap, Speaker, other_mic1ID, other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime, speechduration):


		if statusSpeech == "idle":
			triggerExp = round (speechduration % self.minidle, 1)
			# if self.p : print ("start checking idle expression")
			#print (f"duration {speechduration} min speech {self.minspeech} and ratio {speechduration % self.minspeech} and trigger {triggerExp}")
			if triggerExp == 0.0 : # x seconds minimium for checking new expression   eg 3.0
				# print (f"duration speech {speechduration}")
				if self.p : print ("ACT: start checking idle expression para mover ")
				atualtime = time.time()
				self.state = statusSpeech
				self.startState = startState
				# todo include idle reactions
				durationState = atualtime - self.startState
				goAheadHearing, goAheadPraising, goAheadTEW, goAheadTE = self.validateNextExpr (statusSpeech, Speaker, other_mic1ID, other_mic2ID, durationState)
				if goAheadTE :
					goAhead = self.func ("turnexchange")
					#Speaker = self.nextSpeaker
					if goAhead : self.updateSpeakerTE(Speaker, other_mic1ID, other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime)
				elif goAheadTEW :
					goAhead = self.func ("tewarning")
				#elif goAheadPraising :
					#goAhead = self.func ("praising")
				elif goAheadHearing :
					print ("ACT ERR : ")
					print("ACT: Speaker 1: " + str(self.actualSpeaker) + " Speaker 2: " + str(self.nextSpeaker) + " Speaker 3: " + str(self.otherSpeaker) + " New speaker" + str(self.newSpeaker) )
					print("ACT: Speaker 1: " + str(Speaker)+ " Speaker 2: " + str(other_mic1ID) + " Speaker 3: " + str(other_mic2ID) + " New speaker" + str(self.newSpeaker) )
					goAhead = self.func ("hearing")

		if statusSpeech == "talking":
			triggerExp = round (speechduration % self.minspeech, 1)
			#print (f"duration {speechduration} min speech {self.minspeech} and ratio {speechduration % self.minspeech} and trigger {triggerExp}")

			if triggerExp == 0.0 : # x seconds minimium for checking new expression   eg 1.0
				# print (f"duration speech {speechduration}")
				if self.p : print ("ACT: start checking talking expression")
				# if overlap : self.func("mixedup") # toDo adicionar confused after delta time
				self.updateSpeakingTime (Speaker, other_mic1ID, other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime)
				self.state = statusSpeech
				self.startState = startState
				if Speaker != self.actualSpeaker: # mudou o speaker
					self.updateInterruptSpeakingTime(Speaker, other_mic1ID, other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime)
					if self.p : print (f"ACT: new speaker from {self.actualSpeaker} to {Speaker} , duração discurso {speechduration}")
					if speechduration >= self.minspeech2move : # minimun to assume a move 3.0s
						# if self.p :
						print (f"ACT:  change from {self.actualSpeaker} to {Speaker} , duração discurso {speechduration}")
						self.newSpeaker = Speaker
						self.startState = startState
						if not overlap :
							goAhead = self.func("changespeaker")
							# if goAhead :
							self.updateSpeaker(Speaker, other_mic1ID, other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime)
							print("ACT: final change speaker -> Speaker 1: " + str(self.actualSpeaker) + " Speaker 2: " + str(self.nextSpeaker) + " Speaker 3: " +str(self.otherSpeaker) + " New speaker" + str(self.newSpeaker) )
						else:
							triggerExpOverlap = round (speechduration % self.minoverlap, 1)
							triggerExpWOverlap = round (speechduration % self.minWoverlap, 1)
							if triggerExpOverlap == 0.0 :
								goAhead = self.func("confused")
							elif triggerExpWOverlap == 0.0 :
								goAhead = self.func("mixedup")

						#todo validar se os tempos ainda estão atualizados, pois só atualiza no fim do changespeaker
				else :
					atualtime = time.time()
					durationState = atualtime - startState
					goAheadHearing, goAheadPraising, goAheadTEW, goAheadTE = self.validateNextExpr (statusSpeech, Speaker, other_mic1ID, other_mic2ID, durationState)
					if goAheadTE :
						goAhead = self.func ("turnexchange")
						#Speaker = self.nextSpeaker
						if goAhead : self.updateSpeakerTE (Speaker, other_mic1ID, other_mic2ID, mic_speakingTime, othermicID1_speakingTime, othermicID2_speakingTime)
					elif goAheadTEW :
						goAhead = self.func ("tewarning")
					elif goAheadPraising :
						goAhead = self.func ("praising")
						if goAhead : self.updateBelonginessRate(Speaker)
					elif goAheadHearing :
						# hearing ou engaging (with BC)
						goAhead = self.func ("engaging")


	def validateNextExpr (self, statusSpeech, Speaker, other_mic1ID, other_mic2ID, durationState):

		if statusSpeech == "idle":
			triggerExpHearing = round (durationState % self.minidlehearing, 1)
			triggerExpPraising = 0.1 # no praising
			triggerExpWTE = round (durationState % self.minidleWTE, 1)
			triggerExpTE = round (durationState % self.minidleTE, 1)
		else :
			triggerExpHearing = round (durationState % self.minhearing, 1)
			triggerExpPraising = round (durationState % self.minpraising, 1)
			triggerExpWTE = round (durationState % self.minWTE, 1)
			triggerExpTE = round (durationState % self.minTE, 1)

		self.slowpace = self.checkBelonginessRateFlag(Speaker, other_mic1ID, other_mic2ID)

		if triggerExpTE == 0.0 :
			return False, False, False, True

		if triggerExpWTE == 0.0 :
			return False, False, True, False

		if triggerExpPraising == 0.0 :
			return False, True, False, False


		if triggerExpHearing == 0.0 :
			return True, False, False, False

		return False, False, False, False


	def checkBelonginessRateFlag(self, speaker1, speaker2, speaker3):

		if self.condition == "inclusive":
			belongRateSP1 = self.returnBelonginessRate(speaker1)
			belongRateSP2 = self.returnBelonginessRate(speaker2)
			belongRateSP3 = self.returnBelonginessRate(speaker3)
			#if self.p : print("ACT: belonginess rate speaker " + str(belongRateSP1) + " speaker 2: " + str(belongRateSP2) + " speaker 3: " + str(belongRateSP3))
			if (belongRateSP1 < belongRateSP2) and (belongRateSP1 < belongRateSP3):
				# least belonginess RAte child

				return True
			else:
				# not the least belonginess RAte child
				return False
		else:
			return False  # assume the some motivation to all participants


	def returnBelonginessRate (self, speakerID):
		if speakerID == self.speakerID1 :
			return self.belonginessID1
		if speakerID == self.speakerID2 :
			return self.belonginessID2
		if speakerID == self.speakerID3 :
			return self.belonginessID3

	def updateBelonginessRate (self, speakerID):
		if speakerID == self.speakerID1 :
			self.belonginessID1 += 1.0
		if speakerID == self.speakerID2 :
			self.belonginessID2 += 1.0
		if speakerID == self.speakerID3 :
			self.belonginessID3 += 1.0

	def updateInterruptSpeakingTime (self, speaker1, speaker2, speaker3, speakingTime1, speakingTime2, speakingTime3):
		# record time child interrupted and was interrupted by
		if speaker1 != self.actualSpeaker :

			if speaker1 == self.speakerID1 : self.speakingInterruptTimeID1 += self.minspeech
			if speaker1 ==  self.speakerID2 : self.speakingInterruptTimeID2 += self.minspeech
			if speaker1 ==  self.speakerID3 : self.speakingInterruptTimeID3 += self.minspeech
			if self.actualSpeaker == self.speakerID1 : self.speakingInterruptedbyTimeID1 += self.minspeech
			if self.actualSpeaker ==  self.speakerID2 : self.speakingInterruptedbyTimeID2 += self.minspeech
			if self.actualSpeaker ==  self.speakerID3 : self.speakingInterruptedbyTimeID3 += self.minspeech

	def updateSpeakingTime (self, speaker1, speaker2, speaker3, speakingTime1, speakingTime2, speakingTime3):

		if speaker1 == self.speakerID1 : self.speakingTimeID1 = speakingTime1
		else :
			if speaker1 == self.speakerID2 : self.speakingTimeID2 = speakingTime1
			else:  self.speakingTimeID3 = speakingTime1

		if speaker2 == self.speakerID1 : self.speakingTimeID1 = speakingTime2
		else :
			if speaker2 == self.speakerID2 : self.speakingTimeID2 = speakingTime2
			else:  self.speakingTimeID3 = speakingTime2

		if speaker3 == self.speakerID1 : self.speakingTimeID1 = speakingTime3
		else :
			if speaker3 == self.speakerID2 : self.speakingTimeID2 = speakingTime3
			else : self.speakingTimeID3 = speakingTime3


	def updateSpeaker (self, Speaker, other_mic1ID, other_mic2ID, speakingTime1, speakingTime2, speakingTime3):

		oldSpeaker = self.actualSpeaker
		self.actualSpeaker = Speaker
		self.newSpeaker = 0

		if self.condition == "inclusive":
			if speakingTime2 <= speakingTime3 :
				self.nextSpeaker = other_mic1ID
				self.otherSpeaker = other_mic2ID
			else :
				self.nextSpeaker = other_mic2ID
				self.otherSpeaker = other_mic1ID

		if self.condition == "control":
			listspeakers = []
			listspeakers.append (other_mic1ID)
			listspeakers.append (other_mic2ID)
			nextSpeaker = random.choice(listspeakers)
			if nextSpeaker == other_mic1ID:
				self.nextSpeaker = other_mic1ID
				self.otherSpeaker = other_mic2ID
			else :
				self.nextSpeaker = other_mic2ID
				self.otherSpeaker = other_mic1ID


	def updateSpeakerTE (self, Speaker, other_mic1ID, other_mic2ID, speakingTime1, speakingTime2, speakingTime3):

		if Speaker == self.nextSpeaker:
			sp2ID = other_mic1ID
			sp2t = speakingTime2
			sp3ID = other_mic2ID
			sp3t = speakingTime3

		if other_mic1ID == self.nextSpeaker:
			sp2ID = Speaker
			sp2t = speakingTime1
			sp3ID = other_mic2ID
			sp3t = speakingTime3

		if other_mic2ID == self.nextSpeaker:
			sp2ID = Speaker
			sp2t = speakingTime1
			sp3ID = other_mic1ID
			sp3t = speakingTime2

		oldSpeaker = self.actualSpeaker
		#if oldSpeaker == Speaker:
		#	print (f" no TE {self.actualSpeaker} to {Speaker}  - no TE")
		#	return

		self.actualSpeaker = self.nextSpeaker
		self.newSpeaker = 0

		if self.condition == "inclusive":
			if sp2t < sp3t :
				self.nextSpeaker = sp2ID
				self.otherSpeaker = sp3ID
			else :
				self.nextSpeaker = sp3ID
				self.otherSpeaker = sp2ID

		if self.condition == "control":
			listspeakers = []
			listspeakers.append (sp2ID)
			listspeakers.append (sp3ID)
			nextSpeaker = random.choice(listspeakers)
			if nextSpeaker == sp2ID:
				self.nextSpeaker = sp2ID
				self.otherSpeaker = sp3ID
			else :
				self.nextSpeaker = sp3ID
				self.otherSpeaker = sp2ID


	#===============================================================================
	#
	#                              ROBOT Expression
	#
	#===============================================================================

	def func(self, expression):
		if self.condition == "baseline" : return False
		exp, goAhead = self.registerExpression(expression)
		# print (f"condition {self.condition}")

		#DOUBLE-CLICK
		if exp == "end":
			if goAhead == False:
				print("ACT: tried to end but robot is still doing stuff")
			else:
				#endingLoop = asyncio.new_event_loop()
				self.finishActivity()
				actualSpeakername = self.checkName(self.actualSpeaker)
				nextSpeakername = self.checkName(self.nextSpeaker)
				otherSpeakername = self.checkName(self.otherSpeaker)
				self.robot.executeExpression(expression, self.actualSpeaker, actualSpeakername, self.nextSpeaker, nextSpeakername, self.otherSpeaker, otherSpeakername, False)
				if self.p : print("ACT: played exoression " + expression)
		#finishActivity()
		else:

			if goAhead:
				#expressionLoop = asyncio.new_event_loop()
				actualSpeakername = self.checkName(self.actualSpeaker)
				nextSpeakername = self.checkName(self.nextSpeaker)
				otherSpeakername = self.checkName(self.otherSpeaker)

				nextSpeaker = self.nextSpeaker
				# if organicly change speaker the next speaker will be newSpeaker
				if self.newSpeaker != 0 :
					nextSpeaker = self.newSpeaker
					nextSpeakername = self.checkName(self.newSpeaker)


				if self.condition == "inclusive":
					print("ACT: Inclusive condition " + str(self.behavior_cond) + ", " + str(self.count), "expression " + expression)
					self.robot.executeExpression(expression, self.actualSpeaker, actualSpeakername, nextSpeaker, nextSpeakername, self.otherSpeaker, otherSpeakername, self.slowpace)
					self.count = self.count + 1
				elif self.condition == "control":
					print("ACT: Control condition " + str(self.behavior_cond) + ", " + str(self.count) +
						  "expression" + expression)
					self.robot.executeExpression(expression, self.actualSpeaker, actualSpeakername, nextSpeaker, nextSpeakername, self.otherSpeaker, otherSpeakername, self.slowpace)
					self.count = self.count + 1

				if self.p : print("ACT: played exoression " + expression)

		return goAhead


	def registerExpression(self, expressionID):
		#Register all button presses, even those who did nothing
		now = datetime.datetime.now()

		goAhead = True
		actualSpeakerBelonginessRate = self.returnBelonginessRate(self.actualSpeaker)

		if expressionID == "praising" and self.condition == "inclusive" and self.slowpace == False :
			if self.p: print("\nACT: expression : no praising , goAhead: " + str(goAhead))
			self.logExpression.append(("nopraising", now, goAhead, self.actualSpeaker, self.nextSpeaker, self.otherSpeaker, self.newSpeaker, self.state, str(actualSpeakerBelonginessRate)))
			goAhead = False
		else:
			goAhead = self.checkRobotBehavior(expressionID, now)
			self.logExpression.append((expressionID, now, goAhead, self.actualSpeaker, self.nextSpeaker, self.otherSpeaker, self.newSpeaker, self.state, str(actualSpeakerBelonginessRate)))

		# if p:
		print("\nACT: state activated : " + str(self.state) + " expression activated: " + str(expressionID) + str(now))
		print("ACT: Speaker 1: " + str(self.actualSpeaker) + " Speaker 2: " + str(self.nextSpeaker) + " Speaker 3: " + str(self.otherSpeaker) + " New speaker" + str(self.newSpeaker) + " BelonginessRate " + str(actualSpeakerBelonginessRate))
		print("\nACT: expression : " + str(expressionID)  , "goAhead: " + str(goAhead))

		return expressionID, goAhead



	def checkRobotBehavior(self, expression, presentTime):

		if self.p: print("ACT: checking if i can go")
		#goAhead = False validar
		goAhead = True
		if expression == "end":
			if ( len(self.logExpression)==1 and self.logExpression[0][0]!="end" ) or len(self.logExpression) > 1 :
				if self.p :
					print("ACT: entrei no novo if")
					print(self.logExpression)

				for (e,t,g, sp1,sp2,sp3,nsp, s, br) in reversed(self.logExpression):
					if e != "end":
						if g == True: break
				prev_expression = e
				before = self.activatedExpression[prev_expression]
				delta = presentTime - before

				#if condition == "inclusive": okTime = checkExpressionTime(prev_expression)
				#elif condition == "control": okTime = checkNeutralTime()

				okTime = self.checkExpressionTime(prev_expression)

				if delta.total_seconds() > okTime:
					if self.p :  print ("ACT: check expression time " + str(okTime) + "versus time done" + str(delta.total_seconds()))
					goAhead = True
		else:
			if len(self.logStates) == 0:
				self.activatedExpression[expression] = presentTime
				goAhead = True

			else:
				if self.logStates[-1][0] != expression:
					prev_expression = self.logStates[-1][0]
					timeExpressionStarted = self.activatedExpression[prev_expression]
					#print("timeEmotionStarted: " + str(timeEmotionStarted))

					time = self.checkExpressionTime(prev_expression)
					#elif condition == "naoEmotivo": time = checkNeutralTime()

					okTime = timeExpressiontarted + datetime.timedelta(0,time)

					#print("oktime: " + str(okTime))
					if presentTime > okTime:
						if self.p :  print ("ACT: check expression time " + str(okTime) + "versus time done" + str(presentTime))
						self.activatedExpression[expression] = presentTime
						goAhead = True
					#print("a emocao anterior: " + prev_emotion + "ja acabou, entao vou comecar eu")

				elif self.logStates[-1][0] == expression:
					#duploclique
					before = self.activatedExpression[expression]
					delta = presentTime - before

					okTime = self.checkExpressionTime(expression)
					if self.p :  print ("ACT: check expression time " + str(okTime) + "versus time done" + str(delta.total_seconds()))
					if delta.total_seconds() > okTime:
						self.activatedExpression[emotion] = presentTime
						goAhead = True
					#print("repetir a emocao: " + emotion)
		return goAhead

#===============================================================================
#
#                             CONFIGURATIONS
#
#===============================================================================

	def checkExpressionTime(self, expression):
		if expression == "greetings" : return 25 #15
		elif expression == "firstspeaker" : return 15 #25
		elif expression == "turnexchange" : return 20 #50
		elif expression == "changespeaker" : return 20
		elif expression == "hearing" : return 20 #40
		elif expression == "tewarning" : return 20 #25
		elif expression == "engaging" : return 20 #25
		elif expression == "praising" : return 40 #25
		elif expression == "mixedup" : return 35 #25
		elif expression == "confused" : return 35 #25
		elif expression == "endwarning" : return 20 #25
		elif expression == "goodbye" : return 50 #25
		elif expression == "end" : return 25 #25

	def checkStateTime(self, expression):
		# State least time is by default expression time plus 20
		if expression == "greetings" : return 90 #15
		elif expression == "firstspeaker" : return 80 #25
		elif expression == "turnexchange" : return 80 #50
		elif expression == "hearing" : return 40 #40
		elif expression == "tewarning" : return 40 #25
		elif expression == "engaging" : return 40 #25
		elif expression == "praising" : return 60 #25
		elif expression == "mixedup" : return 55 #25
		elif expression == "confused" : return 55 #25
		elif expression == "endwarning" : return 40 #25
		elif expression == "goodbye" : return 70 #25
		elif expression == "end" : return 45 #25

	def checkIdleTime(self):
		return 10

	def checkName(self, speaker):

		if speaker == self.speakerID1: # name1
			return self.name1
		if speaker == self.speakerID2: # name2
			return self.name2
		if speaker == self.speakerID3: # name3
			return self.name3


	def updateTimePerExpression(self, expresssion, now): # avaliar se é necessário ou apagar

		if self.previousState == "empty":
			previousRoom = expression
			logTotalTimePerRoom[emotion] = now
		else:
			if previousRoom != emotion:
				#	if emotion not in logTimePerRoom.keys():
				delta = now - logTotalTimePerRoom[previousRoom]
				logTotalTimePerRoom[previousRoom] = delta
				logTotalTimePerRoom[emotion] = now
				if previousRoom in logTotalTimePerRoom.keys():
					delta = now - activatedButtons[previousRoom]
					logTotalTimePerRoom[previousRoom] = logTotalTimePerRoom[previousRoom] + delta
				previousRoom = emotion

	def printActMetrics(self):
		print("Activity metrics")

		print("speaker_id 1 {}".format(self.speakerID1))
		print("speaking time {}".format(self.speakingTimeID1))
		print("speaking Interrupted by id 1 {}".format(self.speakingInterruptTimeID1))
		print("speaking id 1 Interrupted by others  {}".format(self.speakingInterruptedbyTimeID1))
		print("belonginess rate   {}".format(self.belonginessID1))

		print("speaker_id 2 {}".format(self.speakerID2))
		print("speaking time {}".format(self.speakingTimeID2))
		print("speaking Interrupted by id 2 {}".format(self.speakingInterruptTimeID2))
		print("speaking id 2 Interrupted by others  {}".format(self.speakingInterruptedbyTimeID2))
		print("belonginess rate   {}".format(self.belonginessID2))


		print("speaker_id 3 {}".format(self.speakerID3))
		print("speaking time {}".format(self.speakingTimeID3))
		print("speaking Interrupted by id 3 {}".format(self.speakingInterruptTimeID3))
		print("speaking id 3 Interrupted by others  {}".format(self.speakingInterruptedbyTimeID3))
		print("belonginess rate   {}".format(self.belonginessID3))

	def logActMetrics(self):
		activity_logs = []
		name = str(self.startTime)
		file = "Logs\\" + "ACT" + name + ".log"
		logging.basicConfig(filename=file, level=logging.DEBUG)
		logging.info("====== starttime   ======")
		logging.info(str(self.startTime))
		logging.info("====== condition  ======")
		logging.info(str(self.condition))
		logging.info("====== behavior condition ======")
		logging.info(str(self.behavior_cond))

		logging.info("======SPEAKER 1 ======")
		logging.info(str(self.speakerID1))
		logging.info("======Speaking Time ======")
		logging.info(str(self.speakingTimeID1))
		logging.info("======Speaking Interrupted Count ======")
		logging.info(str(self.speakingInterruptTimeID1))
		logging.info("======Speaking Interruted by others Count ======")
		logging.info(str(self.speakingInterruptedbyTimeID1))
		logging.info("=====Belonginess ======")
		logging.info(str(self.belonginessID1))

		logging.info("======SPEAKER 2 ======")
		logging.info(str(self.speakerID2))
		logging.info("======Speaking Time ======")
		logging.info(str(self.speakingTimeID2))
		logging.info("======Speaking Interrupted Count ======")
		logging.info(str(self.speakingInterruptTimeID2))
		logging.info("======Speaking Interruted by others Count ======")
		logging.info(str(self.speakingInterruptedbyTimeID2))
		logging.info("=====Belonginess ======")
		logging.info(str(self.belonginessID2))

		logging.info("======SPEAKER 3======")
		logging.info(str(self.speakerID3))
		logging.info("======Speaking Time ======")
		logging.info(str(self.speakingTimeID3))
		logging.info("======Speaking Interrupted Count ======")
		logging.info(str(self.speakingInterruptTimeID3))
		logging.info("======Speaking Interruted by others Count ======")
		logging.info(str(self.speakingInterruptedbyTimeID3))
		logging.info("=====Belonginess ======")
		logging.info(str(self.belonginessID3))

		# logs

		activity_logs.append(str(self.speakerID1))
		activity_logs.append(str(self.speakingTimeID1))
		activity_logs.append(str(self.speakingInterruptTimeID1))
		activity_logs.append(str(self.speakingInterruptedbyTimeID1))
		activity_logs.append(str(self.belonginessID1))

		activity_logs.append(str(self.speakerID2))
		activity_logs.append(str(self.speakingTimeID2))
		activity_logs.append(str(self.speakingInterruptTimeID2))
		activity_logs.append(str(self.speakingInterruptedbyTimeID2))
		activity_logs.append(str(self.belonginessID2))

		activity_logs.append(str(self.speakerID3))
		activity_logs.append(str(self.speakingTimeID3))
		activity_logs.append(str(self.speakingInterruptTimeID3))
		activity_logs.append(str(self.speakingInterruptedbyTimeID3))
		activity_logs.append(str(self.belonginessID3))

		return activity_logs

#===============================================================================
#
#                                   MAIN
#
#===============================================================================

