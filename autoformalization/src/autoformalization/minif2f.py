import asyncio
from datasets import load_dataset
import aiohttp
from typing import List, Dict, Any
import json
from aiohttp import ClientTimeout
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), retry=retry_if_exception_type((asyncio.TimeoutError, aiohttp.ClientError)))
async def query_prover(session: aiohttp.ClientSession, statements: List[str]) -> List[str]:
    url = 'https://justinchiu--deepseek-prover-web.modal.run'
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompts": statements,
        "settings": {},
    }
    timeout = ClientTimeout(total=180)  # 3 minutes timeout
    try:
        async with session.post(url, headers=headers, json=data, timeout=timeout) as response:
            results = await response.json()
        return results
    except asyncio.TimeoutError:
        logger.warning("Request to prover timed out. Retrying...")
        raise
    except aiohttp.ClientError as e:
        logger.warning(f"Client error occurred: {e}. Retrying...")
        raise

@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), retry=retry_if_exception_type((asyncio.TimeoutError, aiohttp.ClientError, json.JSONDecodeError)))
async def query_lean_server(session: aiohttp.ClientSession, lean_codes: List[str]) -> List[Dict[str, Any]]:
    url = 'https://justinchiu--verifier-verify.modal.run/'
    headers = {'Content-Type': 'application/json'}
    data = [{"code": lean_code.replace("```","").strip()} for lean_code in lean_codes]
    timeout = ClientTimeout(total=180)  # 3 minutes timeout
    try:
        async with session.post(url, headers=headers, json=data, timeout=timeout) as response:
            results = await response.json()
        return results
    except asyncio.TimeoutError:
        logger.warning("Request to Lean server timed out. Retrying...")
        raise
    except aiohttp.ClientError as e:
        logger.warning(f"Client error occurred: {e}. Retrying...")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON. Response text: {await response.text()}")
        raise

async def test_lean_server(session: aiohttp.ClientSession):
    lean_codes = ["import Mathlib"]
    results = await query_lean_server(session, lean_codes)
    print(results)

async def test_minif2f_lean4():
    async with aiohttp.ClientSession() as session:
        dataset = load_dataset("cat-searcher/minif2f-lean4")
        samples = dataset["test"]
        theorems_without_sorry = [
            sample["formal_statement"].replace(" sorry", "")
            for sample in samples
        ]
        prompts = [
            "Complete the following Lean 4 code:\n\n```lean4\n" + theorem
            for theorem in theorems_without_sorry
        ]
        generations = await query_prover(session, prompts)
        full_programs = [
            "import Mathlib\n" + theorem + generation[0]
            for theorem, generation in zip(theorems_without_sorry, generations)
        ]
        results = await asyncio.gather(*[query_lean_server(session, [program]) for program in full_programs])
        print(f"Processed {len(results)} programs")

        with open("results.txt", "w") as f:
            f.write(json.dumps(results))

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4())
