"""CSS styling utilities for admin frontend."""

import streamlit as st


def load_css():
    """Load global CSS stylesheet."""
    css_file = ".streamlit/style.css"
    try:
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f">> CSS file not found: {css_file}")
