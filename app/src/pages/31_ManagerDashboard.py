import logging
import streamlit as st
from modules.nav import SideBarLinks  # Custom navigation component (if used)
import requests

# Set up logging for debugging
logger = logging.getLogger(__name__)

# Configure the page layout
st.set_page_config(layout="wide")

# Add sidebar navigation
SideBarLinks()

# Main Title
st.title(f"Welcome Hiring Manager, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

# Button to view and manage availability
if st.button("Manage JobListings", type="primary", use_container_width=True):
    st.switch_page("pages/32_PostJob.py")  

# Button to view and update co-op reviews
if st.button("Manage Co-op Reviews", type="primary", use_container_width=True):
    st.switch_page("pages/28_coop_reviews.py")  # Link to the co-op reviews management page

# Button to view career projections
if st.button("View Career Projections", type="primary", use_container_width=True):
    st.switch_page("pages/29_career_projections.py")  # Link to the career projections page
