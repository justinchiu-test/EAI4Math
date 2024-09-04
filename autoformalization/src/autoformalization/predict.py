import datasets
import openai
import pdb
import numpy as np

from autoformalization.constants import (
    ISABELLE_TRAIN_PATH,
    ISABELLE_VAL_PATH,
    LEAN_TRAIN_PATH,
    LEAN_VAL_PATH,
    LEAN_TEST_PATH,
)


FORMALIZE_PROMPT = """Formalize the following statement in lean4.
{statement}"""


def formalize_prompt(statement):
    prompt = FORMALIZE_PROMPT.format(statement=statement)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that formalizes mathematical statements in Lean4."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()


def main():
    lean = datasets.load_dataset(
        "json",
        data_files={
            "train": LEAN_TRAIN_PATH,
            "validation": LEAN_VAL_PATH,
            "test": LEAN_TEST_PATH,
        },
    )

    def predict(x):
        x["prediction"] = formalize_prompt(x["input"])
        return x

    predictions = lean.map(predict)
    predictions.save_to_disk("")


if __name__ == "__main__":
    main()
