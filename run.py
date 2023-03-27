import argparse
import pathlib
from random import getrandbits
import matplotlib.pyplot as plt

from vadSpeech import *
from activityRobotAll import *
import numpy as np

#from activityRobotAll import *

def handle_int(sig, chunk):
    global leave, got_a_sentence
    leave = True
    got_a_sentence = True

# ############ #
# Presentation #
# ############ #



def plotmic(timeline, mic1_logs, mic2_logs, mic3_logs, ylabel, name):
    plt.clf()
    plt.xlabel('Microphones')
    plt.ylabel(ylabel)
    plt.plot(timeline, mic1_logs)
    plt.plot(timeline, mic1_logs)
    plt.plot(timeline, mic1_logs)
    plt.title(name)
    plt.savefig('%s.pdf' % name, bbox_inches='tight')
    plt.close()


def plotactivity(timeline, activty_logs, robot_log,  ylabel, name):
    plt.clf()
    plt.xlabel('Activity')
    plt.ylabel(ylabel)
    plt.plot(timeline, activty_logs, robot_log)
    plt.title(name)
    plt.savefig('%s.pdf' % name, bbox_inches='tight')
    plt.close()


def  plotrobotactivity(robot_log, ylabel, name):
    plt.clf()
    plt.xlabel('Robot Expression ')
    plt.ylabel(ylabel)
    plt.plot(timeline, robot_logs)
    plt.title(name)
    plt.savefig('%s.pdf' % name, bbox_inches='tight')
    plt.close()

#===============================================================================
#
#                                   MAIN
#
#===============================================================================


# signal.signal(signal.SIGINT, handle_int)
def main():


    # ####################
    # 1 - Configuration  #
    # ####################

    parser = argparse.ArgumentParser()

    parser.add_argument('condition', choices=[
        'inclusive',
        'control',
        "baseline"
    ], help="Which condition should the activity run?", default='inclusive')

    # type of behaviour
    parser.add_argument('-behavior_cond', choices=[
        'implicit',
        'explicit'
     ], help="Which condition should the activity run?", default='explicit')

    parser.add_argument('-numspeakers', help="Number of children speaking", type=int, default=3)
    parser.add_argument('-sessionDuration', help="Maximimum duration time (s) ", type=int, default=360) #1200 20m 600 10m

    # VAD configurations
    parser.add_argument('-deviceIDs', help="Mics IDs used.", nargs="+", default=[1, 2, 4])
    parser.add_argument('-silenceDb', help="Max db allowed to assume nonspeaking per speaker", nargs="+", default=[40.0, 40.0, 40.0])
#    parser.add_argument('-speakerTolerance', help="Number of padding to assume a speaker change (s) ", type=int, default=15)
#    parser.add_argument('-overlapTolerance', help="Number of chunks to assume an overlap (s)", type=int, default=10)

    # Robot Parameters
    parser.add_argument('-name', help="Name of the child for explicit reference", nargs="+", default=["ines", "filipa", "catarina"])
    #parser.add_argument('-idleTime', type=float, help="Time to maintain idle stage (s)", default=5.0)
    #parser.add_argument('-mixedupTime', type=float, help="Time to maintain mixedup stage (s)", default=10.0)
    #parser.add_argument('-confusedTime', type=float, help="Time to maintain confused stage (s)", default=10.0)
    #parser.add_argument('-maxspeechTime', type=float, help="Max time to maintain speechTime per user (s)", default=150.0) # 2.5 minutos



    # Miscellaneous
    parser.add_argument('-save_logs', default = True , help='Whether or not to log activity ')
    parser.add_argument('-debug_active', default = False , help='Whether or not to debug activity ')

    opt = parser.parse_args()

    # study condition
    condition = opt.condition
    behavior_cond = opt.behavior_cond
    endSession = False

    # init robot
    StartTime = time.time()
    activity = activityRobot(start_time = StartTime,
                             condition=condition,
                             behavior_cond=behavior_cond,
                             speakerID1 = 1,
                             speakerID2 = 2,
                             speakerID3 = 3,
                             name1 = opt.name[0],
                             name2 = opt.name[1],
                             name3 = opt.name[2],
                             state="empty",
                             p = opt.debug_active)
    # init microphones
    print ("StartTime")
    print (StartTime)
    print (datetime.datetime.now())
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(f"Current Time {current_time}")
    print(f"silence db  {opt.silenceDb[0]}")

    #create Vad objects - mics
    mic1 = vadSpeech(device_id=opt.deviceIDs[0], micID = 1, start_time=StartTime, silenceDb=opt.silenceDb[0], speakersfile_wave=opt.name[0], activity=activity, condition= condition)
    mic2 = vadSpeech(device_id=opt.deviceIDs[1], micID = 2, start_time=StartTime, silenceDb=opt.silenceDb[1], speakersfile_wave=opt.name[1], activity=activity, condition= condition)
    mic3 = vadSpeech(device_id=opt.deviceIDs[2], micID = 3, start_time=StartTime, silenceDb=opt.silenceDb[2], speakersfile_wave=opt.name[2], activity=activity, condition= condition)

    # update diferent mics . one per child
    mic1.other_mic1 = mic2
    mic1.other_mic2 = mic3
    mic1.other_mic1ID = 2
    mic1.other_mic2ID = 3

    mic2.other_mic1 = mic1
    mic2.other_mic2 = mic3
    mic2.other_mic1ID = 1
    mic2.other_mic2ID = 3

    mic3.other_mic1 = mic1
    mic3.other_mic2 = mic2
    mic3.other_mic1ID = 1
    mic3.other_mic2ID = 2

    activity.func("greetings")
    activity.func("firstspeaker")

    #start detecting sound
    print ("detect thread")
    mic1.detect_background()
    mic2.detect_background()
    mic3.detect_background()


    # end detecting sound
    endSession = False
    endWsession = False
    while not endSession :
        sessionRealDur = time.time() - StartTime
        if (sessionRealDur >= (opt.sessionDuration - 10)) and not endWsession:
            endWsession = True
            activity.func("goodbye")
        if sessionRealDur >= opt.sessionDuration:
            activity.func("end")
            endSession = True
            print("stop detecting")
            #mic1.leave = True
            #mic2.leave = True
            #mic3.leave = True

    mic1.stop_detecting()
    mic2.stop_detecting()
    mic3.stop_detecting()


    EndTime = time.time()
    print (datetime.datetime.now())
    t = time.localtime()
    endcurrent_time = time.strftime("%H:%M:%S", t)
    print(f"End Time {endcurrent_time}")
    """


    print ("inicio teste TE ")

    # teste TE 1:2
    print ("WTE 1 : 2")
    activity.func("tewarning")
    time.sleep(5)

    print ("TE 1 : 2")
    activity.func("turnexchange")

    # teste TE 2:3
    activity.actualSpeaker = activity.speakerID2
    activity.nextSpeaker = activity.speakerID3
    activity.otherSpeaker = activity.speakerID1

    print ("WTE 2 : 3")
    activity.func("tewarning")
    time.sleep(5)
    print ("TE 2 : 3")
    activity.func("turnexchange")


    # teste TE 3:2
    activity.actualSpeaker = activity.speakerID3
    activity.nextSpeaker = activity.speakerID2
    activity.otherSpeaker = activity.speakerID1

    print ("WTE 3 : 2")
    activity.func("tewarning")
    time.sleep(5)
    print ("TE 3 : 2")
    activity.func("turnexchange")

    # teste TE 2:1
    activity.actualSpeaker = activity.speakerID2
    activity.nextSpeaker = activity.speakerID1
    activity.otherSpeaker = activity.speakerID1

    print ("WTE 2 : 1")
    activity.func("tewarning")
    time.sleep(5)
    print ("TE 2 : 1")
    activity.func("turnexchange")

    # teste TE 1:3
    activity.actualSpeaker = activity.speakerID1
    activity.nextSpeaker = activity.speakerID3
    activity.otherSpeaker = activity.speakerID1

    print ("WTE 1 : 3")
    activity.func("tewarning")
    time.sleep(5)
    print ("TE 1 : 3")
    activity.func("turnexchange")

    # teste TE 3:1
    activity.actualSpeaker = activity.speakerID3
    activity.nextSpeaker = activity.speakerID1
    activity.otherSpeaker = activity.speakerID2

    print ("WTE 3 : 1")
    activity.func("tewarning")
    time.sleep(5)
    print ("TE 3 : 1")
    activity.func("turnexchange")
    
    print ("inicio teste CE ")

    # teste cE 1:3
    activity.actualSpeaker = activity.speakerID1
    activity.nextSpeaker = activity.speakerID3
    activity.otherSpeaker = activity.speakerID2
    print ("CE 1 : 3")
    activity.func("changespeaker")

    # teste cE 3:1
    activity.actualSpeaker = activity.speakerID3
    activity.nextSpeaker = activity.speakerID1
    activity.otherSpeaker = activity.speakerID2
    print ("CE 3 : 1")
    activity.func("changespeaker")

    # teste cE 1:2
    activity.actualSpeaker = activity.speakerID1
    activity.nextSpeaker = activity.speakerID2
    activity.otherSpeaker = activity.speakerID3
    print ("CE 1 : 2")
    activity.func("changespeaker")

    # teste cE 2:3
    activity.actualSpeaker = activity.speakerID2
    activity.nextSpeaker = activity.speakerID3
    activity.otherSpeaker = activity.speakerID1
    print ("CE 2 : 3")
    activity.func("changespeaker")

    # teste cE 3:2
    activity.actualSpeaker = activity.speakerID3
    activity.nextSpeaker = activity.speakerID2
    activity.otherSpeaker = activity.speakerID1
    print ("CE 3 : 2")
    activity.func("changespeaker")


    # teste cE 2:1
    activity.actualSpeaker = activity.speakerID2
    activity.nextSpeaker = activity.speakerID1
    activity.otherSpeaker = activity.speakerID3
    print ("CE 2 : 1")
    activity.func("changespeaker")

    print ("fim teste cores")

    print ("hearing ")
    activity.func("hearing")
    time.sleep(5)

    print ("engaging")
    activity.func("engaging")
    time.sleep(5)

    print ("praising")
    activity.func("praising")
    time.sleep(5)

    print ("confused")
    activity.func("mixedup")
    time.sleep(5)
    activity.func("confused")
    time.sleep(2)

    print ("end warning")
    activity.func("endwarning")

    time.sleep(5)
    print ("goodbye")
    activity.func("goodbye")
    time.sleep(2)

    print ("end")
    activity.func("end")
    time.sleep(5)

    """

    # print speech metrics

    if opt.debug_active:
        mic1.printMicMetrics()
        mic2.printMicMetrics()
        mic3.printMicMetrics()
        activity.printActMetrics()
    if opt.save_logs :
        mic1_logs = []
        mic2_logs = []
        mic3_logs = []
        activity_logs = []
        robot_logs = []
        mic1_logs = mic1.logMicMetrics()
        mic2_logs = mic2.logMicMetrics()
        mic3_logs = mic3.logMicMetrics()
        activity_logs = activity.logActMetrics()


    # ############### #
    # 4 - Plot & Save #
    # ############### #

    if opt.save_logs:

        unique_id = getrandbits(64)

        print(f"*** Plotting and saving activity logs ***", end="", flush=True)
        # todo : if there is an additional condition add to the directory // add robot information
        plot_directory = f"plots/{opt.condition}/{behavior_cond}/{StartTime}"
        pathlib.Path(plot_directory).mkdir(parents=True, exist_ok=True)

        # todo : plots // add robot information
        # plotmic(timeline, mic1_logs, mic2_logs, mic3_logs, ylabel='Microphone', name=f"{plot_directory}/microphone_{unique_id}")
        # plotactivity(timeline, activity_logs, activity.robot_log, ylabel='Activity', name=f"{plot_directory}/activity_{unique_id}")
        # plotrobotactivity(timeline, activity.robot_log, ylabel='Robot Expression', name=f"{plot_directory}/activityrobot_{unique_id}")

        result_directory = f"results/{opt.condition}/{behavior_cond}"
        pathlib.Path(result_directory).mkdir(parents=True, exist_ok=True)

        with open(f"{result_directory}/final_logs_{StartTime}.txt", "w") as text_file:
            text_file.write(f"{opt.condition} {behavior_cond} {current_time} - {endcurrent_time}, {opt.name[0]} {opt.name[1]} {opt.name[2]}, {StartTime} - {EndTime}  ")

        print ("data frames ")
        print (mic1_logs)
        print (mic2_logs)
        print (mic3_logs)
        print (activity_logs)
        print (activity.robot_log)

        np.save(result_directory + f"/mic1_logs_{StartTime}.npy", np.array(mic1_logs, dtype=object))
        np.save(result_directory + f"/mic2_logs_{StartTime}.npy", np.array(mic2_logs, dtype=object))
        np.save(result_directory + f"/mic3_logs_{StartTime}.npy", np.array(mic3_logs, dtype=object))
        np.save(result_directory + f"/activity_logs_{StartTime}.npy", np.array(activity_logs, dtype=object))
        np.save(result_directory + f"/robot_logs_{StartTime}.npy", np.array(activity.robot_log, dtype=object))

        if not opt.debug_active : print(" (Done)\n", flush=True)



if __name__ == '__main__':
    main()