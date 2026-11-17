"""Bounded session memory with turn and character budgets."""
from typing import Any
from guardrails import check_user_message


def build_conversation_input(
    history: list[Any], latest_message: str, max_turns: int = 8,
    max_history_chars: int = 12000,
) -> list[dict[str, str]]:
    """Use recent valid exchanges; trim oldest first to bound context size.

    The current message is always included. The history budget is approximate
    (characters, not tokens); no LLM summary or persistent user memory.
    """
    cleaned = []
    for item in history or []:
        if isinstance(item, dict):
            role, content = item.get('role'), item.get('content')
            if role in ('user', 'assistant') and isinstance(content, str):
                cleaned.append({'role': role, 'content': content})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            user, assistant = item
            if isinstance(user, str):
                cleaned.append({'role': 'user', 'content': user})
            if isinstance(assistant, str):
                cleaned.append({'role': 'assistant', 'content': assistant})

    # Treat the full history as untrusted. Do not replay blocked user turns or
    # assistant refusals from those turns as instructions in future requests.
    safe = []
    for msg in cleaned:
        if msg['role'] == 'user':
            allowed, _ = check_user_message(msg['content'])
            if not allowed:
                continue
        else:
            allowed, _ = check_user_message(msg['content'])
            if not allowed:
                continue
        safe.append(msg)

    safe = safe[-max_turns * 2:] if max_turns > 0 else []
    budget = max(0, max_history_chars)
    selected = []
    for msg in reversed(safe):
        length = len(msg['content'])
        if length > budget:
            break
        selected.append(msg)
        budget -= length
    selected.reverse()
    selected.append({'role': 'user', 'content': latest_message})
    return selected
