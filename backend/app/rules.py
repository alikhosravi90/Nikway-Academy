def next_completion(ordered: list[str], completed: list[str], lesson: str) -> bool:
    if lesson not in ordered:
        raise ValueError('Unknown lesson')
    if lesson in completed:
        return False
    if ordered.index(lesson) != len(completed):
        raise ValueError('Complete lessons in order')
    return True


def review_transition(status: str, author: str, reviewer: str, decision: str) -> str:
    if author == reviewer:
        raise ValueError('Self review is not permitted')
    if status != 'submitted' or decision not in ('accepted', 'revision_requested'):
        raise ValueError('Invalid review transition')
    return decision
