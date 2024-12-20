import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks  # Custom navigation component (if used)
import requests


st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Welcome Mary! What would you like to do?")

# Button to view and manage availability
if st.button("View and Manage Coffee Chat Availability", 
             type="primary", 
             use_container_width=True):
    st.switch_page("pages/27_availability.py")  # Link to the availability management page

# Button to view and update co-op reviews
if st.button("View and Manage Co-op Reviews", 
             type="primary", 
             use_container_width=True):
    st.switch_page("pages/28_coop_reviews.py")  # Link to the co-op reviews management page

# Button to view career projections
if st.button("View Options for the Future", 
             type="primary", 
             use_container_width=True):
    st.switch_page("pages/29_career_projections.py")  # Link to the career projections page


