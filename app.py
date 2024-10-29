import streamlit as st
import google.generativeai as genai
import re

# Configure page
st.set_page_config(page_title="Migliora il tuo testo prima di inviarlo!", layout="wide")

# Function to load system prompt from file
def load_system_prompt():
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read().strip()
            if not system_prompt:
                st.warning("prompt.txt is empty. Using default system prompt.")
                return "Please improve the following text and explain your improvements. Put the improved text between <improved_text> tags and the explanation between <explanation> tags."
            return system_prompt
    except FileNotFoundError:
        st.warning("prompt.txt not found. Using default system prompt.")
        return "Please improve the following text and explain your improvements. Put the improved text between <improved_text> tags and the explanation between <explanation> tags."

# Function to extract content between tags
def extract_tagged_content(text):
    improved_text = ""
    explanation = ""
    
    # Extract improved text
    improved_match = re.search(r'<improved_text>(.*?)</improved_text>', text, re.DOTALL)
    if improved_match:
        improved_text = improved_match.group(1).strip()
    
    # Extract explanation
    explanation_match = re.search(r'<explanation>(.*?)</explanation>', text, re.DOTALL)
    if explanation_match:
        explanation = explanation_match.group(1).strip()
    
    return improved_text, explanation

# Initialize Gemini AI
def initialize_gemini(api_key, system_prompt):
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-002",
            generation_config=generation_config,
            system_instruction=system_prompt,
            safety_settings="BLOCK_NONE"
        )
        
        return model.start_chat(history=[])
    except Exception as e:
        st.error(f"Errore di inizializzazione di gemini: {str(e)}")
        return None

# Display system prompt in sidebar
def show_system_prompt(system_prompt):
    with st.sidebar:
        st.subheader("System Prompt attuale")
        with st.expander("Mostra il prompt"):
            st.code(system_prompt, language="text")

# Main app
def main():
    st.title("Migliora il tuo testo in italiano")
    
    # Load system prompt at startup
    system_prompt = load_system_prompt()
    
    # Create a sidebar for API key input and system prompt display
    with st.sidebar:
        st.header("Configuration")
        # Use text_input with type="password" for the API key
        api_key = st.text_input(
            "inserisci la tua Google Gemini API Key",
            type="password",
            help="Ottieni la tua chiave da Google AI Studio"
        )
        
        # Add a link to get API key
        st.markdown("""
        [Ottieni la chiave da qua](https://makersuite.google.com/app/apikey)
        """)
        
        # Display current system prompt
        show_system_prompt(system_prompt)
    
    # Only show the main interface if API key is provided
    if not api_key:
        st.warning("Inserisci la tua chiave API di google gen ia prima di iniziare")
        return
    
    # Initialize or reinitialize chat session when API key changes
    if ('current_api_key' not in st.session_state or 
        st.session_state.current_api_key != api_key or 
        'system_prompt' not in st.session_state or 
        st.session_state.system_prompt != system_prompt):
        
        st.session_state.chat_session = initialize_gemini(api_key, system_prompt)
        st.session_state.current_api_key = api_key
        st.session_state.system_prompt = system_prompt
    
    # Text input
    user_input = st.text_area("Inserisci il testo da migliorare", height=200)
    
    if st.button("Non facciamo brutta figura!"):
        if st.session_state.chat_session and user_input:
            try:
                # Show a spinner while processing
                with st.spinner("Claudio giunta sta migliorando questo obbrobrio"):
                    # Send just the user input since system prompt is already configured
                    response = st.session_state.chat_session.send_message(user_input)
                    
                    # Extract improved text and explanation
                    improved_text, explanation = extract_tagged_content(response.text)
                    
                    # Display results
                    if improved_text:
                        st.subheader("Testo migliorato")
                        st.write(improved_text)
                    
                    if explanation:
                        with st.expander("Mostra in cosa devi migliorare"):
                            st.write(explanation)
                    
                    if not improved_text and not explanation:
                        st.warning("Non sono stati trovati i tag adatti, verra mostrato il testo nativo")
                        st.write(response.text)
                        
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
        else:
            st.error("Inserisci un testo e controlla che la API sia valida")

if __name__ == "__main__":
    main()