#Streamlit frontend 
import streamlit as st
import pandas as pd
import smtplib
import ssl
import time
from pathlib import Path
from email.message import EmailMessage
from email.utils import formataddr

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Modular Cold Email Automation", page_icon="✉️", layout="wide")

st.title("✉️ Modular Cold Email Automation Dashboard")
st.markdown("Exclusively configured for customized multi-user dispatch.")

# --- CORE FUNCTIONS (ADAPTED FOR STREAMLIT) ---

def render_template(template, row):
    """Fills {field} placeholders using data row keys."""
    text = template
    for key, value in row.items():
        # Match case-insensitive or direct replacement
        text = text.replace("{" + str(key).strip().lower() + "}", str(value))
        text = text.replace("{" + str(key).strip() + "}", str(value))
    return text

def build_message(sender_email, sender_name, row, subject_template, body_template, resume_bytes, resume_name):
    """Constructs the EmailMessage object with attachment."""
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
    """Validates the SMTP credentials before starting the blast."""
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

# User profiles quick select helper
user_profile = st.sidebar.selectbox("Select User Profile Slots", ["User 1 (Kushagra)", "User 2 (Saumya)", "Custom Setup"])

# Autofill names based on slot selections to make it seamless
default_name = "Kushagra Omar" if "Kushagra" in user_profile else ("Saumya Verma" if "Saumya" in user_profile else "")
default_subject = "Exploring AI/ML Opportunities at {company} - Kushagra Omar" if "Kushagra" in user_profile else "Application for Associate Project Manager - Saumya Verma"

sender_name = st.sidebar.text_input("Sender Display Name", value=default_name)
sender_email = st.sidebar.text_input("Sender Email Address", placeholder="your-email@gmail.com")
app_password = st.sidebar.text_input("Gmail App Password", type="password", help="16-character security app password generated from Google Account.")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ SMTP Configuration")
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", value=465)
smtp_mode = st.sidebar.selectbox("SMTP Mode", ["ssl", "starttls"], index=0)

st.sidebar.markdown("---")
st.sidebar.header("⏳ Automation Pacing")
delay_sec = st.sidebar.slider("Delay between emails (seconds)", min_value=10, max_value=300, value=60, step=5, 
                              help="Keeping this above 60s prevents your account from hitting spam limits.")
max_retries = st.sidebar.number_input("Max Retries per failed email", min_value=0, max_value=5, value=2)

# Verify button connection status
if st.sidebar.button("Test SMTP Connection"):
    if not sender_email or not app_password:
        st.sidebar.error("Please enter email and password first.")
    else:
        with st.sidebar.spinner("Testing..."):
            success, msg = test_smtp_connection(smtp_server, smtp_port, smtp_mode, sender_email, app_password)
            if success:
                st.sidebar.success(msg)
            else:
                st.sidebar.error(f"Failed: {msg}")


# --- MAIN INTERFACE: CONTENT & UPLOADS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Upload Materials")
    uploaded_csv = st.file_uploader("Upload HR Contact List (CSV)", type=["csv"])
    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with col2:
    st.subheader("📝 Email Template Editor")
    subject_template = st.text_input("Email Subject Template", value=default_subject)
    
    # Custom initial template body based on selection
    if "Saumya" in user_profile:
        initial_body = "Dear {name},\n\nI am writing to express my interest in the Project Manager position at {company}..."
    else:
        initial_body = "Hi {name},\n\nMy name is Kushagra Omar, currently working as an AI Engineer. I'm reaching out to see if {company} has any openings..."
        
    body_template = st.text_area("Email Body Template (use {name}, {company}, {title} tags)", value=initial_body, height=250)


# --- PROCESSING DATA ---
if uploaded_csv:
    try:
        # Load data safely
        df = pd.read_csv(uploaded_csv)
        # Normalize column names to lowercase for consistency
        df.columns = [c.strip().lower() for c in df.columns]
        
        st.markdown("### 📋 Recipient Preview Data")
        st.dataframe(df.head(5))
        
        if "email" not in df.columns:
            st.error("❌ Crucial Error: The uploaded CSV must contain an 'email' column header.")
            st.stop()
            
        recipients_count = len(df)
        st.info(f"Loaded {recipients_count} valid rows from the mailing list.")
        
        # Action validation trigger
        st.markdown("---")
        st.subheader("🚀 Campaign Dispatch Control")
        
        if st.button(f"Start Mailing Blast to {recipients_count} Recipients"):
            if not sender_email or not app_password:
                st.error("❌ Missing identity parameters. Provide email and credentials on the sidebar.")
            elif not uploaded_resume:
                st.warning("⚠️ Proceeding without attaching a resume file.")
                resume_bytes, resume_name = None, None
            else:
                resume_bytes = uploaded_resume.read()
                resume_name = uploaded_resume.name
                
                # Setup Live Progress Widgets
                progress_bar = st.progress(0)
                status_text = st.empty()
                log_box = st.code("", language="text")
                
                sent_count = 0
                failed_count = 0
                logs = []
                
                # Start SMTP Context session loop
                try:
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
                            if not email_address or "@" not in email_address:
                                continue
                            
                            # Clean row dictionary mapping data rows 
                            row_dict = row.to_dict()
                            
                            is_sent = False
                            # Attempt with retry logic
                            for attempt in range(1, max_retries + 2):
                                try:
                                    msg_obj = build_message(
                                        sender_email, sender_name, row_dict, 
                                        subject_template, body_template, 
                                        resume_bytes, resume_name
                                    )
                                    server.send_message(msg_obj)
                                    is_sent = True
                                    break
                                except Exception as inner_e:
                                    if attempt <= max_retries:
                                        time.sleep(2)
                                    else:
                                        err_msg = str(inner_e)
                                        
                            if is_sent:
                                sent_count += 1
                                logs.append(f"✅ [{index+1}/{recipients_count}] Sent successfully to: {email_address}")
                            else:
                                failed_count += 1
                                logs.append(f"❌ [{index+1}/{recipients_count}] Failed delivery to {email_address} | Reason: {err_msg}")
                            
                            # Update live UI feeds
                            progress_percent = int(((index + 1) / recipients_count) * 100)
                            progress_bar.progress(progress_percent)
                            status_text.markdown(f"**Progress Status:** Live sent: `{sent_count}` | Failures: `{failed_count}`")
                            log_box.code("\n".join(logs[-15:])) # Show last 15 actions lines
                            
                            # Standard delay throttle pause between emails except on final iteration
                            if index < recipients_count - 1:
                                status_text.markdown(f"**Progress Status:** Live sent: `{sent_count}` | Failures: `{failed_count}` (Waiting {delay_sec}s pacing delay...)")
                                time.sleep(delay_sec)
                                
                    st.success(f"🎉 Campaign complete! Successfully sent: {sent_count} emails. Failed: {failed_count} emails.")
                    
                except Exception as smtp_session_err:
                    st.error(f"🚨 Connection dropped unexpectedly or configuration timed out: {smtp_session_err}")
                    
    except Exception as e:
        st.error(f"Error reading file elements: {e}")
else:
    st.info("💡 Upload your custom HR spreadsheet CSV list on the dashboard to initialize the email blast tools.")