"""
ADRION 369 — Semantic Steganography Detector (FFT-based) v5.6
==============================================================
Detects hidden intent in seemingly neutral language using
frequency-domain analysis of linguistic features.

The Goodness Analyzer's 4th layer: FFT-based spectral analysis
of token patterns to expose steganographic encoding in prompts.

Attack vector: adversary encodes harmful instructions across
multiple benign-looking sentences using statistical patterns
invisible to keyword/regex detection.

Detection method:
1. Extract linguistic feature vector from text
2. Apply FFT to detect periodic patterns (hidden structure)
3. Compute spectral energy in suspicious frequency bands
4. Flag if energy exceeds threshold (natural language is noisy/aperiodic)

Reference: docs/SECURITY_HARDENING.md, Goodness Analyzer Layer 4
"""

import math
import re
from typing import Dict, List, Optional, Tuple


# ── Linguistic Feature Extraction ────────────────────────────────────────────

_WORD_RE = re.compile(r'\b\w+\b', re.UNICODE)
_SENTENCE_RE = re.compile(r'[.!?]+')

# Suspicious tokens commonly used in encoded instructions
_STEGO_MARKERS: frozenset = frozenset({
    "ignore", "override", "bypass", "execute", "system", "admin",
    "prompt", "instruction", "forget", "disregard", "pretend",
    "roleplay", "jailbreak", "sudo", "root", "shell",
    "inject", "payload", "escalate", "privilege",
    # PL equivalents
    "zignoruj", "omiń", "obejdź", "wykonaj", "administrator",
    "polecenie", "zapomnij", "udawaj", "eskaluj",
})


def _extract_features(text: str) -> List[float]:
    """
    Extract a per-token linguistic feature vector.

    Features per token:
    - Length (normalized)
    - Position of vowels (ratio)
    - Capitalization pattern
    - Repetition within window

    Returns a flattened feature sequence suitable for FFT.
    """
    tokens = _WORD_RE.findall(text.lower())
    if len(tokens) < 4:
        return []

    features = []
    max_len = max(len(t) for t in tokens) if tokens else 1

    for idx, token in enumerate(tokens):
        # Feature 1: Normalized length
        length_feat = len(token) / max_len

        # Feature 2: Vowel ratio
        vowels = sum(1 for c in token if c in "aeiouyąęó")
        vowel_ratio = vowels / len(token) if token else 0.0

        # Feature 3: Position in text (normalized)
        position_feat = idx / len(tokens)

        # Feature 4: Repeat count in local window
        window_start = max(0, idx - 5)
        window = tokens[window_start:idx]
        repeat_feat = window.count(token) / 5.0

        # Combine into single value for FFT
        combined = (length_feat * 0.3 + vowel_ratio * 0.25 +
                    position_feat * 0.15 + repeat_feat * 0.3)
        features.append(combined)

    return features


def _extract_sentence_features(text: str) -> List[float]:
    """
    Extract per-sentence structural features.

    Steganographic content often has unnaturally uniform
    sentence structure (same length, same punctuation pattern).
    """
    sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
    if len(sentences) < 3:
        return []

    features = []
    max_len = max(len(s) for s in sentences)
    for sent in sentences:
        words = _WORD_RE.findall(sent)
        features.append(len(sent) / max_len if max_len else 0.0)
        features.append(len(words) / 50.0)  # Normalized word count
    return features


# ── FFT Implementation (pure Python — no numpy dependency) ───────────────────

def _fft_magnitude(signal: List[float]) -> List[float]:
    """
    Compute FFT magnitude spectrum using Cooley-Tukey.

    For signals not power-of-2 length, zero-pads to next power of 2.
    Returns magnitudes for positive frequencies only.
    """
    n = len(signal)
    if n == 0:
        return []

    # Zero-pad to next power of 2
    n_padded = 1
    while n_padded < n:
        n_padded *= 2

    # Pad signal
    padded = signal + [0.0] * (n_padded - n)

    # Iterative Cooley-Tukey FFT
    real, imag = _fft_iterative(padded, n_padded)

    # Return magnitudes for positive frequencies (first half)
    magnitudes = []
    for k in range(n_padded // 2):
        mag = math.sqrt(real[k] ** 2 + imag[k] ** 2) / n_padded
        magnitudes.append(mag)

    return magnitudes


def _fft_iterative(signal: List[float], n: int) -> Tuple[List[float], List[float]]:
    """Iterative radix-2 Cooley-Tukey FFT."""
    # Bit-reversal permutation
    bits = int(math.log2(n))
    real = [0.0] * n
    imag = [0.0] * n

    for i in range(n):
        j = _bit_reverse(i, bits)
        real[j] = signal[i]

    # Butterfly operations
    size = 2
    while size <= n:
        half = size // 2
        angle_step = -2.0 * math.pi / size
        for start in range(0, n, size):
            for k in range(half):
                angle = angle_step * k
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)

                idx_even = start + k
                idx_odd = start + k + half

                t_real = cos_a * real[idx_odd] - sin_a * imag[idx_odd]
                t_imag = sin_a * real[idx_odd] + cos_a * imag[idx_odd]

                real[idx_odd] = real[idx_even] - t_real
                imag[idx_odd] = imag[idx_even] - t_imag
                real[idx_even] = real[idx_even] + t_real
                imag[idx_even] = imag[idx_even] + t_imag
        size *= 2

    return real, imag


def _bit_reverse(x: int, bits: int) -> int:
    """Reverse the lower 'bits' bits of integer x."""
    result = 0
    for _ in range(bits):
        result = (result << 1) | (x & 1)
        x >>= 1
    return result


# ── Spectral Analysis ────────────────────────────────────────────────────────

def _spectral_energy(magnitudes: List[float], band_start: float, band_end: float) -> float:
    """
    Compute energy in a frequency band (normalized to [0,1]).

    Natural language has most energy at low frequencies (DC component).
    Steganographic encoding creates peaks in mid/high frequencies.
    """
    if not magnitudes:
        return 0.0

    n = len(magnitudes)
    start_idx = max(0, int(n * band_start))
    end_idx = min(n, int(n * band_end))

    if start_idx >= end_idx:
        return 0.0

    band_energy = sum(m ** 2 for m in magnitudes[start_idx:end_idx])
    total_energy = sum(m ** 2 for m in magnitudes)

    if total_energy < 1e-10:
        return 0.0

    return band_energy / total_energy


def _peak_to_average_ratio(magnitudes: List[float]) -> float:
    """
    Compute peak-to-average ratio in the spectrum.

    Natural text: low PAR (diffuse spectrum)
    Steganographic text: high PAR (periodic structure creates sharp peaks)
    """
    if len(magnitudes) < 4:
        return 0.0

    # Skip DC component (index 0)
    ac_mags = magnitudes[1:]
    if not ac_mags:
        return 0.0

    peak = max(ac_mags)
    avg = sum(ac_mags) / len(ac_mags) if ac_mags else 0.0

    if avg < 1e-10:
        return 0.0

    return peak / avg


# ── Main Detector ────────────────────────────────────────────────────────────

class SteganographyDetector:
    """
    FFT-based semantic steganography detector.

    Analyzes text for hidden periodic patterns that indicate
    encoded instructions. Part of the Goodness Analyzer Layer 4.

    Detection layers:
    1. Keyword/marker presence scoring
    2. Token-level FFT analysis (periodic structure)
    3. Sentence-level FFT analysis (structural uniformity)
    4. Combined risk score
    """

    # Thresholds (tuned for false-positive minimization)
    MARKER_WEIGHT: float = 0.30
    TOKEN_FFT_WEIGHT: float = 0.35
    SENTENCE_FFT_WEIGHT: float = 0.20
    PAR_WEIGHT: float = 0.15

    # Suspicious frequency bands (mid-high = likely artificial)
    MID_BAND: Tuple[float, float] = (0.2, 0.5)
    HIGH_BAND: Tuple[float, float] = (0.5, 0.8)

    # Risk thresholds
    LOW_RISK: float = 0.25
    MEDIUM_RISK: float = 0.50
    HIGH_RISK: float = 0.75

    def __init__(
        self,
        alert_threshold: float = 0.50,
        block_threshold: float = 0.75,
    ) -> None:
        self._alert_threshold = alert_threshold
        self._block_threshold = block_threshold

    def analyze(self, text: str) -> Dict:
        """
        Analyze text for steganographic patterns.

        Returns:
            {
                "risk_score": float (0.0-1.0),
                "risk_level": "NONE" | "LOW" | "MEDIUM" | "HIGH",
                "action": "ALLOW" | "ALERT" | "BLOCK",
                "details": {...},
            }
        """
        if not isinstance(text, str) or len(text.strip()) < 10:
            return {
                "risk_score": 0.0,
                "risk_level": "NONE",
                "action": "ALLOW",
                "details": {"reason": "text_too_short"},
            }

        # Layer 1: Marker detection
        marker_score = self._score_markers(text)

        # Layer 2: Token-level FFT
        token_features = _extract_features(text)
        token_fft_score = 0.0
        token_par = 0.0
        if len(token_features) >= 8:
            magnitudes = _fft_magnitude(token_features)
            mid_energy = _spectral_energy(magnitudes, *self.MID_BAND)
            high_energy = _spectral_energy(magnitudes, *self.HIGH_BAND)
            token_fft_score = min(1.0, (mid_energy + high_energy * 1.5) * 2.0)
            token_par = min(1.0, _peak_to_average_ratio(magnitudes) / 10.0)

        # Layer 3: Sentence-level FFT
        sent_features = _extract_sentence_features(text)
        sent_fft_score = 0.0
        if len(sent_features) >= 6:
            magnitudes = _fft_magnitude(sent_features)
            mid_energy = _spectral_energy(magnitudes, *self.MID_BAND)
            sent_fft_score = min(1.0, mid_energy * 3.0)

        # Combined score
        risk_score = (
            self.MARKER_WEIGHT * marker_score +
            self.TOKEN_FFT_WEIGHT * token_fft_score +
            self.SENTENCE_FFT_WEIGHT * sent_fft_score +
            self.PAR_WEIGHT * token_par
        )
        risk_score = min(1.0, max(0.0, risk_score))

        # Risk level
        if risk_score >= self.HIGH_RISK:
            risk_level = "HIGH"
        elif risk_score >= self.MEDIUM_RISK:
            risk_level = "MEDIUM"
        elif risk_score >= self.LOW_RISK:
            risk_level = "LOW"
        else:
            risk_level = "NONE"

        # Action
        if risk_score >= self._block_threshold:
            action = "BLOCK"
        elif risk_score >= self._alert_threshold:
            action = "ALERT"
        else:
            action = "ALLOW"

        return {
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "action": action,
            "details": {
                "marker_score": round(marker_score, 4),
                "token_fft_score": round(token_fft_score, 4),
                "sentence_fft_score": round(sent_fft_score, 4),
                "peak_to_average_ratio": round(token_par, 4),
                "token_count": len(token_features),
                "sentence_count": len(sent_features) // 2,
            },
        }

    def _score_markers(self, text: str) -> float:
        """Score based on presence of suspicious steganographic markers."""
        tokens = set(_WORD_RE.findall(text.lower()))
        matches = tokens & _STEGO_MARKERS
        if not matches:
            return 0.0
        # Diminishing returns: 1 match = 0.3, 2 = 0.5, 3+ = 0.7+
        count = len(matches)
        return min(1.0, 0.3 + 0.2 * math.log2(count) if count > 1 else 0.3)
