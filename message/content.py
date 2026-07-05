"""
message/content.py
------------------
Available merge tags (from your Excel columns):  {name}  {title}  {company}
"""

SUBJECT = "Application for Associate Project Manager - Saumya Verma"

BODY = """Dear {name},

I hope you are doing well.

I am writing to express my interest in the {title} position at {company}.
With experience in coordination, documentation, stakeholder communication,
and project tracking, I believe I would be a good fit for this opportunity.

I have hands-on experience working with tools such as MS Excel and MS Word,
along with project coordination practices involving timeline tracking,
follow-ups, and cross-functional collaboration. I am highly organized,
detail-oriented, and eager to contribute to a dynamic environment like
{company}.

My interest in project management and process improvement, combined with
my ability to communicate effectively and manage responsibilities
efficiently, motivates me to apply for this role.

I have attached my resume for your consideration and would welcome the
opportunity to discuss how my skills and enthusiasm align with your team's
requirements.

Thank you for your time and consideration. I look forward to hearing from you.

Kind regards,
Saumya Verma
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