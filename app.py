import streamlit as st
import ollama
import sys,subprocess

os = sys.platform
if os == "win32":
    subprocess.run("powershell -ExecutionPolicy Bypass -File ./preload.ps1", shell=True, check=True)
    subprocess.run("./preload.ps1", shell=True, check=True)
elif os == "linux":
    subprocess.run("chmod +x ./preload.sh", shell=True, check=True)
    subprocess.run("./preload.sh", shell=True, check=True)
elif os == "darwin":
    subprocess.run("chmod +x ./preload.sh", shell=True, check=True)
    subprocess.run("./preload.sh", shell=True, check=True)
else:
    print("Unsupported OS")
    sys.exit(1)

st.title("StreamLlama")
st.markdown("### A Streamlit app for Ollama")
# init chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# init models
if "model" not in st.session_state:
    st.session_state["model"] = ""
try:
    models = [model["name"] for model in ollama.list()["models"]]
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# Model selection
st.session_state["model"] = st.selectbox("Choose your model", models)

#Sidebar
with st.sidebar:
    st.write("### Reset Chat history")
    if st.button("Reset chat"):
        st.session_state["messages"] = []

# Stream chat messages
def model_res_generator():
    stream = ollama.chat(
        model=st.session_state["model"],
        messages=st.session_state["messages"],
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
if prompt := st.chat_input("Enter prompt here.."):
        # add latest message to history in format {role, content}
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_res_generator())
        st.session_state["messages"].append({"role": "assistant", "content": message})

