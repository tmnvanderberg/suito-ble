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

bikeDataNames = {
    "cadence": "Instantaneous Cadence",
    "avg_power": "Average Power",
    }

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
        print('init BikeDataService')
        self.bikeData = {
            string: value for value, string in enumerate(bikeDataList, start=1)
        }
        self.subscribers = []
        self.count = 0

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)

    def notify_subscribers(self, name, value):
        for subscriber in self.subscribers:
            subscriber.bikeServiceUpdate(name, value)

    def set_value(self, name, value):
        # if (name == "Instantaneous Power"):
        #     print(f"value {name}:{value}")
        self.bikeData[name] = value
        self.notify_subscribers(name, value)

    def get_value(self, name):
        print(self.bikeData)
        print(f"count: {self.count}")
        print(f"get: {name} {self.bikeData[name]}")
        return self.bikeData[name]

    async def callback(self, sender: int, data: bytearray):
        print("-------")
        print(f"callback count: {self.count}")
        for feature, byte in zip(bikeDataList, list(data)):
            if (feature == "Instantaneous Power"):
                print(f"{feature}:{byte}")
                self.count += 1
            self.set_value(feature, str(byte))

class Trainer:
    def __init__(self):
        print('init Trainer')
        self.bikeDataService = BikeDataService()
        with open("characteristics.json") as file:
            self.gatt = json.load(file)
    
    def getBikeDataService(self):
        return self.bikeDataService

    async def enable_notifications(self, client, characteristic_uuid, callback):
        await client.start_notify(characteristic_uuid, callback)

    async def connect(self, deviceName):
        scanner = BleakScanner()
        devices = await scanner.discover()
        device = next((d for d in devices if d.name == deviceName), None)
        if device:
            print("found device")
            client = BleakClient(device)

            await client.connect()
            print("connected")

            await self.enable_notifications(
                client,
                find_gatt_uuid(self.gatt, "Indoor Bike Data"),
                self.bikeDataService.callback,
            )

        else:
            raise TimeoutError("device not found!")

    async def start(self):
        print("starting..")
        await self.connect("SUITO")

    @classmethod
    async def create(cls):
        trainer = Trainer()
        await trainer.start()
        return trainer

# bikeDataService = BikeDataService()

# trainer = Trainer()

class Services:
    def __init__(self, trainer):
        print('init Services')
        self.trainer = trainer
        
    async def start(self):
        self.trainer = await Trainer.create()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/avg_power")
# async def avg_power():
#     bikeDataService = trainer.getBikeDataService()
#     power = bikeDataService.get_value(bikeDataNames['avg_power'])
#     print(f"avg power request, returning {power}");
#     return {"avg_power" : power }

# @app.get("/inst_power")
# async def instant_power():
#     bikeDataService = trainer.getBikeDataService()
#     power = bikeDataService.get_value("Instantaneous Power")
#     print(f"Power request, returning {power}");
#     return {"instant_power" : power }

# @app.get("/cadence")
# async def cadence():
#     bikeDataService = trainer.getBikeDataService()
#     cadence = bikeDataService.get_value(bikeDataNames['cadence'])
#     print(f"Cadence request, returning {cadence}");
#     return {"cadence" : cadence }

async def main():
    trainer = Trainer()
    services = Services(trainer)
    await services.start()
    print("services started..", services)
    config = uvicorn.Config("server:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
    while(True):
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
