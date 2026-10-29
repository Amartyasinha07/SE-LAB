import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status

# ==========================================
# Code Coverage Test Suite (>90% Line Coverage)
# ==========================================

# 1. boarding_fee tests
def test_boarding_fee_within_included_days():
    # Dog included days = 2, staying 1 day -> extra <= 0 -> fee = 0
    assert boarding_fee("dog", 1, False) == 0

def test_boarding_fee_dog_premium_extended():
    # Dog premium kennel: included = 2 + 1 = 3
    # days = 15 -> extra = 12 (> 10)
    # rate = 30 + 10 + 5 = 45 -> fee = 12 * 45 = 540
    assert boarding_fee("dog", 15, True) == 540

def test_boarding_fee_cat_standard():
    # Cat included = 3, staying 5 days -> extra = 2 (<= 10)
    # rate = 20 -> fee = 2 * 20 = 40
    assert boarding_fee("cat", 5, False) == 40


# 2. admission_ok tests
def test_admission_senior_pass():
    # Senior pet with 3 vaccinations
    assert admission_ok(10, 3, True) is True

def test_admission_underage():
    # Pet under 1 year old
    assert admission_ok(0.5, 3, False) is False

def test_admission_adult_pass():
    # Adult pet with 2 vaccinations
    assert admission_ok(3, 2, False) is True


# 3. checkout_status tests
def test_checkout_long_stay_weekend_open():
    # Long stay (cutoff = 30) + weekend (+20) = 50 cutoff
    # 60 minutes left >= 50 -> "open"
    assert checkout_status(60, True, True) == "open"

def test_checkout_short_stay_weekday_late():
    # Short stay (cutoff = 15) + weekday (0) = 15 cutoff
    # 10 minutes left: >= 15 - 15 (0) and < 15 -> "late"
    assert checkout_status(10, False, False) == "late"

def test_checkout_short_stay_weekday_closed():
    # Short stay (15 cutoff); -5 minutes left -> "closed"
    assert checkout_status(-5, False, False) == "closed"
