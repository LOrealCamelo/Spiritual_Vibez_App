"""
Pydantic v2 Data Models & Request/Response Schemas for AuraMystic API
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class BirthDataRequest(BaseModel):
    birth_date: str = Field(..., description="YYYY-MM-DD", examples=["1996-11-05"])
    birth_time: str = Field(..., description="Local HH:MM (24h)", examples=["14:30"])
    name: str = Field('', max_length=80)
    place_id: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = None
    time_fold: Optional[int] = Field(None, ge=0, le=1, description="0 first / 1 second occurrence during a repeated DST hour")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    zodiac: str = 'tropical'
    house_system: str = 'placidus'
    chart_system: Optional[str] = Field("placidus", description="placidus | tropical | progressed | draconic")

class BaZiRequest(BaseModel):
    birth_year: int = Field(1996, ge=1900, le=2100)
    birth_month: Optional[int] = Field(11, ge=1, le=12)
    birth_day: Optional[int] = Field(5, ge=1, le=31)
    birth_hour: Optional[int] = Field(14, ge=0, le=23)
    polarity: Optional[str] = Field("Yin Feminine", description="Yin Feminine | Yang Masculine | Balanced Sovereign")

class RelocationRequest(BaseModel):
    city: str = Field("Utica, NY", description="Target city name")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    birth_date: Optional[str] = "1996-11-05"
    birth_time: Optional[str] = "14:30"

class LifePathRequest(BaseModel):
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_year: int = Field(..., ge=1900, le=2100)

class SynastryRequest(BaseModel):
    partner_a_sign: str = Field(..., examples=["Scorpio"])
    partner_a_birthdate: Optional[str] = Field("1996-11-05")
    partner_a_gender: Optional[str] = Field("Divine Feminine")
    partner_b_sign: str = Field(..., examples=["Taurus"])
    partner_b_birthdate: Optional[str] = Field("1994-05-12")
    partner_b_gender: Optional[str] = Field("Divine Masculine")

class DealSlotRequest(BaseModel):
    spread_id: str = Field("reset-energy")
    slot_num: int = Field(1, ge=1, le=15)
    exclude_card_ids: List[int] = Field(default_factory=list)

class DealSpreadRequest(BaseModel):
    spread_id: str = Field("reset-energy")
    save_to_journal: bool = Field(False)

class DrawnCardItem(BaseModel):
    slot: int
    card_id: int
    orientation: str = "Upright"

class SynthesizeSpreadRequest(BaseModel):
    spread_id: str = Field("reset-energy")
    drawn_cards: List[DrawnCardItem]
    save_to_journal: bool = Field(True)

class StudyAnswerRequest(BaseModel):
    user_id: str = Field("default_mystic")
    card_id: int
    selected_keyword: str

class RitualCompleteRequest(BaseModel):
    intention_notes: Optional[str] = Field("", description="Personal intention or manifestation note")

class JonasFertilityRequest(BaseModel):
    birth_date: str = Field("1996-11-05")
    last_period_date: str = Field("2026-10-22")
    cycle_length: int = Field(28, ge=20, le=45)

class MenstrualCycleRequest(BaseModel):
    last_period_date: str = Field(..., description="YYYY-MM-DD", examples=["2026-10-22"])
    cycle_length: int = Field(28, ge=20, le=45)

class ShadowJournalCreateRequest(BaseModel):
    prompt: str
    entry_text: str
    moon_phase: Optional[str] = "Waxing Gibbous in Pisces"
    tags: Optional[List[str]] = Field(default_factory=list)

class PendulumRequest(BaseModel):
    question: str = Field(..., description="Yes or no question for the Amethyst Pendulum")

class RuneCastRequest(BaseModel):
    focus_intention: Optional[str] = Field("General Spiritual Path & Sovereign Alignment")
    rune_count: int = Field(3, ge=1, le=9)

class OracleChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = Field("auramystic_default_session")
    zodiac_sign: Optional[str] = Field("Scorpio")

class StoreCartAddRequest(BaseModel):
    session_id: str = Field("auramystic_default_session")
    product_id: str
    quantity: int = Field(1, ge=1, le=20)
