"""Engineering calculator with OpenAI Responses API function tools."""
import json
import math
import re

# JSON schemas supplied to the LLM; execution remains entirely in Python.
TOOL_SCHEMAS = [
    {"type": "function", "name": "calculate_power", "description": "Compute electrical power in watts from voltage in volts and current in amperes (P=VI).", "parameters": {"type": "object", "properties": {"voltage": {"type": "number"}, "current": {"type": "number"}}, "required": ["voltage", "current"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "calculate_voltage", "description": "Compute voltage in volts from power in watts and current in amperes (V=P/I).", "parameters": {"type": "object", "properties": {"power": {"type": "number"}, "current": {"type": "number"}}, "required": ["power", "current"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "calculate_current", "description": "Compute current in amperes from power in watts and voltage in volts (I=P/V).", "parameters": {"type": "object", "properties": {"power": {"type": "number"}, "voltage": {"type": "number"}}, "required": ["power", "voltage"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "calculate_resistance", "description": "Compute resistance in ohms from voltage in volts and current in amperes (R=V/I).", "parameters": {"type": "object", "properties": {"voltage": {"type": "number"}, "current": {"type": "number"}}, "required": ["voltage", "current"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "convert_units", "description": "Convert between common electrical and temperature units: V/mV, A/mA, W/kW, ohm/kohm, C/F/K.", "parameters": {"type": "object", "properties": {"value": {"type": "number"}, "from_unit": {"type": "string"}, "to_unit": {"type": "string"}}, "required": ["value", "from_unit", "to_unit"], "additionalProperties": False}, "strict": True},
]

_FACTORS = {"V": ("voltage", 1), "mV": ("voltage", .001), "A": ("current", 1), "mA": ("current", .001), "W": ("power", 1), "kW": ("power", 1000), "ohm": ("resistance", 1), "kohm": ("resistance", 1000)}


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError("Arguments must be finite numbers")
    return value


def execute_tool(name, arguments):
    """Whitelist dispatch; never evaluate model-provided code or expressions."""
    if not isinstance(arguments, dict):
        raise ValueError("Expected an argument object")
    expected = {"calculate_power": {"voltage", "current"}, "calculate_voltage": {"power", "current"}, "calculate_current": {"power", "voltage"}, "calculate_resistance": {"voltage", "current"}, "convert_units": {"value", "from_unit", "to_unit"}}
    if name not in expected or set(arguments) != expected[name]:
        raise ValueError("Unknown function or incorrect arguments")
    if name == "convert_units":
        value = _number(arguments["value"])
        source, target = arguments["from_unit"], arguments["to_unit"]
        if source in ("C", "F", "K") and target in ("C", "F", "K"):
            kelvin = value + 273.15 if source == "C" else (value - 32) * 5/9 + 273.15 if source == "F" else value
            if kelvin < 0:
                raise ValueError("Temperature cannot be below absolute zero")
            result = kelvin - 273.15 if target == "C" else (kelvin - 273.15) * 9/5 + 32 if target == "F" else kelvin
        else:
            if source not in _FACTORS or target not in _FACTORS or _FACTORS[source][0] != _FACTORS[target][0]:
                raise ValueError("Unsupported or incompatible units")
            result = value * _FACTORS[source][1] / _FACTORS[target][1]
        return {"value": result, "unit": target, "formula": f"Convert {source} to {target}"}
    args = {k: _number(v) for k, v in arguments.items()}
    if name == "calculate_power":
        result, unit, formula = args["voltage"] * args["current"], "W", "P = V × I"
    elif name == "calculate_voltage":
        if args["current"] == 0: raise ValueError("Current must not be zero")
        result, unit, formula = args["power"] / args["current"], "V", "V = P / I"
    elif name == "calculate_current":
        if args["voltage"] == 0: raise ValueError("Voltage must not be zero")
        result, unit, formula = args["power"] / args["voltage"], "A", "I = P / V"
    else:
        if args["current"] == 0: raise ValueError("Current must not be zero")
        result, unit, formula = args["voltage"] / args["current"], "ohm", "R = V / I"
    if not math.isfinite(result): raise ValueError("Result outside supported range")
    return {"value": result, "unit": unit, "formula": formula}


_CALC_INTENT = re.compile(r"\b(?:calculate|compute|convert|conversion|how many (?:watts|amps|amperes|volts|ohms)|power consumption|what is the (?:power|voltage|current|resistance))\b", re.I)

def is_calculator_query(message):
    return bool(_CALC_INTENT.search(message))


def answer_with_tools(client, model, instructions, conversation, max_rounds=3):
    """Complete Responses API function-call round trips, including tool results."""
    messages = list(conversation)
    for _ in range(max_rounds):
        response = client.responses.create(model=model, instructions=instructions, input=messages, tools=TOOL_SCHEMAS, tool_choice="auto", max_output_tokens=800)
        calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
        if not calls:
            return (response.output_text or "").strip() or "I couldn't produce an answer."
        # Responses requires the function call items alongside their outputs.
        messages.extend(response.output)
        for call in calls:
            try:
                result = execute_tool(call.name, json.loads(call.arguments))
                output = json.dumps({"ok": True, **result})
            except (ValueError, TypeError, json.JSONDecodeError, OverflowError) as exc:
                output = json.dumps({"ok": False, "error": str(exc)})
            messages.append({"type": "function_call_output", "call_id": call.call_id, "output": output})
    return "I couldn't complete the calculation after several tool steps. Please simplify the request."
