import asyncio
import json

from bleak import BleakClient

address = "FD:99:E8:D9:5A:C2"

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

fitnessMachineStatusUUID = find_gatt_uuid(gatt, "Fitness Machine Status")

try :
    async def main(address):
        async with BleakClient(address) as client:
            characteristic_read = await client.read_gatt_char(fitnessMachineStatusUUID)
            print("Characteristic:", characteristic_read)
    asyncio.run(main(address))
except Exception as inst:
    print("Failed.")
    print(type(inst))
    print(inst)


