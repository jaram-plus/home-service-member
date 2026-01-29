"""CSS styling utilities for admin frontend."""

import streamlit as st


def load_css(file_name=".streamlit/style.css"):
    """Load CSS stylesheet.

    Args:
        file_name: Path to CSS file relative to app root. Defaults to .streamlit/style.css
    """
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f">> CSS file not found: {file_name}")
