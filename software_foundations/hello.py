import requests

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
    submit_prompts(["hi"])
