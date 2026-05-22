from difflib import SequenceMatcher

def normalize_name(name: str) -> str:
    return " ".join(name.lower().strip().split())

def names_match(a: str, b: str, threshold: float = 0.85) -> bool:
    a, b = normalize_name(a), normalize_name(b)
    if a == b:
        return True
    # "Sarah Chen" vs "sarah.chen" vs "s.chen"
    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio >= threshold

def deduplicate_employees(employees: list[dict]) -> list[dict]:
    """Merge employees with the same name/email across sources."""
    seen: list[dict] = []
    for emp in employees:
        name = emp.get("name", "")
        email = (emp.get("email") or "").lower()
        merged = False
        for existing in seen:
            ex_email = (existing.get("email") or "").lower()
            if (email and ex_email and email == ex_email) or \
               names_match(name, existing.get("name", "")):
                # Merge: prefer non-null fields
                for k, v in emp.items():
                    if v and not existing.get(k):
                        existing[k] = v
                merged = True
                break
        if not merged:
            seen.append(dict(emp))
    return seen

def deduplicate_power_nodes(nodes: list[dict]) -> list[dict]:
    """Remove duplicate nodes in power structure output from Groq."""
    seen_names: set[str] = set()
    result = []
    for node in nodes:
        key = normalize_name(node.get("name", ""))
        if not key or key in seen_names:
            continue
        seen_names.add(key)
        result.append(node)
    return result