import asyncio
from fastapi import FastAPI

app = FastAPI()

async def process_data(data):
    # Simulating an asynchronous data processing routine
    await asyncio.sleep(1)
    return data.upper()

async def async_routine():
    while True:
        # Simulating some background task
        await asyncio.sleep(5)
        print("Performing background task")

async def start_async_routine():
    await async_routine()

@app.post("/data")
async def receive_data(data: str):
    processed_data = await process_data(data)
    return {"processed_data": processed_data}

if __name__ == "__main__":
    # Start the FastAPI application
    asyncio.run(start_async_routine())  # Start the background async routine
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
