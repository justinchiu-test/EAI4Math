import asyncio
import aiohttp
from typing import List
import json

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

async def test_minif2f_lean4():
    with open("data/minif2f_test.jsonl", "r") as f:
        data = [json.loads(line) for line in f]

    for item in data:
        lean_code = item["lean"]
        result = await query_lean_server([lean_code])
        print(f"Input: {lean_code}")
        print(f"Output: {result}")
        print()

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4())
from typing import List
import json
