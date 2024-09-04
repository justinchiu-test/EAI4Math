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


TRANSLATE_PROMPT = """
"""


def translate_isabelle_to_lean(code):
    pass


def build_nl_statement_to_isabelle(data):
    # is this too slow lol
    return {x["input"]: x["output"] for x in data}


def main():
    isabelle = datasets.load_dataset(
        "json",
        data_files=[ISABELLE_TRAIN_PATH, ISABELLE_VAL_PATH],
    )["train"]
    lean = datasets.load_dataset(
        "json",
        data_files={
            "train": LEAN_TRAIN_PATH,
            "validation": LEAN_VAL_PATH,
            "test": LEAN_TEST_PATH,
        },
    )

    statement_store = build_nl_statement_to_isabelle(isabelle)

    def link_isabelle_to_lean(x):
        statement = x["input"]
        x["isabelle"] = statement_store.get(statement, "UNLINKED")
        return x

    linked_lean = lean.map(link_isabelle_to_lean)
    pdb.set_trace()


if __name__ == "__main__":
    main()
