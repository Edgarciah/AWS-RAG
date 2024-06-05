import streamlit as st
from chatbot import answer_query

# Set the page configuration to adjust layout and set the title
st.set_page_config(page_title='LOKA PoC', layout='centered', page_icon=':robot_face:')

# Display the application header/title with a logo
logo_html = """
<div style='background-color:#ffffff;padding-bottom:20px;border-radius:0px;text-align:center'>
    <img src='https://assets-global.website-files.com/6490383845d4c0f51f929ca8/6491968bd08ddae77b4fb3d8_loka-logo-footer.svg' style='height:90px;width:250px;margin:0;'>
</div>
"""
st.markdown(logo_html, unsafe_allow_html=True)

# Initialize session state for storing messages if not already set
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages stored in the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if a question has been input by the user
if question := st.chat_input("Ask a question..."):
    # Display the user's question with a user icon
    with st.chat_message("user"):
        st.markdown(question)
    
    # Add the user's question to the session state
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Generate and display the assistant's response
    with st.chat_message("assistant"):
        # Placeholder for the assistant's response
        message_placeholder = st.empty()
        
        # Display a status message while processing the query
        with st.status("Analyzing context...", expanded=False) as status:
            # Get the answer to the user's question
            answer = answer_query(question)
            # Display the answer in the placeholder
            message_placeholder.markdown(f"{answer}")
        
    # Add the assistant's response to the session state
    st.session_state.messages.append({"role": "assistant", "content": answer})
