"""Independent arithmetic cases for the local Pythagorean profile."""
import xml.etree.ElementTree as ET
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.metadata import reduction

client = TestClient(app)


def calculate(name="O'ralle Rivenunti", birthday="1986-09-09", **extra):
    return client.post('/api/synastry/metadata', json={
        'full_name': name, 'birth_date': birthday, 'reference_year': 2026, **extra})


def test_fictional_profile_arithmetic_and_complete_original_reading():
    result = calculate()
    assert result.status_code == 200
    report = result.json()
    expected = {'life_path': [24, 6], 'expression': [78, 15, 6],
                'soul_urge': [38, 11], 'personality': [40, 4],
                'birthday': [9], 'maturity': [12, 3], 'personal_year': [19, 10, 1]}
    for key, steps in expected.items():
        assert report['core'][key]['steps'] == steps
    assert report['core']['soul_urge']['display_number'] == '11/2'
    assert report['missing_numbers'] == [7, 8]
    assert report['challenges'] == [0, 3, 3, 3]
    assert [p['number'] for p in report['pinnacles']] == [9, 6, 6, 6]
    assert report['karmic_debts'] == []  # 40 -> 4 never passes through 13.
    assert sum(len(p.split()) for s in report['sections'] for p in s['paragraphs']) > 2000
    ET.fromstring(report['report_svg'])


@pytest.mark.parametrize('total,expected', [(29, [29, 11]), (22, [22]),
                                          (33, [33]), (49, [49, 13, 4])])
def test_master_numbers_and_actual_intermediate_totals(total, expected):
    assert reduction(total)['steps'] == expected


def test_component_life_path_and_user_selected_vowel_y():
    result = calculate('Lynn', '1990-07-15', y_vowel_positions=[2]).json()
    assert result['core']['life_path']['steps'] == [14, 5]
    assert result['core']['expression']['total'] == 20
    assert result['core']['soul_urge']['total'] == 7
    assert result['core']['personality']['total'] == 13
    assert any(d['compound'] == 13 for d in result['karmic_debts'])
    assert calculate('Lynn').json()['core']['soul_urge'] is None
    assert calculate('AEIOU').json()['core']['personality'] is None


def test_diacritics_and_punctuation_have_consistent_values_and_escaped_svg():
    a = calculate('Éva-Marie').json()
    b = calculate('Eva Marie').json()
    assert a['core'] == b['core']
    report = calculate('<Eva & Marie>').json()
    assert '&lt;Eva &amp; Marie&gt;' in report['report_svg']
    ET.fromstring(report['report_svg'])


@pytest.mark.parametrize('body', [
    {'full_name': '123'}, {'full_name': ''}, {'full_name': '名字'},
    {'birth_date': '2025-02-29'}, {'birth_date': '1899-01-01'},
    {'reference_year': 1800}, {'y_vowel_positions': [1]},
])
def test_invalid_input_is_rejected_without_fabricated_results(body):
    payload = {'full_name': "O'ralle Rivenunti", 'birth_date': '1986-09-09',
               'reference_year': 2026, **body}
    assert client.post('/api/synastry/metadata', json=payload).status_code == 422
