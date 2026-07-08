"""
message/content.py
------------------
Available merge tags (from your CSV columns):  {name}  {title}  {company}
"""

# SUBJECT = "Application for Associate Project Manager - Saumya Verma"

# BODY = """Dear {name},

# I hope you are doing well.

# I am writing to express my interest in the Project Manager position at {company}.
# With experience in coordination, documentation, stakeholder communication,
# and project tracking, I believe I would be a good fit for this opportunity.

# I have hands-on experience working with tools such as MS Excel and MS Word,
# along with project coordination practices involving timeline tracking,
# follow-ups, and cross-functional collaboration. I am highly organized,
# detail-oriented, and eager to contribute to a dynamic environment like
# {company}.

# My interest in project management and process improvement, combined with
# my ability to communicate effectively and manage responsibilities
# efficiently, motivates me to apply for this role.

# I have attached my resume for your consideration and would welcome the
# opportunity to discuss how my skills and enthusiasm align with your team's
# requirements.

# Thank you for your time and consideration. I look forward to hearing from you.

# Kind regards,
# Saumya Verma
# """

SUBJECT = "Exploring AI/ML Opportunities at {company} - Kushagra Omar"

BODY = """Hi {name},

My name is Kushagra Omar, currently working as an AI Engineer. I'm reaching out to see if {company} has any openings, now or in the near future, 
for someone who builds AI/ML systems.

What I do: design and build agentic and LLM-driven applications, then take them all the way to deployment - orchestrating multi-agent workflows on 
the AI side and standing up the services, APIs, and databases behind them.

What I work with:
- Agentic AI & LLMs: LangGraph, LangChain, CrewAI, LangSmith, RAG 
- ML: PyTorch, scikit-learn, MLflow, DVC
- Backend & infra: FastAPI, React, PostgreSQL, Redis, MongoDB, AWS
- Strong CS fundamentals: DSA (150+ problems solved), System Design, OOP, DBMS

What I bring: someone who can own an AI feature from idea to deployed product, works well across the stack, learns fast, and is genuinely invested
in agentic AI and applied ML.

I've attached my resume for your reference. Even if there's nothing open right now, I'd be grateful to be kept in mind for future roles you can reach
me anytime.

Best,
Kushagra Omar
+91 9307553372 | kushagra.omar@gmail.com
LinkedIn: linkedin.com/in/kushagraomar3355 | GitHub: github.com/Kushagra3355

"""


def render(template, row):
    """Fill {field} placeholders using a recipient's row dict.
    Unknown placeholders are left untouched instead of crashing."""
    text = template
    for key, value in row.items():
        text = text.replace("{" + key + "}", str(value))
    return text


def build_subject(row):
    return render(SUBJECT, row)


def build_body(row):
    return render(BODY, row)