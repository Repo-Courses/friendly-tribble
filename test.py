import time
import streamlit as st
import requests

@st.cache(allow_output_mutation=True)
def get_cached_token_data():
    return {"access_token": "", "expiry_time": 0}

def get_access_token(client_id, client_secret):
    token_data = get_cached_token_data()
    
    current_time = time.time()
    if current_time < token_data["expiry_time"]:
        return token_data["access_token"]

    url = "https://auth.emsicloud.com/connect/token"
    payload = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&scope=emsi_open"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)

    if response.ok:
        token_info = response.json()
        token_data["access_token"] = token_info.get("access_token", "")
        # Set the expiry time to be the current time plus the expires_in duration minus a small buffer (e.g., 300 seconds)
        token_data["expiry_time"] = current_time + token_info.get("expires_in", 3600) - 300
        return token_data["access_token"]
    else:
        st.error("Failed to retrieve access token. Please check your credentials.")
        return ""

def extract_skills_from_document(access_token, document_text):
    url = 'https://emsiservices.com/skills/versions/latest/extract'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {"text": document_text}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extract_skill_names(api_response):
    skill_names = []
    if 'data' in api_response:
        for skill in api_response['data']:
            if 'skill' in skill and 'name' in skill['skill']:
                skill_names.append(skill['skill']['name'])
    return skill_names

def find_matching_skills(jd_skills, cv_skills):
    return set(jd_skills) & set(cv_skills)

def calculate_match_rate(cv_skills, jd_skills):
    total_skills = len(jd_skills)
    matched_skills = len(set(cv_skills) & set(jd_skills))
    return (matched_skills / total_skills) * 100 if total_skills > 0 else 0

def main():
    st.title("Skill Extractor App")

    # Retrieve access token
    client_id = "yvy2i5xt5dloz8v2"  # Your client ID
    client_secret = "iJbuwPyI"  # Your client secret
    access_token = get_access_token(client_id, client_secret)

    if access_token:
        # Text area for job description and CV input
        jd_text = st.text_area("Paste your job description here:", height=150)
        cv_text = st.text_area("Paste your CV here:", height=300)

        # Button to extract skills
        if st.button("Extract Skills"):
            # Extract skills from job description
            jd_skills_response = extract_skills_from_document(access_token, jd_text)
            jd_skill_names = extract_skill_names(jd_skills_response)

            # Extract skills from CV
            cv_skills_response = extract_skills_from_document(access_token, cv_text)
            cv_skill_names = extract_skill_names(cv_skills_response)

            # Display the extracted skills
            st.subheader("Skills Extracted from Job Description:")
            st.write(jd_skill_names)

            st.subheader("Skills Extracted from CV:")
            st.write(cv_skill_names)

            # Find and display matching skills
            matching_skills = find_matching_skills(jd_skill_names, cv_skill_names)
            st.subheader("CV Skills Matching with Job Description:")
            for skill in matching_skills:
                st.write(skill)

            # Calculate and display match rate
            match_rate = calculate_match_rate(cv_skill_names, jd_skill_names)
            st.subheader(f"Match Rate: {match_rate:.2f}%")

if __name__ == "__main__":
    main()
