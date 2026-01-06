# Semantic Journey Analyzer

A Streamlit application that classifies content into customer journey stages using semantic embeddings and NLP.

## Features

- **Semantic Classification**: Uses sentence transformers to analyze content semantically
- **Customer Journey Stages**: Classifies content into Awareness, Consideration, Purchase, and Loyalty stages
- **File Upload**: Supports CSV and Excel file uploads
- **Quick Text Analysis**: Analyze text directly without file uploads
- **Visual Analytics**: Interactive charts showing distribution and confidence scores
- **Export Results**: Download results as CSV or Excel

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/semantic-journey-analyzer.git
cd semantic-journey-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Upload Dataset

1. Prepare a CSV or Excel file with two columns:
   - `URL`: Identifier for each content piece
   - `Text`: The content text to analyze

2. Upload the file using the sidebar file uploader

3. Click "Analyze Dataset" to process

4. View results, charts, and download the analysis

### Quick Text Analysis

1. Paste text directly into the text area (one entry per line)
2. Click "Analyze Text"
3. View results and download

## Input Format

Your dataset should have the following structure:

| URL | Text |
|-----|------|
| /product-guide | Learn how to use our platform effectively... |
| /pricing | Compare our pricing plans and features... |
| /reviews | See what customers say about us... |

## Journey Stages

- **Awareness**: Educational content, guides, tutorials
- **Consideration**: Comparisons, reviews, feature evaluations
- **Purchase**: Pricing, buying options, checkout
- **Loyalty**: Support, documentation, API guides

## Technology Stack

- **Streamlit**: Web application framework
- **Sentence Transformers**: Semantic text embeddings
- **Plotly**: Interactive visualizations
- **Pandas**: Data processing
- **PyTorch**: Machine learning backend

## Deployment on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Deploy your app by selecting the repository

## Configuration

The app uses the `all-MiniLM-L6-v2` model for semantic embeddings. You can modify the journey archetypes in the code:

```python
JOURNEY_ARCHETYPES = {
    "Awareness": "educational guide tutorial...",
    "Consideration": "best top reviews comparison...",
    "Purchase": "buy price pricing cost...",
    "Loyalty": "login support documentation..."
}
```

## Performance

- First run downloads the ML model (~90MB)
- Model is cached for subsequent uses
- Processing speed: ~100-500 URLs per minute

## Limitations

- Text analysis is language-dependent (optimized for English)
- Classification accuracy depends on content clarity
- Large files (>10,000 rows) may take several minutes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions, please open an issue on GitHub.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Uses [Sentence Transformers](https://www.sbert.net/)
- Powered by [Hugging Face](https://huggingface.co/)