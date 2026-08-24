# ==================================================
# IMPORTS
# ==================================================

from string import Template
from textwrap import dedent
from dotenv import dotenv_values
from openai import OpenAI

# ==================================================
# OPENAI CONFIGURATION
# ==================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==================================================
# UTILS
# ==================================================

def comma(x):
    return ', '.join(x)

def newline(x):
    return '\n'.join(x)

def normalize(x):
    return dedent(x.strip())

# ==================================================
# INTRO GENERATION
# ==================================================

def create_intro(
    about_me_info: str,
    ad_info: str,
    company_info: str,
):
    res = openai_client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """
Jesteś specjalistą ds. rekrutacji. Tworzysz krótki, naturalny profil zawodowy do CV, dopasowany do konkretnej oferty pracy.

Napisz profil w pierwszej osobie, tak jakby kandydat sam przedstawiał swoje doświadczenie zawodowe.

Profil powinien:
1. Rozpoczynać się od krótkiego przedstawienia kandydata i jego poziomu doświadczenia.
2. Wskazywać 1–2 najważniejsze kompetencje istotne dla stanowiska.
3. Wspominać o konkretnym doświadczeniu, projekcie lub obszarze pracy, jeśli wynika on z dostarczonych danych.
4. Być naturalny i konkretny — powinien brzmieć jak tekst napisany przez człowieka, a nie opis wygenerowany przez AI.

ZASADY STYLU:
- Zawsze używaj pierwszej osoby: „Jestem...”, „Mam doświadczenie...”, „Specjalizuję się...”.
- Nie używaj trzeciej osoby.
- Nie opisuj kandydata jako „doświadczony specjalista”, „kandydat”, „osoba”, itp.
- Unikaj ogólnych i marketingowych sformułowań, takich jak:
  „łączę umiejętności techniczne z...”
  „doskonale rozumiem potrzeby biznesowe”
  „tworzę wartość dla organizacji”
  „wspieram transformację cyfrową”
  „jestem nastawiony na rozwój”
  oraz podobnych ogólników.
- Nie dodawaj informacji, których nie ma w danych.
- Nie wymieniaj wielu technologii — wybierz tylko najważniejsze.
- Nie próbuj na siłę kończyć profilu zdaniem o motywacji, podejściu zawodowym lub celach.
- Jeżeli nie ma konkretnej informacji potrzebnej do zakończenia profilu, zakończ go naturalnie na ostatnim konkretnym fakcie.
- Nie powtarzaj informacji znajdujących się w innych sekcjach CV.

Nie dodawaj zdań opisujących wpływ, efekty, wartość lub korzyści wynikające z pracy kandydata, jeśli nie zostały podane w danych.

Nie używaj konstrukcji:
- "co pozwala mi..."
- "dzięki czemu..."
- "umożliwia mi..."
- "wspierając..."
- "przyczyniając się do..."

Opisuj wyłącznie doświadczenie, specjalizację i konkretne obszary pracy.

DŁUGOŚĆ:
- 2–3 zdania.
- Jeden akapit.
- Maksymalnie około 300 znaków.
- Priorytetem jest naturalność i konkret, a nie wykorzystanie całego limitu znaków.
                """,
            },
            {
                "role": "user",
                "content": f"""
# Informacje o mnie
{about_me_info}

# Informacje o oferowanym stanowisku
{ad_info}

# Informacje o firmie
{company_info}
                """,
            },
        ],
    )
    return res.choices[0].message.content

# ==================================================
# CV TEMPLATES
# ==================================================

project_template = Template("""
### ${name}

${description}

- **Umiejętności**: ${skills}
- **Wynik**: ${result}
""")

education_school_template = Template("""
- **${degree}** – ${years} – ${school}
""")

education_course_template = Template("""
- **${course}** - ${provider} - ${date}
""")

language_template = Template("""
- **${language}**: ${level}
""")

competition_template = Template("""
- **${name}** - ${date} - ${result}
""")

cv_template = Template("""
# ${name}

email: [${email}](mailto:${email})  
tel: [${phone}](tel:${phone})  
${linkedin}
${github}

## Profil

${intro}

${projects}

${technical_skills}

${portfolio}

${education}

${languages}
""")


volunteering_or_other_template = Template("""

## Wolontariat lub działalność pozazawodowa

${volunteering_or_other}
""")
