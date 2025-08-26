import json, argparse, sys, re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# ===== 1) Setting =====
@dataclass
class Weights:
    context: float = 0.40
    system: float  = 0.35
    clarity: float = 0.25

@dataclass
class EvalConfig:
    weights: Weights = field(default_factory=Weights)
    judge_model: str = "gpt-4o"

def read_jsonl(path: str) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                print(f"[WARN] {path}:{i} JSON parse error: {e}", file=sys.stderr)
    return rows

def build_metrics(cfg: EvalConfig, system_prompt: str) -> List[GEval]:
    def make_geval_metric(name: str, steps: List[str], model: str) -> GEval:
        return GEval(
            name=name,
            evaluation_steps=steps,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            model=model,
            threshold=0.5,
        )

    is_case_study = "[TASK=CaseStudy]" in system_prompt
    is_qa = "[TASK=QA]" in system_prompt
    is_guide = "[TASK=GUIDELINE]" in system_prompt

    # 1) Context Grounding
    m_context = make_geval_metric(
        "Context Grounding",
        [
            "Is the main content of the output based strictly on the facts/scope in [Context]?",
            "Is there any hallucination or contradiction with the provided context?",
        ],
        cfg.judge_model,
    )

    # 2) System prompt format adherence (task-specific format checks)
    system_steps: List[str] = [
        "Were the requirements of the system message generally complied with?"
    ]
    if is_qa:
        system_steps += [
            "For [TASK=QA]"
            "Does the answer avoid unnecessary introductions or lengthy explanations?",
            "Are the units and figures preserved exactly as presented in the context?",
            "Is the response concise and straightforward?",
        ]
    if is_guide:
        system_steps += [
            "For [TASK=GUIDELINE",
            "Is the answer presented in a numbered list format?",
            "Does each item contain concise short sentences with clear action instructions?",
            "Does it only include step-by-step guidelines without unnecessary introductions or explanations?",
        ]
    if is_case_study:
        system_steps += [
            "For [TASK=CaseStudy]",
            "Does the output follow the required summary format (Incident Overview, Data/Location, Casualties, Rescue, etc.)?",
            "Is the case sufficiently specific and consistent with the provided context?",
            "Is the analysis and discussion systematic and logical?",
        ]
    m_system = make_geval_metric("System Format Adherence", system_steps, cfg.judge_model)

    # 3) Clarity & Conciseness
    m_clarity = make_geval_metric(
        "Clarity & Conciseness",
        [
            "Is the output clear and unambiguous?",
            "Is it concise and focused on the key points without redundancy or fluff?",
        ],
        cfg.judge_model,
    )

    return [m_context, m_system, m_clarity]

def extract_fields(rec: Dict, default_system_prompt: Optional[str]) -> Tuple[str, str, str]:
    """
    Returns only (system, user, prediction).
    - Top-level: system/system_prompt, user/user_input/input/question/query, prediction/output/answer/model_output/generation
    - If messages exist, supplements system/user fields.
    - If there is a top-level context and 'Context:' is not present in user, automatically combines them (not parsing, just concatenation).
    """
    system_prompt = rec.get("system_prompt") or rec.get("system") or None
    user_text = (
        rec.get("user")
        or rec.get("user_input")
        or rec.get("input")
        or rec.get("question")
        or rec.get("query")
        or None
    )
    prediction = (
        rec.get("prediction")
        or rec.get("output")
        or rec.get("answer")
        or rec.get("model_output")
        or rec.get("generation")
        or ""
    )

    # Supplement messages
    msgs = rec.get("messages")
    if isinstance(msgs, list) and msgs:
        if system_prompt is None:
            sys_parts = [m.get("content", "") for m in msgs if m.get("role") == "system" and m.get("content")]
            if sys_parts:
                system_prompt = "\n".join(sys_parts)
        if user_text is None:
            user_msgs = [m.get("content", "") for m in msgs if m.get("role") == "user" and m.get("content")]
            if user_msgs:
                user_text = user_msgs[-1]

    if system_prompt is None:
        system_prompt = default_system_prompt or ""

    # If context exists as a separate key, combine it into user_text in the "Context/Input" format.
    top_ctx = rec.get("context") or rec.get("Context")
    if top_ctx and user_text:
        if not re.search(r'\bcontext\s*[:：]', user_text, re.IGNORECASE):
            user_text = f"Context: {top_ctx}\nInput: {user_text}"
    elif top_ctx and not user_text:
        user_text = f"Context: {top_ctx}\nInput:"

    if user_text is None:
        user_text = ""

    return system_prompt, user_text, prediction

# ===================== 4) Single Example Scoring =====================
def score_single(system_prompt: str, user_text: str, prediction: str, cfg: EvalConfig) -> Dict:
    joint_input = (
        f"[SYSTEM]\n{system_prompt}\n\n"
        f"[USER MESSAGE]\n{user_text}\n\n"
        f"(Note: The USER MESSAGE contains both 'Context:' and 'Input:'.)\n"
        f"Evaluate the quality of the output based on the above information."
    )
    metrics = build_metrics(cfg, system_prompt)
    tc = LLMTestCase(input=joint_input, actual_output=prediction)

    details: Dict[str, Dict] = {}
    for m in metrics:
        m.measure(tc)
        details[m.name] = {"score": m.score, "reason": m.reason}

    W = cfg.weights
    final = (
        details["Context Grounding"]["score"] * W.context +
        details["System Format Adherence"]["score"] * W.system +
        details["Clarity & Conciseness"]["score"] * W.clarity
    )
    return {"final": final, "geval": details}

def evaluate_jsonl(path: str, cfg: EvalConfig, default_system_prompt: Optional[str]) -> Dict:
    rows = read_jsonl(path)
    per_item, sums, n = [], {
        "final": 0.0,
        "Context Grounding": 0.0,
        "System Format Adherence": 0.0,
        "Clarity & Conciseness": 0.0,
    }, 0

    for idx, rec in enumerate(rows):
        sys_prompt, user_text, pred = extract_fields(rec, default_system_prompt)
        if not pred:
            print(f"[WARN] {path}:{idx+1} - prediction is empty, skipping", file=sys.stderr)
            continue

        result = score_single(sys_prompt, user_text, pred, cfg)
        per_item.append({
            "index": idx,
            "final": result["final"],
            "metrics": {k: v["score"] for k, v in result["geval"].items()},
            "reasons": {k: v["reason"] for k, v in result["geval"].items()},
        })
        n += 1
        sums["final"] += result["final"]
        for k in list(sums.keys()):
            if k == "final":
                continue
            sums[k] += result["geval"][k]["score"]

    if n == 0:
        return {"path": path, "count": 0, "avg": {}, "items": []}

    avg = {k: (v / n) for k, v in sums.items()}
    return {"path": path, "count": n, "avg": avg, "items": per_item}

def main():
    parser = argparse.ArgumentParser(description="Score two JSONL files with GEval and compare averages.")
    parser.add_argument("--file_a", type=str, required=True, help="Path to the first JSONL file (e.g., llama_merge)")
    parser.add_argument("--file_b", type=str, required=True, help="Path to the second JSONL file (e.g., llama_base)")
    parser.add_argument("--system_prompt", type=str, default=None,
                        help="Use a common system prompt string if system/system_prompt is missing in records")
    parser.add_argument("--model", type=str, default="gpt-4o")
    args = parser.parse_args()

    cfg = EvalConfig(judge_model=args.model)

    report_a = evaluate_jsonl(args.file_a, cfg, args.system_prompt)
    report_b = evaluate_jsonl(args.file_b, cfg, args.system_prompt)

    def pretty(report: Dict) -> str:
        if report["count"] == 0:
            return f"{report['path']} -> 항목 0개"
        a = report["avg"]
        lines = [
            f"{report['path']} (n={report['count']})",
            f"  avg.final = {a['final']:.4f}",
            f"    - Context Grounding         : {a['Context Grounding']:.4f}",
            f"    - System Format Adherence   : {a['System Format Adherence']:.4f}",
            f"    - Clarity & Conciseness     : {a['Clarity & Conciseness']:.4f}",
        ]
        return "\n".join(lines)

    print(pretty(report_a))
    print(pretty(report_b))

    if report_a.get("count", 0) and report_b.get("count", 0):
        a_final = report_a["avg"]["final"]
        b_final = report_b["avg"]["final"]
        diff = a_final - b_final
        winner = "A(file_a)" if diff > 0 else ("B(file_b)" if diff < 0 else "Tie")
        print("\n=== Comparison ===")
        print(f"Winner: {winner} | diff = {diff:.4f}")

if __name__ == "__main__":
    main()