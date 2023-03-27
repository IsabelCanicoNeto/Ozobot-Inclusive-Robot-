import asyncio
import struct
from bleak import BleakScanner
from bleak import BleakClient
import time
import simpleaudio as sa



#===============================================================================
#
#                             CONNECTION FUNCTION
#
#===============================================================================

async def run():
    devices = await BleakScanner.discover()
    print("devices")
    for d in devices:
        if "Ozo" in d.name:
            print(d.address)
            print("aqui")
            print(d.name)
            print(d.metadata['uuids'])
            client = BleakClient(d.address)
            try:
                await client.connect()
                print(client.is_connected)

                #blocks random behaviors
                initialCommand = b"\x50\x02\x01"
                await client.write_gatt_char("8903136c-5f13-4548-a885-c58779136703", initialCommand, response=False)

                await behavior(client)

            except Exception as e:
                print(e)



#===============================================================================
#
#                             BEHAVIOR FUNCTIONS
#
#===============================================================================


async def behavior(client):
    '''for service in client.services:
        print("[Service] {0}: {1}".format(service.uuid, service.description))
        for char in service.characteristics:
            if "read" in char.properties:
                value = await client.read_gatt_char(char.uuid)
                print("characteristic: " + str(char) + ", value: " + str(value))
    '''
    a = await checkBattery(client)
    print(a)


    await asyncio.sleep(10)

    print("drive")
    await drive(client,400,400,2)
    print("spin left")
    await spin_left(client,90,5)
    print("lightsoff")
    await turnOffAllLights(client)




#===============================================================================
#
#                             MOVEMENT FUNCTIONS
#
#===============================================================================



async def drive(client,   left_speed: int, right_speed: int, time_secs: float):
    '''
    Responsible for driving ozobot evo
    args:
        - left_speed  : speed of left mmotor (not sure about the units)
        - right_speed : speed of right motor (not sure about the units)
        - time_secs   : duration of the movement (in seconds)
    '''
    #2500 IS REALLY FAST

    driveConstant = 64
    #    command = struct.pack('<Bhhh', driveConstant, left_speed, right_speed, 1000*time_secs)
    command = struct.pack('<Bhhh', driveConstant, left_speed, right_speed, int(time_secs * 1000) & 0xffff)
    await client.write_gatt_char("8903136c-5f13-4548-a885-c58779136702", command, response=False)
    return




async def spin(client, speed: int, time_secs: float):
    '''
    Responsible for spinning ozobot evo
    args:
        - speed     : speed of the spin (not sure about the units)
        - time_secs : duration of the movement (in seconds)
    '''

    await drive(client, speed, -speed, time_secs)




async def spin_left(client, speed: int, time_secs: float):
    '''
    Responsible for spinning left
    args:
        - speed     : speed of the spin (not sure about the units)
        - time_secs : duration of the movement (in seconds)
    '''
    await spin(client, -abs(speed), time_secs)





async def spin_right(client, speed: int, time_secs: float):
    '''
    Responsible for spinning right
    args:
        - speed     : speed of the spin (not sure about the units)
        - time_secs : duration of the movement (in seconds)
    '''
    await spin(client, abs(speed), time_secs)


async def stop(client):
    """ Stops an ongoing move.
    """
    driveConstant = 64
    command = struct.pack('<Bhhh', driveConstant, 0, 0, 0)
    await client.write_gatt_char("8903136c-5f13-4548-a885-c58779136702", command, response=False)





#===============================================================================
#
#                             LIGHTS FUNCTIONS
#
#===============================================================================



async def changeLight(client, led:int , red:int , green:int , blue:int):
    '''
    Responsible for changing the lights' color on ozobot evo.
    args:
        - led : led's id
              1 -> top(0x01)
              2 -> left(0x02)
              4 -> center_left(0x04)
              8 -> center(0x08)
             16 -> center_right(0x10)
             32 -> right(0x20)
            128 -> rear(0x80)
            255 -> allLeds(0xff)

        - red   : red component(0-255)
        - green : green component(0-255)
        - bue   : blue component(0-255)
    '''

    lightsConstant = 68
    command = struct.pack('<BHBBB', lightsConstant, led, red, green, blue)
    await client.write_gatt_char("8903136c-5f13-4548-a885-c58779136703", command, response=False)



async def changeAllLights(client, red: int, green: int, blue: int):
    '''
    Responsible for changing all the lights.
    args:
        - red   : red component(0-255)
        - green : green component(0-255)
        - bue   : blue component(0-255)
    '''

    await changeLight(client, 255, red, green, blue)






async def turnOffLight(client, led: int):
    '''
    Responsible for truning off the given light
    args:
        - led : led's id
              1 -> top(0x01)
              2 -> left(0x02)
              4 -> center_left(0x04)
              8 -> center(0x08)
             16 -> center_right(0x10)
             32 -> right(0x20)
            128 -> rear(0x80)
            255 -> allLeds(0xff)
    '''

    await changeLight(client, led, 0, 0, 0)




async def turnOffAllLights(client):
    '''
    Responsible for truning off all the lights
    '''
    await changeLight(client, 255, 0, 0, 0)



#===============================================================================
#
#                                   BATTERY
#
#===============================================================================
async def checkBattery(client):
    asciiValue = await client.read_gatt_char("00002a19-0000-1000-8000-00805f9b34fb")
    return ord(asciiValue)


#===============================================================================
#
#                                   SOUND
#
#===============================================================================

def playSound(file):
    '''
    Responsible for playing a sound file
    args:
        - file : path to the sound file, it has to be a .WAV file
    '''

    wave_obj = sa.WaveObject.from_wave_file(file)
    play_obj = wave_obj.play()
    play_obj.wait_done()    #faz com que o programa fique a espera que acabe, pode se tirar




#===============================================================================
#
#                                   MAIN
#
#===============================================================================

#
#print ("ola")
#loop = asyncio.get_event_loop()
#loop.run_until_complete(run())
#
