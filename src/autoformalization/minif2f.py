import asyncio
import aiohttp
from typing import List
import json
import aiofiles

async def query_prover(statements: List[str]):
    url = "http://localhost:8080/query"
    headers = {"Content-Type": "application/json"}
    data = {"statements": statements}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.json()

async def query_lean_server(lean_codes: List[str]):
    url = "http://localhost:8080/lean"
    headers = {"Content-Type": "application/json"}
    data = {"lean_codes": lean_codes}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.json()

async def load_jsonl(file_path: str) -> List[dict]:
    async with aiofiles.open(file_path, mode='r') as f:
        return [json.loads(line) async for line in f]

async def test_minif2f_lean4():
    data = await load_jsonl("data/minif2f_test.jsonl")

    tasks = []
    for item in data:
        lean_code = item["lean"]
        tasks.append(query_lean_server([lean_code]))

    results = await asyncio.gather(*tasks)

    for item, result in zip(data, results):
        print(f"Input: {item['lean']}")
        print(f"Output: {result}")
        print()

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4())
