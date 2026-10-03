import asyncio
import httpx
import time
import random

URL = "http://localhost:8000/predict"

async def send_event(client, sem, i):
    async with sem:  # Limit concurrent open connections
        payload = {
            "user_id": f"user_{random.randint(1, 100)}",
            "amount": round(random.uniform(5.0, 500.0), 2)
        }
        try:
            start = time.perf_counter()
            res = await client.post(URL, json=payload)
            lat = (time.perf_counter() - start) * 1000
            print(f"Req {i}: Status {res.status_code} | Total Latency: {lat:.2f}ms | API Internal Latency: {res.json()['latency_ms']}ms")
        except Exception as e:
            print(f"Failed req {i}: {e}")

async def main():
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    sem = asyncio.Semaphore(20) # Keep realistic concurrency
    
    async with httpx.AsyncClient(limits=limits, timeout=5.0) as client:
        tasks = [send_event(client, sem, i) for i in range(100)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())