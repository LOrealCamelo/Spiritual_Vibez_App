/**
 * AuraMystic Full-Stack TypeScript API Client for React Native (Expo) & Web
 */
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchDailyTransits(sign: string = 'Scorpio') {
  const res = await fetch(`${API_BASE_URL}/astrology/daily-transits?sign=${encodeURIComponent(sign)}`);
  return res.json();
}

export async function calculateNatalMoonPhase(birth_date: string, birth_time: string = '14:30') {
  const res = await fetch(`${API_BASE_URL}/astrology/moon-phase`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ birth_date, birth_time }),
  });
  return res.json();
}

export async function calculateLifePath(birth_month: number, birth_day: number, birth_year: number) {
  const res = await fetch(`${API_BASE_URL}/synastry/life-path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ birth_month, birth_day, birth_year }),
  });
  return res.json();
}

export async function generateSynastryReport(partner_a_sign: string, partner_b_sign: string) {
  const res = await fetch(`${API_BASE_URL}/synastry/compatibility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ partner_a_sign, partner_b_sign }),
  });
  return res.json();
}

export async function fetchStudyQuizQuestion(card_id?: number) {
  const query = card_id !== undefined ? `?card_id=${card_id}` : '';
  const res = await fetch(`${API_BASE_URL}/tarot/study/quiz${query}`);
  return res.json();
}

export async function dealSpreadSlot(spread_id: string, slot_num: number, exclude_card_ids: number[] = []) {
  const res = await fetch(`${API_BASE_URL}/tarot/spreads/deal-slot`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ spread_id, slot_num, exclude_card_ids }),
  });
  return res.json();
}

export async function dealEntireSpread(spread_id: string, save_to_journal: boolean = false) {
  const res = await fetch(`${API_BASE_URL}/tarot/spreads/deal-all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ spread_id, save_to_journal }),
  });
  return res.json();
}

export async function askOracle(message: string, zodiac_sign: string = 'Scorpio') {
  const res = await fetch(`${API_BASE_URL}/oracle/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, zodiac_sign }),
  });
  return res.json();
}
