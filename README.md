# 📄 CVTailor

An AI-powered Streamlit application for creating professional, job-tailored CVs and generating one-page PDF documents.

CVTailor allows users to enter their professional information, provide a target job offer and company details, and generate a tailored professional profile using the OpenAI API.

The application combines AI-generated content with deterministic PDF generation, validation, and dynamic document layout.

---

# 📸 Screenshots

## Main Application

The main interface allows users to enter their personal information, professional background, and additional CV data.

![Main Application](screenshots/workflow1.png)

---

## CV Data and Validation

Users can add projects, experience, education, skills, languages, and other information.

The application validates the entered data and provides feedback when the generated CV requires too much space.

![CV Data and Validation](screenshots/workflow2.png)

---

## Input Validation

The application validates required fields and prevents CV generation when required information is missing or invalid.

![Input Validation](screenshots/workflow3.png)

---

# 📄 Generated CV Examples

The generator was tested with different professional profiles and career levels.

## Junior Python Developer

A junior IT profile focused on Python development, backend projects, technical skills, education, courses, and portfolio.

![Junior Python Developer](screenshots/cv2.png)

---

## Senior AI Engineer

A senior technical profile with extensive professional experience, education, portfolio, and language information.

![Senior AI Engineer](screenshots/cv1.png)

---

## Marketing Specialist

A non-technical profile demonstrating that the application can generate CVs for different industries and different combinations of available information.

![Marketing Specialist](screenshots/cv3.png)

---

# ✨ Features

- Structured CV data input
- Personal and contact information
- Job offer input
- Company information
- AI-generated professional profile
- Projects
- Work experience
- Technical skills
- Education
- Courses
- Languages
- Volunteering and other activities
- Portfolio
- Dynamic CV layout
- One-page PDF generation
- PDF preview
- PDF download
- Input validation
- URL validation
- One-page content validation
- Custom fonts
- Clickable email, phone, LinkedIn, GitHub, and portfolio links

---

# 🤖 AI Profile Generation

The professional profile is generated using the OpenAI API.

The model receives:

- candidate information,
- job offer information,
- company information.

The prompt is designed to generate a short professional profile written in the first person.

The generated profile is constrained to:

- 2–3 sentences,
- approximately 300 characters,
- natural and concise language,
- relevant experience and skills,
- information provided by the candidate only.

The prompt also prevents generic AI-style statements and unsupported claims.

---

# 📄 PDF Generation

The final CV is generated as a one-page PDF using ReportLab.

The PDF generator is responsible for:

- document layout,
- typography,
- custom fonts,
- section headings,
- spacing,
- hyperlinks,
- bullet points,
- dynamic lower-section layout,
- one-page validation.

The application prevents the final document from being generated when the CV cannot fit on a single page.

---

# 🏛 Architecture

The application follows a simple pipeline combining structured user input, AI-generated content, and deterministic PDF generation.

    User
     │
     ▼
    Streamlit UI
     │
     ├── Personal information
     ├── Job offer
     ├── Company information
     ├── Projects
     ├── Experience
     ├── Skills
     ├── Education
     ├── Courses
     ├── Languages
     └── Additional activities
     │
     ▼
    OpenAI API
     │
     └── Professional profile generation
     │
     ▼
    CV Data
     │
     ▼
    ReportLab PDF Generator
     │
     ├── Layout
     ├── Typography
     ├── Sections
     ├── Links
     └── One-page validation
     │
     ▼
    PDF Preview
     │
     ▼
    PDF Download

### Main Components

**Streamlit**

Responsible for the user interface, form handling, validation, preview, and application flow.

**OpenAI API**

Generates the professional profile based on the candidate's information, target position, and company.

**CV Factory**

Contains reusable templates and helper functions used to structure CV content.

**ReportLab**

Generates the final one-page PDF document and handles the document layout.

---

# 🛠 Tech Stack

- Python 3.11
- Streamlit
- OpenAI API
- ReportLab
- python-dotenv
- Git / GitHub

---

# 📁 Project Structure

    .
    ├── fonts/
    │   ├── DejaVuSans.ttf
    │   └── DejaVuSans-Bold.ttf
    │
    ├── screenshots/
    │   ├── workflow1.png
    │   ├── workflow2.png
    │   ├── workflow3.png
    │   ├── cv1.png
    │   ├── cv2.png
    │   └── cv3.png
    │
    ├── app.py
    ├── cv_factory.py
    ├── pdf_generator.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

---

# 🚀 Installation

Clone the repository:

    git clone https://github.com/Goldmanski/cv-tailor.git
    cd cv-tailor

Create a virtual environment:

    python -m venv .venv

Activate it.

### Windows

    .venv\Scripts\activate

### Linux / macOS

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Create a `.env` file in the project root:

    OPENAI_API_KEY=your_openai_api_key

---

# ▶️ Run

Start the Streamlit application:

    streamlit run app.py

The application will open in your browser.

---

# 📄 Example Workflow

1. Enter personal and contact information.
2. Add information about professional experience and skills.
3. Add projects, education, courses, languages, and other relevant information.
4. Provide the target job offer.
5. Optionally provide information about the company.
6. Generate the professional profile using OpenAI.
7. Review the generated CV.
8. Check validation messages if the CV exceeds the available space.
9. Generate the final PDF.
10. Preview and download the CV.

---

# 🎯 Design Goals

The project focuses on:

- Combining generative AI with deterministic document generation
- Creating job-tailored professional profiles
- Keeping AI-generated content concise and controlled
- Supporting different career levels and industries
- Maintaining a one-page CV constraint
- Providing clear validation feedback
- Separating CV content generation from PDF rendering
- Creating a simple and practical user experience

---

# 🔮 Possible Future Improvements

- Additional CV templates
- More advanced job-description analysis
- Multilingual CV generation
- Additional PDF layouts
- More granular AI customization
- Export to additional document formats
- Additional CV validation rules
- Improved customization of typography and spacing

---

# 👤 Author

Created by Eliasz Nowicki as a portfolio project focused on Python, AI Engineering, generative AI, Streamlit application development, and document generation.