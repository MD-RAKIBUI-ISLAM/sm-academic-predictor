import streamlit as st
import streamlit.components.v1 as components
from auth_utils import is_logged_in, current_user, logout


def render_navbar(active: str = ""):
    """
    Render a simplified top navbar: brand on the left, user info + logout
    on the right. Page navigation is handled by Streamlit's native sidebar.
    """
    
    # query param চেক করে লগআউট হ্যান্ডেল করা
    if st.query_params.get("action") == "logout":
        logout()
        st.query_params.clear()
        st.rerun()

    user = current_user() if is_logged_in() else None

    if user:
        initials = "".join([n[0].upper() for n in user["full_name"].split()[:2]])
        right_html = f"""
            <div class="navbar-user">
                <div class="navbar-avatar">{initials}</div>
                <span class="navbar-username">{user['full_name']}</span>
                <a href="?action=logout" target="_self" class="navbar-logout-btn">Log Out</a>
            </div>
        """
    else:
        right_html = '<a href="/Login" target="_self" class="navbar-login-link">🔑 Log In</a>'

    st.markdown(
        f"""
        <div class="custom-navbar" id="custom-navbar">
            <div class="navbar-brand">
                🎓 EduPulse
                <span class="navbar-brand-sub" style="margin-left:6px;">Social Media & Academic Insight</span>
            </div>
            <div class="navbar-right">{right_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navbar alignment script
    components.html(
        """
        <script>
        function syncNavbar() {
            const doc = window.parent.document;
            const main = doc.querySelector('[data-testid="stMain"]');
            const navbar = doc.getElementById('custom-navbar');
            if (!main || !navbar) return;
            const rect = main.getBoundingClientRect();
            navbar.style.left = rect.left + 'px';
            navbar.style.width = rect.width + 'px';
        }

        syncNavbar();
        window.parent.addEventListener('resize', syncNavbar);

        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            new MutationObserver(syncNavbar).observe(sidebar, { attributes: true });
            sidebar.addEventListener('transitionend', syncNavbar);
        }
        setInterval(syncNavbar, 400);
        </script>
        """,
        height=0,
    )