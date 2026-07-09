import streamlit as st
import pandas as pd
import smtplib
import ssl
import time
import base64
from pathlib import Path
from email.message import EmailMessage
from email.utils import formataddr

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Modular Cold Email Automation", page_icon="✉️", layout="wide")

st.title("✉️ Cold Email Automation Dashboard & Inspector")
st.markdown("Configure, completely inspect rendered messages, and verify documents before sending.")

# --- CORE FUNCTIONS ---

def render_template(template, row):
    """Fills {field} placeholders using data row keys case-insensitively."""
    text = template
    for key, value in row.items():
        text = text.replace("{" + str(key).strip().lower() + "}", str(value))
        text = text.replace("{" + str(key).strip() + "}", str(value))
    return text

def build_message(sender_email, sender_name, row, subject_template, body_template, resume_bytes, resume_name):
    """Constructs the EmailMessage object."""
    msg = EmailMessage()
    msg["From"] = formataddr((sender_name, sender_email)) if sender_name else sender_email
    msg["To"] = row["email"]
    msg["Subject"] = render_template(subject_template, row)
    msg.set_content(render_template(body_template, row))

    if resume_bytes:
        msg.add_attachment(
            resume_bytes,
            maintype="application",
            subtype="octet-stream",
            filename=resume_name,
        )
    return msg

def test_smtp_connection(server_host, port, mode, sender_email, password):
    """Validates the SMTP credentials."""
    try:
        context = ssl.create_default_context()
        if mode == "ssl":
            server = smtplib.SMTP_SSL(server_host, port, context=context, timeout=15)
        else:
            server = smtplib.SMTP(server_host, port, timeout=15)
            server.starttls(context=context)
        
        with server:
            server.login(sender_email, password)
        return True, "Connection Successful!"
    except Exception as e:
        return False, str(e)

# --- SIDEBAR: CREDENTIALS & CONFIGURATION ---
st.sidebar.header("🔑 Authentication & Settings")

user_profile = st.sidebar.selectbox("Select User Profile Slots", ["User 1 (Kushagra)", "User 2 (Saumya)", "Custom Setup"])

# Pull defaults from st.secrets dynamically
if "Kushagra" in user_profile:
    default_name = "Kushagra Omar"
    default_subject = "Exploring AI/ML Opportunities at {company} - Kushagra Omar"
    default_email = st.secrets.get("kushagra_creds", {}).get("email", "")
    default_pass = st.secrets.get("kushagra_creds", {}).get("password", "")
    initial_body = """Hi {name},

My name is Kushagra Omar, currently working as an AI Engineer. I'm reaching out to see if {company} has any openings, now or in the near future, for someone who builds AI/ML systems.

What I do: design and build agentic and LLM-driven applications, then take them all the way to deployment - orchestrating multi-agent workflows on the AI side and standing up the services, APIs, and databases behind them.

What I work with:
- Agentic AI & LLMs: LangGraph, LangChain, CrewAI, LangSmith, RAG 
- ML: PyTorch, scikit-learn, MLflow, DVC
- Backend & infra: FastAPI, React, PostgreSQL, Redis, MongoDB, AWS
- Strong CS fundamentals: DSA (150+ problems solved), System Design, OOP, DBMS

What I bring: someone who can own an AI feature from idea to deployed product, works well across the stack, learns fast, and is genuinely invested in agentic AI and applied ML.

I've attached my resume for your reference. Even if there's nothing open right now, I'd be grateful to be kept in mind for future roles you can reach me anytime.

Best,
Kushagra Omar
+91 9307553372 | kushagra.omar@gmail.com
LinkedIn: linkedin.com/in/kushagraomar3355 | GitHub: github.com/Kushagra3355"""

elif "Saumya" in user_profile:
    default_name = "Saumya Verma"
    default_subject = "Application for Associate Project Manager - Saumya Verma"
    default_email = st.secrets.get("saumya_creds", {}).get("email", "")
    default_pass = st.secrets.get("saumya_creds", {}).get("password", "")
    initial_body = """Dear {name},

I hope you are doing well.

I am writing to express my interest in the Project Manager position at {company}.
With experience in coordination, documentation, stakeholder communication, and project tracking, I believe I would be a good fit for this opportunity.

I have hands-on experience working with tools such as MS Excel and MS Word, along with project coordination practices involving timeline tracking, follow-ups, and cross-functional collaboration. I am highly organized, detail-oriented, and eager to contribute to a dynamic environment like {company}.

My interest in project management and process improvement, combined with my ability to communicate effectively and manage responsibilities efficiently, motivates me to apply for this role.

I have attached my resume for your consideration and would welcome the opportunity to discuss how my skills and enthusiasm align with your team's requirements.

Thank you for your time and consideration. I look forward to hearing from you.

Kind regards,
Saumya Verma"""
else:
    default_name, default_subject, default_email, default_pass, initial_body = "", "", "", "", ""

sender_name = st.sidebar.text_input("Sender Display Name", value=default_name)
sender_email = st.sidebar.text_input("Sender Email Address", value=default_email)
app_password = st.sidebar.text_input("Gmail App Password", type="password", value=default_pass)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ SMTP & Pacing")
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", value=465)
smtp_mode = st.sidebar.selectbox("SMTP Mode", ["ssl", "starttls"], index=0)
delay_sec = st.sidebar.slider("Delay between emails (seconds)", min_value=10, max_value=300, value=60, step=5)
max_retries = st.sidebar.number_input("Max Retries per email", min_value=0, max_value=5, value=2)

if st.sidebar.button("Test SMTP Connection"):
    with st.spinner("Testing..."):
        success, msg = test_smtp_connection(smtp_server, smtp_port, smtp_mode, sender_email, app_password)
        if success: st.sidebar.success(msg)
        else: st.sidebar.error(f"Failed: {msg}")

# --- MAIN INTERFACE: CONFIGURATION & UPLOADS ---
upload_col, template_col = st.columns(2)

with upload_col:
    st.subheader("📁 1. Upload Materials")
    uploaded_csv = st.file_uploader("Upload HR Contact List (CSV)", type=["csv"])
    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with template_col:
    st.subheader("📝 2. Edit Master Blueprints")
    subject_template = st.text_input("Subject Template", value=default_subject)
    body_template = st.text_area("Body Template (Use tags like {name}, {company})", value=initial_body, height=250)

# --- THE INSPECTOR PANEL ---
st.markdown("---")
st.subheader("🔍 3. Live Campaign Inspector")

if uploaded_csv:
    try:
        df = pd.read_csv(uploaded_csv)
        df.columns = [c.strip().lower() for c in df.columns]
        
        if "email" not in df.columns:
            st.error("❌ The CSV must contain an 'email' column header.")
            st.stop()

        preview_tab, text_tab, document_tab = st.tabs([
            "📋 Recipient Matrix Spreadsheet", 
            "👀 Full Message Preview (Actual Render)", 
            "📄 Attached Document Preview"
        ])

        with preview_tab:
            st.markdown("#### Raw data rows from your uploaded spreadsheet:")
            st.dataframe(df)

        with text_tab:
            st.markdown("#### Select a row index below to see the exact final message that will go out:")
            selected_index = st.number_input(
                f"Choose row to preview (0 to {len(df)-1})", 
                min_value=0, max_value=len(df)-1, value=0, step=1
            )
            
            target_row = df.iloc[selected_index].to_dict()
            rendered_subject = render_template(subject_template, target_row)
            rendered_body = render_template(body_template, target_row)
            
            st.info(f"**Target Destination Inbox:** {target_row.get('email', 'N/A')}")
            st.markdown(f"**Actual Outgoing Subject:**")
            st.code(rendered_subject, language="text")
            st.markdown(f"**Actual Outgoing Body:**")
            st.text_area("Complete Rendered Output Text Area", value=rendered_body, height=350, disabled=True)

        with document_tab:
            if uploaded_resume:
                st.markdown(f"#### Attached File: `{uploaded_resume.name}`")
                
                resume_bytes = uploaded_resume.getvalue()
                
                # Native Download & View Button Fallback to bypass Chrome Sandbox policy limits
                st.download_button(
                    label="📥 Open / Download PDF to Verify Layout",
                    data=resume_bytes,
                    file_name=uploaded_resume.name,
                    mime="application/pdf",
                    help="Click here if Chrome prevents the inline preview block from rendering directly below."
                )
                
                st.markdown("---")
                
                base64_pdf = base64.b64encode(resume_bytes).decode('utf-8')
                pdf_display = f"""
                <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf">
                    <p>Your browser does not support embedded PDFs. Please use the download button above to view the file.</p>
                </iframe>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No resume attached yet. Upload a PDF in section 1 to review it here.")

        # --- DISPATCH CAMPAIGN TRIGGER ---
        st.markdown("---")
        st.subheader("🚀 4. Execute Campaign Blast")
        
        if st.button(f"Start Mailing Blast to {len(df)} Recipients"):
            if not sender_email or not app_password:
                st.error("❌ Please provide SMTP details and email authentication parameters.")
                st.stop()
                
            resume_data = uploaded_resume.read() if uploaded_resume else None
            resume_title = uploaded_resume.name if uploaded_resume else None
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_box = st.code("", language="text")
            
            sent_count, failed_count = 0, 0
            logs = []
            
            context = ssl.create_default_context()
            if smtp_mode == "ssl":
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                server.starttls(context=context)
                
            with server:
                server.login(sender_email, app_password)
                
                for index, row in df.iterrows():
                    email_address = str(row["email"]).strip()
                    row_dict = row.to_dict()
                    
                    is_sent = False
                    err_msg = ""
                    
                    for attempt in range(1, max_retries + 2):
                        try:
                            msg_obj = build_message(
                                sender_email, sender_name, row_dict, 
                                subject_template, body_template, 
                                resume_data, resume_title
                            )
                            server.send_message(msg_obj)
                            is_sent = True
                            break
                        except Exception as inner_e:
                            err_msg = str(inner_e)
                            if attempt <= max_retries:
                                time.sleep(2)
                                
                    if is_sent:
                        sent_count += 1
                        logs.append(f"✅ [{index+1}/{len(df)}] Sent to: {email_address}")
                    else:
                        failed_count += 1
                        logs.append(f"❌ [{index+1}/{len(df)}] Failed to {email_address} | {err_msg}")
                    
                    pct = int(((index + 1) / len(df)) * 100)
                    progress_bar.progress(pct)
                    status_text.markdown(f"**Live Status:** Sent: `{sent_count}` | Failed: `{failed_count}`")
                    log_box.code("\n".join(logs[-10:]))
                    
                    if index < len(df) - 1:
                        time.sleep(delay_sec)
                        
            st.success(f"🎉 Complete! Successfully sent {sent_count} emails; {failed_count} failed.")

    except Exception as e:
        st.error(f"Error processing CSV structural entries: {e}")
else:
    st.info("💡 Drop your destination HR Contact Spreadsheet CSV file above to populate the interactive inspector tool layout panels.")