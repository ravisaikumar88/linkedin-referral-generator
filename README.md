# LinkedIn Referral Message Generator 💼

A Streamlit web app that generates casual, personalized LinkedIn referral messages using AI. The app automatically scrapes job details from posting URLs and uses Google Gemini API to create human-friendly messages.

## Features

✨ **Smart Job Scraping** - Automatically extracts job title and company name from job URLs  
🤖 **AI-Powered Messages** - Uses Google Gemini to generate casual, professional messages  
📋 **Easy Copy** - One-click copy to clipboard functionality  
🎨 **Clean UI** - Simple, intuitive Streamlit interface  
⚠️ **Error Handling** - Graceful fallbacks for scraping failures and API errors  

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Gemini API Key

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Create a `.env` file in the project directory:**

```bash
# Copy the example file
cp .env.example .env
```

**Edit `.env` and add your API key:**

```
GOOGLE_API_KEY=your-api-key-here
```

The app will automatically load the API key from this file when it starts.

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter Person Name** - The name of the person you're messaging (e.g., "Sahil", "Vishnu")
2. **Paste Job Link** - The URL of the job posting
3. **Click Generate** - The app will:
   - Scrape job title and company name from the URL
   - Generate a casual LinkedIn message using AI
   - Display the message ready to copy
4. **Copy & Send** - Copy the message and paste it on LinkedIn

## Example

**Input:**
- Person Name: `Sahil`
- Job Link: `https://www.linkedin.com/jobs/view/123456789`

**Output:**
```
Hi Sahil,

I came across the Machine Learning Engineer role at Google and thought it aligned perfectly with my background. I'm currently exploring AI/ML roles and would love to get your insights on the team and culture.

Here's the posting I'm interested in: https://www.linkedin.com/jobs/view/123456789

I've shared my resume for your reference. If you think I'd be a good fit, I'd really appreciate any guidance or a referral.

Thanks so much for your time!
```

## Technical Details

- **Framework:** Streamlit
- **AI Model:** Google Gemini Pro
- **Web Scraping:** BeautifulSoup + Requests
- **Python Version:** 3.8+

## Error Handling

The app handles:
- ❌ Empty input fields
- ❌ Invalid URLs
- ❌ Scraping failures (uses generic wording)
- ❌ Gemini API errors
- ❌ Missing API key

## Notes

- Messages are always casual and friendly (no tone selection needed)
- No emojis or hashtags in generated messages
- Messages are ready to paste directly into LinkedIn
- You can edit the generated message before copying

## License

MIT License - Feel free to use and modify!
