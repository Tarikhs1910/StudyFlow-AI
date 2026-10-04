def set_background(image_path):

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        /* Full page background */
        .stApp {{
            background-image:
                linear-gradient(
                    rgba(255, 255, 255, 0.20),
                    rgba(255, 255, 255, 0.20)
                ),
                url("data:image/jpeg;base64,{encoded_image}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        /* Remove the large white box */
        .block-container {{
            background: transparent !important;
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.75) !important;
        }}

        /* Input sections */
        .stTextInput,
        .stSelectbox,
        .stDateInput,
        .stTimeInput,
        .stFileUploader {{
            background: rgba(255, 255, 255, 0.70);
            border-radius: 12px;
        }}

        /* Make normal text clearly visible */
        .stApp p,
        .stApp label,
        .stApp span,
        .stApp div {{
            color: #222222 !important;
        }}

        /* Headings */
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4 {{
            color: #111111 !important;
        }}

        /* Buttons */
        .stButton button {{
            color: #111111 !important;
        }}

        /* Text input */
        .stTextInput input,
        .stTextArea textarea {{
            color: #222222 !important;
            background-color: rgba(255, 255, 255, 0.85) !important;
        }}

        /* Select boxes */
        .stSelectbox div[data-baseweb="select"] {{
            color: #222222 !important;
            background-color: rgba(255, 255, 255, 0.85) !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )