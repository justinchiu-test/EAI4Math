import asyncio
from datasets import load_dataset
import aiohttp
from typing import List, Dict, Any
import json


async def query_prover(session: aiohttp.ClientSession, statements: List[str]) -> List[str]:
    url = 'https://justinchiu--deepseek-prover-web.modal.run'
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompts": statements,
        "settings": {},
    }
    
    async with session.post(url, headers=headers, json=data) as response:
        results = await response.json()
    
    return results

async def query_lean_server(session: aiohttp.ClientSession, lean_codes: List[str]) -> List[Dict[str, Any]]:
    url = 'https://justinchiu--verifier-verify.modal.run/'
    headers = {'Content-Type': 'application/json'}
    data = [{"code": lean_code.replace("```","").strip()} for lean_code in lean_codes]
    
    async with session.post(url, headers=headers, json=data) as response:
        try:
            results = await response.json()
        except json.JSONDecodeError:
            print(f"Error decoding JSON. Response text: {await response.text()}")
            results = []
    
    return results

async def test_lean_server(session: aiohttp.ClientSession):
    lean_codes = ["import Mathlib"]
    results = await query_lean_server(session, lean_codes)
    print(results)

async def test_minif2f_lean4():
    async with aiohttp.ClientSession() as session:
        dataset = load_dataset("cat-searcher/minif2f-lean4")
        samples = dataset["test"]
        theorems_without_sorry = [
            "Complete the following Lean 4 code:\n\n```lean4\n"
            + sample["formal_statement"].replace(" sorry", "")
            for sample in samples
        ]
        generations = await query_prover(session, theorems_without_sorry)
        full_programs = [
            "import Mathlib\n" + theorem + generation[0]
            for theorem, generation in zip(theorems_without_sorry, generations)
        ]
        results = await asyncio.gather(*[query_lean_server(session, [program]) for program in full_programs])
        print(f"Processed {len(results)} programs")
        # You can add more processing here instead of using pdb

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4())
