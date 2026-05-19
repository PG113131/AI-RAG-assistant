import streamlit as st
from datetime import datetime

from ingest import save_memory
from rag_pipeline import retriever, llm
from database import cursor

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Memory Diary",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: #0f172a;
    color: white;
}

/* Headings */
h1, h2, h3 {
    color: #38bdf8 !important;
    font-weight: 800 !important;
}

/* Labels */
label, p, span, div {
    color:#38bdf8  !important;
    font-weight: 700 !important;
}

/* Input text */
input, textarea {
    color: white !important;
    font-weight: 700 !important;
    background-color: #1e293b !important;
}

/* Text input boxes */
.stTextInput input {
    color: white !important;
    font-weight: bold !important;
    background-color: #1e293b !important;
}

/* Text area */
.stTextArea textarea {
    color: white !important;
    font-weight: bold !important;
    background-color: #1e293b !important;
}

/* Streamlit Button */
.stButton > button {
    background-color: black !important;
    color: white !important;

    font-weight: 700 !important;
    font-size: 16px !important;

    border: none !important;
    border-radius: 10px !important;

    padding: 10px 20px !important;

    transition: all 0.2s ease !important;

    opacity: 1 !important;
}

/* Hover State */
.stButton > button:hover {
    background-color: black !important;
    color: white !important;

    opacity: 1 !important;

    border: none !important;
}

/* Focus State */
.stButton > button:focus {
    background-color: black !important;
    color: white !important;

    outline: none !important;
    box-shadow: none !important;

    opacity: 1 !important;
}

/* Active State */
.stButton > button:active {
    background-color: black !important;
    color: white !important;

    opacity: 1 !important;
}

/* Memory cards */
.memory-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    color: white;
    font-weight: bold;
    border: 1px solid #334155;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("AI Memory Diary")

page = st.sidebar.radio(
    "Navigation",
    [
        "Add Memory",
        "Saved Memories",
        "Ask AI"
    ]
)

# ==========================================
# ADD MEMORY
# ==========================================

if page == "Add Memory":

    st.title("Add Memory")

    title = st.text_input("Memory Title")

    content = st.text_area(
        "Write your memory",
        height=250
    )

    if st.button("Save Memory"):

        if title and content:

            save_memory(title, content)

            st.success("Memory Saved Successfully")

        else:
            st.warning("Please fill all fields")

# ==========================================
# SAVED MEMORIES
# ==========================================

elif page == "Saved Memories":

    st.title("Saved Memories")

    # -----------------------------
    # SEARCH SECTION
    # -----------------------------

    search_text = st.text_input(
        "Search memories"
    )

    search_date = st.date_input(
        "Filter by Date",
        value=None
    )

    # -----------------------------
    # SQL QUERY
    # -----------------------------

    query = """
    SELECT id, title, content, created_at
    FROM memories
    WHERE 1=1
    """

    params = []

    # Search by text
    if search_text:

        query += """
        AND (
            title LIKE ?
            OR content LIKE ?
        )
        """

        params.append(f"%{search_text}%")
        params.append(f"%{search_text}%")

    # Search by date
    if search_date:

        formatted_date = search_date.strftime("%Y-%m-%d")

        query += """
        AND DATE(created_at) = ?
        """

        params.append(formatted_date)

    query += """
    ORDER BY created_at DESC
    """

    cursor.execute(query, params)

    rows = cursor.fetchall()

    # -----------------------------
    # DISPLAY MEMORIES
    # -----------------------------

    if rows:

        for row in rows:

            st.markdown(
                f"""
                <div class="memory-card">

                <h3>{row[1]}</h3>

                <p>{row[2]}</p>

                <small>
                Created At: {row[3]}
                </small>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No memories found")

# ==========================================
# ASK AI
# ==========================================

elif page == "Ask AI":

    st.title("Ask AI About Your Memories")

    query = st.text_input(
        "Ask a question"
    )

    if st.button("Ask AI"):

        if query:

            # Retrieve docs
            docs = retriever.invoke(query)

            # Build context
            context = "\n\n".join(
                [doc.page_content for doc in docs]
            )

            # Prompt
            prompt = f"""
You are an AI memory assistant.

Answer ONLY from the provided context.

If answer is not found,
say:
"I could not find relevant memory."

Context:
{context}

Question:
{query}
"""

            # Generate response
            response = llm.invoke(prompt)

            # Show answer
            st.subheader("Answer")

            st.write(response.content)

        else:
            st.warning("Please enter a question")