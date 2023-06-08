import asyncio
import json

from bleak import BleakClient, BleakScanner

def find_gatt_uuid(gatt, description):
    for primary in gatt:
        if primary['description'] == description:
            return primary['uuid']
        for characteristic in primary['characteristics']:
            if characteristic['description'] == description:
                return characteristic['uuid']
    return ""

with open('output.json') as file:
    gatt = json.load(file)

async def enable_notifications(client, characteristic_uuid):
    await client.start_notify(characteristic_uuid, notification_callback)

async def notification_callback(sender: int, data: bytearray):
    print("notification received", sender, data);

async def connect(deviceName):
    scanner = BleakScanner()
    devices = await scanner.discover()
    device = next((d for d in devices if d.name == deviceName), None)
    if device:
        client = BleakClient(device)
        await client.connect()
        print('connected')
        await enable_notifications(client, find_gatt_uuid(gatt, "Indoor Bike Data"))
        print("entering sleep loop")
        while True:
            await asyncio.sleep(1) 

device = "SUITO"
asyncio.run(connect(device))

