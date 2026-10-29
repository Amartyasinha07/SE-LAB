import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status

# =====================================================================
# Branch Coverage Test Suite (Achieving 100% Code and Branch Coverage)
# =====================================================================

# ---------------------------------------------------------------------
# 1. Tests for boarding_fee()
# ---------------------------------------------------------------------

def test_boarding_fee_invalid_pet_type():
    """Branch: pet_type not in INCLUDED_DAYS -> raises ValueError"""
    with pytest.raises(ValueError, match="unknown pet type"):
        boarding_fee("bird", 5, False)


def test_boarding_fee_negative_days():
    """Branch: days < 0 -> raises ValueError"""
    with pytest.raises(ValueError, match="invalid days"):
        boarding_fee("dog", -1, False)


def test_boarding_fee_within_or_exact_included_days():
    """Branch: extra <= 0 returns 0 (both strictly less and exactly zero)"""
    # Dog included = 2; days = 1 -> extra = -1 <= 0
    assert boarding_fee("dog", 1, False) == 0
    # Dog included = 2; days = 2 -> extra = 0 <= 0
    assert boarding_fee("dog", 2, False) == 0


def test_boarding_fee_dog_standard_extra_days():
    """Branch: extra > 0, pet_type == 'dog', extra <= 10"""
    # Dog included = 2, days = 5 -> extra = 3 <= 10
    # rate = 30 -> 3 * 30 = 90
    assert boarding_fee("dog", 5, False) == 90


def test_boarding_fee_dog_premium_extended():
    """Branch: is_premium and pet_type != 'rabbit' (True), extra > 10, dog branch (True)"""
    # Dog included = 2 + 1 (premium) = 3
    # days = 15 -> extra = 12 > 10
    # rate = 30 + 10 + 5 = 45 -> 12 * 45 = 540
    assert boarding_fee("dog", 15, True) == 540


def test_boarding_fee_cat_standard_extra_days():
    """Branch: pet_type != 'dog' (rate = 20), extra <= 10, is_premium = False"""
    # Cat included = 3, days = 5 -> extra = 2 <= 10
    # rate = 20 -> 2 * 20 = 40
    assert boarding_fee("cat", 5, False) == 40


def test_boarding_fee_cat_extended():
    """Branch: pet_type != 'dog', extra > 10, nested dog check evaluates to False"""
    # Cat included = 3, days = 15 -> extra = 12 > 10
    # rate = 20 + 10 = 30 (no dog bonus) -> 12 * 30 = 360
    assert boarding_fee("cat", 15, False) == 360


def test_boarding_fee_rabbit_premium_no_extra_day():
    """Branch: is_premium is True, but pet_type == 'rabbit' evaluates to False"""
    # Rabbit included = 4 (premium adds nothing for rabbit)
    # days = 6 -> extra = 2, rate = 20 -> 2 * 20 = 40
    assert boarding_fee("rabbit", 6, True) == 40


# ---------------------------------------------------------------------
# 2. Tests for admission_ok()
# ---------------------------------------------------------------------

def test_admission_senior_eligible():
    """Branch: is_senior = True and vaccinations >= 3 -> True"""
    assert admission_ok(10, 3, True) is True
    assert admission_ok(8, 4, True) is True


def test_admission_senior_ineligible():
    """Branch: is_senior = True and vaccinations < 3 -> False"""
    assert admission_ok(10, 2, True) is False
    assert admission_ok(7, 0, True) is False


def test_admission_puppy_underage():
    """Branch: is_senior = False and pet_age_years < 1 -> False"""
    assert admission_ok(0.8, 5, False) is False
    assert admission_ok(0.0, 3, False) is False


def test_admission_adult_eligible():
    """Branch: is_senior = False, pet_age_years >= 1, and vaccinations >= 2 -> True"""
    assert admission_ok(1.0, 2, False) is True
    assert admission_ok(4, 3, False) is True


def test_admission_adult_ineligible():
    """Branch: is_senior = False, pet_age_years >= 1, and vaccinations < 2 -> False"""
    assert admission_ok(2, 1, False) is False
    assert admission_ok(5, 0, False) is False


# ---------------------------------------------------------------------
# 3. Tests for checkout_status()
# ---------------------------------------------------------------------

def test_checkout_long_stay_weekend():
    """Branches: is_long_stay = True (cutoff=30), is_weekend = True (+20 -> cutoff=50)"""
    # minutes_left >= 50 -> 'open'
    assert checkout_status(50, True, True) == 'open'
    assert checkout_status(65, True, True) == 'open'
    # minutes_left >= 50 - 15 (35) and < 50 -> 'late'
    assert checkout_status(35, True, True) == 'late'
    assert checkout_status(45, True, True) == 'late'
    # minutes_left < 35 -> 'closed'
    assert checkout_status(34, True, True) == 'closed'
    assert checkout_status(0, True, True) == 'closed'


def test_checkout_short_stay_weekday():
    """Branches: is_long_stay = False (cutoff=15), is_weekend = False (cutoff=15)"""
    # minutes_left >= 15 -> 'open'
    assert checkout_status(15, False, False) == 'open'
    assert checkout_status(30, False, False) == 'open'
    # minutes_left >= 15 - 15 (0) and < 15 -> 'late'
    assert checkout_status(0, False, False) == 'late'
    assert checkout_status(10, False, False) == 'late'
    # minutes_left < 0 -> 'closed'
    assert checkout_status(-1, False, False) == 'closed'


def test_checkout_long_stay_weekday():
    """Branches: is_long_stay = True (cutoff=30), is_weekend = False (cutoff=30)"""
    assert checkout_status(30, True, False) == 'open'
    assert checkout_status(20, True, False) == 'late'
    assert checkout_status(10, True, False) == 'closed'


def test_checkout_short_stay_weekend():
    """Branches: is_long_stay = False (cutoff=15), is_weekend = True (+20 -> cutoff=35)"""
    assert checkout_status(35, False, True) == 'open'
    assert checkout_status(25, False, True) == 'late'
    assert checkout_status(15, False, True) == 'closed'
