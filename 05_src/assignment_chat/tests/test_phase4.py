"""Offline unit tests for calculator and Responses API tool loop."""
import sys
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.calculator_service import execute_tool, is_calculator_query, answer_with_tools

class CalculatorTests(unittest.TestCase):
    def test_power(self):
        self.assertEqual(execute_tool("calculate_power", {"voltage":12,"current":2.5})["value"],30)
    def test_current(self):
        self.assertEqual(execute_tool("calculate_current", {"power":120,"voltage":24})["value"],5)
    def test_voltage(self):
        self.assertEqual(execute_tool("calculate_voltage", {"power":60,"current":5})["value"],12)
    def test_resistance(self):
        self.assertEqual(execute_tool("calculate_resistance", {"voltage":12,"current":2})["value"],6)
    def test_units(self):
        self.assertEqual(execute_tool("convert_units", {"value":2500,"from_unit":"mA","to_unit":"A"})["value"],2.5)
    def test_temperature(self):
        self.assertAlmostEqual(execute_tool("convert_units", {"value":0,"from_unit":"C","to_unit":"F"})["value"],32)
    def test_zero_division(self):
        with self.assertRaises(ValueError): execute_tool("calculate_resistance", {"voltage":12,"current":0})
    def test_bad_units(self):
        with self.assertRaises(ValueError): execute_tool("convert_units", {"value":12,"from_unit":"V","to_unit":"A"})
    def test_router(self):
        self.assertTrue(is_calculator_query("Calculate power at 12V and 2.5A"))
        self.assertFalse(is_calculator_query("According to the knowledge base, what is RAG?"))
    def test_function_call_round_trip(self):
        class FakeResponses:
            def __init__(self): self.inputs=[]
            def create(self, **kwargs):
                self.inputs.append(kwargs["input"])
                if len(self.inputs)==1:
                    return SimpleNamespace(output=[SimpleNamespace(type="function_call",name="calculate_power",arguments=json.dumps({"voltage":12,"current":2.5}),call_id="call_1")],output_text="")
                self_result=self.inputs[-1][-1]
                self.assert_placeholder = self_result
                return SimpleNamespace(output=[],output_text="Power is 30 W.")
        responses=FakeResponses()
        client=SimpleNamespace(responses=responses)
        answer=answer_with_tools(client,"model","instructions",[{"role":"user","content":"Calculate power"}])
        self.assertEqual(answer,"Power is 30 W.")
        self.assertEqual(json.loads(responses.inputs[-1][-1]["output"])["value"],30)

if __name__ == "__main__": unittest.main()
