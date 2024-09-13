import datasets
import json
from openai import OpenAI
import pdb
import numpy as np

from autoformalization.constants import (
    ISABELLE_TRAIN_PATH,
    ISABELLE_VAL_PATH,
    LEAN_TRAIN_PATH,
    LEAN_VAL_PATH,
    LEAN_TEST_PATH,
)
from autoformalization.viz.utils import (replacements, split_text_and_keep_equations)

client = OpenAI()
VISUALIZE = True

FORMALIZE_PROMPT = """Formalize the following statement in lean4.
{statement}"""


def get_system_prompt(fewshot_examples):
    examples = "\n\n".join([f"{x['input']}\n{x['output']}" for x in fewshot_examples])
    return f"""
You are a helpful assistant that formalizes mathematical statements in Lean4. You return only code that formalizes the statement. Do not try to prove the statement.

Here are a few examples.

# Examples
{examples}
""".strip()


def formalize_prompt(system_prompt, statement):
    prompt = FORMALIZE_PROMPT.format(statement=statement)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        #model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def get_predictions(system_prompt, data):
    return [formalize_prompt(system_prompt, x["input"]) for x in data]

def viz(statements, predictions, answers):
    import streamlit as st
    st.set_page_config(layout="wide")

    idx = st.number_input("Prior example number", min_value=0, max_value=len(predictions)-1)

    st.write(statements[idx])
    col1, col2 = st.columns(2)
    with col1:
        st.code(predictions[idx])
    with col2:
        st.code(answers[idx])


def main():
    """
    lean = datasets.load_dataset(
        "json",
        data_files={
            "train": LEAN_TRAIN_PATH,
            "validation": LEAN_VAL_PATH,
            "test": LEAN_TEST_PATH,
        },
    )
    """

    with open("../data/lean_workbook.json") as f:
        data = json.loads(f.read())
    #fewshot_data = lean["train"].select(list(range(10)))
    #val_data = lean["validation"].select(list(range(10)))

    fewshot_data = [{
        "input": x["natural_language_statement"],
        "output": x["formal_statement"],
    } for x in data[0:10]]
    val_data = [{
        "input": x["natural_language_statement"],
        "output": x["formal_statement"],
    } for x in data[56000:56010]]

    system_prompt = get_system_prompt(fewshot_data)
    predictions = get_predictions(system_prompt, val_data)
    answers = [x["output"] for x in val_data]

    if VISUALIZE:
        viz([x["input"] for x in val_data], predictions, answers)

    # lean.add_column("predictions", predictions)
    # lean.save_to_disk("results/mathlib_predictions")


if __name__ == "__main__":
    main()
