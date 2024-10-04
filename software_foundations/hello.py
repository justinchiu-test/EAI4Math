import requests
from pathlib import Path

def load_data(path):
    with path.open("r")  as f:
        return f.read()

def submit_prompts(prompts):
    response = requests.post(
        "https://justinchiu--deepseek-prover-web.modal.run",
        json={
            "prompts": prompts,
        },
    )
    if response.status_code == 200:
        import pdb; pdb.set_trace()
        return response.json()

    import pdb; pdb.set_trace()


if __name__ == "__main__":
    data_path = Path("data/multiset.v")
    prompt = load_data("data")
    submit_prompts([prompt])
