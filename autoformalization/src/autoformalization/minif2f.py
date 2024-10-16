import asyncio
from datasets import load_dataset
import aiohttp
from typing import List, Dict, Any
import json
from aiohttp import ClientTimeout, ContentTypeError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import logging
from asyncio import Semaphore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def query_prover(
    session: aiohttp.ClientSession,
    statements: List[str],
    n: int,
) -> List[str]:
    url = 'https://justinchiu--deepseek-prover-web.modal.run'
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompts": statements,
        "settings": {"n": n},
    }
    timeout = ClientTimeout(total=None)  # 3 minutes timeout
    try:
        async with session.post(url, headers=headers, json=data, timeout=timeout) as response:
            response.raise_for_status()
            results = await response.json()
        return results
    except asyncio.TimeoutError:
        logger.warning("Request to prover timed out. Retrying...")
        return [[""] for x in statements]
    except aiohttp.ClientError as e:
        logger.warning(f"Client error occurred: {e}. Retrying...")
        return [[""] for x in statements]


async def query_lean_server(session: aiohttp.ClientSession, lean_codes: List[str]) -> List[Dict[str, Any]]:
    url = 'https://justinchiu--verifier-verify.modal.run/'
    headers = {'Content-Type': 'application/json'}
    data = [{"code": lean_code.replace("```","").strip()} for lean_code in lean_codes]
    timeout = ClientTimeout(total=300)  # 3 minutes timeout
    try:
        async with session.post(url, headers=headers, json=data, timeout=timeout) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                logger.error(f"Unexpected content type: {content_type}")
                raise ContentTypeError(
                    response.request_info,
                    response.history,
                    message=f"Unexpected content type: {content_type}",
                    headers=response.headers
                )
            results = await response.json()
        return results
    except asyncio.TimeoutError:
        logger.warning("Request to Lean server timed out. Retrying...")
        return [{"complete": False} for x in lean_codes]
    except aiohttp.ClientError as e:
        logger.warning(f"Client error occurred: {e}. Retrying...")
        return [{"complete": False} for x in lean_codes]
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON. Response text: {await response.text()}")
        return [{"complete": False} for x in lean_codes]
    except ContentTypeError as e:
        logger.error(f"Content type error: {e}")
        return [{"complete": False} for x in lean_codes]

async def test_lean_server(session: aiohttp.ClientSession):
    lean_codes = ["import Mathlib"]
    results = await query_lean_server(session, lean_codes)
    print(results)


async def test_minif2f_lean4(n=128):
    async with aiohttp.ClientSession() as session:
        semaphore = Semaphore(10)  # Limit concurrency to 10
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

        async def query_with_semaphore(prompt):
            async with semaphore:
                return await query_prover(session, [prompt], n)

        all_generations = await asyncio.gather(
            *[query_with_semaphore(prompt) for prompt in prompts]
        )
        # extra batching dim
        all_generations = [x[0] for x in all_generations]

        full_programs = [
            "import Mathlib\n" + theorem + generation
            for theorem, generations in zip(theorems_without_sorry, all_generations)
            for generation in generations
        ]

        semaphore = Semaphore(50)  # Limit concurrency to 50
        async def query_lean_with_semaphore(program):
            async with semaphore:
                return await query_lean_server(session, [program])

        results = await asyncio.gather(*[query_lean_with_semaphore(program) for program in full_programs])

        grouped_results = []
        idx = 0
        for generations in all_generations:
            grouped_results.append(results[idx:idx+len(generations)])
            idx += len(generations)
        print(f"Processed {len(results)} programs")

        with open("results.txt", "w") as f:
            f.write(json.dumps(grouped_results))

        passrate = sum([any([r[0]["complete"] for r in rs]) for rs in grouped_results]) / len(grouped_results)
        print(f"Pass@{n}:", passrate)

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4(n=128))
