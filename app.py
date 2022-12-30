"""App which summarizes terms & conditions"""

# Import from 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components

# Import modules
import scrape as scr
import oai

# Define functions
def summarize(text: str):
    """Summarize text."""
    summary_prompt = "\n\nThe above is the terms and conditions for an application. Tell me what company it is and very basic information about what is covered by the T&C. If anything is not covered that is usually covered, mention this. Aim for around 75 words. \n\n"
    child_safety_prompt = "\n\nThe above is the terms and conditions for an application. Tell me up to five things it says about children and age restrictions. Be very specific. Tell me things that do not exist in every company's terms & conditions policies. Format your answer in bullets ending in a period. Use this bullet • \n\n"
    data_privacy_prompt = "\n\nThe above is the terms and conditions for an application. Tell me up to five things it says about data privacy and how data is used by the company, including if it follows GDPR. Be very specific. Tell me things that do not exist in every company's terms & conditions policies. Format your answer in bullets ending in a period. Use this bullet •  \n\n"
    liabilities_prompt = "\n\nThe above is the terms and conditions for an application. Tell me up to five liabilities that a user faces when using the product. Format your answer in bullets ending in a period. Use this bullet • Tell me what is not covered by the terms and conditions. Mention anything about hacks, law enforcement when it comes to privacy, misuse of the platform, and more. Talk about responsibilities the user faces. Be very speific and tell me things that do not exist in every company's terms & conditions policies.  \n\n"
    extras_prompt = "\n\nThe above is the terms and conditions for an application. Tell me the three biggest takeaways that are of utmost important for all users to know. Be very specific. Format your answer in bullets ending in a period. Use this bullet • Focus on things that do not exist in all terms & conditions.  \n\n"

    openai = oai.Openai()
    flagged = openai.moderate(text)
    if flagged:
        st.session_state.error = "Input flagged as inappropriate."
        return
    st.session_state.error = ""
    st.session_state.summary = (
        openai.complete(prompt=text + summary_prompt)
    )
    st.session_state.child_safety = (
        openai.complete(prompt=text + child_safety_prompt)
    )
    st.session_state.data_privacy = (
        openai.complete(prompt=text + data_privacy_prompt)
    )
    st.session_state.liabilities = (
        openai.complete(prompt=text + liabilities_prompt)
    )
    st.session_state.extras = (
        openai.complete(prompt=text + extras_prompt)
    )


# Render streamlit page
st.set_page_config(page_title="T&C Simplified", page_icon="🤓")
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "error" not in st.session_state:
    st.session_state.error = ""

st.title("Simplify terms & conditions")
st.markdown(
    """This mini-app scrapes the text from a terms and conditions page, and summarizes them into the main points 
    anyone should know before using an application. It utilizes OpenAI's GPT-3 based [Davinci model](https://beta.openai.com/docs/models/overview). Find me on [Twitter](https://twitter.com/catmcgeecode).  
    This may take around a minute to run so please be patient!"""
)

url = st.text_input(label="Terms & Conditions URL")
if url:
        scraper = scr.Scraper()
        response = scraper.request_url(url)
        if "invalid" in str(response).lower():
            st.error(str(response))
        elif response.status_code != 200:
            st.error(f"Response status {response.status_code}")
        else:
            url_text = (
                scraper.extract_content(response)[:6000].strip().replace("\n", " ")
            )
            summarize(url_text)
            if st.session_state.summary:
                st.subheader("Summary")
                st.write(st.session_state.summary.strip().replace("•", "\n•"))
                st.subheader("Child safety")
                st.write(st.session_state.child_safety.strip().replace("•", "\n•"))
                st.subheader("Data privacy")
                st.markdown(st.session_state.data_privacy.strip().replace("•", "\n•"))
                st.subheader("User liabilities and responsibilities")
                st.write(st.session_state.liabilities.strip().replace("•", "\n•"))
                st.subheader("Important considerations that are not common in all T&Cs")
                st.write(st.session_state.extras.strip().replace("•", "\n•"))
               
            # Force responsive layout for columns also on mobile
                st.write(
                    """<style>
                    [data-testid="column"] {
                        width: calc(50% - 1rem);
                        flex: 1 1 calc(50% - 1rem);
                        min-width: calc(50% - 1rem);
                    }
                    </style>""",
                    unsafe_allow_html=True,
                )
                st.button(
                        label="Regenerate summary",
                        type="secondary",
                        on_click=summarize,
                        args=[url_text],
                    )

if st.session_state.error:
    st.error(st.session_state.error)