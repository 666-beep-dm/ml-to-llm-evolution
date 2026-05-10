"""
src/training/data_module.py
Loads, validates, and splits the instruction-response dataset.
Auto-generates a synthetic dataset when no local file is found.
"""

from __future__ import annotations
import json
import logging
import random
from pathlib import Path
from typing import List, Tuple, Dict

from datasets import Dataset

logger = logging.getLogger(__name__)

CHAT_TEMPLATE = (
    "<|system|>\nYou are a helpful AI assistant.\n"
    "<|user|>\n{instruction}\n"
    "<|assistant|>\n{response}"
)

# ── Synthetic dataset (fallback) ──────────────────────────────────────────────
SYNTHETIC_PAIRS: List[Dict[str, str]] = [
    {"instruction": "What is LoRA?",
     "response": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that inserts trainable low-rank matrices into frozen model layers, reducing trainable parameters by up to 99%."},
    {"instruction": "Explain gradient checkpointing.",
     "response": "Gradient checkpointing saves GPU memory by recomputing intermediate activations during the backward pass instead of storing them all, trading compute for memory."},
    {"instruction": "What is 4-bit quantization?",
     "response": "4-bit quantization compresses model weights to 4 bits, reducing memory footprint by roughly 8x compared to float32, enabling large models to run on consumer GPUs."},
    {"instruction": "What does PEFT stand for?",
     "response": "PEFT stands for Parameter-Efficient Fine-Tuning, a family of techniques that fine-tune only a small fraction of model weights while keeping the base model frozen."},
    {"instruction": "What is the role of lora_alpha?",
     "response": "lora_alpha is a scaling factor applied to LoRA outputs. The effective multiplier is lora_alpha / r. Setting alpha = 2*r is a common heuristic for stable training."},
    {"instruction": "What is bitsandbytes?",
     "response": "bitsandbytes is a PyTorch library providing 8-bit and 4-bit quantized layers, enabling large model training and inference on limited GPU memory."},
    {"instruction": "What is the SFTTrainer?",
     "response": "SFTTrainer from the TRL library wraps HuggingFace Trainer with helpers for supervised fine-tuning, handling prompt formatting and PEFT integration automatically."},
    {"instruction": "What are target_modules in LoraConfig?",
     "response": "target_modules specifies which linear layers receive LoRA adapters. Targeting q_proj and v_proj (attention query and value projections) is a common effective choice."},
    {"instruction": "How does gradient accumulation help training?",
     "response": "Gradient accumulation sums gradients over N micro-batches before updating weights, simulating a larger batch size without the memory cost of loading all samples at once."},
    {"instruction": "What is mixed precision training?",
     "response": "Mixed precision training uses float16 for activations and gradients but maintains float32 master weights, reducing memory use and accelerating training on tensor-core GPUs."},
    {"instruction": "What is perplexity in NLP?",
     "response": "Perplexity measures how well a language model predicts a text. Lower perplexity indicates better prediction; it equals exp(average cross-entropy loss) over the evaluation set."},
    {"instruction": "What is cosine similarity?",
     "response": "Cosine similarity measures the angle between two vectors, returning a value in [-1, 1]. Values near 1 indicate high similarity, used in NLP to compare sentence embeddings."},
    {"instruction": "What is an instruction-tuned model?",
     "response": "An instruction-tuned model is fine-tuned on pairs of instructions and desired responses, teaching it to follow natural language directives rather than just continuing text."},
    {"instruction": "What is causal language modeling?",
     "response": "Causal language modeling trains a model to predict the next token given all previous tokens. The autoregressive property allows iterative text generation."},
    {"instruction": "How do you merge LoRA adapters?",
     "response": "Call model.merge_and_unload() on a PeftModel to fuse the low-rank matrices into the base weights, producing a standard model with no inference overhead."},
    {"instruction": "What is the AdamW optimizer?",
     "response": "AdamW decouples L2 regularization from the gradient update step, applying weight decay directly to parameters for better generalization than standard Adam."},
    {"instruction": "What is paged_adamw_32bit?",
     "response": "paged_adamw_32bit is a bitsandbytes optimizer that pages optimizer states to CPU RAM when GPU memory is exhausted, enabling training of larger models on 4 GB GPUs."},
    {"instruction": "What is a chat template?",
     "response": "A chat template wraps messages in special delimiter tokens expected by the model. Consistent use of the same template at training and inference is essential for correct behavior."},
    {"instruction": "What is VRAM?",
     "response": "VRAM is dedicated GPU memory used to store model weights, activations, gradients, and optimizer states. 4 GB is the minimum practical size for fine-tuning 1B-parameter models."},
    {"instruction": "What is FastAPI?",
     "response": "FastAPI is a modern async Python web framework for building APIs. It provides automatic OpenAPI documentation, type validation via Pydantic, and high performance via ASGI."},
    {"instruction": "What is an async endpoint in FastAPI?",
     "response": "An async endpoint is defined with `async def`. It runs in an event loop without blocking other requests, essential for I/O-bound tasks like database queries or HTTP calls."},
    {"instruction": "What is Pydantic?",
     "response": "Pydantic is a Python library for data validation using type annotations. FastAPI uses it for request/response models, providing automatic validation and serialization."},
    {"instruction": "What is Docker Compose?",
     "response": "Docker Compose defines and runs multi-container applications via a YAML file. Services, networks, and volumes are declared together, enabling reproducible deployments."},
    {"instruction": "What is a Docker volume?",
     "response": "A Docker volume is persistent storage managed by Docker that outlives container restarts. It is used to share files between containers or persist model weights across runs."},
    {"instruction": "What is the NVIDIA Container Toolkit?",
     "response": "The NVIDIA Container Toolkit allows Docker containers to access the host GPU. It injects CUDA libraries into containers, enabling GPU-accelerated workloads without host installation."},
    {"instruction": "What is overfitting in LLM fine-tuning?",
     "response": "Overfitting occurs when the model memorizes training examples rather than generalizing. Signs include very low training loss but high validation loss and repetitive generated text."},
    {"instruction": "What is a learning rate warmup?",
     "response": "Learning rate warmup gradually increases LR from near zero at the start of training. It stabilizes early optimization when gradients are noisy and prevents large destructive updates."},
    {"instruction": "What is a cosine LR scheduler?",
     "response": "A cosine scheduler decays the learning rate following a cosine curve from its peak value to near zero. It typically yields better final models than linear decay for LLM fine-tuning."},
    {"instruction": "What is tokenization?",
     "response": "Tokenization splits raw text into integer token IDs the model processes. The tokenizer also handles special tokens like BOS, EOS, and PAD required by the architecture."},
    {"instruction": "What is the difference between base and fine-tuned models?",
     "response": "A base model is trained on broad unlabeled text and predicts next tokens. A fine-tuned model is further trained on task-specific labeled data, specializing its behavior."},
    {"instruction": "What is a LoRA adapter checkpoint?",
     "response": "A LoRA adapter checkpoint contains only the trained low-rank weight matrices, typically just a few MB. It is loaded on top of the frozen base model at inference time."},
    {"instruction": "What is the TRL library?",
     "response": "TRL (Transformer Reinforcement Learning) is a HuggingFace library for fine-tuning LLMs with supervised fine-tuning, reward modeling, and reinforcement learning from human feedback."},
    {"instruction": "What is sentence embedding?",
     "response": "A sentence embedding is a fixed-size dense vector representing a sentence's meaning. It is computed by passing the sentence through an encoder and pooling the hidden states."},
    {"instruction": "What is eval loss vs train loss?",
     "response": "Train loss measures model error on training examples during optimization. Eval loss measures error on held-out examples. A gap where eval loss rises while train loss falls indicates overfitting."},
    {"instruction": "What is the purpose of pad_token?",
     "response": "The pad token fills shorter sequences in a batch to uniform length. For GPT-style models it is often set to EOS token since they have no dedicated pad token by default."},
    {"instruction": "What is torch.no_grad()?",
     "response": "torch.no_grad() is a context manager that disables gradient computation, reducing memory use and speeding up inference where gradients are not needed."},
    {"instruction": "What is a model checkpoint?",
     "response": "A model checkpoint is a saved snapshot of model weights at a specific training step. Checkpoints allow resuming training after interruption and selecting the best-performing state."},
    {"instruction": "What does device_map auto do?",
     "response": "device_map=auto from Accelerate automatically distributes model layers across available GPUs and CPU RAM, enabling models larger than single GPU memory to run."},
    {"instruction": "What is beam search?",
     "response": "Beam search keeps the top-K candidate sequences at each generation step, expanding all beams and pruning to K at each step. It trades compute for higher-quality outputs than greedy decoding."},
    {"instruction": "What is top-p sampling?",
     "response": "Top-p (nucleus) sampling draws the next token from the smallest set of tokens whose cumulative probability exceeds p. It balances diversity and coherence in generated text."},
    {"instruction": "What is repetition penalty?",
     "response": "Repetition penalty reduces the probability of tokens already present in the generated sequence, discouraging the model from producing repetitive or looping text."},
    {"instruction": "What is the difference between LoRA and full fine-tuning?",
     "response": "Full fine-tuning updates all model weights, requiring large memory and compute. LoRA freezes base weights and trains only tiny adapter matrices, achieving similar results with 10-100x less memory."},
    {"instruction": "What is RLHF?",
     "response": "Reinforcement Learning from Human Feedback (RLHF) fine-tunes a language model using human preference ratings. A reward model scores outputs, and the LLM is optimized to maximize that score via PPO."},
    {"instruction": "What is DPO?",
     "response": "Direct Preference Optimization (DPO) is an alternative to RLHF that fine-tunes an LLM directly on preference pairs without a separate reward model, simplifying the training pipeline."},
    {"instruction": "What is a system prompt?",
     "response": "A system prompt is an initial instruction given to the model before the user message. It sets the assistant's persona, constraints, and behavior for the entire conversation."},
    {"instruction": "What is flash attention?",
     "response": "Flash Attention is a memory-efficient attention algorithm that fuses operations and uses tiling to avoid materializing the full attention matrix, reducing memory from O(n^2) to O(n)."},
    {"instruction": "What is quantization-aware training?",
     "response": "Quantization-aware training simulates quantization noise during forward passes so the model learns to be robust to low-precision weights, yielding better accuracy than post-training quantization."},
    {"instruction": "What is a transformer block?",
     "response": "A transformer block consists of a multi-head self-attention layer followed by a feed-forward network, each wrapped with layer normalization and residual connections."},
    {"instruction": "What is the feed-forward network in a transformer?",
     "response": "The feed-forward network (FFN) in each transformer block applies two linear projections with a nonlinear activation (GELU or SiLU) in between, processing each token independently."},
    {"instruction": "What is weight decay?",
     "response": "Weight decay penalizes large parameter values by adding their L2 norm to the loss. It acts as regularization, preventing individual weights from growing too large during training."},
]


def validate_record(record: Dict[str, str], idx: int) -> bool:
    required = {"instruction", "response"}
    if not required.issubset(record.keys()):
        logger.warning("Record %d missing keys %s — skipping.", idx, required - record.keys())
        return False
    if not record["instruction"].strip() or not record["response"].strip():
        logger.warning("Record %d has empty instruction or response — skipping.", idx)
        return False
    return True


def load_or_generate(data_path: str) -> List[Dict[str, str]]:
    p = Path(data_path)
    if p.exists():
        records, bad = [], 0
        with p.open(encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if validate_record(rec, i):
                        records.append(rec)
                    else:
                        bad += 1
                except json.JSONDecodeError:
                    logger.warning("Line %d: invalid JSON — skipping.", i)
                    bad += 1
        logger.info("Loaded %d valid / %d bad records from '%s'.", len(records), bad, data_path)
        return records
    else:
        logger.warning("Dataset '%s' not found — generating %d synthetic pairs.", data_path, len(SYNTHETIC_PAIRS))
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            for rec in SYNTHETIC_PAIRS:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        logger.info("Synthetic dataset written to '%s'.", data_path)
        return SYNTHETIC_PAIRS


def format_prompt(rec: Dict[str, str]) -> str:
    return CHAT_TEMPLATE.format(instruction=rec["instruction"], response=rec["response"])


def build_datasets(
    data_path: str,
    train_split: float = 0.85,
    seed: int = 42,
) -> Tuple[Dataset, Dataset]:
    records = load_or_generate(data_path)
    random.seed(seed)
    random.shuffle(records)

    n_train = max(1, int(len(records) * train_split))
    train_records = records[:n_train]
    test_records  = records[n_train:]

    logger.info("Split: train=%d  test=%d", len(train_records), len(test_records))

    train_ds = Dataset.from_dict({"text": [format_prompt(r) for r in train_records]})
    test_ds  = Dataset.from_dict({"text": [format_prompt(r) for r in test_records],
                                   "instruction": [r["instruction"] for r in test_records],
                                   "response":    [r["response"]    for r in test_records]})
    return train_ds, test_ds
