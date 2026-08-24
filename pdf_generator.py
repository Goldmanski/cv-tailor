# ==================================================
# IMPORTS
# ==================================================

from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Flowable,
    Table,
    TableStyle,
)

from pathlib import Path

# ==================================================
# FONT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "fonts"

pdfmetrics.registerFont(
    TTFont("DejaVuSans", FONT_DIR / "DejaVuSans.ttf")
)

pdfmetrics.registerFont(
    TTFont("DejaVuSans-Bold", FONT_DIR / "DejaVuSans-Bold.ttf")
)

# ==================================================
# CV MARGIN CONFIGURATION
# ==================================================

CV_PREFERRED_BOTTOM_MARGIN_MM = 15
CV_MIN_BOTTOM_MARGIN_MM = 8

# ==================================================
# CUSTOM FLOWABLES
# ==================================================

# --------------------------------------------------
# CV NAME
# --------------------------------------------------

class SpacedTitle(Flowable):
    def __init__(
        self,
        text,
        font_name="DejaVuSans-Bold",
        font_size=28,
        char_space=6,
    ):
        super().__init__()
        self.text = text.upper()
        self.font_name = font_name
        self.font_size = font_size
        self.char_space = char_space
        self.height = 35

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        text = self.canv.beginText()
        text.setFont(self.font_name, self.font_size)
        text.setCharSpace(self.char_space)

        text_width = pdfmetrics.stringWidth(
            self.text,
            self.font_name,
            self.font_size,
        )

        total_width = text_width + (
            len(self.text) - 1
        ) * self.char_space

        x = (self.width - total_width) / 2

        text.setTextOrigin(x, 0)
        text.textOut(self.text)

        self.canv.drawText(text)

# --------------------------------------------------
# JOB TITLE
# --------------------------------------------------

class SpacedJobTitle(Flowable):
    def __init__(
        self,
        text,
        font_name="DejaVuSans",
        font_size=13.2,
        char_space=3,
    ):
        super().__init__()
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.char_space = char_space
        self.height = 17

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        text = self.canv.beginText()
        text.setFont(self.font_name, self.font_size)
        text.setCharSpace(self.char_space)

        text_width = pdfmetrics.stringWidth(
            self.text,
            self.font_name,
            self.font_size,
        )

        total_width = text_width + (
            len(self.text) - 1
        ) * self.char_space

        x = (self.width - total_width) / 2

        text.setTextOrigin(x, 0)
        text.textOut(self.text)

        self.canv.drawText(text)

# --------------------------------------------------
# SECTION HEADING
# --------------------------------------------------

class SpacedHeading(Flowable):
    def __init__(
        self,
        text,
        font_name="DejaVuSans-Bold",
        font_size=10,
        char_space=2.5,
    ):
        super().__init__()

        self.text = text.upper()
        self.font_name = font_name
        self.font_size = font_size

        if len(self.text) > 30:
            self.char_space = 1.2
        else:
            self.char_space = char_space

        self.leading = 13
        self.lines = []
        self.height = self.leading

    def _text_width(self, text):
        if not text:
            return 0

        return (
            pdfmetrics.stringWidth(
                text,
                self.font_name,
                self.font_size,
            )
            + (len(text) - 1) * self.char_space
        )

    def wrap(self, availWidth, availHeight):
        self.width = availWidth

        words = self.text.split()
        lines = []
        current_line = ""

        for word in words:
            candidate = (
                word
                if not current_line
                else f"{current_line} {word}"
            )

            if self._text_width(candidate) <= availWidth:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)

                current_line = word

        if current_line:
            lines.append(current_line)

        self.lines = lines
        self.height = len(lines) * self.leading

        return availWidth, self.height

    def draw(self):
        text = self.canv.beginText()

        text.setFont(
            self.font_name,
            self.font_size,
        )

        text.setCharSpace(
            self.char_space
        )

        y = self.height - self.font_size

        for line in self.lines:
            text.setTextOrigin(0, y)
            text.textOut(line)
            y -= self.leading

        self.canv.drawText(text)

# ==================================================
# PDF GENERATOR
# ==================================================

def display_url(url):
    return (
        url
        .removeprefix("https://www.")
        .removeprefix("http://www.")
        .removeprefix("https://")
        .removeprefix("http://")
    )

def make_breakable_url(url):
    return (
        url
        .replace("/", "/\u200b")
        .replace("-", "-\u200b")
        .replace("_", "_\u200b")
        .replace(".", ".\u200b")
    )

def generate_cv_pdf(
    name,
    job_title,
    email,
    phone,
    linkedin,
    github,
    intro,
    projects,
    experience,
    skills_languages,
    skills_tools,
    skills_databases,
    skills_other,
    portfolio_url,
    education,
    languages,
    volunteering,
):

# --------------------------------------------------
# DOCUMENT CONFIGURATION
# --------------------------------------------------

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=19 * mm,
        bottomMargin=CV_MIN_BOTTOM_MARGIN_MM * mm,
    )

# --------------------------------------------------
# STYLES
# --------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CVTitle",
        parent=styles["Title"],
        fontName="DejaVuSans-Bold",
        fontSize=22,
        leading=25,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    heading_style = ParagraphStyle(
        "CVHeading",
        parent=styles["Heading2"],
        fontName="DejaVuSans-Bold",
        fontSize=10,
        leading=13,
        spaceBefore=10,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
    "CVBody",
    parent=styles["BodyText"],
    fontName="DejaVuSans",
    fontSize=9.72,
    leading=17,
    spaceAfter=4,
    char_space=1,
    textColor=colors.HexColor("#666666"),
)

    bullet_body_style = ParagraphStyle(
        "CVBulletBody",
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-10,
    )

    compact_body_style = ParagraphStyle(
        "CVCompactBody",
        parent=body_style,
        leading=11,
        spaceAfter=0,
    )

    compact_bullet_body_style = ParagraphStyle(
        "CVCompactBulletBody",
        parent=compact_body_style,
        leftIndent=10,
        firstLineIndent=-10,
    )

    volunteering_body_style = ParagraphStyle(
        "CVVolunteeringBody",
        parent=body_style,
        leading=17,
        spaceAfter=0,
        leftIndent=10,
        firstLineIndent=-10,
    )

    project_title_style = ParagraphStyle(
        "CVProjectTitle",
        parent=body_style,
        fontName="DejaVuSans-Bold",
        fontSize=9.72,
        leading=13,
        spaceBefore=2,
        spaceAfter=5,
        textColor=colors.HexColor("#333333"),
    )

    contact_style = ParagraphStyle(
        "CVContact",
        parent=body_style,
        alignment=TA_CENTER,
        fontSize=9.8,
        leading=14,
        spaceAfter=3,
    )

# --------------------------------------------------
# SECTION HEADER
# --------------------------------------------------

    def add_section_header(title):
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey,
                spaceBefore=6,
                spaceAfter=7,
            )
        )

        story.append(
            SpacedHeading(
                title,
                font_name="DejaVuSans-Bold",
                font_size=10,
                char_space=2.5,
            )
        )

# --------------------------------------------------
# CV HEADER
# --------------------------------------------------

    story = []

    story.append(
        SpacedTitle(name)
    )

    if job_title:
        story.append(Spacer(1, 9))
        story.append(
            SpacedJobTitle(job_title)
        )

    story.append(Spacer(1, 9))

    linkedin_display = (
        make_breakable_url(display_url(linkedin))
        if linkedin
        else ""
    )

    github_display = (
        make_breakable_url(display_url(github))
        if github
        else ""
    )

    story.append(
        Paragraph(
            f'<link href="tel:{phone}">{phone}</link> • '
            f'<link href="mailto:{email}">{email}</link>'
            + (
                f' • <link href="{linkedin}">{linkedin_display}</link>'
                if linkedin
                else ""
            )
            + (
                f' • <link href="{github}">{github_display}</link>'
                if github
                else ""
            ),
            contact_style,
        )
    )

    story.append(Spacer(1, 14))

# --------------------------------------------------
# PROFILE
# --------------------------------------------------

    add_section_header("Profil zawodowy")

    story.append(Paragraph(intro, body_style))

# --------------------------------------------------
# PROJECTS
# --------------------------------------------------

    if projects:
        add_section_header("Projekty")
        story.append(Spacer(1, 4))

        for project in projects:
            story.append(
                Paragraph(
                    project["name"],
                    project_title_style,
                )
            )

            story.append(
                Paragraph(
                    f"• {project['description']}",
                    bullet_body_style,
                )
            )

            story.append(
                Paragraph(
                    f"• {project['skills']}",
                    bullet_body_style,
                )
            )

            if project["result"].strip():
                story.append(
                    Paragraph(
                        f"• <b>Rezultat:</b> {project['result']}",
                        bullet_body_style,
                    )
                )

# --------------------------------------------------
# WORK EXPERIENCE
# --------------------------------------------------

    if experience:
        add_section_header("Doświadczenie zawodowe")
        story.append(Spacer(1, 4))

        for item in experience:
            story.append(
                Paragraph(
                    f"<b>{item['position']}</b> — {item['company']}",
                    project_title_style,
                )
            )

            story.append(
                Paragraph(
                    f"• {item['years']}",
                    bullet_body_style,
                )
            )

            if item["description"].strip():
                story.append(
                    Paragraph(
                        f"• {item['description']}",
                        bullet_body_style,
                    )
                )

# --------------------------------------------------
# TECHNICAL SKILLS
# --------------------------------------------------

    if any([
        skills_languages,
        skills_tools,
        skills_databases,
        skills_other,
    ]):
        add_section_header("Umiejętności techniczne")

        if skills_languages:
            story.append(
                Paragraph(
                    f"• Języki programowania: {skills_languages}",
                    bullet_body_style
                )
            )

        if skills_tools:
            story.append(
                Paragraph(
                    f"• Biblioteki i narzędzia: {skills_tools}",
                    bullet_body_style,
                )
            )

        if skills_databases:
            story.append(
                Paragraph(
                    f"• Bazy danych: {skills_databases}",
                    bullet_body_style,
                )
            )

        if skills_other:
            story.append(
                Paragraph(
                    f"• Inne: {skills_other}",
                    bullet_body_style,
                )
            )

# ==================================================
# OPTIONAL SECTIONS
# ==================================================

    # Dolna część CV — dynamiczny układ dwukolumnowy
    bottom_sections = []

    portfolio_section = None
    education_section = None
    courses_section = None
    languages_section = None
    volunteering_section = None

# --------------------------------------------------
# PORTFOLIO
# --------------------------------------------------

    if portfolio_url and portfolio_url.strip():
        portfolio_section = [
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey,
                spaceBefore=6,
                spaceAfter=7,
            ),
            SpacedHeading(
                "Portfolio",
                font_name="DejaVuSans-Bold",
                font_size=10,
                char_space=2.5,
            ),
            Spacer(1, 4),
            Paragraph(
                f'<link href="{portfolio_url}">'
                f'{make_breakable_url(display_url(portfolio_url))}'
                f'</link>',
                bullet_body_style,
            ),
        ]

        bottom_sections.append(portfolio_section)

# --------------------------------------------------
# EDUCATION
# --------------------------------------------------

    if education:
        education_section = [
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey,
                spaceBefore=6,
                spaceAfter=7,
            ),
            SpacedHeading(
                "Edukacja",
                font_name="DejaVuSans-Bold",
                font_size=10,
                char_space=2.5,
            ),
            Spacer(1, 4),
        ]

        for item in education:
            if item["type"] == "school":
                degree = item["degree"].strip().replace(" ", "\u00A0")
                years = item["years"].strip().replace(" ", "\u00A0")
                school = item["school"].strip().replace(" ", "\u00A0")

                education_section.append(
                    Paragraph(
                        f"<b>{degree}</b> — {school}",
                        project_title_style,
                    )
                )

                education_section.append(
                    Paragraph(
                        f"•\u00A0{years}",
                        bullet_body_style,
                    )
                )

        course_items = [
            item
            for item in education
            if item["type"] == "course"
        ]

        if course_items:
            education_section.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.lightgrey,
                    spaceBefore=6,
                    spaceAfter=7,
                )
            )

            education_section.append(
                SpacedHeading(
                    "Kursy",
                    font_name="DejaVuSans-Bold",
                    font_size=10,
                    char_space=2.5,
                )
            )

            education_section.append(
                Spacer(1, 4)
            )

            education_section.append(
                Spacer(1, 4)
            )

            for item in course_items:
                course = item["course"].strip().replace(" ", "\u00A0")
                provider = item["provider"].strip().replace(" ", "\u00A0")
                date = item["date"].strip().replace(" ", "\u00A0")

                education_section.append(
                    Paragraph(
                        f"<b>{course}</b> — {provider}",
                        project_title_style,
                    )
                )

                education_section.append(
                    Paragraph(
                        f"•\u00A0{date}",
                        bullet_body_style,
                    )
                )

        bottom_sections.append(education_section)

# --------------------------------------------------
# LANGUAGES
# --------------------------------------------------

    if languages:
        languages_section = [
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey,
                spaceBefore=6,
                spaceAfter=7,
            ),
            SpacedHeading(
                "Języki",
                font_name="DejaVuSans-Bold",
                font_size=10,
                char_space=2.5,
            ),
            Spacer(1, 4),
        ]

        for language in languages:
            languages_section.append(
                Paragraph(
                    f"• {language['language']}: {language['level']}",
                    compact_bullet_body_style,
                )
            )

        bottom_sections.append(languages_section)

# --------------------------------------------------
# VOLUNTEERING
# --------------------------------------------------

    if volunteering:
        volunteering_section = [
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey,
                spaceBefore=6,
                spaceAfter=7,
            ),
            SpacedHeading(
                "Wolontariat lub działalność pozazawodowa",
                font_name="DejaVuSans-Bold",
                font_size=10,
                char_space=2.5,
            ),
            Spacer(1, 4),
        ]

        volunteering_lines = [
            line.strip()
            for line in volunteering.splitlines()
            if line.strip()
        ]

        current_activity = None
        current_date = None
        has_activity = False

        for line in volunteering_lines:

            if " - " in line:

                if current_activity is not None:
                    volunteering_section.append(
                        Paragraph(
                            f"<b>{current_activity}</b>",
                            project_title_style,
                        )
                    )

                    volunteering_section.append(
                        Paragraph(
                            f"•\u00A0{current_date}",
                            bullet_body_style,
                        )
                    )

                if has_activity:
                    volunteering_section.append(
                        Spacer(1, 6)
                    )

                activity_name, activity_date = line.rsplit(
                    " - ",
                    1,
                )

                if " - " in activity_name:
                    organization, role = activity_name.split(
                        " - ",
                        1,
                    )

                    current_activity = (
                        f"{role.strip()} — "
                        f"{organization.strip()}"
                    )
                else:
                    current_activity = activity_name.strip()

                current_date = activity_date.strip()
                has_activity = True

            else:
                if current_activity is not None:

                    volunteering_section.append(
                        Paragraph(
                            f"<b>{current_activity}</b>",
                            project_title_style,
                        )
                    )

                    volunteering_section.append(
                        Paragraph(
                            f"•\u00A0{current_date}",
                            bullet_body_style,
                        )
                    )

                    volunteering_section.append(
                        Paragraph(
                            f"•\u00A0{line.strip()}",
                            bullet_body_style,
                        )
                    )

                    current_activity = None
                    current_date = None

        if current_activity is not None:

            volunteering_section.append(
                Paragraph(
                    f"<b>{current_activity}</b>",
                    project_title_style,
                )
            )

            volunteering_section.append(
                Paragraph(
                    f"•\u00A0{current_date}",
                    bullet_body_style,
                )
            )

        bottom_sections.append(volunteering_section)

# ==================================================
# DYNAMIC BOTTOM LAYOUT
# ==================================================

    if bottom_sections:

        # Kolejność sekcji:
        # Portfolio
        # Edukacja
        # Języki
        # Wolontariat
        #
        # Chcemy:
        # Edukacja       -> pełna szerokość
        # Wolontariat    -> pełna szerokość
        # Portfolio      -> lewa kolumna
        # Języki         -> prawa kolumna

        # --------------------------------------------------
        # EDUCATION — FULL WIDTH
        # --------------------------------------------------

        if education_section:
            story.append(
                Table(
                    [[education_section]],
                    colWidths=[doc.width],
                    hAlign="LEFT",
                    style=TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ]
                    ),
                )
            )

        # --------------------------------------------------
        # VOLUNTEERING — FULL WIDTH
        # --------------------------------------------------

        if volunteering_section:
            story.append(
                Table(
                    [[volunteering_section]],
                    colWidths=[doc.width],
                    hAlign="LEFT",
                    style=TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ]
                    ),
                )
            )

        # --------------------------------------------------
        # PORTFOLIO + LANGUAGES — TWO COLUMNS
        # --------------------------------------------------

        small_sections = [
            section
            for section in [portfolio_section, languages_section]
            if section
        ]

        if small_sections:

            left = (
                small_sections[0]
                if len(small_sections) > 0
                else []
            )

            right = (
                small_sections[1]
                if len(small_sections) > 1
                else []
            )

            lower_table = Table(
                [[left, right]],
                colWidths=[
                    doc.width * 0.48,
                    doc.width * 0.48,
                ],
                hAlign="LEFT",
            )

            lower_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (0, 0), 8),
                        ("LEFTPADDING", (1, 0), (1, 0), 8),
                    ]
                )
            )

            story.append(lower_table)

# ==================================================
# PDF BUILD & VALIDATION
# ==================================================

    page_bottom_positions = {}

    def track_bottom_position(flowable):
        current_y = doc.frame._y

        if doc.page not in page_bottom_positions:
            page_bottom_positions[doc.page] = current_y
        else:
            page_bottom_positions[doc.page] = min(
                page_bottom_positions[doc.page],
                current_y,
            )

    doc.afterFlowable = track_bottom_position

    doc.build(story)

    # CV musi nadal mieścić się na jednej stronie.
    # Jeśli nie mieści się nawet przy minimalnym marginesie,
    # generowanie zostaje zablokowane.
    if doc.page > 1:
        raise ValueError(
            f"CV nie mieści się na 1 stronie przy minimalnym "
            f"marginesie {CV_MIN_BOTTOM_MARGIN_MM} mm. "
            "Skróć treść lub usuń część danych."
        )

    # Rzeczywisty margines pomiędzy końcem treści
    # a dolną krawędzią strony.
    bottom_margin_mm = (
        page_bottom_positions[1] / mm
    )

    # Przekazujemy informację o rzeczywistym marginesie
    # do aplikacji Streamlit.
    buffer.cv_bottom_margin_mm = bottom_margin_mm

    buffer.seek(0)
    return buffer