"""
Talking Rabbitt – Conversational AI for Business Data
A minimal MVP that allows users to upload CSV files and ask questions in natural language.
"""

import streamlit as st
import pandas as pd
import groq
import os
import matplotlib.pyplot as plt

# Configure page
st.set_page_config(
    page_title="Talking Rabbitt – Conversational AI for Business Data",
    page_icon="🐰",
    layout="centered"
)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'answer' not in st.session_state:
    st.session_state.answer = None
if 'chart' not in st.session_state:
    st.session_state.chart = None
if 'pandas_code' not in st.session_state:
    st.session_state.pandas_code = None
if 'pandas_result' not in st.session_state:
    st.session_state.pandas_result = None


def get_groq_client():
    """Initialize Groq client with API key from environment variable or user input."""
    # First, try to read from environment variable GROQ_API_KEY
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Fallback to user input in session state
    if not api_key:
        api_key = st.session_state.get("groq_api_key", "")
    
    if api_key:
        return groq.Groq(api_key=api_key)
    return None


def generate_pandas_query(user_question, df_columns):
    """
    Generate pandas code using Groq LLM to analyze the dataframe.
    
    Args:
        user_question: The natural language question from the user
        df_columns: List of column names in the dataframe
    
    Returns:
        str: Generated pandas code
    """
    client = get_groq_client()
    if client is None:
        return None
    
    prompt = f"""You are a data analyst. Convert the user's question into pandas code using a dataframe called df.

DataFrame columns: {df_columns}

User Question: {user_question}

Instructions:
1. Generate pandas code to answer the question
2. The dataframe is named 'df' in the code
3. Store the result in a variable called 'result'
4. Return ONLY the pandas code, nothing else

Example:
If user asks "What is the total revenue by region?"
Return: result = df.groupby('Region')['Revenue'].sum()
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
        # Extract pandas code from response
        pandas_code = None
        lines = response_text.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                code_lines.append(line.strip())
        
        # If no code block, try to get the whole response
        if not code_lines:
            code_lines = [line.strip() for line in lines if line.strip() and not line.startswith('You are') and not line.startswith('DataFrame') and not line.startswith('User Question') and not line.startswith('Instructions')]
        
        if code_lines:
            pandas_code = '\n'.join(code_lines)
        
        return pandas_code
        
    except Exception as e:
        return f"Error generating code: {str(e)}"


def execute_pandas_code(pandas_code, df):
    """
    Safely execute generated pandas code and return the result.
    
    Returns:
        DataFrame or Series: The result of executing the pandas code
    """
    if not pandas_code:
        return None
    
    try:
        # Create a local namespace with df available
        local_namespace = {'df': df.copy(), 'pd': pd}
        
        # Execute the code
        exec(pandas_code, globals(), local_namespace)
        
        # Get the result - look for common variable names.
        # Avoid using boolean operators like "or" with pandas objects,
        # as they raise "The truth value of a Series is ambiguous".
        result = local_namespace.get('result')
        if result is None:
            result = local_namespace.get('agg_result')
        if result is None:
            result = local_namespace.get('summary')
        
        if result is None:
            return None
        
        # Return the result (could be Series, DataFrame, or scalar)
        return result
        
    except Exception as e:
        # Return error message as string so it can be displayed
        return f"Error executing code: {str(e)}"


def create_chart(chart_type, result):
    """Create matplotlib chart based on chart type and result."""
    if result is None:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    try:
        # Convert Series to DataFrame if needed for plotting
        plot_data = result
        if isinstance(result, pd.Series):
            plot_data = result.to_frame()
        
        if chart_type == "bar":
            if isinstance(result, pd.Series):
                result.plot(kind='bar', ax=ax, color='steelblue')
            else:
                result.plot(kind='bar', ax=ax, color='steelblue')
        elif chart_type == "line":
            if isinstance(result, pd.Series):
                result.plot(kind='line', ax=ax, color='steelblue', marker='o')
            else:
                result.plot(kind='line', ax=ax, color='steelblue', marker='o')
        elif chart_type == "pie":
            if isinstance(result, pd.Series):
                result.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
            else:
                result.iloc[:, 0].plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
        elif chart_type == "scatter":
            result.plot(kind='scatter', ax=ax, color='steelblue')
        else:
            ax.text(0.5, 0.5, 'Unsupported chart type', ha='center', va='center')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig
    except Exception as e:
        # Fallback: create a simple bar chart from the result
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            if isinstance(result, pd.Series):
                result.plot(kind='bar', ax=ax, color='steelblue')
            elif isinstance(result, pd.DataFrame):
                result.plot(kind='bar', ax=ax, color='steelblue')
            else:
                ax.bar(range(len(result)), result.values if hasattr(result, 'values') else list(result))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            return fig
        except:
            return None


def main():
    """Main application function."""
    # Header
    st.title("🐰 Talking Rabbitt")
    st.markdown("### Conversational AI for Business Data")
    st.markdown("Upload a CSV file and ask questions about your data in natural language!")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("Groq API Key", type="password", help="Get your free API key from https://console.groq.com/")
        if api_key:
            st.session_state.groq_api_key = api_key
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Ask clear questions about your data
        - Request charts explicitly (e.g., "Show me a bar chart...")
        - Questions are answered based on the uploaded data
        """)
    
    # File uploader
    uploaded_file = st.file_uploader("📁 Upload your CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(f"✅ Successfully loaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error loading CSV: {str(e)}")
    
    # Display dataframe preview (first 5 rows)
    if st.session_state.df is not None:
        df = st.session_state.df
        
        st.markdown("---")
        st.subheader("📊 Data Preview")
        st.dataframe(df.head(5))
        st.caption(f"Showing first 5 rows of {len(df)} total rows")
        
        # Question input section
        st.markdown("---")
        st.subheader("💬 Ask a Question")
        
        # Text input for question
        question = st.text_input(
            "Enter your question about the data:",
            placeholder="e.g., What is the total revenue? Show me a bar chart of sales by category."
        )
        
        # Ask Rabbitt button
        if st.button("🐰 Ask Rabbitt", type="primary"):
            if question.strip():
                # Check if API key is available
                client = get_groq_client()
                if client is None:
                    st.error("⚠️ Please enter your Groq API key in the sidebar to continue!")
                else:
                    # Initialize variables
                    pandas_code = None
                    pandas_result = None
                    text_summary = None
                    chart = None
                    
                    # Generate pandas code using Groq
                    df_columns = list(df.columns)
                    with st.spinner("🤔 Analyzing your question..."):
                        pandas_code = generate_pandas_query(question, df_columns)
                    
                    # Execute the generated pandas code
                    if pandas_code and not pandas_code.startswith("Error"):
                        with st.spinner("📊 Running analysis..."):
                            pandas_result = execute_pandas_code(pandas_code, df)
                        
                        # Generate text summary using LLM (only if result is valid)
                        if pandas_result is not None and not isinstance(pandas_result, str):
                            try:
                                summary_prompt = f"""Based on the following pandas analysis result, provide a clear text answer to this question: "{question}"

Result:
{pandas_result.to_string() if hasattr(pandas_result, 'to_string') else str(pandas_result)}

Provide a concise, human-readable answer:"""
                                summary_response = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": summary_prompt}],
                                    temperature=0.3,
                                    max_tokens=300
                                )
                                text_summary = summary_response.choices[0].message.content
                            except Exception as e:
                                text_summary = None
                        
                        # ALWAYS generate a chart for visualization (only if result is valid DataFrame/Series)
                        if pandas_result is not None and isinstance(pandas_result, (pd.DataFrame, pd.Series)):
                            # Check if user explicitly wants a specific chart
                            user_wants_chart = 'bar' in question.lower() or 'chart' in question.lower() or 'graph' in question.lower() or 'plot' in question.lower()
                            
                            # Check for time-based data
                            time_keywords = ['quarter', 'year', 'date', 'month', 'time', 'day', 'week']
                            has_time_data = any(keyword in question.lower() for keyword in time_keywords)
                            
                            # Check if result is grouped/aggregated data
                            is_grouped = isinstance(pandas_result, (pd.DataFrame, pd.Series)) and hasattr(pandas_result, 'index')
                            
                            # Auto-detect or use explicit chart type - ALWAYS show a chart
                            if user_wants_chart:
                                if 'line' in question.lower():
                                    chart = create_chart('line', pandas_result)
                                elif 'pie' in question.lower():
                                    chart = create_chart('pie', pandas_result)
                                elif 'scatter' in question.lower():
                                    chart = create_chart('scatter', pandas_result)
                                else:
                                    chart = create_chart('bar', pandas_result)
                            elif is_grouped:
                                # Auto-detect chart type based on data
                                if has_time_data:
                                    chart = create_chart('line', pandas_result)
                                else:
                                    chart = create_chart('bar', pandas_result)
                            else:
                                # Try bar chart as default for any result
                                chart = create_chart('bar', pandas_result)
                    
                    # Store results in session state
                    st.session_state.pandas_code = pandas_code
                    st.session_state.pandas_result = pandas_result
                    st.session_state.text_summary = text_summary
                    st.session_state.chart = chart
                    st.session_state.answer = "Analysis completed successfully!"
            else:
                st.warning("Please enter a question!")
    
    # Display answer and chart
    if st.session_state.answer:
        st.markdown("---")
        st.subheader("🎯 Answer")
        
        # Always show the answer text
        st.markdown(st.session_state.answer)
        
        # Display executed pandas code if available
        if st.session_state.get('pandas_code'):
            st.markdown("---")
            st.subheader("🐍 Generated Pandas Code")
            st.code(st.session_state.pandas_code, language="python")
        
        # Display pandas execution result if available
        if st.session_state.get('pandas_result') is not None:
            st.markdown("---")
            st.subheader("📊 Analysis Result")
            result = st.session_state.pandas_result
            if isinstance(result, str):
                # This is an error message
                st.error(result)
            elif isinstance(result, (pd.DataFrame, pd.Series)):
                st.dataframe(result)
            else:
                st.write(result)
        
        # Always show chart section if chart exists
        if st.session_state.chart:
            st.markdown("---")
            st.subheader("📈 Visualization")
            st.pyplot(st.session_state.chart)
        else:
            st.markdown("*No chart available for this query*")

    else:
        # Show welcome message when no data is loaded
        st.info("👆 Please upload a CSV file to get started!")
        
        # Show example questions
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        - What is the total [column name]?
        - Show me a bar chart of [column] by [column]
        - What are the top 5 [items] by [metric]?
        - What is the average [value] per [category]?
        """)


if __name__ == "__main__":
    main()

