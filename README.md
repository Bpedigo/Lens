# Text Analysis Desktop Application

A powerful desktop application built with Python and CustomTkinter that leverages OpenAI's GPT models to perform sophisticated text analysis. This tool allows users to analyze text using various predefined prompts, making it easy to get different analytical perspectives on any piece of text.

## Features

- **Modern UI**: Built with CustomTkinter for a clean, modern interface
- **Multiple Analysis Types**: Four different analysis buttons with customizable prompts
- **Single & Multiple Prompts**: Support for both single and multiple-prompt analysis
- **Editable Prompts**: Easy-to-customize prompt system using text files
- **Copy & Clear Functions**: Quick actions for managing text content
- **Real-time Analysis**: Instant feedback with loading animations
- **Error Handling**: Robust error management system

## Default Analysis Types

1. **General Analysis** (Single Prompt)
   - Detailed breakdown of key points, main arguments, and overall structure
   - Highlights important insights and conclusions

2. **Thematic & Communication Analysis** (Multiple Prompts)
   - Theme identification, argument analysis, and bias detection
   - Writing style evaluation and improvement suggestions

3. **Critical Analysis** (Single Prompt)
   - Strengths and weaknesses assessment
   - Evidence evaluation and improvement areas

4. **Logic & Rhetoric Analysis** (Multiple Prompts)
   - Logical structure and fallacy identification
   - Rhetorical device analysis and persuasion evaluation

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. Run the application:
```bash
python src/main.py
```

2. Input your text in the main text area

3. Choose an analysis type:
   - Use single prompt buttons for focused analysis
   - Use multiple prompt buttons for varied perspectives

4. Edit prompts:
   - Click the "Edit" button below any analysis button
   - Modify the prompt in the popup window
   - For multiple prompts, use "--------" as a separator

5. Use additional features:
   - Copy button to copy results
   - Clear button to reset the interface

## Customizing Prompts

Prompts are stored in the `prompts` directory:
- `button1.txt`: General analysis prompt
- `button2.txt`: Thematic & communication analysis prompts
- `button3.txt`: Critical analysis prompt
- `button4.txt`: Logic & rhetoric analysis prompts

Edit these files directly or use the in-app edit buttons to customize the analysis prompts.

## Requirements

- Python 3.8+
- OpenAI API key
- Required packages (see requirements.txt):
  - customtkinter
  - openai
  - python-dotenv
  - pyperclip

## License

[Your chosen license]

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Acknowledgments

- Built with CustomTkinter for the modern UI
- Powered by OpenAI's GPT models
- Inspired by the need for sophisticated text analysis tools 