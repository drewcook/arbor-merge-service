import aiohttp
import asyncio
import time


async def main():
    tasks = []
    cids = ["bafybeifsdxxztl5jtgh7doue3ytqpv5yurren2lkeq6rdxaigjc22haevi",
            "bafybeigfocxfmpne6n4f2adls7ejlighfrz2t6fjtd7xebxnexnwyilf3m"]

    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/merge", json={"sample_cids": [cids[0]]}) as resp:
            print(await resp.json())
        # for x in range(5):
        #     tasks.append(session.post("http://localhost:8000/merge", json={"sample_cids": [cid for cid in cids]}))
        # print(await asyncio.gather(*tasks))


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"Elapsed {time.time() - start}s")
