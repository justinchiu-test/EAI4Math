import asyncio
from datasets import load_dataset
import requests
from typing import List
import json


async def query_prover(statements: List[str]):
    url = 'https://justinchiu--deepseek-prover-web.modal.run'
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompts": statements,
        "settings": {},
    }
    data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=data)

    results = json.loads(response.text)
    return results

async def query_lean_server(lean_codes: List[str]):
    url = 'https://justinchiu--verifier-verify.modal.run/'
    headers = {'Content-Type': 'application/json'}
    data = [{"code": lean_code.replace("```","").strip()} for lean_code in lean_codes]
    data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=data)

    try:
        results = json.loads(response.text)
    except:
        import pdb; pdb.set_trace()
    return results

def test_lean_server():
    lean_codes = ["import Mathlib"]
    results = query_lean_server(lean_codes)
    print(results)

#test_lean_server()


async def test_minif2f_lean4():
    dataset = load_dataset("cat-searcher/minif2f-lean4")
    samples = dataset["test"]
    theorems_without_sorry = [
        "Complete the following Lean 4 code:\n\n```lean4\n"
        + sample["formal_statement"].replace(" sorry", "")
        for sample in samples
    ]
    generations = query_prover(theorems_without_sorry)
    full_programs = [
        "import Mathlib\n" + theorem + generation[0]
        for theorem, generation in zip(theorems_without_sorry, generations)
    ]
    results = [
        query_lean_server([program])
        for program in full_programs
    ]
    import pdb; pdb.set_trace()

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4())
import asyncio
from datasets import load_dataset
import requests
from typing import List
import json


async def query_prover(statements: List[str]):
    url = 'https://justinchiu--deepseek-prover-web.modal.run'
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompts": statements,
        "settings": {},
    }
    data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=data)

    results = json.loads(response.text)
    return results

async def query_lean_server(lean_codes: List[str]):
    url = 'https://justinchiu--verifier-verify.modal.run/'
    headers = {'Content-Type': 'application/json'}
    data = [{"code": lean_code.replace("```","").strip()} for lean_code in lean_codes]
    data = json.dumps(data)
    
    response = requests.post(url, headers=headers, data=data)

    try:
        results = json.loads(response.text)
    except:
        import pdb; pdb.set_trace()
    return results

def test_lean_server():
    lean_codes = ["import Mathlib"]
    results = query_lean_server(lean_codes)
    print(results)

#test_lean_server()


async def test_minif2f_lean4():
    dataset = load_dataset("cat-searcher/minif2f-lean4")
    samples = dataset["test"]
    theorems_without_sorry = [
        "Complete the following Lean 4 code:\n\n```lean4\n"
        + sample["formal_statement"].replace(" sorry", "")
        for sample in samples
    ]
    generations = query_prover(theorems_without_sorry)
    full_programs = [
        "import Mathlib\n" + theorem + generation[0]
        for theorem, generation in zip(theorems_without_sorry, generations)
    ]
    results = [
        query_lean_server([program])
        for program in full_programs
    ]
    import pdb; pdb.set_trace()

if __name__ == "__main__":
    asyncio.run(test_minif2f_lean4())
