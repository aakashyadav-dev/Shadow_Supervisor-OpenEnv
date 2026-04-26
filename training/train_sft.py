"""
Optional Hugging Face TRL SFT training script for Shadow Supervisor.

Default behavior:
- runs in dry-run mode,
- validates that data/sft_training_data.jsonl exists,
- explains the TRL command to run when GPU/internet is available.

Actual TRL training:
    python training/train_sft.py --use_trl --model_name sshleifer/tiny-gpt2

Note:
This script is included to satisfy the hackathon training pipeline requirement.
For reliable Mac demo evidence, use training/train_trl.py tiny imitation fallback.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.open("r", encoding="utf-8") if line.strip())


def dry_run(dataset_path: Path) -> None:
    print("✅ SFT dry run successful.")
    print(f"Dataset: {dataset_path}")
    print(f"Rows: {count_jsonl(dataset_path)}")
    print()
    print("To run real TRL SFT training on GPU/Colab:")
    print("  python training/train_sft.py --use_trl --model_name sshleifer/tiny-gpt2")
    print()
    print("For hackathon demo without GPU, use:")
    print("  python training/train_trl.py")


def run_trl_training(dataset_path: Path, model_name: str, output_dir: Path) -> None:
    try:
        from datasets import load_dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer
    except Exception as exc:
        print("❌ TRL dependencies could not be imported.")
        print("Install/verify dependencies:")
        print("  pip install datasets transformers trl accelerate torch")
        print("Error:", repr(exc))
        return

    print("Loading dataset...")
    dataset = load_dataset("json", data_files=str(dataset_path))["train"]

    print("Loading model/tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(model_name)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-5,
        logging_steps=5,
        save_steps=50,
        save_total_limit=1,
        report_to=[],
    )

    try:
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            dataset_text_field="text",
            tokenizer=tokenizer,
            max_seq_length=1024,
        )
    except TypeError:
        # Compatibility fallback for newer TRL versions.
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            processing_class=tokenizer,
        )

    print("Starting TRL SFT training...")
    trainer.train()

    print("Saving model...")
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    metadata = {
        "model_name": model_name,
        "dataset": str(dataset_path),
        "output_dir": str(output_dir),
        "note": "TRL SFT run completed.",
    }
    (output_dir / "shadow_supervisor_sft_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"✅ TRL SFT training complete. Saved to: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_trl", action="store_true")
    parser.add_argument("--model_name", default="sshleifer/tiny-gpt2")
    parser.add_argument("--output_dir", default="outputs/sft_shadow_supervisor")
    args = parser.parse_args()

    dataset_path = DATA_DIR / "sft_training_data.jsonl"

    if not dataset_path.exists():
        print("SFT dataset not found.")
        print("Run first:")
        print("  python training/build_expert_dataset.py")
        raise SystemExit(1)

    output_dir = ROOT_DIR / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.use_trl:
        dry_run(dataset_path)
        return

    run_trl_training(dataset_path, args.model_name, output_dir)


if __name__ == "__main__":
    main()
