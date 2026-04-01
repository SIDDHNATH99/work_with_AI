"""
Safe math expression evaluator using Python's AST.
No eval() — only whitelisted operators and functions are allowed.
"""

import ast
import math
import operator as op

_OPERATORS = {
    ast.Add:      op.add,
    ast.Sub:      op.sub,
    ast.Mult:     op.mul,
    ast.Div:      op.truediv,
    ast.Pow:      op.pow,
    ast.Mod:      op.mod,
    ast.FloorDiv: op.floordiv,
    ast.USub:     op.neg,
    ast.UAdd:     op.pos,
}

_SAFE_NAMES = {
    "pi": math.pi, "e": math.e, "tau": math.tau, "inf": math.inf,
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "sqrt": math.sqrt, "log": math.log, "log2": math.log2, "log10": math.log10,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
    "ceil": math.ceil, "floor": math.floor, "exp": math.exp,
    "degrees": math.degrees, "radians": math.radians,
    "factorial": math.factorial, "gcd": math.gcd,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, complex)):
            raise ValueError(f"Literal type not supported: {type(node.value).__name__}")
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in _SAFE_NAMES:
            raise ValueError(f"Unknown name: {node.id!r}")
        return _SAFE_NAMES[node.id]
    if isinstance(node, ast.BinOp):
        fn = _OPERATORS.get(type(node.op))
        if fn is None:
            raise ValueError(f"Operator not supported: {type(node.op).__name__}")
        return fn(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        fn = _OPERATORS.get(type(node.op))
        if fn is None:
            raise ValueError(f"Unary operator not supported: {type(node.op).__name__}")
        return fn(_eval(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_NAMES:
            raise ValueError(f"Function not allowed: {getattr(node.func, 'id', '?')!r}")
        fn = _SAFE_NAMES[node.func.id]
        if not callable(fn):
            raise ValueError(f"'{node.func.id}' is a constant, not callable")
        return fn(*[_eval(a) for a in node.args])
    raise ValueError(f"AST node type not supported: {type(node).__name__}")


def safe_calculate(expression: str) -> dict:
    if not expression or len(expression) > 500:
        return {"error": "Expression must be non-empty and under 500 characters"}
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval(tree)
        # Convert result to a JSON-safe type
        if isinstance(result, complex):
            return {"expression": expression, "result": str(result)}
        if isinstance(result, float) and (math.isinf(result) or math.isnan(result)):
            return {"expression": expression, "result": str(result)}
        return {"expression": expression, "result": result}
    except (ZeroDivisionError, OverflowError) as exc:
        return {"expression": expression, "error": str(exc)}
    except Exception as exc:
        return {"expression": expression, "error": f"Parse/eval error: {exc}"}
