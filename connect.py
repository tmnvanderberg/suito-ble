import asyncio
import json
from re import L

from bleak import BleakClient, BleakScanner

featureList = [
"Average Speed Supported",
"Cadence Supported",
"Total Distance Supported",
"Inclination Supported",
"Elevation Gain Supported",
"Pace Supported",
"Step Count Supported",
"Resistance Level Supported",
"Stride Count Supported",
"Expended Energy Supported",
"Heart Rate Measurement Supported",
"Metabolic Equivalent Supported",
"Elapsed Time Supported",
"Remaining Time Supported",
"Power Measurement Supported",
"Force on Belt and Power Output Supported",
"User Data Retention Supported"]

bikeDataList = [
"More Data",
"Average Speed",
"Instantaneous Cadence",
"Average Cadence",
"Total Distance",
"Resistance Level",
"Instantaneous Power",
"Average Power",
"Expended Energy",
"Heart Rate",
"Metabolic Equivalent",
"Elapsed Time",
"Remaining Time"
]

def find_gatt_uuid(gatt, description):
    for primary in gatt:
        if primary['description'] == description:
            return primary['uuid']
        for characteristic in primary['characteristics']:
            if characteristic['description'] == description:
                return characteristic['uuid']
    raise NameError("gatt undefined")

with open('output.json') as file:
    gatt = json.load(file)

async def enable_notifications(client, characteristic_uuid, callback):
    await client.start_notify(characteristic_uuid, callback)

async def dummySubCallback(sender: int, data: bytearray):
    print("notification received", sender, data);

async def bikeDataCallback(sender: int, data: bytearray):
    print("sender:", sender);
    for feature, byte in zip(bikeDataList, list(data)):
        print(feature, ":", byte)

def prettyPrintFeatures(featureList, byteList):
    for feature, byte in zip(featureList, byteList):
        print(feature, ":", byte)

def dummyCallback(characteristic, characteristicValue):
    print(characteristic, characteristicValue)

def fitnessFeaturesCallback(characteristic, characteristicValue):
    print(" = ", characteristic, " = ")
    prettyPrintFeatures(featureList, characteristicValue) 
    

subscriptions = {'Indoor Bike Data' : bikeDataCallback,
                 'Fitness Machine Status' : dummySubCallback,
                 'Training Status': dummySubCallback
                 }

reads = {
        'Supported Power Range' : dummyCallback,
        'Supported Resistance Level Range': dummyCallback,
        'Fitness Machine Feature': fitnessFeaturesCallback
        }

async def connect(deviceName):
    scanner = BleakScanner()
    devices = await scanner.discover()
    device = next((d for d in devices if d.name == deviceName), None)
    if device:
        client = BleakClient(device)
        await client.connect()
        print('connected')
        for characteristic, callback in reads.items():
            characteristic_value = await client.read_gatt_char(find_gatt_uuid(gatt, characteristic))
            callback(characteristic, list(characteristic_value))
        for characteristic, callback in subscriptions.items():
            await enable_notifications(client, find_gatt_uuid(gatt, characteristic), callback)
        print("entering loop")
        while True:
            await asyncio.sleep(1) 

device = "SUITO"
asyncio.run(connect(device))

