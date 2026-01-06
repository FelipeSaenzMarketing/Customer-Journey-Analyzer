import streamlit as st
import pandas as pd
import plotly.express as px
from sentence_transformers import SentenceTransformer, util
import io
from typing import Dict, List, Tuple
import numpy as np

st.set_page_config(
    page_title="Semantic Journey Analyzer",
    page_layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

JOURNEY_ARCHETYPES = {
    "Awareness": "educational guide tutorial definition what is learn problem context help info",
    "Consideration": "best top reviews comparison vs versus pros cons evaluate features alternatives",
    "Purchase": "buy price pricing cost subscription quote cart checkout order demo",
    "Loyalty": "login support documentation help center api manual changelog status"
}

STAGE_COLORS = {
    "Awareness": "#1f77b4",
    "Consideration": "#ff7f0e", 
    "Purchase": "#2ca02c",
    "Loyalty": "#d62728",
    "Insufficient Data": "#7f7f7f"
}

def calculate_journey_stage(text: str, model: SentenceTransformer, archetype_embeddings: Dict) -> Tuple[str, Dict[str, float]]:
    if not text or text.strip() == "":
        return "Insufficient Data", {stage: 0.0 for stage in JOURNEY_ARCHETYPES.keys()}
    
    try:
        text_embedding = model.encode(text, convert_to_tensor=True)
        
        scores = {}
        for stage, embedding in archetype_embeddings.items():
            similarity = util.pytorch_cos_sim(text_embedding, embedding).item()
            scores[stage] = round(similarity, 4)
        
        assigned_stage = max(scores, key=scores.get)
        return assigned_stage, scores
    
    except Exception as e:
        st.warning(f"Error processing text: {str(e)}")
        return "Insufficient Data", {stage: 0.0 for stage in JOURNEY_ARCHETYPES.keys()}

def process_dataframe(df: pd.DataFrame, model: SentenceTransformer, archetype_embeddings: Dict) -> pd.DataFrame:
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_rows = len(df)
    
    for idx, row in df.iterrows():
        url = row.get('URL', f"Row_{idx+1}")
        text = str(row.get('Text', ''))
        
        stage, scores = calculate_journey_stage(text, model, archetype_embeddings)
        
        result = {
            'URL': url,
            'Text_Preview': text[:100] + '...' if len(text) > 100 else text,
            'Journey_Stage': stage,
            'Max_Confidence': max(scores.values()),
            'Score_Awareness': scores['Awareness'],
            'Score_Consideration': scores['Consideration'],
            'Score_Purchase': scores['Purchase'],
            'Score_Loyalty': scores['Loyalty']
        }
        results.append(result)
        
        progress_bar.progress((idx + 1) / total_rows)
        status_text.text(f"Processing: {idx + 1}/{total_rows} URLs")
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def process_manual_text(text_input: str, model: SentenceTransformer, archetype_embeddings: Dict) -> pd.DataFrame:
    lines = [line.strip() for line in text_input.split('\n') if line.strip()]
    
    results = []
    for idx, line in enumerate(lines, 1):
        stage, scores = calculate_journey_stage(line, model, archetype_embeddings)
        
        result = {
            'Line_Number': idx,
            'Text_Preview': line[:100] + '...' if len(line) > 100 else line,
            'Journey_Stage': stage,
            'Max_Confidence': max(scores.values()),
            'Score_Awareness': scores['Awareness'],
            'Score_Consideration': scores['Consideration'],
            'Score_Purchase': scores['Purchase'],
            'Score_Loyalty': scores['Loyalty']
        }
        results.append(result)
    
    return pd.DataFrame(results)

def create_distribution_chart(df: pd.DataFrame) -> None:
    stage_counts = df['Journey_Stage'].value_counts().reset_index()
    stage_counts.columns = ['Journey_Stage', 'Count']
    
    fig = px.bar(
        stage_counts,
        x='Journey_Stage',
        y='Count',
        color='Journey_Stage',
        color_discrete_map=STAGE_COLORS,
        title="Distribution of Content Across Customer Journey Stages",
        labels={'Journey_Stage': 'Customer Journey Stage', 'Count': 'Number of URLs'}
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Customer Journey Stage",
        yaxis_title="Count",
        template="plotly_white",
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_confidence_chart(df: pd.DataFrame) -> None:
    df_plot = df.copy()
    df_plot['Index'] = range(1, len(df_plot) + 1)
    
    hover_data_col = 'URL' if 'URL' in df.columns else 'Line_Number'
    
    fig = px.scatter(
        df_plot,
        x='Index',
        y='Max_Confidence',
        color='Journey_Stage',
        color_discrete_map=STAGE_COLORS,
        hover_data=[hover_data_col, 'Max_Confidence'],
        title="Confidence Score Analysis by Content",
        labels={
            'Index': 'Content Index',
            'Max_Confidence': 'Confidence Score',
            'Journey_Stage': 'Stage'
        }
    )
    
    fig.update_layout(
        template="plotly_white",
        height=450,
        xaxis_title="Content Index",
        yaxis_title="Confidence Score"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Journey Analysis')
        
        worksheet = writer.sheets['Journey Analysis']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return output.getvalue()

def main():
    st.title("Semantic Journey Analyzer")
    st.markdown("Classify content into customer journey phases using semantic embeddings")
    
    try:
        model = load_model()
        
        archetype_embeddings = {}
        for stage, text in JOURNEY_ARCHETYPES.items():
            archetype_embeddings[stage] = model.encode(text, convert_to_tensor=True)
        
        with st.sidebar:
            st.header("Data Input")
            
            uploaded_file = st.file_uploader(
                "Upload Dataset",
                type=['csv', 'xlsx'],
                help="Upload a CSV or Excel file with 'URL' and 'Text' columns"
            )
            
            st.markdown("---")
            st.subheader("Journey Stages")
            st.markdown("""
            - **Awareness**: Educational content
            - **Consideration**: Comparisons, reviews
            - **Purchase**: Pricing, buying options
            - **Loyalty**: Support, documentation
            """)
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                if 'URL' not in df.columns or 'Text' not in df.columns:
                    st.error("Dataset must contain 'URL' and 'Text' columns")
                    
                    st.subheader("Column Mapping")
                    st.write("Available columns:", list(df.columns))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        url_col = st.selectbox("Select URL column:", df.columns)
                    with col2:
                        text_col = st.selectbox("Select Text column:", df.columns)
                    
                    if st.button("Apply Mapping"):
                        df = df.rename(columns={url_col: 'URL', text_col: 'Text'})
                        st.success("Columns mapped successfully")
                        st.rerun()
                else:
                    st.success(f"File uploaded successfully: {len(df)} rows")
                    
                    if st.button("Analyze Dataset", type="primary"):
                        with st.spinner("Analyzing content..."):
                            results_df = process_dataframe(df, model, archetype_embeddings)
                        
                        st.success("Analysis complete")
                        
                        st.subheader("Results Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total URLs", len(results_df))
                        with col2:
                            awareness_count = len(results_df[results_df['Journey_Stage'] == 'Awareness'])
                            st.metric("Awareness", awareness_count)
                        with col3:
                            consideration_count = len(results_df[results_df['Journey_Stage'] == 'Consideration'])
                            st.metric("Consideration", consideration_count)
                        with col4:
                            purchase_count = len(results_df[results_df['Journey_Stage'] == 'Purchase'])
                            st.metric("Purchase", purchase_count)
                        
                        st.subheader("Visual Analysis")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            create_distribution_chart(results_df)
                        
                        with col2:
                            create_confidence_chart(results_df)
                        
                        st.subheader("Detailed Results")
                        st.dataframe(
                            results_df,
                            use_container_width=True,
                            height=400
                        )
                        
                        st.subheader("Download Results")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv_data = convert_df_to_csv(results_df)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="semantic_journey_analysis.csv",
                                mime="text/csv"
                            )
                        
                        with col2:
                            excel_data = convert_df_to_excel(results_df)
                            st.download_button(
                                label="Download Excel",
                                data=excel_data,
                                file_name="semantic_journey_analysis.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        else:
            st.info("Upload a dataset in the sidebar or use the quick analysis below")
            
            st.subheader("Quick Text Analysis")
            text_input = st.text_area(
                "Paste Text for Quick Analysis",
                height=200,
                placeholder="Enter text content, one entry per line...",
                help="Enter multiple lines of text. Each line will be analyzed separately."
            )
            
            if st.button("Analyze Text", type="primary") and text_input:
                with st.spinner("Analyzing text..."):
                    results_df = process_manual_text(text_input, model, archetype_embeddings)
                
                st.success("Analysis complete")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    create_distribution_chart(results_df)
                
                with col2:
                    create_confidence_chart(results_df)
                
                st.subheader("Detailed Results")
                st.dataframe(results_df, use_container_width=True)
                
                st.subheader("Download Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = convert_df_to_csv(results_df)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="semantic_journey_analysis.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    excel_data = convert_df_to_excel(results_df)
                    st.download_button(
                        label="Download Excel",
                        data=excel_data,
                        file_name="semantic_journey_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page and try again")

if __name__ == "__main__":
    main()