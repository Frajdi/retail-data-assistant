from dotenv import load_dotenv

load_dotenv()

import json

from langsmith import Client



DATASET_NAME = "retail_data_agent_evals"
DATASET_PATH = "evals/datasets/retail_agent_golden_dataset.json"


client = Client()


def load_cases() -> list[dict]:

    with open(DATASET_PATH, "r") as file:
        return json.load(file)


def main():
    cases = load_cases()

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Golden evaluation dataset for the Retail Data Assistant.",
    )

    client.create_examples(
        dataset_id=dataset.id,
        inputs=[
            case["inputs"]
            for case in cases
        ],
        outputs=[
            case["outputs"]
            for case in cases
        ],
    )

    print(
        f"Uploaded {len(cases)} examples "
        f"to '{DATASET_NAME}'"
    )


if __name__ == "__main__":
    main()