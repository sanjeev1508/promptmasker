# PromptMasker

<p align="center">
  <img src="./promptmasker.png" alt="PromptMasker" width="400"/>
</p>



PromptMasker is a **prompt-sanitization utility** that heuristically detects and masks
sensitive data in raw text before it is sent to LLMs, logs, or external services.

It is designed to sit **before** your model call or logging layer and reduce the risk of
accidentally leaking credentials or personal data.

This is **redaction**, not encryption.

---

## Why PromptMasker exists

LLMs are often fed:
- raw user input  
- debugging prompts  
- logs copied from real systems  

Those inputs frequently contain:
- API keys
- emails
- phone numbers
- internal IDs

PromptMasker is built to **intercept that text early** and neutralize obvious sensitive
tokens without requiring rigid schemas or strict formatting.

---

## What it masks

PromptMasker attempts to detect and mask:

- **API keys / secrets**  
  Context-aware, alphanumeric tokens near phrases like *“api key”*

- **Email addresses**  
  Detected by structure and local intent

- **Phone / mobile numbers**  
  Numeric tokens (8–15 digits) near phone-related phrases

- **Generic sensitive tokens**  
  Long numeric or mixed alphanumeric identifiers via fallback heuristics

---

## How detection works (important)

Detection is **heuristic and layered**, not rule-perfect:

- Fuzzy keyword matching  
  (`api key`, `email id`, `phone no`, etc.)

- Sliding context windows  
  (tokens near intent phrases are prioritized)

- Structural heuristics  
  (length, digits, alphanumeric composition)

- Global fallback  
  for obviously sensitive-looking tokens

This means:
- false positives are possible  
- behavior is intentionally conservative  

That trade-off is deliberate.

---

## What PromptMasker is NOT

- Not encryption  
- Not anonymization  
- Not compliance-grade security  

If you need cryptographic guarantees, **do not use this**.

---

## Installation

```bash
pip install promptmasker
```
---

## Sample Usage

```bash
from promptmasker import PromptMasker

masker = PromptMasker(mode="hash", salt="session")
text = "My api key is sk-1234567890 and email test@example.com"

print(masker.mask(text))
```
