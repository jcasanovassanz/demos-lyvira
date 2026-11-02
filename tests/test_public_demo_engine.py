import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from public_demo_engine import Assessment, evaluate  # noqa: E402


class PublicDemoEngineTest(unittest.TestCase):
    def make(self, **changes):
        values = dict(
            area="Ventas", process="Preparar propuestas", frequency=4, time=4,
            repetition=4, rules=4, review=4, impact=4, risk="medio",
            task_types=("Redactar",), goal="Reducir tiempo"
        )
        values.update(changes)
        return Assessment(**values)

    def test_good_candidate_recommends_assistance(self):
        result = evaluate(self.make())
        self.assertEqual(result["ai_role"], "Asistir con IA")
        self.assertEqual(result["score"], 24)

    def test_unclear_rules_prioritize_standardization(self):
        result = evaluate(self.make(rules=1))
        self.assertEqual(result["ai_role"], "Estandarizar antes de automatizar")
        self.assertTrue(result["blockers"])

    def test_high_risk_keeps_human_control(self):
        result = evaluate(self.make(risk="alto"))
        self.assertEqual(result["ai_role"], "Asistencia con control humano")

    def test_sales_area_returns_deeper_analysis(self):
        result = evaluate(self.make(area="Ventas", area_details={
            "stage": "Preparación de propuesta",
            "lead_source": "Varios canales",
            "notes": "Dispersas en varios sitios",
            "crm": "CRM, pero no siempre actualizado",
            "proposal": "Propuesta comercial",
            "approvals": "Dirección comercial y operaciones",
            "bottlenecks": ["Precio o descuentos", "Redactar propuesta"],
        }))
        self.assertIn("sales_analysis", result)
        self.assertGreaterEqual(len(result["sales_analysis"]["pilot_scope"]), 3)
        self.assertTrue(result["sales_analysis"]["gaps_to_clarify"])


if __name__ == "__main__":
    unittest.main()
