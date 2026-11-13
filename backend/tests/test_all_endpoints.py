"""
Comprehensive Automated Verification Suite for AuraMystic Backend API
Verifies all 8 routers, database persistence, ephemeris engine, 78-card Tarot & 48 spreads,
numerology/synastry, frequencies/rituals, menstrual/shadow work, divination, oracle AI, and storefront.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.main import app, health_check
from backend.models import (
    BirthDataRequest, BaZiRequest, RelocationRequest,
    LifePathRequest, SynastryRequest,
    DealSlotRequest, DealSpreadRequest, SynthesizeSpreadRequest, DrawnCardItem, StudyAnswerRequest,
    RitualCompleteRequest, JonasFertilityRequest,
    MenstrualCycleRequest, ShadowJournalCreateRequest,
    PendulumRequest, RuneCastRequest,
    OracleChatRequest, StoreCartAddRequest
)
from backend.routers import astrology, synastry, tarot, rituals, wellness, divination, oracle_ai, store

def run_all_tests():
    # Health
    h = health_check()
    assert h["status"] == "online" and len(h["modules"]) == 8

    # 1. Astrology & Charts
    transits = astrology.get_daily_transits(sign="Scorpio", date="2026-11-05")
    assert transits["selected_sign"] == "Scorpio"
    assert "forecast" in transits and len(transits["forecast"]["details"]) == 5

    moon = astrology.calculate_natal_moon_phase(BirthDataRequest(birth_date="1996-11-05", birth_time="14:30", place_id="5142056"))
    assert "natal_moon_phase" in moon and "illumination_percentage" in moon

    for sys_name in ("placidus", "tropical", "progressed"):
        chart = astrology.generate_natal_chart(BirthDataRequest(birth_date="1996-11-05", birth_time="14:30", place_id="5142056", chart_system=sys_name))
        assert len(chart["placements"]) == 10 and len(chart["houses"]) == 12 and chart["wheel_svg"]

    lunar_cal = astrology.get_lunar_calendar(13)
    assert lunar_cal["days_in_cycle"] == 28 and len(lunar_cal["days"]) == 28

    bazi = astrology.get_bazi_pillars(body=BaZiRequest(birth_year=1996, polarity="Yin Feminine"))
    assert "year_pillar" in bazi["pillars"] and "day_master" in bazi["pillars"]

    reloc = astrology.post_astrocartography_relocation(RelocationRequest(birth_date="1996-11-05", birth_time="14:30", place_id="5142056"))
    assert reloc["report_type"] == "astrocartography" and len(reloc["planets"]) == 10

    # 2. Numerology & Synastry
    lp = synastry.calculate_life_path(LifePathRequest(birth_month=11, birth_day=5, birth_year=1996))
    assert lp["life_path_number"] in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)

    lessons = synastry.get_all_numerology_lessons()
    assert len(lessons["lessons"]) == 12

    compat = synastry.generate_synastry_report(SynastryRequest(partner_a_sign="Scorpio", partner_b_sign="Taurus"))
    assert compat["overall_affinity_percent"] == 94
    assert "emotional_depth" in compat["sub_scores"]

    # 3. Tarot Study & 48 Spreads Studio
    cards_res = tarot.list_tarot_cards(suit="all", search=None)
    assert cards_res["count"] == 78

    hierophant = tarot.get_card_detail(5)
    assert hierophant["name"] == "The Hierophant"

    quiz = tarot.get_study_quiz_question(card_id=5)
    assert quiz["card_name"] == "The Hierophant" and quiz["correct_answer"] == "TRADITION"

    ans_res = tarot.submit_study_quiz_answer(StudyAnswerRequest(user_id="loreal_test", card_id=5, selected_keyword="TRADITION"))
    assert ans_res["is_correct"] is True and ans_res["progress"]["current_streak"] >= 1

    cats = tarot.get_spread_categories()
    assert cats["total_spreads"] == 48 and len(cats["categories"]) == 7

    reset_sp = tarot.get_reset_your_energy_spread()
    assert reset_sp["id"] == "reset-energy" and reset_sp["cardCount"] == 4

    slot_deal = tarot.deal_single_slot(DealSlotRequest(spread_id="reset-energy", slot_num=1))
    assert slot_deal["slot"] == 1 and "card" in slot_deal

    full_deal = tarot.deal_entire_spread(DealSpreadRequest(spread_id="reset-energy", save_to_journal=True))
    assert len(full_deal["positions"]) == 4 and "NeuroSpicy Mystic" in full_deal["holistic_synthesis"]

    synth = tarot.synthesize_custom_spread(SynthesizeSpreadRequest(
        spread_id="reset-energy",
        drawn_cards=[DrawnCardItem(slot=1, card_id=5, orientation="Upright")],
        save_to_journal=True
    ))
    assert len(synth["positions"]) == 1

    saved_readings = tarot.get_saved_readings()
    assert len(saved_readings["readings"]) >= 2

    # 4. Solfeggio Frequencies, Rituals & Ancient Fertility
    freqs = rituals.get_solfeggio_frequencies()
    assert len(freqs["frequencies"]) == 8

    rits = rituals.search_rituals(category="money", query=None)
    assert rits["count"] >= 2

    comp = rituals.mark_ritual_complete("ritual-1", RitualCompleteRequest(intention_notes="Abundance activation"))
    assert comp["status"] == "completed"

    fert = rituals.get_ancient_fertility_practices()
    assert len(fert["practices"]) == 3

    jonas = rituals.calculate_jonas_lunar_fertility(JonasFertilityRequest(birth_date="1996-11-05", last_period_date="2026-10-22", cycle_length=28))
    assert "jonas_cosmobiology_window" in jonas

    # 5. Wellness: Menstrual Cycle & Shadow Work Journal
    cyc = wellness.calculate_lunar_menstrual_cycle(MenstrualCycleRequest(last_period_date="2026-10-23", cycle_length=28))
    assert cyc["phase_name"] == "Ovulatory"

    j_entry = wellness.create_shadow_journal_entry(ShadowJournalCreateRequest(
        prompt="What boundary protects my peace?",
        entry_text="Honoring my async working rhythm and protecting my nervous system."
    ))
    assert j_entry["status"] == "saved"
    j_list = wellness.list_shadow_journal_entries()
    assert len(j_list["entries"]) >= 1

    # 6. Divination Hub: Pendulum & Runes
    pend = divination.dowse_amethyst_pendulum(PendulumRequest(question="Is this launch aligned with my highest timeline?"))
    assert "answer" in pend and "swing_geometry" in pend

    runes = divination.cast_elder_futhark_runes(RuneCastRequest(rune_count=3))
    assert len(runes["cast_runes"]) == 3

    # 7. AI Mystic Oracle
    chat1 = oracle_ai.chat_with_oracle(OracleChatRequest(message="How do I interpret The High Priestess reversed?"))
    assert "High Priestess" in chat1["oracle_response"]
    hist = oracle_ai.get_oracle_chat_history(session_id="auramystic_default_session")
    assert len(hist["messages"]) >= 1

    # 8. Storefront
    prods = store.get_store_products()
    assert prods["store_url"] == "https://www.neurospicymystic.com" and len(prods["products"]) == 4

    cart = store.add_to_cart(StoreCartAddRequest(session_id="test_bag", product_id="528hz-tuning-forks", quantity=1))
    assert cart["subtotal_usd"] == 64.00

    print("ALL 28 BACKEND ENDPOINT TESTS PASSED WITH ZERO ERRORS!")

if __name__ == "__main__":
    run_all_tests()
