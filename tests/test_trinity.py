"""
ADRION 369 — Tests: Trinity Engine
====================================
Testy jednostkowe dla core/trinity.py v5.3.
Uruchom: python -m pytest tests/test_trinity.py -v

Pokrycie:
    - Obliczanie Trinity Score z wagami 0.33/0.34/0.33
    - Wszystkie 4 strefy bramki decyzyjnej
    - Minimum per-perspective floor
    - Dimensional Balance (IMBALANCED / BALANCED)
    - Asymmetry detection
    - G5 compliance (reasoning >= 20 znaków)
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.trinity import TrinityEngine, PerspectiveResult


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    return TrinityEngine()


def p(score: float, reasoning: str = "Test reasoning — minimum dwadzieścia znaków.") -> PerspectiveResult:
    """Helper: tworzy PerspectiveResult"""
    return PerspectiveResult(score=score, reasoning=reasoning)


# ── Testy wag ─────────────────────────────────────────────────────────────────

class TestWeights:

    def test_weights_sum_to_one(self, engine):
        """Wagi muszą sumować się do 1.0"""
        total = sum(engine.weights.values())
        assert abs(total - 1.0) < 1e-9, f"Wagi sumują się do {total}, oczekiwano 1.0"

    def test_weights_values(self, engine):
        """Wagi zgodne z dokumentacją docs/01_CORE_TRINITY.md"""
        assert engine.weights["material"]     == 0.33
        assert engine.weights["intellectual"] == 0.34
        assert engine.weights["essential"]    == 0.33

    def test_score_calculation(self, engine):
        """Weryfikacja ręcznie obliczonego Trinity Score"""
        mat, intel, ess = 0.8, 0.9, 0.7
        expected = 0.33 * mat + 0.34 * intel + 0.33 * ess
        result = engine.calculate_score(p(mat), p(intel), p(ess))
        assert abs(result.score - round(expected, 4)) < 1e-4


# ── Testy bramek decyzyjnych ──────────────────────────────────────────────────

class TestDecisionGates:

    def test_deny_below_030(self, engine):
        """score < 0.30 → DENY"""
        result = engine.calculate_score(p(0.28), p(0.28), p(0.28))
        assert result.decision == "DENY"

    def test_hold_sentinel_030_055(self, engine):
        """score ∈ [0.30, 0.55) → HOLD_SENTINEL_REVIEW"""
        result = engine.calculate_score(p(0.45), p(0.45), p(0.45))
        assert result.decision == "HOLD_SENTINEL_REVIEW"

    def test_hold_human_055_070(self, engine):
        """score ∈ [0.55, 0.70) → HOLD_HUMAN_REVIEW"""
        result = engine.calculate_score(p(0.62), p(0.62), p(0.62))
        assert result.decision == "HOLD_HUMAN_REVIEW"

    def test_proceed_above_070(self, engine):
        """score ≥ 0.70, wszystkie perspektywy ≥ 0.40 → PROCEED"""
        result = engine.calculate_score(p(0.80), p(0.80), p(0.80))
        assert result.decision == "PROCEED"
        assert result.status == "BALANCED"

    def test_grock_gray_zone_055_escalate(self, engine):
        """
        Raport Grock: atak z perspektywami 0.55 (gray zone).
        Oczekiwany wynik: HOLD (nie PROCEED) — strefa 0.55 to jeszcze HOLD_HUMAN.
        """
        # score = 0.33*0.55 + 0.34*0.55 + 0.33*0.55 = 0.55
        result = engine.calculate_score(p(0.55), p(0.55), p(0.55))
        assert result.decision == "HOLD_HUMAN_REVIEW", (
            f"Grock attack: score=0.55 powinno dać HOLD, dostano {result.decision}"
        )


# ── Testy minimum per-perspective ─────────────────────────────────────────────

class TestMinimumPerPerspective:

    def test_deny_if_any_below_025(self, engine):
        """Perspektywa < 0.25 → DENY (floor violation)"""
        result = engine.calculate_score(p(0.20), p(0.90), p(0.90))
        assert result.decision == "DENY"
        assert "FLOOR_VIOLATION" in result.status

    def test_hold_if_proceed_but_weak_perspective(self, engine):
        """Score ≥ 0.70 ale jedna perspektywa < 0.40 → HOLD (nie PROCEED)"""
        # Score wysoki przez dwie bardzo wysokie perspektywy
        result = engine.calculate_score(p(0.95), p(0.95), p(0.35))
        # score ≈ 0.33*0.95 + 0.34*0.95 + 0.33*0.35 = 0.749... ≥ 0.70
        # ale essential=0.35 < MIN_PROCEED_PER_PERSP=0.40 → HOLD
        assert result.decision in ("HOLD_SENTINEL_REVIEW", "HOLD_HUMAN_REVIEW"), (
            f"Asymetryczna perspektywa powinna blokować PROCEED, dostano {result.decision}"
        )

    def test_prespective_validation_error(self):
        """PerspectiveResult z krótkim reasoning → ValueError (G5)"""
        with pytest.raises(ValueError, match="[Rr]easoning must be.* 20"):
            PerspectiveResult(score=0.5, reasoning="Za krótkie")

    def test_prespective_score_out_of_range(self):
        """PerspectiveResult z score > 1.0 → ValueError"""
        with pytest.raises(ValueError, match="Score must be in"):
            PerspectiveResult(score=1.5, reasoning="Test reasoning — minimum dwadzieścia znaków.")


# ── Testy Dimensional Balance ─────────────────────────────────────────────────

class TestDimensionalBalance:

    def test_balanced_when_std_dev_low(self, engine):
        """std_dev ≤ 0.30 → BALANCED"""
        result = engine.calculate_score(p(0.80), p(0.82), p(0.78))
        assert result.status == "BALANCED"

    def test_imbalanced_when_std_dev_high(self, engine):
        """std_dev > 0.30 → IMBALANCED"""
        result = engine.calculate_score(p(0.90), p(0.50), p(0.40))
        assert "IMBALANCED" in result.status or "ASYMMETRIC" in result.status


# ── Testy asymmetry detection ─────────────────────────────────────────────────

class TestAsymmetryDetection:

    def test_asymmetry_detected_when_spread_large(self, engine):
        """spread > 0.45 → ASYMMETRY_DETECTED flag"""
        # max=0.95, min=0.45 → spread=0.50 > 0.45
        result = engine.calculate_score(p(0.95), p(0.70), p(0.45))
        assert any("ASYMMETRY" in f for f in result.flags), (
            f"Duży spread powinien wygenerować ASYMMETRY flag, flags={result.flags}"
        )


# ── Testy jawności (glass-box) ────────────────────────────────────────────────

class TestGlassBox:

    def test_weights_publicly_accessible(self, engine):
        """Wagi są publicznie dostępne (property weights)"""
        w = engine.weights
        assert "material" in w
        assert "intellectual" in w
        assert "essential" in w

    def test_gates_publicly_accessible(self, engine):
        """Bramki są publicznie dostępne (property gates)"""
        g = engine.gates
        assert "deny_below" in g
        assert "proceed_above" in g
        assert g["deny_below"] == 0.30
        assert g["proceed_above"] == 0.70


# ── Testy scenariuszy z raportu Grock ────────────────────────────────────────

class TestGrockReportScenarios:

    def test_grock_attack_all_055_gray_zone(self, engine):
        """
        Raport Grock §Prompt-atak v3: wszystkie perspektywy = 0.55.
        Oczekiwany wynik: HOLD (nie PROCEED) — system MUSI eskalować.
        """
        result = engine.calculate_score(p(0.55), p(0.55), p(0.55))
        assert result.decision != "PROCEED", "Atak Grock (0.55 gray zone) nie powinien dać PROCEED"
        assert "HOLD" in result.decision

    def test_grock_attack_asymmetric_high_essential(self, engine):
        """
        Raport Grock §Luka 1: wysoka Essential, niskie pozostałe.
        Stara wersja: mogło dać PROCEED przez wysoką Essential.
        Nowa wersja: wykryta asymetria → HOLD.
        """
        # Essential bardzo wysoka, reszta słaba
        result = engine.calculate_score(p(0.45), p(0.45), p(0.95))
        # score ≈ 0.33*0.45 + 0.34*0.45 + 0.33*0.95 = 0.628 → HOLD_HUMAN lub blokada asymetrii
        assert result.decision != "PROCEED", (
            "Asymetryczna Essential=0.95 nie powinna dać PROCEED bez checkpointa"
        )
