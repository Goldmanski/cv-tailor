# ==================================================
# IMPORTS
# ==================================================

import streamlit as st
from html import escape
import base64
import re
from pathlib import Path
from urllib.parse import urlparse

from cv_factory import (
    create_intro,
    cv_template,
    project_template,
    education_school_template,
    education_course_template,
    language_template,
    normalize,
)

from pdf_generator import (
    generate_cv_pdf,
    CV_PREFERRED_BOTTOM_MARGIN_MM,
)

# ==================================================
# PREVIEW FONT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "fonts"

dejavu_regular = base64.b64encode(
    (FONT_DIR / "DejaVuSans.ttf").read_bytes()
).decode()

dejavu_bold = base64.b64encode(
    (FONT_DIR / "DejaVuSans-Bold.ttf").read_bytes()
).decode()

# ==================================================
# STREAMLIT CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="CVTailor",
    page_icon="📄",
    layout="centered",
)

st.markdown(
    """
    <style>

    /* ==================================================
   BUTTONS
   ================================================== */

    /* wspólny styl */
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stDownloadButton > button {
        width: 100%;
        min-height: 38px;
        border-radius: 7px;
        border: 1px solid #555861;
        background-color: transparent;
        color: #f1f1f1;
        font-weight: 600;
        transition:
            background-color 0.15s ease,
            border-color 0.15s ease,
            color 0.15s ease,
            transform 0.1s ease;
    }

    /* zwykły przycisk — hover */
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        border-color: #8a8d95;
        background-color: #303139;
        color: #ffffff;
    }

    /* SPRAWDŹ DANE — akcja pomocnicza */

    [data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        min-height: 42px;
        margin-top: 4px;
    }

    /* kliknięcie */
    [data-testid="stSidebar"] .stButton > button:active,
    [data-testid="stSidebar"] .stDownloadButton > button:active {
        transform: scale(0.99);
    }

    /* ==================================================
    PRIMARY – główna akcja
    ================================================== */

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #ffffff;
        color: #18191d;
        border: 1px solid #ffffff;
        font-weight: 700;
        min-height: 46px;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.12);
        margin-top: 8px;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #e6e6e6;
        border-color: #e6e6e6;
        color: #18191d;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:active {
        transform: scale(0.99);
    }

    /* ==================================================
    DOWNLOAD — pobranie CV
    ================================================== */

    [data-testid="stSidebar"] .stDownloadButton > button {
        background-color: transparent;
    }

    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        background-color: #303139;
    }

    /* ==================================================
   EXPANDERS
   ================================================== */

    [data-testid="stSidebar"] [data-testid="stExpander"] {
        border: 1px solid #3a3c45;
        border-radius: 7px;
        background-color: transparent;
        margin-bottom: 8px;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] details {
        border: none;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        padding: 0.65rem 0.75rem;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
        background-color: #303139;
    }

    /* ==================================================
    HEADER
    ================================================== */

    .app-title {
        font-size: 34px;
        font-weight: 750;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        line-height: 1.1;
    }

    .app-subtitle {
        font-size: 15px;
        color: #9a9ca5;
        margin-top: 0;
        margin-bottom: 28px;
    }

    /* ==================================================
    STATUS MESSAGES
    ================================================== */

    .status-success {
        display: flex;
        align-items: center;
        width: 100%;
        box-sizing: border-box;

        padding: 9px 12px;
        margin: 6px 0;

        border: 1px solid rgba(34, 197, 94, 0.28);
        border-radius: 6px;

        background: rgba(34, 197, 94, 0.10);
        color: #d9fbe5;

        font-size: 14px;
        font-weight: 500;
    }

    /* ==================================================
    ERRORS — komunikaty walidacji
    ================================================== */

    .cv-error {
        background-color: #3a2024;
        border: 1px solid #6b3038;
        border-radius: 7px;
        padding: 12px 14px;
        margin-bottom: 10px;
        color: #f1f1f1;
    }

    .cv-error-title {
        font-weight: 700;
        margin-bottom: 8px;
    }

    .cv-error-item {
        margin: 3px 0;
        color: #e6e6e6;
    }

    /* ==================================================
    VALIDATION — błędne pola formularza
    ================================================== */

    /* ==================================================
    NORMALNE POLA — fokus bez czerwonej ramki
    ================================================== */

    [class*="st-key-normal-"] div[data-baseweb="input"]:focus-within,
    [class*="st-key-normal-"] div[data-baseweb="textarea"]:focus-within {
        border-color: #555861 !important;
        box-shadow: 0 0 0 1px #555861 !important;
    }

    /* ==================================================
    ZWYKŁE POLA — fokus bez czerwonej ramki
    ================================================== */

    [data-testid="stSidebar"] div[data-baseweb="input"]:focus-within,
    [data-testid="stSidebar"] div[data-baseweb="textarea"]:focus-within {
        border-color: #555861 !important;
        box-shadow: 0 0 0 1px #555861 !important;
    }


    /* ==================================================
    BŁĘDNE POLA — czerwone również po kliknięciu
    ================================================== */

    [class*="st-key-validation-"] div[data-baseweb="input"],
    [class*="st-key-validation-"] div[data-baseweb="textarea"] {
        border-color: #e53935 !important;
    }

    [class*="st-key-validation-"] div[data-baseweb="input"]:focus-within,
    [class*="st-key-validation-"] div[data-baseweb="textarea"]:focus-within {
        border-color: #e53935 !important;
        box-shadow: 0 0 0 1px #e53935 !important;
    }

    [class*="st-key-normal-"] input:-webkit-autofill,
    [class*="st-key-normal-"] input:-webkit-autofill:hover,
    [class*="st-key-normal-"] input:-webkit-autofill:focus {
        -webkit-box-shadow: 0 0 0 1000px #0e1016 inset !important;
        -webkit-text-fill-color: #f1f1f1 !important;
        background-color: #0e1016 !important;
    }

    /* ==================================================
    DYNAMIC VALIDATION — błędne pola
    ================================================== */

    [class*="st-key-validation-project-name-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-project-skills-"] [data-testid="stTextInput"] input,

    [class*="st-key-validation-experience-position-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-experience-company-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-experience-years-"] [data-testid="stTextInput"] input,

    [class*="st-key-validation-education-degree-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-education-school-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-education-years-"] [data-testid="stTextInput"] input,

    [class*="st-key-validation-course-name-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-course-provider-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-course-date-"] [data-testid="stTextInput"] input,

    [class*="st-key-validation-language-name-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-language-level-"] [data-testid="stTextInput"] input,

    [class*="st-key-validation-volunteering-name-"] [data-testid="stTextInput"] input,
    [class*="st-key-validation-volunteering-date-"] [data-testid="stTextInput"] input {
        border: 1px solid #e53935 !important;
    }

    .cv-warning {
        background-color: #3d3218;
        border: 1px solid #8a6d1d;
        border-radius: 7px;
        padding: 12px 14px;
        margin-bottom: 10px;
        color: #f1f1f1;
    }

    .cv-warning-title {
        font-weight: 700;
        margin-bottom: 6px;
    }

    .cv-warning-item {
        color: #e6e6e6;
    }

    .cv-success {
        background-color: #123d2a;
        border: 1px solid #1f6b47;
        border-radius: 7px;
        padding: 12px 14px;
        margin-bottom: 10px;
        color: #f1f1f1;
    }

    .cv-success-title {
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# URL VALIDATION
# ==================================================

def is_valid_url(value):
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False

def is_valid_email(value):
    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            value.strip(),
        )
    )

def is_valid_phone(value):
    cleaned = value.strip()

    if not re.fullmatch(r"[+0-9()\-\s]+", cleaned):
        return False

    digits = re.sub(r"\D", "", cleaned)
    return 7 <= len(digits) <= 15

# ==================================================
# SESSION STATE
# ==================================================

if "generated_pdf" not in st.session_state:
    st.session_state.generated_pdf = None

if "generated_pdf_signature" not in st.session_state:
    st.session_state.generated_pdf_signature = None

if "generated_intro" not in st.session_state:
    st.session_state.generated_intro = ""

if "generated_intro_data" not in st.session_state:
    st.session_state.generated_intro_data = None

if "validation_errors" not in st.session_state:
    st.session_state.validation_errors = []

def has_validation_error(prefix):
    return any(
        error.startswith(prefix)
        for error in st.session_state.validation_errors
    )

if "validation_ran" not in st.session_state:
    st.session_state.validation_ran = False

if "tailor_requested" not in st.session_state:
    st.session_state.tailor_requested = False

# ==================================================
# APP HEADER
# ==================================================

st.markdown("""
<h1 style="
    font-size: 2.8rem;
    margin-bottom: 0.15rem;
">
    ✨ CVTailor
</h1>

<p style="
    font-size: 1rem;
    color: #9aa0a6;
    font-style: italic;
    margin-top: 0;
    margin-bottom: 1.8rem;
">
    Tailor your CV to every opportunity.
</p>

<p style="
    font-size: 1.05rem;
    line-height: 1.7;
    margin-bottom: 1.2rem;
">
    <strong>Chcesz dopasować swoje CV do konkretnego stanowiska?</strong>
    Uzupełnij dane o sobie, wklej treść ogłoszenia i opisz pracodawcę.
    CVTailor wykorzysta AI, aby przygotować dokument dopasowany do wybranej roli.
    Możesz również dodać swoje doświadczenie, wykształcenie, umiejętności i projekty,
    aby jeszcze lepiej zaprezentować swoje mocne strony.
</p>
""", unsafe_allow_html=True)

with st.expander("💡 Jak to działa?"):
    st.markdown("""
    **1. Zacznij od podstaw**  
    Podaj swoje dane oraz krótko opowiedz o sobie.

    **2. Wybierz ofertę**  
    Wklej treść ogłoszenia, na które chcesz odpowiedzieć.

    **3. Opisz pracodawcę**  
    Dodaj najważniejsze informacje o firmie, jej działalności, technologii lub kulturze organizacyjnej.

    **4. Rozwiń swój profil — opcjonalnie**  
    Możesz uzupełnić doświadczenie zawodowe, wykształcenie, umiejętności, projekty, języki i inne elementy, które chcesz pokazać.

    **5. Dopasuj CV**  
    CVTailor przeanalizuje całość i przygotuje dokument dopasowany do wybranego stanowiska oraz pracodawcy.

    Nie odpowiada Ci wygenerowane CV? Zmień opis lub kliknij „Dopasuj CV” ponownie, a AI zaproponuje zmodyfikowaną wersję.

    **6. Pobierz gotowy dokument**  
    Twoje spersonalizowane CV będzie dostępne w formacie PDF.
    """)

# ==================================================
# SIDEBAR — CV DATA
# ==================================================

# --------------------------------------------------
# REQUIRED DATA
# --------------------------------------------------

with st.sidebar:
    st.header("🔴 Dane podstawowe")

# --------------------------------------------------
# PERSONAL DATA
# --------------------------------------------------

    personal_data_error = any(
        error in st.session_state.validation_errors
        for error in (
            "Podaj imię i nazwisko.",
            "Podaj adres e-mail.",
            "Podaj numer telefonu.",
            "E-mail: podaj poprawny adres e-mail.",
            "Telefon: podaj poprawny numer telefonu.",
            "LinkedIn: podaj poprawny adres URL.",
            "GitHub: podaj poprawny adres URL.",
        )
    )

    with st.sidebar.expander(
        "👤 Dane osobowe",
        expanded=personal_data_error,
    ):

        name_error = (
            "Podaj imię i nazwisko."
            in st.session_state.validation_errors
        )

        email_error = (
            "Podaj adres e-mail."
            in st.session_state.validation_errors
            or
            "E-mail: podaj poprawny adres e-mail."
            in st.session_state.validation_errors
        )

        phone_error = (
            "Podaj numer telefonu."
            in st.session_state.validation_errors
            or
            "Telefon: podaj poprawny numer telefonu."
            in st.session_state.validation_errors
        )

        with st.container(
            key="validation-name" if name_error else "normal-name"
        ):
            name = st.text_input(
                "Imię i nazwisko",
                placeholder="np. Jan Kowalski",
            )

        with st.container(
            key="validation-email" if email_error else "normal-email"
        ):
            email = st.text_input(
                "E-mail",
                placeholder="np. jan.kowalski@example.com",
            )

        with st.container(
            key="validation-phone" if phone_error else "normal-phone"
        ):
            phone = st.text_input(
                "Telefon",
                placeholder="np. 123456789",
            )

        linkedin_error = (
            "LinkedIn: podaj poprawny adres URL."
            in st.session_state.validation_errors
        )

        with st.container(
            key="validation-linkedin" if linkedin_error else "normal-linkedin"
        ):
            linkedin = st.text_input(
                "LinkedIn (opcjonalnie)",
                placeholder="np. https://linkedin.com/in/jan-kowalski",
            )

        github_error = (
            "GitHub: podaj poprawny adres URL."
            in st.session_state.validation_errors
        )

        with st.container(
            key="validation-github" if github_error else "normal-github"
        ):
            github = st.text_input(
                "GitHub (opcjonalnie)",
                placeholder="np. https://github.com/jan-kowalski",
            )
# --------------------------------------------------
# ABOUT ME
# --------------------------------------------------

    about_me_error = (
        "Podaj informacje w sekcji „O mnie”."
        in st.session_state.validation_errors
    )

    with st.expander(
        "🧑 O mnie",
        expanded=about_me_error,
    ):
        with st.container(
            key="validation-about-me" if about_me_error else "normal-about-me"
        ):
            about_me_info = st.text_area(
                "Informacje o mnie",
                height=300,
                placeholder=(
                    "Opisz swoje doświadczenie, umiejętności, "
                    "projekty, wykształcenie i inne informacje..."
                ),
                label_visibility="collapsed",
            )

# --------------------------------------------------
# JOB OFFER
# --------------------------------------------------

    job_offer_error = (
        "Wklej treść oferty pracy."
        in st.session_state.validation_errors
    )

    with st.expander(
        "🎯 Oferta pracy",
        expanded=job_offer_error,
    ):

        with st.container(
            key="normal-job-title"
        ):
            job_title = st.text_input(
                "Stanowisko (opcjonalnie)",
                placeholder="np. Junior AI/ML Developer",
            )

        with st.container(
            key="validation-ad-info" if job_offer_error else "normal-ad-info"
        ):
            ad_info = st.text_area(
                "Oferta pracy",
                height=400,
                placeholder="Wklej treść oferty pracy...",
                label_visibility="collapsed",
            )

# --------------------------------------------------
# COMPANY INFORMATION
# --------------------------------------------------

    company_error = (
        "Podaj informacje o firmie."
        in st.session_state.validation_errors
    )

    with st.expander(
        "🏢 Informacje o firmie",
        expanded=company_error,
    ):

        with st.container(
            key="validation-company" if company_error else "normal-company"
        ):
            company_info = st.text_area(
                "Informacje o firmie",
                height=300,
                placeholder=(
                    "Wklej informacje o firmie, jej działalności, "
                    "technologiach, projektach lub kulturze organizacyjnej..."
                ),
                label_visibility="collapsed",
            )

# --------------------------------------------------
# OPTIONAL DATA
# --------------------------------------------------

    st.header("🟢 Dane dodatkowe")

# --------------------------------------------------
# PROJECTS
# --------------------------------------------------

    projects_section_error = has_validation_error("Projekt ")

    with st.sidebar.expander(
        "📁 Projekty",
        expanded=projects_section_error,
    ):

        if "projects" not in st.session_state:
            st.session_state.projects = []

        for i, project in enumerate(st.session_state.projects):

            st.markdown(f"**Projekt {i + 1}**")

            project_name_error = (
                f"Projekt {i + 1}: brak nazwy."
                in st.session_state.validation_errors
            )

            project_skills_error = (
                f"Projekt {i + 1}: brak umiejętności."
                in st.session_state.validation_errors
            )

            with st.container(
                key=f"validation-project-name-{i}"
                if project_name_error
                else f"normal-project-name-{i}"
            ):
                project["name"] = st.text_input(
                    "Nazwa projektu",
                    value=project["name"],
                    placeholder="np. Half Marathon Predictor",
                    key=f"project_name_{i}",
                )

            project["description"] = st.text_area(
                "Opis (opcjonalnie)",
                value=project["description"],
                height=150,
                placeholder=(
                    "Opisz cel projektu, jego działanie "
                    "i najważniejsze funkcje..."
                ),
                key=f"project_description_{i}",
            )

            with st.container(
                key=f"validation-project-skills-{i}"
                if project_skills_error
                else f"normal-project-skills-{i}"
            ):
                project["skills"] = st.text_input(
                    "Umiejętności",
                    value=project["skills"],
                    placeholder="np. Python, Pandas, Streamlit",
                    key=f"project_skills_{i}",
                )

            project["result"] = st.text_input(
            "Rezultat (opcjonalnie)",
            value=project["result"],
            placeholder="np. wdrożona aplikacja dostępna online",
            key=f"project_result_{i}",
        )

            if st.button(
                f"🗑️ Usuń projekt {i + 1}",
                key=f"remove_project_{i}",
                use_container_width=True,
                type="tertiary",
            ):
                st.session_state.projects.pop(i)
                st.rerun()

        if st.button(
            "➕ Dodaj projekt",
            use_container_width=True,
        ):
            st.session_state.projects.append(
                {
                    "name": "",
                    "description": "",
                    "skills": "",
                    "result": "",
                }
            )
            st.rerun()

# --------------------------------------------------
# WORK EXPERIENCE
# --------------------------------------------------

    experience_section_error = has_validation_error("Doświadczenie ")

    with st.sidebar.expander(
        "💼 Doświadczenie zawodowe",
        expanded=experience_section_error,
    ):

        if "work_experience" not in st.session_state:
            st.session_state.work_experience = []

        for i, experience in enumerate(st.session_state.work_experience):

            st.markdown(f"**Doświadczenie {i + 1}**")

            experience_position_error = (
                f"Doświadczenie {i + 1}: brak stanowiska."
                in st.session_state.validation_errors
            )

            experience_company_error = (
                f"Doświadczenie {i + 1}: brak firmy."
                in st.session_state.validation_errors
            )

            experience_years_error = (
                f"Doświadczenie {i + 1}: brak okresu."
                in st.session_state.validation_errors
            )

            with st.container(
                key=f"validation-experience-position-{i}"
                if experience_position_error
                else f"normal-experience-position-{i}"
            ):
                experience["position"] = st.text_input(
                    "Stanowisko",
                    value=experience["position"],
                    placeholder="np. Konsultant utrzymania klienta",
                    key=f"experience_position_{i}",
                )

            with st.container(
                key=f"validation-experience-company-{i}"
                if experience_company_error
                else f"normal-experience-company-{i}"
            ):
                experience["company"] = st.text_input(
                    "Firma",
                    value=experience["company"],
                    placeholder="np. Vectra",
                    key=f"experience_company_{i}",
                )

            with st.container(
                key=f"validation-experience-years-{i}"
                if experience_years_error
                else f"normal-experience-years-{i}"
            ):
                experience["years"] = st.text_input(
                    "Okres",
                    value=experience["years"],
                    placeholder="np. 2025–obecnie",
                    key=f"experience_years_{i}",
                )

            experience["description"] = st.text_area(
                "Opis (opcjonalnie)",
                value=experience["description"],
                height=120,
                placeholder=(
                    "Opisz zakres obowiązków, odpowiedzialność "
                    "i najważniejsze osiągnięcia..."
                ),
                key=f"experience_description_{i}",
            )

            if st.button(
                f"🗑️ Usuń doświadczenie {i + 1}",
                key=f"remove_experience_{i}",
                use_container_width=True,
            ):
                st.session_state.work_experience.pop(i)
                st.rerun()

        if st.button(
            "➕ Dodaj doświadczenie",
            use_container_width=True,
        ):
            st.session_state.work_experience.append(
                {
                    "position": "",
                    "company": "",
                    "years": "",
                    "description": "",
                }
            )
            st.rerun()

# --------------------------------------------------
# TECHNICAL SKILLS
# --------------------------------------------------

    with st.sidebar.expander("🛠️ Umiejętności techniczne", expanded=False):

        if "technical_skills_added" not in st.session_state:
            st.session_state.technical_skills_added = False

        if st.session_state.technical_skills_added:

            skills_languages = st.text_input(
                "Języki programowania (opcjonalnie)",
                placeholder="np. Python, SQL",
            )

            skills_tools = st.text_input(
                "Biblioteki i narzędzia (opcjonalnie)",
                placeholder="np. Pandas, Streamlit, Scikit-learn",
            )

            skills_databases = st.text_input(
                "Bazy danych (opcjonalnie)",
                placeholder="np. PostgreSQL, Qdrant",
            )

            skills_other = st.text_input(
                "Inne (opcjonalnie)",
                placeholder="np. Git, Docker, Linux",
            )

            if st.button("🗑️ Usuń umiejętności", use_container_width=True):
                st.session_state.technical_skills_added = False
                st.rerun()

        else:

            skills_languages = ""
            skills_tools = ""
            skills_databases = ""
            skills_other = ""

            if st.button("➕ Dodaj umiejętności", use_container_width=True):
                st.session_state.technical_skills_added = True
                st.rerun()

# --------------------------------------------------
# PORTFOLIO
# --------------------------------------------------

    with st.sidebar.expander("🔗 Portfolio", expanded=False):
        portfolio_url = st.text_input(
            "Adres portfolio (opcjonalnie)",
            placeholder="np. https://github.com/jan-kowalski/portfolio",
        )

# --------------------------------------------------
# EDUCATION
# --------------------------------------------------
    
    education_section_error = (
        has_validation_error("Szkoła / uczelnia ")
        or has_validation_error("Kurs ")
    )

    with st.sidebar.expander(
        "🎓 Edukacja",
        expanded=education_section_error,
    ):

        if "education_schools" not in st.session_state:
            st.session_state.education_schools = []

        st.markdown("**Szkoła / uczelnia**")

        for i, education in enumerate(st.session_state.education_schools):

            st.markdown(f"**Szkoła / uczelnia {i + 1}**")

            education_degree_error = (
                f"Szkoła / uczelnia {i + 1}: brak kierunku / stopnia."
                in st.session_state.validation_errors
            )

            education_school_error = (
                f"Szkoła / uczelnia {i + 1}: brak nazwy szkoły."
                in st.session_state.validation_errors
            )

            education_years_error = (
                f"Szkoła / uczelnia {i + 1}: brak lat."
                in st.session_state.validation_errors
            )

            with st.container(
                key=f"validation-education-degree-{i}"
                if education_degree_error
                else f"normal-education-degree-{i}"
            ):
                education["degree"] = st.text_input(
                    "Kierunek / stopień",
                    value=education["degree"],
                    placeholder="np. Inżynieria sieci komputerowych",
                    key=f"education_degree_{i}",
                )

            with st.container(
                key=f"validation-education-school-{i}"
                if education_school_error
                else f"normal-education-school-{i}"
            ):
                education["school"] = st.text_input(
                    "Szkoła / uczelnia",
                    value=education["school"],
                    placeholder="np. Politechnika Gdańska",
                    key=f"education_school_{i}",
                )

            with st.container(
                key=f"validation-education-years-{i}"
                if education_years_error
                else f"normal-education-years-{i}"
            ):
                education["years"] = st.text_input(
                    "Lata",
                    value=education["years"],
                    placeholder="np. 2020-2024",
                    key=f"education_years_{i}",
                )

            
            if st.button(
                f"🗑️ Usuń szkołę / uczelnię {i + 1}",
                key=f"remove_education_{i}",
                use_container_width=True,
            ):
                st.session_state.education_schools.pop(i)
                st.rerun()

        if st.button(
            "➕ Dodaj szkołę / uczelnię",
            use_container_width=True,
        ):
            st.session_state.education_schools.append(
                {
                    "degree": "",
                    "school": "",
                    "years": "",
                }
            )
            st.rerun()

        st.markdown("**Kursy**")

        if "courses" not in st.session_state:
            st.session_state.courses = []

        for i, course in enumerate(st.session_state.courses):
            st.markdown(f"**Kurs {i + 1}**")

            course_name_error = (
                f"Kurs {i + 1}: brak nazwy."
                in st.session_state.validation_errors
            )

            course_provider_error = (
                f"Kurs {i + 1}: brak organizatora."
                in st.session_state.validation_errors
            )

            course_date_error = (
                f"Kurs {i + 1}: brak daty."
                in st.session_state.validation_errors
            )

            with st.container(
                key=f"validation-course-name-{i}"
                if course_name_error
                else f"normal-course-name-{i}"
            ):
                course["course"] = st.text_input(
                    "Nazwa kursu",
                    value=course["course"],
                    key=f"course_name_{i}",
                    placeholder="np. Data Science",
                )

            with st.container(
                key=f"validation-course-provider-{i}"
                if course_provider_error
                else f"normal-course-provider-{i}"
            ):
                course["provider"] = st.text_input(
                    "Organizator",
                    value=course["provider"],
                    key=f"course_provider_{i}",
                    placeholder="np. GOTOIT",
                )

            with st.container(
                key=f"validation-course-date-{i}"
                if course_date_error
                else f"normal-course-date-{i}"
            ):
                course["date"] = st.text_input(
                    "Data",
                    value=course["date"],
                    key=f"course_date_{i}",
                    placeholder="np. 2025",
                )

            if st.button(
                f"🗑️ Usuń kurs {i + 1}",
                key=f"remove_course_{i}",
                use_container_width=True,
            ):
                st.session_state.courses.pop(i)
                st.rerun()

        if st.button(
            "➕ Dodaj kurs",
            use_container_width=True,
        ):
            st.session_state.courses.append(
                {
                    "course": "",
                    "provider": "",
                    "date": "",
                }
            )
            st.rerun()

# --------------------------------------------------
# LANGUAGES
# --------------------------------------------------

    languages_section_error = has_validation_error("Język ")

    with st.sidebar.expander(
        "🌐 Języki",
        expanded=languages_section_error,
    ):

        if "languages" not in st.session_state:
            st.session_state.languages = []

        for i, language in enumerate(st.session_state.languages):

            st.markdown(f"**Język {i + 1}**")

            language_name_error = (
                f"Język {i + 1}: brak języka."
                in st.session_state.validation_errors
            )

            language_level_error = (
                f"Język {i + 1}: brak poziomu."
                in st.session_state.validation_errors
            )

            with st.container(
                key=f"validation-language-name-{i}"
                if language_name_error
                else f"normal-language-name-{i}"
            ):
                language["language"] = st.text_input(
                    "Język",
                    value=language["language"],
                    placeholder="np. Angielski",
                    key=f"language_name_{i}",
                )

            with st.container(
                key=f"validation-language-level-{i}"
                if language_level_error
                else f"normal-language-level-{i}"
            ):
                language["level"] = st.text_input(
                    "Poziom",
                    value=language["level"],
                    placeholder="np. B2",
                    key=f"language_level_{i}",
                )

        if st.session_state.languages:
            for i, language in enumerate(st.session_state.languages):

                # tutaj pola języka...

                if st.button(
                    f"🗑️ Usuń język {i + 1}",
                    key=f"remove_language_{i}",
                    use_container_width=True,
                ):
                    st.session_state.languages.pop(i)
                    st.rerun()

        if st.button(
            "➕ Dodaj język",
            use_container_width=True,
        ):
            st.session_state.languages.append(
                {
                    "language": "",
                    "level": "",
                }
            )
            st.rerun()

    if "volunteering" not in st.session_state:
        st.session_state.volunteering = []

# --------------------------------------------------
# VOLUNTEERING / OTHER
# --------------------------------------------------

    volunteering_section_error = has_validation_error("Działalność ")

    with st.expander(
        "🏆 Wolontariat lub działalność pozazawodowa",
        expanded=volunteering_section_error,
    ):

        for i, volunteering in enumerate(st.session_state.volunteering):

            st.markdown(f"**Działalność {i + 1}**")

            volunteering_name_error = (
                f"Działalność {i + 1}: brak nazwy."
                in st.session_state.validation_errors
            )

            volunteering_date_error = (
                f"Działalność {i + 1}: brak daty."
                in st.session_state.validation_errors
            )

            with st.container(
                key=f"validation-volunteering-name-{i}"
                if volunteering_name_error
                else f"normal-volunteering-name-{i}"
            ):
                volunteering["name"] = st.text_input(
                    "Nazwa",
                    value=volunteering["name"],
                    placeholder="np. Amnesty International",
                    key=f"volunteering_name_{i}",
                )

            with st.container(
                key=f"validation-volunteering-date-{i}"
                if volunteering_date_error
                else f"normal-volunteering-date-{i}"
            ):
                volunteering["date"] = st.text_input(
                    "Data",
                    value=volunteering["date"],
                    placeholder="np. 2024–obecnie",
                    key=f"volunteering_date_{i}",
                )

            volunteering["description"] = st.text_area(
                "Opis (opcjonalnie)",
                value=volunteering["description"],
                height=100,
                placeholder=(
                    "Opisz krótko swoją działalność, rolę "
                    "lub zakres zaangażowania..."
                ),
                key=f"volunteering_description_{i}",
            )

            if st.button(
                f"🗑️ Usuń działalność {i + 1}",
                key=f"remove_volunteering_{i}",
                use_container_width=True,
            ):
                st.session_state.volunteering.pop(i)
                st.rerun()

        if st.button(
            "➕ Dodaj działalność",
            use_container_width=True,
        ):
            st.session_state.volunteering.append(
                {
                    "name": "",
                    "date": "",
                    "description": "",
                }
            )
            st.rerun()

# ==================================================
# VALIDATION & CV GENERATION
# ==================================================

    current_pdf_signature = repr(
        (
            name,
            email,
            phone,
            linkedin,
            github,
            about_me_info,
            job_title,
            ad_info,
            company_info,
            st.session_state.projects,
            st.session_state.work_experience,
            st.session_state.technical_skills_added,
            skills_languages,
            skills_tools,
            skills_databases,
            skills_other,
            portfolio_url,
            st.session_state.education_schools,
            st.session_state.courses,
            st.session_state.languages,
            st.session_state.volunteering,
        )
    )

    validate_button = st.button(
        "✅ Sprawdź dane",
        use_container_width=True,
    )

    tailor_button = st.button(
        "✨ Dopasuj moje CV",
        use_container_width=True,
        type="primary",
    )

    if validate_button or tailor_button:
        st.session_state.generated_pdf = None
        st.session_state.validation_ran = True

        if tailor_button:
            st.session_state.tailor_requested = True

# ==================================================
# VALIDATION
# ==================================================

current_intro_data = (
    about_me_info.strip(),
    ad_info.strip(),
    company_info.strip(),
)

if (
    st.session_state.generated_intro
    and st.session_state.generated_intro_data is not None
    and current_intro_data != st.session_state.generated_intro_data
):
    st.session_state.generated_intro = ""
    st.session_state.generated_intro_data = None

errors = []

if validate_button or tailor_button:
    if not name.strip():
        errors.append("Podaj imię i nazwisko.")

    if not email.strip():
        errors.append("Podaj adres e-mail.")
    elif not is_valid_email(email):
        errors.append("E-mail: podaj poprawny adres e-mail.")

    if not phone.strip():
        errors.append("Podaj numer telefonu.")
    elif not is_valid_phone(phone):
        errors.append("Telefon: podaj poprawny numer telefonu.")

    if linkedin.strip() and not is_valid_url(linkedin):
        errors.append("LinkedIn: podaj poprawny adres URL.")

    if github.strip() and not is_valid_url(github):
        errors.append("GitHub: podaj poprawny adres URL.")   

    if not about_me_info.strip():
        errors.append("Podaj informacje w sekcji „O mnie”.")

    if not ad_info.strip():
        errors.append("Wklej treść oferty pracy.")

    if not company_info.strip():
        errors.append("Podaj informacje o firmie.")

    for i, project in enumerate(st.session_state.projects):
        if not project["name"].strip():
            errors.append(f"Projekt {i + 1}: brak nazwy.")
        if not project["skills"].strip():
            errors.append(f"Projekt {i + 1}: brak umiejętności.")

    for i, experience in enumerate(st.session_state.work_experience):
        if not experience["position"].strip():
            errors.append(
                f"Doświadczenie {i + 1}: brak stanowiska."
            )

        if not experience["company"].strip():
            errors.append(
                f"Doświadczenie {i + 1}: brak firmy."
            )

        if not experience["years"].strip():
            errors.append(
                f"Doświadczenie {i + 1}: brak okresu."
            )

    for i, education in enumerate(st.session_state.education_schools):
        if not education["degree"].strip():
            errors.append(f"Szkoła / uczelnia {i + 1}: brak kierunku / stopnia.")
        if not education["school"].strip():
            errors.append(f"Szkoła / uczelnia {i + 1}: brak nazwy szkoły.")
        if not education["years"].strip():
            errors.append(f"Szkoła / uczelnia {i + 1}: brak lat.")

    for i, course in enumerate(st.session_state.courses):
        if not course["course"].strip():
            errors.append(f"Kurs {i + 1}: brak nazwy.")
        if not course["provider"].strip():
            errors.append(f"Kurs {i + 1}: brak organizatora.")
        if not course["date"].strip():
            errors.append(f"Kurs {i + 1}: brak daty.")

    for i, language in enumerate(st.session_state.languages):
        if not language["language"].strip():
            errors.append(f"Język {i + 1}: brak języka.")
        if not language["level"].strip():
            errors.append(f"Język {i + 1}: brak poziomu.")

    for i, activity in enumerate(st.session_state.volunteering):
        if not activity["name"].strip():
            errors.append(f"Działalność {i + 1}: brak nazwy.")
        if not activity["date"].strip():
            errors.append(f"Działalność {i + 1}: brak daty.")

    st.session_state.validation_errors = errors
    st.rerun()

# ==================================================
# CV DATA PREPARATION
# ==================================================

if st.session_state.validation_ran:
    if st.session_state.validation_errors:
        error_items = "".join(
            f'<div class="cv-error-item">• {error}</div>'
            for error in st.session_state.validation_errors
        )

        st.markdown(
            f"""
            <div class="cv-error">
                <div class="cv-error-title">✕ Znaleziono problemy:</div>
                {error_items}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("✓ Wszystkie dane są kompletne.")

if st.session_state.tailor_requested and not st.session_state.validation_errors:
    intro = create_intro(
        about_me_info=about_me_info,
        ad_info=ad_info,
        company_info=company_info,
    )

    st.session_state.generated_intro = intro

    st.session_state.generated_intro_data = (
        about_me_info.strip(),
        ad_info.strip(),
        company_info.strip(),
    )

# --------------------------------------------------
# PROJECT DATA
# --------------------------------------------------

    project_data = []

    for project in st.session_state.projects:
        project_data.append(
            {
                "name": project["name"].strip(),
                "description": normalize(project["description"]),
                "skills": project["skills"].strip(),
                "result": project["result"].strip(),
            }
        )

# --------------------------------------------------
# EXPERIENCE DATA
# --------------------------------------------------

    experience_data = []

    for experience in st.session_state.work_experience:
        experience_data.append(
            {
                "position": experience["position"].strip(),
                "company": experience["company"].strip(),
                "years": experience["years"].strip(),
                "description": normalize(
                    experience["description"]
                ),
            }
        )

# --------------------------------------------------
# EDUCATION DATA
# --------------------------------------------------

    education_data = []

    for education in st.session_state.education_schools:
        education_data.append(
            {
                "type": "school",
                "degree": education["degree"].strip(),
                "school": education["school"].strip(),
                "years": education["years"].strip(),
            }
        )

    for course in st.session_state.courses:
        education_data.append(
            {
                "type": "course",
                "course": course["course"].strip(),
                "provider": course["provider"].strip(),
                "date": course["date"].strip(),
            }
        )

# --------------------------------------------------
# LANGUAGE DATA
# --------------------------------------------------

    languages_data = []

    for language in st.session_state.languages:
        languages_data.append(
            {
                "language": language["language"].strip(),
                "level": language["level"].strip(),
            }
        )

# --------------------------------------------------
# VOLUNTEERING DATA
# --------------------------------------------------

    volunteering_or_other = ""
    volunteering_markdown = ""

    for activity in st.session_state.volunteering:
        activity_name = activity["name"].strip()
        activity_date = activity["date"].strip()
        activity_description = normalize(activity["description"])

        volunteering_or_other += (
            f"{activity_name} - {activity_date}\n\n"
        )

        if activity_description:
            volunteering_or_other += (
                f"{activity_description}\n\n"
            )

        volunteering_markdown += (
            f"- **{activity_name}** – {activity_date}"
        )

        if activity_description:
            volunteering_markdown += (
                f" – {activity_description}"
            )

        volunteering_markdown += "\n"

# ==================================================
# PDF GENERATION
# ==================================================

    try:
        pdf = generate_cv_pdf(
            name=name,
            job_title=job_title,
            email=email,
            phone=phone,
            linkedin=linkedin,
            github=github,
            intro=intro,
            projects=project_data,
            experience=experience_data,
            skills_languages=skills_languages,
            skills_tools=skills_tools,
            skills_databases=skills_databases,
            skills_other=skills_other,
            portfolio_url=portfolio_url,
            education=education_data,
            languages=languages_data,
            volunteering=volunteering_or_other,
        )

    except ValueError as error:
        st.markdown(
            f"""
            <div class="cv-error">
                <div class="cv-error-title">✕ CV przekracza bezpieczny obszar strony</div>
                <div class="cv-error-item">{error}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.generated_pdf = None
        st.session_state.tailor_requested = False

    else:
        st.session_state.generated_pdf = pdf
        st.session_state.generated_pdf_signature = current_pdf_signature
        st.session_state.tailor_requested = False

        bottom_margin_mm = getattr(
            pdf,
            "cv_bottom_margin_mm",
            CV_PREFERRED_BOTTOM_MARGIN_MM,
        )

        if bottom_margin_mm < CV_PREFERRED_BOTTOM_MARGIN_MM:
            st.markdown(
                f"""
                <div class="cv-warning">
                    <div class="cv-warning-title">
                        ⚠ CV jest blisko dolnego marginesu.
                    </div>
                    <div class="cv-warning-item">
                        Pozostało {bottom_margin_mm:.1f} mm wolnego miejsca.
                        Zalecany margines to {CV_PREFERRED_BOTTOM_MARGIN_MM} mm.
                        Możesz nadal wygenerować i pobrać CV.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="cv-success">
                    <div class="cv-success-title">
                        ✓ CV jest gotowe i mieści się na 1 stronie.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==================================================
# MARKDOWN CV GENERATION
# ==================================================

    projects_markdown = ""

    if st.session_state.projects:
        projects_markdown = "## Projekty\n\n"

        for project in st.session_state.projects:
            projects_markdown += project_template.substitute(
                name=project["name"].strip(),
                description=normalize(project["description"]),
                skills=project["skills"].strip(),
                result=project["result"].strip(),
            )

    technical_skills = ""

    if st.session_state.technical_skills_added:
        technical_skills = (
            "## Umiejętności techniczne\n\n"
            f"- **Języki programowania**: {skills_languages}\n"
            f"- **Biblioteki i narzędzia**: {skills_tools}\n"
            f"- **Bazy danych**: {skills_databases}\n"
            f"- **Inne**: {skills_other}\n"
        )

    portfolio = ""


    if portfolio_url.strip():
        portfolio = (
            f"## Portfolio\n\n"
            f"[Moje portfolio znajdziesz tutaj]({portfolio_url.strip()})"
        )

    education_markdown = ""

    if st.session_state.education_schools:
        education_markdown = "## Wykształcenie\n\n"

        for education in st.session_state.education_schools:
            education_markdown += education_school_template.substitute(
                degree=education["degree"].strip(),
                school=education["school"].strip(),
                years=education["years"].strip(),
            )

    if st.session_state.courses:
        education_markdown += "## Kursy\n\n"

        for course in st.session_state.courses:
            education_markdown += education_course_template.substitute(
                course=course["course"].strip(),
                provider=course["provider"].strip(),
                date=course["date"].strip(),
            )

    languages_markdown = ""

    if st.session_state.languages:
        languages_markdown = "## Języki obce\n\n"

        for language in st.session_state.languages:
            languages_markdown += language_template.substitute(
                language=language["language"].strip(),
                level=language["level"].strip(),
            )

    linkedin_markdown = ""

    if linkedin.strip():
        linkedin_markdown = f"LinkedIn: [{linkedin}]({linkedin})"

    github_markdown = ""

    if github.strip():
        github_markdown = f"GitHub: [{github}]({github})"       

    cv = cv_template.substitute(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin_markdown,
        github=github_markdown,
        intro=intro,
        projects=projects_markdown,
        technical_skills=technical_skills,
        portfolio=portfolio,
        education=education_markdown,
        languages=languages_markdown,
    )

    if volunteering_markdown:
        cv += volunteering_markdown

# ==================================================
# PDF DOWNLOAD
# ==================================================

if (
    st.session_state.generated_pdf is not None
    and st.session_state.generated_pdf_signature == current_pdf_signature
):
    st.download_button(
        label="📄 Pobierz CV PDF",
        data=st.session_state.generated_pdf,
        file_name="CV.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ==================================================
# CV PREVIEW
# ==================================================

st.divider()

st.header("📄 Podgląd CV")

preview_css = """
    <style>
        
        @font-face {
        font-family: "DejaVu Sans";
        src: url("data:font/ttf;base64,DEJAVU_REGULAR") format("truetype");
        font-weight: 400;
    }

    @font-face {
        font-family: "DejaVu Sans";
        src: url("data:font/ttf;base64,DEJAVU_BOLD") format("truetype");
        font-weight: 700;
    }
        .cv-page {
    width: 210mm;
    height: 297mm;

    margin: 0 auto;
    padding: 92px 64px 57px 64px;

    box-sizing: border-box;

    background: white;

            box-shadow:
                0 4px 20px rgba(0, 0, 0, 0.10);

            color: #222222;
        }

        .cv-header {
            text-align: center;
        }

        .cv-name {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 34px;
            font-weight: 700;
            letter-spacing: 5px;
            text-transform: uppercase;

            margin-bottom: 3px;
        }

        .cv-job-title {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 18px;
            letter-spacing: 2.5px;

            margin-bottom: 12px;
        }

        .cv-contact {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13px;
            line-height: 1.5;
            white-space: normal;
            overflow-wrap: anywhere;
        }

        .cv-contact a {
            color: #333333;
            text-decoration: none;
            white-space: nowrap;
        }

        .contact-separator {
            margin: 0 5px;
            color: #999999;
        }

        .cv-header-separator {
            width: 100%;
            height: 1px;

            background: #d9d9d9;

            margin-top: 29px;
        }

        .cv-section {
            margin-top: 6pt;
        }

        .cv-main-section {
            margin-top: 6pt;
            padding-top: 7pt;
            border-top: 1px solid #d9d9d9;
        }

        .cv-bottom-layout {
            width: 100%;
        }

        .cv-bottom-full-width {
            width: 100%;
        }

        .cv-bottom-full-width .cv-section {
            margin-top: 6pt;
            padding-top: 7pt;
            border-top: 1px solid #d9d9d9;
        }

        .cv-bottom-small-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            column-gap: 4%;
            margin-top: 0;
        }

        .cv-bottom-small-cell {
            min-width: 0;
        }

        .cv-bottom-small-cell .cv-section {
            margin-top: 6pt;
            padding-top: 7pt;
            border-top: 1px solid #d9d9d9;
        }

        .cv-section-title {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;

            margin-bottom: 4px;
        }

        .cv-profile-text {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 9.72pt;
            line-height: 17pt;

            color: #555555;
            margin: 0;
        }

                .cv-projects {
            margin-top: 6pt;
        }

        .cv-project {
            margin-bottom: 16px;
        }

        .cv-project-name {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            font-weight: 700;
            line-height: 1.4;

            margin-bottom: 5px;
        }
        
        .cv-bullet {
            padding-left: 10px;
            text-indent: -10px;
        }

        .cv-project-description {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            line-height: 1.5;

            color: #555555;
            margin: 0 0 5px 0;
            padding-left: 10px;
            text-indent: -10px;
        }

        .cv-project-meta {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            line-height: 1.45;

            color: #555555;
            margin: 0 0 4pt 0;
        }

        .cv-project-meta strong {
            font-weight: 700;
            color: #333333;
        }

        .cv-technical-skills .cv-project-meta strong {
            font-weight: 400;
            color: #555555;
        }

        .cv-experience {
            margin-top: 6pt;
        }

        .cv-experience-item {
            margin-bottom: 18px;
        }

        .cv-experience-title {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            font-weight: 700;
            line-height: 1.4;

            margin-bottom: 6px;
        }

        .cv-experience-meta {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            line-height: 1.45;

            color: #555555;
            margin: 0 0 4pt 0;
        }

        .cv-education {
            margin-top: 24px;
        }

        .cv-education-item {
            margin-bottom: 12px;
        }

        .cv-education-title {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 4px;
        }

        .cv-education-meta {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            line-height: 1.45;
            color: #555555;
            margin: 2px 0;
        }

        .cv-nowrap {
            white-space: nowrap;
        }

        .cv-wrap-bullet {
            display: inline-block;
            max-width: 100%;
            white-space: normal;
            vertical-align: top;
        }

        .cv-education-years {
            white-space: nowrap;
        }

        .cv-languages {
            margin-top: 24px;
        }

        .cv-language-item {
            font-family: "DejaVu Sans", sans-serif;
            font-size: 13.5px;
            line-height: 1.45;
            color: #555555;
            margin: 0;
        }

        /* ==================================================
        VALIDATION — podświetlenie błędnych pól
        ================================================== */

        .validation-error {
            border: 1px solid #e53935;
            border-radius: 6px;
            padding: 4px;
        }

        </style>
    """

preview_css = preview_css.replace(
    "DEJAVU_REGULAR",
    dejavu_regular,
).replace(
    "DEJAVU_BOLD",
    dejavu_bold,
)

st.markdown(
    preview_css,
    unsafe_allow_html=True,
)

contact_items = []

if phone.strip():
    contact_items.append(
        f'<a href="tel:{escape(phone, quote=True)}">{escape(phone)}</a>'
    )

if email.strip():
    contact_items.append(
        f'<a href="mailto:{escape(email, quote=True)}">{escape(email)}</a>'
    )

if linkedin.strip():
    linkedin_display = (
    linkedin.strip()
    .replace("https://", "")
    .replace("http://", "")
    .replace("www.", "")
    .rstrip("/")
)

    contact_items.append(
        f'<a href="{escape(linkedin.strip(), quote=True)}">'
        f'{escape(linkedin_display)}'
        f'</a>'
    )

if github.strip():
    github_display = (
    github.strip()
    .replace("https://", "")
    .replace("http://", "")
    .replace("www.", "")
    .rstrip("/")
)

    contact_items.append(
        f'<a href="{escape(github.strip(), quote=True)}">'
        f'{escape(github_display)}'
        f'</a>'
    )

contact_line = " <span class='contact-separator'>•</span> ".join(
    contact_items
)

projects_html = ""

if st.session_state.projects:

    project_items = []

    for project in st.session_state.projects:

        project_name = escape(project["name"].strip())
        project_description = escape(project["description"].strip())
        project_skills = escape(project["skills"].strip())
        project_result = escape(project["result"].strip())

        project_html = f"""
        <div class="cv-project">

            <div class="cv-project-name">
                {project_name}
            </div>
        """

        if project_description:
            project_html += f"""
            <div class="cv-project-description cv-bullet">
                • {project_description}
            </div>
            """

        if project_skills:
            project_html += f"""
            <div class="cv-project-meta cv-bullet">
                • {project_skills}
            </div>
            """

        if project_result:
            project_html += f"""
            <div class="cv-project-meta cv-bullet">
                • Rezultat: {project_result}
            </div>
            """
            
        project_html += """
        </div>
        """

        project_items.append(project_html)

    projects_html = f"""
    <div class="cv-section cv-main-section cv-projects">

        <div class="cv-section-title">
            Projekty
        </div>

        {"".join(project_items)}

        </div>
    """

# ==================================================
# TECHNICAL SKILLS HTML
# ==================================================

technical_skills_html = ""

if st.session_state.technical_skills_added:

    skills_items = []

    if skills_languages.strip():
        skills_items.append(
            f"• <strong>Języki programowania:</strong> {escape(skills_languages)}"
        )

    if skills_tools.strip():
        skills_items.append(
            f"• <strong>Biblioteki i narzędzia:</strong> {escape(skills_tools)}"
        )

    if skills_databases.strip():
        skills_items.append(
            f"• <strong>Bazy danych:</strong> {escape(skills_databases)}"
        )

    if skills_other.strip():
        skills_items.append(
            f"• <strong>Inne:</strong> {escape(skills_other)}"
        )

    if skills_items:
        technical_skills_html = f"""
        <div class="cv-section cv-main-section cv-technical-skills">

            <div class="cv-section-title">
                Umiejętności techniczne
            </div>

            {"".join(
                f'<div class="cv-project-meta cv-bullet">{item}</div>'
                for item in skills_items
            )}

        </div>
        """

# ==================================================
# PORTFOLIO HTML
# ==================================================

portfolio_html = ""

if portfolio_url.strip():

    portfolio_display = (
        portfolio_url.strip()
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .rstrip("/")
    )

    portfolio_html = f"""
    <div class="cv-section cv-portfolio">

        <div class="cv-section-title">
            Portfolio
        </div>

        <div class="cv-project-meta">
            <a href="{escape(portfolio_url.strip(), quote=True)}">
                {escape(portfolio_display)}
            </a>
        </div>

    </div>
    """

# ==================================================
# EDUCATION HTML
# ==================================================

education_html = ""

if st.session_state.education_schools:
    education_items = []

    for education in st.session_state.education_schools:
        degree = escape(education["degree"].strip())
        school = escape(education["school"].strip())
        years = escape(education["years"].strip())

        education_item_html = f"""
        <div class="cv-education-item">

            <div class="cv-education-title">
                <span class="cv-nowrap"><strong>{degree}</strong></span>
                —
                <span class="cv-nowrap">{school}</span>
            </div>

            <div class="cv-education-meta cv-bullet">
                • {years}
            </div>

        </div>
        """

        education_items.append(education_item_html)

    education_html = f"""
    <div class="cv-section cv-education">

        <div class="cv-section-title">
            Edukacja
        </div>

        {"".join(education_items)}

    </div>
    """


courses_html = ""

if st.session_state.courses:
    course_items = []

    for course in st.session_state.courses:
        course_name = escape(course["course"].strip())
        provider = escape(course["provider"].strip())
        date = escape(course["date"].strip())

        course_item_html = f"""
        <div class="cv-education-item">

            <div class="cv-education-title">
                <span class="cv-nowrap"><strong>{course_name}</strong></span>
                —
                <span class="cv-nowrap">{provider}</span>
            </div>

            <div class="cv-education-meta cv-bullet">
                • {date}
            </div>

        </div>
        """

        course_items.append(course_item_html)

    courses_html = f"""
    <div class="cv-section cv-education">

        <div class="cv-section-title">
            Kursy
        </div>

        {"".join(course_items)}

    </div>
        """

# ==================================================
# LANGUAGES HTML
# ==================================================

languages_html = ""

if st.session_state.languages:

    language_items = []

    for language in st.session_state.languages:

        language_name = escape(language["language"].strip())
        language_level = escape(language["level"].strip())

        language_item_html = f"""
        <div class="cv-language-item cv-bullet">
            • {language_name}: {language_level}
        </div>
        """

        language_items.append(language_item_html)

    languages_html = f"""
    <div class="cv-section cv-languages">

        <div class="cv-section-title">
            Języki
        </div>

        {"".join(language_items)}

    </div>
    """

# ==================================================
# VOLUNTEERING HTML
# ==================================================

volunteering_html = ""

if st.session_state.volunteering:

    volunteering_items = []

    for activity in st.session_state.volunteering:

        activity_name_raw = activity["name"].strip()

        if " - " in activity_name_raw:
            organization, role = activity_name_raw.split(" - ", 1)

            activity_role = escape(role.strip())
            activity_organization = escape(organization.strip())

        else:
            activity_role = escape(activity_name_raw)
            activity_organization = ""

        activity_date = escape(activity["date"].strip())
        activity_description = escape(
            activity["description"].strip()
        )

        volunteering_item_html = f"""
        <div class="cv-volunteering-item">

            <div class="cv-volunteering-title">
                <strong>
                    <span class="cv-nowrap">{activity_role}</span>
                    {f' — <span class="cv-nowrap">{activity_organization}</span>' if activity_organization else ''}
                </strong>
            </div>

            <div class="cv-volunteering-meta cv-bullet">
                • {activity_date}
            </div>

            <div class="cv-volunteering-description cv-bullet">
                • {activity_description}
            </div>

        </div>
        """

        volunteering_items.append(volunteering_item_html)

    volunteering_html = f"""
    <div class="cv-section cv-volunteering">

        <div class="cv-section-title">
            Wolontariat lub działalność pozazawodowa
        </div>

        {"".join(volunteering_items)}

    </div>
    """

# ==================================================
# EXPERIENCE HTML
# ==================================================

experience_html = ""

if st.session_state.work_experience:

    experience_items = []

    for experience in st.session_state.work_experience:

        position = escape(experience["position"].strip())
        company = escape(experience["company"].strip())
        years = escape(experience["years"].strip())
        description = escape(experience["description"].strip())

        experience_item_html = f"""
        <div class="cv-experience-item">

            <div class="cv-experience-title">
                <strong>{position}</strong> — {company}
            </div>

            <div class="cv-experience-meta cv-bullet">
                • {years}
            </div>
        """

        if description:
            experience_item_html += f"""
            <div class="cv-experience-meta cv-bullet">
                • {description}
            </div>
            """

        experience_item_html += """
        </div>
        """

        experience_items.append(experience_item_html)

    experience_html = f"""
    <div class="cv-section cv-main-section cv-experience">

        <div class="cv-section-title">
            Doświadczenie zawodowe
        </div>

        {"".join(experience_items)}

    </div>
    """

# ==================================================
# CV PREVIEW
# ==================================================

# ==================================================
# DYNAMIC BOTTOM LAYOUT
# SAME LOGIC AS PDF
# ==================================================

# ==================================================
# PREVIEW BOTTOM LAYOUT
# ==================================================

full_width_sections = []

if education_html:
    full_width_sections.append(education_html)

if courses_html:
    full_width_sections.append(courses_html)

if volunteering_html:
    full_width_sections.append(volunteering_html)


small_sections = []

if portfolio_html:
    small_sections.append(portfolio_html)

if languages_html:
    small_sections.append(languages_html)


full_width_html = "".join(full_width_sections)

small_left = small_sections[0] if len(small_sections) > 0 else ""
small_right = small_sections[1] if len(small_sections) > 1 else ""


bottom_grid_html = f"""
<div class="cv-bottom-layout">

    <div class="cv-bottom-full-width">
        {full_width_html}
    </div>

    <div class="cv-bottom-small-grid">

        <div class="cv-bottom-small-cell">
            {small_left}
        </div>

        <div class="cv-bottom-small-cell">
            {small_right}
        </div>

    </div>

</div>
"""

st.html(
    f"""
    <div class="cv-page">

        <div class="cv-header">

            <div class="cv-name">
                {escape(name)}
            </div>

            <div class="cv-job-title">
                {escape(job_title)}
            </div>

            <div class="cv-contact">
                {contact_line}
            </div>

        </div>

        <div class="cv-header-separator"></div>

        <div class="cv-section">

            <div class="cv-section-title">
                Profil zawodowy
            </div>

            <p class="cv-profile-text">
                {escape(st.session_state.generated_intro)}
            </p>

        </div>

        {projects_html}

        {experience_html}

        {technical_skills_html}

        {bottom_grid_html}

    </div>
    """
)