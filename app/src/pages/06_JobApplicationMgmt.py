import streamlit as st
import requests

st.title("Application Management")

# Section: View Applications
st.header("View Applications")
if st.button("Fetch Applications"):
    if st.session_state.get('authenticated') and st.session_state.get('first_name') == 'Peter':
        response = requests.get(f"http://web-api:4000/ns/applications")
        if response.status_code == 200:
            try:
                data = response.json()
                st.json(data)
            except ValueError:  # Catch JSONDecodeError
                st.warning("No data found for this student.")
        else:
            st.error(f"Failed to fetch applications. Status code: {response.status_code}")


# Section: Withdraw Application
st.header("Withdraw Application")
application_id_withdraw = st.text_input("Enter Application ID to Withdraw", key="application_id_withdraw")
if st.button("Withdraw Application"):
    if application_id_withdraw:
        response = requests.delete(f"http://web-api:4000/applications/{application_id_withdraw}/withdraw")
        if response.status_code == 200:
            st.success("Application withdrawn successfully!")
        else:
            st.error("Failed to withdraw application.")
    else:
        st.warning("Please enter an Application ID.")

# Section: Update Application
st.header("Update Application")
application_id_update = st.text_input("Enter Application ID to Update", key="application_id_update")
status = st.selectbox("Status", ["Applied", "Interested", "Rejected"], key="apply_status")
update_resume_id = st.text_input("Resume ID (Optional)", key="update_resume_id")
if st.button("Update Application"):
    if application_id_update:
        payload = {
            "status": status,
            "resume_id": update_resume_id
        }
        update_response = requests.put(f"http://web-api:4000/applications/{application_id_update}", json=payload)
        if update_response.status_code == 200:
            st.success("Application updated successfully!")
        else:
            st.error("Failed to update application.")
    else:
        st.warning("Please enter an Application ID.")