import streamlit as st
import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure page
st.set_page_config(
    page_title="LinkedIn Referral Message Generator",
    page_icon="💼",
    layout="centered"
)

# Initialize Gemini API
def init_gemini():
    """Initialize Gemini API with API key from environment"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ GOOGLE_API_KEY environment variable not found. Please set it before running the app.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

# Scrape job details from URL
def scrape_job_details(url):
    """
    Scrape job title and company name from job posting URL
    Returns: (job_title, company_name) or (None, None) if scraping fails
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None, None
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()
        
        job_title = None
        company_name = None
        
        # Strategy 1: Look for title in meta tags first (most reliable)
        meta_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'title'})
        if meta_title and meta_title.get('content'):
            content = meta_title.get('content').strip()
            # Don't split generic titles
            if content and content != 'Candidate Experience Site - Lateral':
                job_title = content
        
        # Strategy 2: Look for common job title tags
        if not job_title:
            title_selectors = [
                'h1',
                'h2',
                {'class': re.compile(r'job.*title', re.I)},
                {'class': re.compile(r'position.*name', re.I)},
                {'data-automation': 'job-title'},
                {'itemprop': 'title'},
            ]
            
            for selector in title_selectors:
                if isinstance(selector, str):
                    element = soup.find(selector)
                else:
                    element = soup.find(attrs=selector)
                
                if element and element.get_text(strip=True):
                    text = element.get_text(strip=True)
                    if len(text) > 5 and text != 'Candidate Experience Site - Lateral':
                        job_title = text
                        break
        
        # Strategy 3: Use page title as last resort
        if not job_title:
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                if title_text and title_text != 'Candidate Experience Site - Lateral':
                    job_title = title_text
        
        # Search for company names in page text
        common_companies = [
            'Goldman Sachs', 'JPMorgan', 'Morgan Stanley', 'Google', 'Amazon', 
            'Microsoft', 'Meta', 'Apple', 'Netflix', 'Tesla', 'Uber',
            'Airbnb', 'LinkedIn', 'Salesforce', 'Adobe', 'Oracle', 'IBM',
            'Accenture', 'Deloitte', 'McKinsey', 'BCG', 'Bain'
        ]
        
        for company in common_companies:
            # Search in page text (case-insensitive)
            if re.search(rf'\b{re.escape(company)}\b', page_text, re.I):
                company_name = company
                break
        
        # Try to extract company name from page elements
        if not company_name:
            company_selectors = [
                {'class': re.compile(r'company.*name', re.I)},
                {'class': re.compile(r'employer', re.I)},
                {'class': re.compile(r'organization', re.I)},
                {'data-automation': 'company-name'},
                {'itemprop': 'hiringOrganization'},
            ]
            
            for selector in company_selectors:
                element = soup.find(attrs=selector)
                if element:
                    company_elem = element.find('span') or element.find('a') or element
                    text = company_elem.get_text(strip=True)
                    if text and len(text) > 1 and text not in ['Lateral', 'Candidate Experience']:
                        company_name = text
                        break
        
        # Clean up extracted text
        if job_title:
            job_title = ' '.join(job_title.split())  # Remove extra whitespace
            # Remove trailing location info in parentheses
            job_title = re.sub(r'\s*\([^)]*\)\s*$', '', job_title)
        
        if company_name:
            company_name = ' '.join(company_name.split())
        
        return job_title, company_name
        
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ Network error while fetching job details: {str(e)}")
        return None, None
    except Exception as e:
        st.warning(f"⚠️ Could not scrape job details: {str(e)}")
        return None, None

# Generate message using Gemini
def generate_referral_message(person_name, job_title, company_name, job_link, model):
    """Generate casual LinkedIn referral message using Gemini API"""
    
    # Validate and clean job details - avoid generic/suspicious values
    generic_terms = ['candidate experience', 'lateral', 'site', 'oracle', 'job posting', 'careers']
    
    # Check if job title seems valid
    if job_title:
        job_title_lower = job_title.lower()
        if any(term in job_title_lower for term in generic_terms) or len(job_title) < 5:
            job_title = None  # Ignore generic/invalid titles
    
    # Check if company name seems valid
    if company_name:
        company_name_lower = company_name.lower()
        if any(term in company_name_lower for term in generic_terms) or len(company_name) < 2:
            company_name = None  # Ignore generic/invalid companies
    
    # Build context for the prompt
    if job_title and company_name:
        job_context = f"the {job_title} position at {company_name}"
        job_mention = f"the {job_title} role at {company_name}"
    elif job_title:
        job_context = f"the {job_title} position"
        job_mention = f"the {job_title} role"
    elif company_name:
        job_context = f"a role at {company_name}"
        job_mention = f"this position at {company_name}"
    else:
        job_context = "this opportunity"
        job_mention = "this role at your organization"
    
    # System prompt for Gemini
    prompt = f"""You are a friendly job seeker writing a casual LinkedIn message to request a referral.

Write a casual, friendly LinkedIn message to {person_name} asking for a referral for {job_context}.

CRITICAL REQUIREMENTS:
- Start with: "Hi {person_name},"
- When mentioning the job, use natural phrasing like: "{job_mention}"
- If the job mention is generic (like "this role at your organization"), use phrases like:
  * "this role at your organization" 
  * "this opportunity fits my background"
  * "the position I'm interested in"
- DO NOT invent, assume, or add ANY job title or company name beyond what's provided
- Mention that you're exploring AI/ML roles
- Include the job link naturally in the message: {job_link}
- Mention that you've attached/shared your resume
- Politely ask for insights or referral
- Keep it casual, friendly, and human-sounding
- Be concise (4-6 sentences max)
- NO emojis, NO hashtags, NO markdown formatting
- Sound natural, not robotic or overly formal
- Don't use phrases like "I hope this message finds you well"

Generate ONLY the message text, nothing else."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

# Main app
def main():
    st.title("💼 LinkedIn Referral Message Generator")
    st.markdown("Generate casual, personalized LinkedIn referral messages with AI")
    
    # Initialize Gemini
    model = init_gemini()
    
    # Input fields
    col1, col2 = st.columns(2)
    
    with col1:
        person_name = st.text_input(
            "Person Name",
            placeholder="e.g., Sahil, Vishnu",
            help="Enter the name of the person you're messaging"
        )
    
    with col2:
        job_link = st.text_input(
            "Job Link",
            placeholder="https://...",
            help="Paste the URL of the job posting"
        )
    
    # Generate button
    if st.button("🚀 Generate Message", type="primary", use_container_width=True):
        # Validation
        if not person_name or not person_name.strip():
            st.error("❌ Please enter the person's name")
            return
        
        if not job_link or not job_link.strip():
            st.error("❌ Please enter the job link")
            return
        
        # Validate URL format
        parsed_url = urlparse(job_link)
        if not parsed_url.scheme or not parsed_url.netloc:
            st.error("❌ Please enter a valid URL (must start with http:// or https://)")
            return
        
        # Scrape job details silently (don't display)
        job_title, company_name = scrape_job_details(job_link)
        
        # Always use generic wording since we include the link
        # This avoids showing potentially incorrect scraped data
        final_job_title = None
        final_company_name = None
        
        # Generate message
        with st.spinner("✨ Generating your message..."):
            try:
                message = generate_referral_message(
                    person_name.strip(),
                    final_job_title,  # Always None = generic wording
                    final_company_name,  # Always None = generic wording
                    job_link.strip(),
                    model
                )
                
                # Store in session state
                st.session_state['generated_message'] = message
                
            except Exception as e:
                st.error(f"❌ Error generating message: {str(e)}")
                return
    
    # Display generated message
    if 'generated_message' in st.session_state:
        st.markdown("---")
        st.subheader("📝 Your Message")
        
        # Display message in text area
        message_text = st.text_area(
            "Generated Message",
            value=st.session_state['generated_message'],
            height=250,
            label_visibility="collapsed",
            key="message_output"
        )
        
        # Copy to clipboard button with JavaScript
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True, key="copy_btn"):
                # Use JavaScript to copy text
                st.components.v1.html(
                    f"""
                    <script>
                    const text = {repr(message_text)};
                    navigator.clipboard.writeText(text).then(function() {{
                        console.log('Copied to clipboard successfully!');
                    }}, function(err) {{
                        console.error('Could not copy text: ', err);
                    }});
                    </script>
                    """,
                    height=0,
                )
                st.success("✅ Message copied to clipboard!")
        
        st.info("💡 **Tip:** You can edit the message above before copying if needed!")

if __name__ == "__main__":
    main()
