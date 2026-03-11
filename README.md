## 🚀 MVP Workflow – Talking Rabbitt

The MVP demonstrates the **"Magic Moment"** of conversational analytics, where a user can interact with business data using natural language.

### 🔄 Flow of the System

1. **Upload Data**  
   The user uploads a CSV dataset through the web interface built with Streamlit.

2. **Data Processing**  
   The uploaded CSV file is automatically converted into a **Pandas DataFrame (`df`)**.

3. **Ask a Question**  
   The user asks a natural language question about the dataset, for example:  
   *“Which region generated the highest revenue in Q1?”*

4. **LLM Interpretation**  
   The query is sent to an LLM powered by **Groq**, which converts the natural language question into executable **Pandas code**.

5. **Execute Analysis**  
   Python executes the generated Pandas code on the dataset.

6. **Generate Insights**  
   The system returns:
   - 📊 **Text Insight** – a clear explanation of the result  
   - 📈 **Automated Chart Visualization** – dynamically generated from the query

### ✨ Result

This workflow replaces a **10-minute manual Excel analysis** with a **5-second conversational query**, demonstrating the power of AI-driven business intelligence.

 <img width="929" height="792" alt="Screenshot 2026-03-11 at 6 44 39 PM" src="https://github.com/user-attachments/assets/84170f8d-bfbf-4c1e-9e2f-938674422e44" />
