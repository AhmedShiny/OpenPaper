# OpenPaper

## Overview
This application automatically generates comprehensive research papers on any topic using a combination of AI-powered research tools. It leverages browser-based search capabilities and language models to create well-structured academic papers and saves them as PDF documents. It can take upto 30 minutes to create one.

## Demo

https://github.com/user-attachments/assets/1189fa9d-cf7a-4806-af66-8b9bdf31bb30
> Note: The demo is sped up
## Requirements
- GROQ API key (for language model access) or any other langchain supported model
- Tavily API key (for search functionality)

## Sample papers
https://github.com/AhmedShiny/OpenPaper/tree/main/research_papers

> Note: To increase report size change the char_limit in workflow.py but bear in mind it will      increase token consumption

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   uv venv # recommended
   
   .venv\Scripts\activate  # On Windows
   
   source .venv/bin/activate  # For Mac/Linux:
   ```
3. Install dependencies (create a requirements.txt file with the following):
   ```
   python -m pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   TAVILY_API_KEY=your_google_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

Run the application with:
```
python main.py
```

You will be prompted to enter a research topic. If you press Enter without typing anything, it will use the default topic "Making Diffusion Models Better".

The application will:
1. Research the topic using Tavily and browser-based search
2. Generate a structured outline
3. Create a complete research paper draft
4. Save the paper as a PDF in the project directory


## Disclaimer
**EXPERIMENTAL PROJECT**: This tool is currently in experimental stage and not intended for production use. The automated research and paper generation process can consume significant API resources, potentially resulting in high costs depending on your usage. Please monitor your API usage carefully when using this application.

