import hashlib
import difflib


class PromptMasker:
    API_KEY_PHRASE = "api key"

    PHONE_PHRASES = [
        "phone no",
        "ph no",
        "phone number",
        "mobile no",
        "mobile number",
    ]

    EMAIL_PHRASES = [
        "email",
        "email id",
        "mail id",
        "email address",
    ]

    def __init__(self, mode="hash", salt=""):
        if mode not in {"hash", "mask"}:
            raise ValueError("mode must be 'hash' or 'mask'")
        self.mode = mode
        self.salt = salt

    # ---------- BASIC HELPERS ----------

    def _hash(self, value, length=8):
        return hashlib.sha256((self.salt + value).encode()).hexdigest()[:length]

    def _mask(self, name, value):
        if self.mode == "hash":
            return f"<{name}:{self._hash(value)}>"
        return f"<{name}>"

    def _fuzzy_match(self, text, target, threshold=0.75):
        return difflib.SequenceMatcher(
            None, text.lower(), target.lower()
        ).ratio() >= threshold

    # ---------- VALUE HEURISTICS ----------

    def _looks_like_api_secret(self, token):
        return (
            len(token) >= 8
            and any(c.isalpha() for c in token)
            and any(c.isdigit() for c in token)
        )

    def _looks_like_phone(self, token):
        return token.isdigit() and 8 <= len(token) <= 15

    def _looks_like_email(self, token):
        return "@" in token and "." in token

    def _global_mask_type(self, token):
        if "@" in token:
            return "email"
        if token.isdigit() and len(token) >= 8:
            return "number"
        if token.isalnum() and any(c.isalpha() for c in token) and any(c.isdigit() for c in token):
            return "alphanumeric"
        return None

    # ---------- MAIN API ----------

    def mask(self, text: str) -> str:
        lines = text.splitlines()
        output = []

        for line in lines:
            words = line.split()
            mask_map = {}

            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i + 1]

                if self._fuzzy_match(f"{w1} {w2}", self.API_KEY_PHRASE):
                    for j in range(max(0, i - 5), min(len(words), i + 7)):
                        t = words[j].strip(":=,")
                        if self._looks_like_api_secret(t):
                            mask_map[j] = "api_key"

                if any(self._fuzzy_match(f"{w1} {w2}", p) for p in self.PHONE_PHRASES):
                    for j in range(max(0, i - 3), min(len(words), i + 5)):
                        t = words[j].strip(":=,")
                        if self._looks_like_phone(t):
                            mask_map[j] = "phone"

                if any(self._fuzzy_match(f"{w1} {w2}", p) for p in self.EMAIL_PHRASES):
                    for j in range(max(0, i - 2), min(len(words), i + 4)):
                        t = words[j].strip(":=,")
                        if self._looks_like_email(t):
                            mask_map[j] = "email"

            for idx, word in enumerate(words):
                if idx in mask_map:
                    continue
                clean = word.strip(":=,")
                kind = self._global_mask_type(clean)
                if kind:
                    mask_map[idx] = kind

            for idx, kind in mask_map.items():
                clean = words[idx].strip(":=,")
                words[idx] = words[idx].replace(clean, self._mask(kind, clean))

            output.append(" ".join(words))

        return "\n".join(output)
