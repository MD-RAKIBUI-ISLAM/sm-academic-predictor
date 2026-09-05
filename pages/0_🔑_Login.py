# pages/0_🔑_Login.py

import streamlit as st
from auth_utils import current_user, init_db, is_logged_in, login, logout, signup
from style_utils import load_css

st.set_page_config(page_title="Login / Sign Up", page_icon="🔑", layout="wide")
load_css()

init_db()

if is_logged_in():
    user = current_user()
    initials = "".join([n[0].upper() for n in user["full_name"].split()[:2]])
    status = user["verification_status"]
    badge_class = "badge-pending" if status == "Pending" else "badge-verified"
    badge_text = (
        "🕐 Pending Verification"
        if status == "Pending"
        else "✅ Verified Student"
    )

    st.markdown(
        f"""
        <div class="auth-status-card">
            <div class="auth-avatar">{initials}</div>
            <div style="font-size:1.3rem; font-weight:700; color:#0F172A;">{user['full_name']}</div>
            <div style="color:#64748B; font-size:0.9rem; margin-top:0.1rem;">{user['email']}</div>
            <div style="color:#64748B; font-size:0.85rem; margin-top:0.1rem;">{user['institution']} · Reg. No. {user['registration_number']}</div>
            <div class="auth-status-badge {badge_class}">{badge_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if status == "Pending":
        trial_note = (
            "You've already used your one free trial prediction. Further use "
            "unlocks once your account is verified by the research team."
            if user.get("trial_used")
            else "Your account is pending verification. You have **one free trial** "
                 "prediction available before verification is required for further use."
        )
        st.info(trial_note)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Log Out", use_container_width=True):
            logout()
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.page_link(
            "pages/3_🎒_School_GPA_Predictor.py",
            label="🎓 Predict — School/College",
            use_container_width=True,
        )
    with c2:
        st.page_link(
            "pages/4_🏛️_University_CGPA_Predictor.py",
            label="🏫 Predict — University",
            use_container_width=True,
        )

else:
    st.markdown(
        """
        <div class="auth-hero">
            <div class="auth-hero-icon">🔑</div>
            <div class="auth-hero-title">Welcome to EduPulse</div>
            <div class="auth-hero-sub">Log in or create an account to get your personalized academic-performance prediction.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input(
                "Password", type="password", placeholder="••••••••"
            )
            submitted = st.form_submit_button(
                "Log In", use_container_width=True
            )

        if submitted:
            success, result = login(email, password)
            if success:
                st.session_state["user"] = result
                st.rerun()
            else:
                st.error(result)

    with tab_signup:
        st.caption(
            "We ask for your institutional email and registration number so your status can be verified."
        )

        with st.expander("🔒 How your information is used", expanded=False):
            st.markdown(
                """
                - Your name, email, institution, and registration number are stored
                  in a local database used only for this research tool.
                - This information is used solely to determine whether your account
                  can be verified as belonging to a genuine student, and to allow you
                  one free trial prediction before verification is complete.
                - This is separate from, and not linked to, the original anonymous
                  survey data used to train the prediction models.
                - Your data is not shared with any third party and is not used for
                  any purpose beyond this academic research project.
                - You may request account deletion at any time by contacting the
                  research team.
                """
            )

        with st.form("signup_form"):
            # প্রথম সারিতে ফুল নেম ও ইন্সটিটিউশন
            c_name, c_inst = st.columns(2)
            with c_name:
                full_name = st.text_input("Full Name", placeholder="Jane Doe")
            with c_inst:
                institution = st.text_input(
                    "Institution Name",
                    placeholder="School / College / University",
                )

            # দ্বিতীয় সারিতে রেজিঃ নম্বর ও ইমেইল
            c_reg, c_email = st.columns(2)
            with c_reg:
                registration_number = st.text_input(
                    "Registration Number", placeholder="e.g. 2021-123-456"
                )
            with c_email:
                email = st.text_input(
                    "Email Address", placeholder="Institutional email preferred"
                )

            # তৃতীয় সারিতে পাসওয়ার্ড দুটি
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Min. 6 characters",
                )
            with c_p2:
                confirm_password = st.text_input(
                    "Confirm Password", type="password"
                )

            agree = st.checkbox(
                "I confirm I am a genuine student and the information provided is accurate."
            )
            consent = st.checkbox(
                "I have read and agree to how my information will be used, as described above."
            )
            submitted = st.form_submit_button(
                "Create Account", use_container_width=True
            )

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match.")
            elif not agree:
                st.error(
                    "Please confirm the accuracy of your information to proceed."
                )
            elif not consent:
                st.error(
                    "Please confirm you agree to how your information will be used."
                )
            else:
                success, message = signup(
                    full_name, email, institution, registration_number, password
                )
                if success:
                    st.success(message + " Switch to the Log In tab above.")
                else:
                    st.error(message)