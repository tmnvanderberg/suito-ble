from fastapi import FastAPI

import asyncio
import json
import sys
import uvicorn

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
    "User Data Retention Supported",
]

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
    "Remaining Time",
]

app = FastAPI()

async def dummySubCallback(sender: int, data: bytearray):
    print("notification received", sender, data)


async def bikeDataCallback(sender: int, data: bytearray):
    print("sender:", sender)
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


subscriptions = {
    "Indoor Bike Data": bikeDataCallback,
    "Fitness Machine Status": dummySubCallback,
    "Training Status": dummySubCallback,
}

reads = {
    "Supported Power Range": dummyCallback,
    "Supported Resistance Level Range": dummyCallback,
    "Fitness Machine Feature": fitnessFeaturesCallback,
}


def find_gatt_uuid(gatt, description):
    for primary in gatt:
        if primary["description"] == description:
            return primary["uuid"]
        for characteristic in primary["characteristics"]:
            if characteristic["description"] == description:
                return characteristic["uuid"]
    raise NameError("gatt undefined")


class BikeDataService:
    def __init__(self):
        self.bikeData = {
            string: value for value, string in enumerate(bikeDataList, start=1)
        }
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)

    def notify_subscribers(self, name, value):
        for subscriber in self.subscribers:
            subscriber.bikeServiceUpdate(name, value)

    def set_value(self, name, value):
        self.bikeData[name] = value
        self.notify_subscribers(name, value)

    def get_value(self, name):
        return self.bikeData[name]

    async def callback(self, sender: int, data: bytearray):
        print("--- callback ---")
        for feature, byte in zip(bikeDataList, list(data)):
            self.set_value(feature, byte)


class Trainer:
    def __init__(self, bikeDataService):
        self.bikeDataService = bikeDataService
        with open("characteristics.json") as file:
            self.gatt = json.load(file)

    async def enable_notifications(self, client, characteristic_uuid, callback):
        await client.start_notify(characteristic_uuid, callback)

    async def connect(self, deviceName):
        print("connecting..")
        scanner = BleakScanner()
        devices = await scanner.discover()
        device = next((d for d in devices if d.name == deviceName), None)
        if device:
            print("found device")
            client = BleakClient(device)

            print("connecting..")
            await client.connect()
            print("connected")

            # @todo 
            # for characteristic, callback in reads.items():
            #     characteristic_value = await client.read_gatt_char(
            #         find_gatt_uuid(self.gatt, characteristic)
            #     )

            for characteristic, callback in subscriptions.items():
                await self.enable_notifications(
                    client,
                    find_gatt_uuid(self.gatt, characteristic),
                    self.bikeDataService.callback,
                )

            print("entering loop")
            while True:
                await asyncio.sleep(1)
        else:
            print("device not found")

    async def start(self):
        print("starting..")
        await self.connect("SUITO")

    @classmethod
    async def create(cls, bikeDataService):
        print("creating..")
        trainer = Trainer(bikeDataService)
        await trainer.start()
        return trainer

bikeDataService = BikeDataService()

async def start_services():
    await Trainer.create(bikeDataService)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/power")
async def power():
    return {"Instantaneous Power" : bikeDataService.get_value("Instantaneous Power")}

if __name__ == "__main__":
    asyncio.run(start_services())
    uvicorn.run(app, host="0.0.0.0", port=8000)
