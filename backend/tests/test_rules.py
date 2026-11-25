import pytest
from app.rules import next_completion, review_transition

def test_cannot_skip_lessons():
    with pytest.raises(ValueError):
        next_completion(['one','two'], [], 'two')

def test_completion_replay_is_idempotent():
    assert next_completion(['one','two'], ['one'], 'one') is False
    assert next_completion(['one','two'], ['one'], 'two') is True

def test_unknown_lesson_denied():
    with pytest.raises(ValueError):
        next_completion(['one'], [], 'foreign')

def test_human_review_rejects_self_review_and_terminal_state():
    with pytest.raises(ValueError):
        review_transition('submitted','u1','u1','accepted')
    with pytest.raises(ValueError):
        review_transition('accepted','u1','r1','accepted')
    assert review_transition('submitted','u1','r1','accepted') == 'accepted'
