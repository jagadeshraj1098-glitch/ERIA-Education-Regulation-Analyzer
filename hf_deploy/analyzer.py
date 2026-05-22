import os
import json

PROVIDER = os.environ.get('LLM_PROVIDER', 'groq').lower()


def analyze_regulation(text: str) -> dict:
    if PROVIDER == 'gemini':
        return _analyze_with_gemini(text)
    return _analyze_with_groq(text)


def _build_prompt(text: str) -> str:
    return (
        "You are ERIA, an Education Regulation Impact Analyzer for Indian higher education.\n"
        "Analyze the regulation text and return ONLY valid JSON. No markdown, no backticks, no extra text.\n\n"
        "Regulation text:\n\"\"\"\n"
        + text[:5000]
        + "\n\"\"\"\n\nReturn exactly this JSON:\n"
        + '{\n'
        + '  "category": "one of: Accreditation | Scholarship | Curriculum | Faculty Policy | Examination | Admissions | Infrastructure | Research | Governance | Other",\n'
        + '  "topic_tags": ["tag1", "tag2", "tag3", "tag4"],\n'
        + '  "summary": "8-12 plain-English sentences explaining what the regulation does, why it was introduced, and what it means for students, faculty and institutions. No jargon.",\n'
        + '  "stakeholders": [\n'
        + '    {"name": "Students", "impact": "1-2 sentences on how students are affected"},\n'
        + '    {"name": "Faculty", "impact": "1-2 sentences"},\n'
        + '    {"name": "Colleges / Universities", "impact": "1-2 sentences"},\n'
        + '    {"name": "Academic Administrators", "impact": "1-2 sentences"},\n'
        + '    {"name": "Accreditation / Compliance Teams", "impact": "1-2 sentences"}\n'
        + '  ],\n'
        + '  "short_term": "2-4 sentences on 0-1 year impacts.",\n'
        + '  "medium_term": "2-4 sentences on 1-5 year impacts.",\n'
        + '  "long_term": "2-4 sentences on 5+ year impacts.",\n'
        + '  "positives": ["point 1", "point 2", "point 3", "point 4"],\n'
        + '  "risks": ["risk 1", "risk 2", "risk 3", "risk 4"]\n'
        + '}'
    )


def _parse(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith('```'):
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
    return json.loads(raw.strip())


def _analyze_with_groq(text: str) -> dict:
    try:
        from groq import Groq
    except ImportError:
        return {'error': 'groq not installed. Run: pip install groq'}
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return {'error': 'GROQ_API_KEY not set.'}
    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {'role': 'system', 'content': 'You are ERIA. Return only valid JSON. No markdown or extra text.'},
                {'role': 'user', 'content': _build_prompt(text)}
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return _parse(resp.choices[0].message.content)
    except json.JSONDecodeError as e:
        return {'error': f'JSON parse error: {e}'}
    except Exception as e:
        return {'error': f'Groq error: {e}'}


def _analyze_with_gemini(text: str) -> dict:
    try:
        import google.generativeai as genai
    except ImportError:
        return {'error': 'google-generativeai not installed.'}
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return {'error': 'GEMINI_API_KEY not set.'}
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={'temperature': 0.3, 'max_output_tokens': 2000}
        )
        return _parse(model.generate_content(_build_prompt(text)).text)
    except json.JSONDecodeError as e:
        return {'error': f'JSON parse error: {e}'}
    except Exception as e:
        return {'error': f'Gemini error: {e}'}
