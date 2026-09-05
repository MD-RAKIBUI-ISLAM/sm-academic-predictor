import pandas as pd
import streamlit as st
from auth_utils import get_all_users, init_db, update_verification_status
from style_utils import load_css

st.set_page_config(
    page_title="Admin — Student Verification", page_icon="🛡️", layout="wide"
)
load_css()
init_db()  # ensure the database and users table exist

# --- Simple password gate (for the researcher/supervisor, not students) ---
ADMIN_PASSWORD = st.secrets.get("admin_password", None)

if ADMIN_PASSWORD is None:
    st.error(
        "⚠️ No admin password configured. Add `admin_password = \"...\"` to "
        "`.streamlit/secrets.toml` before using this page."
    )
    st.stop()

    
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    st.markdown(
        """
        <div class="auth-hero" style="margin-top: 2rem;">
            <div class="auth-hero-icon">🛡️</div>
            <div class="auth-hero-title">Admin Restricted Area</div>
            <div class="auth-hero-sub">Enter the administrator password to access student verification records.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            pwd = st.text_input(
                "Admin Password",
                type="password",
                placeholder="Enter password",
            )
            if st.button("Unlock Admin Panel", use_container_width=True):
                if pwd == ADMIN_PASSWORD:
                    st.session_state["admin_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
    st.stop()

# --- Admin panel Header ---
c_head1, c_head2 = st.columns([4, 1])
with c_head1:
    st.markdown("### 🛡️ Admin — Student Verification")
    st.caption("Manage user verification status and institutional access.")
with c_head2:
    if st.button("🔒 Lock Page", use_container_width=True):
        st.session_state["admin_authenticated"] = False
        st.rerun()

st.divider()

users = get_all_users()

if not users:
    st.info("No accounts have been created yet.")
else:
    # Summary counts
    df_users = pd.DataFrame(users)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pending Verification", (df_users["verification_status"] == "Pending").sum())
    c2.metric("Verified Students", (df_users["verification_status"] == "Verified").sum())
    c3.metric("Rejected Accounts", (df_users["verification_status"] == "Rejected").sum())
    c4.metric("Trial Accounts Used", df_users["trial_used"].sum())

    st.divider()
    st.caption(
        "💡 Cross-check each registration number and institutional email against "
        "official student records (when available), then update their status below. "
        "Rejected accounts are immediately logged out and blocked from logging in again."
    )

    for user in users:
        # border=True দিয়ে কন্টেইনারকে কার্ডে রূপান্তর করা হয়েছে
        with st.container(border=True):
            c1, c2 = st.columns([3.5, 1.5])
            with c1:
                status = user["verification_status"]
                badge_class = (
                    "badge-pending"
                    if status == "Pending"
                    else (
                        "badge-verified"
                        if status == "Verified"
                        else "badge-rejected"
                    )
                )

                trial_label = (
                    "✅ Free trial used"
                    if user["trial_used"]
                    else "⬜ Free trial available"
                )

                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">{user['full_name']}</span>
                        <span class="auth-status-badge {badge_class}">{status}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption(f"📧 {user['email']}")
                st.caption(
                    f"🏫 {user['institution']}  ·  🪪 Reg. No. {user['registration_number']}"
                )
                st.caption(
                    f"📅 Signed up: {user['created_at']}  ·  {trial_label}"
                )

            with c2:
                current_status = user["verification_status"]
                new_status = st.selectbox(
                    "Status",
                    ["Pending", "Verified", "Rejected"],
                    index=["Pending", "Verified", "Rejected"].index(
                        current_status
                    ),
                    key=f"status_{user['id']}",
                    label_visibility="collapsed",
                )
                if new_status != current_status:
                    if st.button(
                        "Save",
                        key=f"save_{user['id']}",
                        use_container_width=True,
                    ):
                        update_verification_status(user["id"], new_status)
                        st.success(
                            f"Updated {user['full_name']} to {new_status}."
                        )
                        st.rerun()