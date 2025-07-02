import google.generativeai as genai
import os
from typing import Optional

class GeminiSummarizer:
    def __init__(self, api_key: str):
        """
        Initialize Gemini summarizer with API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def create_summary_prompt(self, conversation_text: str, meeting_stats: dict) -> str:
        """
        Create a well-structured prompt for meeting summarization
        """
        speakers = ", ".join(meeting_stats.get('speaker_word_counts', {}).keys())
        duration = meeting_stats.get('duration', 'Unknown')
        
        prompt = f"""
Please analyze and summarize this meeting transcript in a clear, narrative format.

MEETING DETAILS:
- Duration: {duration}
- Participants: {speakers}
- Total entries: {meeting_stats.get('total_entries', 0)}

TRANSCRIPT:
{conversation_text}

Please provide a comprehensive summary in narrative format that includes:

1. **Meeting Overview**: Brief description of the meeting's main purpose and context
2. **Key Discussion Topics**: Main subjects discussed during the meeting
3. **Important Decisions Made**: Any decisions, agreements, or conclusions reached
4. **Action Items & Next Steps**: Tasks assigned, deadlines mentioned, or follow-up actions
5. **Notable Updates**: Important announcements, status updates, or information shared
6. **Scheduling & Timeline**: Any dates, deadlines, or future meetings mentioned

Write the summary in a flowing narrative style, not bullet points. Focus on the most important information and maintain the context of the business discussion.
"""
        return prompt
    
    def summarize_meeting(self, conversation_text: str, meeting_stats: dict) -> Optional[str]:
        """
        Generate AI summary using Gemini API
        """
        try:
            # Create the prompt
            prompt = self.create_summary_prompt(conversation_text, meeting_stats)
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "❌ Failed to generate summary - empty response from API"
                
        except Exception as e:
            return f"❌ Error generating summary: {str(e)}"
    
    def test_api_connection(self) -> bool:
        """
        Test if the API key and connection work
        """
        try:
            response = self.model.generate_content("Hello, please respond with 'API connection successful'")
            return response and "successful" in response.text.lower()
        except:
            return False


# Configuration and API Key Management
class Config:
    """
    Handle configuration and API key management
    """
    @staticmethod
    def get_api_key():
        """
        Get API key from environment variable or user input
        """
        # First try to get from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("Gemini API key not found in environment variables.")
            print("You can either:")
            print("1. Set GEMINI_API_KEY environment variable")
            print("2. Enter it manually each time")
            print("\nTo get a free API key:")
            print("- Go to https://makersuite.google.com/app/apikey")
            print("- Sign in with Google account")
            print("- Create new API key")
            
        return api_key
    
    @staticmethod
    def save_api_key_to_file(api_key: str):
        """
        Save API key to a local config file (optional)
        """
        try:
            with open('.env', 'w') as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
            print("API key saved to .env file")
        except Exception as e:
            print(f"Could not save API key: {e}")
    
    @staticmethod
    def load_api_key_from_file():
        """
        Load API key from .env file
        """
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY='):
                            return line.split('=', 1)[1].strip()
        except:
            pass
        return None


# Test function
def test_gemini_integration():
    """
    Test the Gemini integration with sample data
    """
    print("Testing Gemini API Integration...")
    print("=" * 50)
    
    # Get API key
    api_key = Config.load_api_key_from_file() or Config.get_api_key()
    
    if not api_key:
        api_key = input("\nPlease enter your Gemini API key: ").strip()
        
        save_key = input("Save this key to .env file? (y/n): ").lower() == 'y'
        if save_key:
            Config.save_api_key_to_file(api_key)
    
    if not api_key:
        print("No API key provided. Cannot test.")
        return
    
    # Initialize summarizer
    summarizer = GeminiSummarizer(api_key)
    
    # Test API connection
    print("Testing API connection...")
    if summarizer.test_api_connection():
        print("✅ API connection successful!")
    else:
        print("❌ API connection failed. Please check your API key.")
        return
    
    # Test with sample data
    sample_conversation = """
    adamnoel: Drive in teams. I think that's what they want. Why did it start recording? Because I plus record? Oh, you did. Okay, make sure you tell Misty, because she's not super keen on us keeping the edits recording sessions.

    Misty Pearson, South Carolina: Morning.

    adamnoel: Morning. Turn it up. There you go! There we go! Hi!

    Misty Pearson, South Carolina: Hello! Are y'all all recovered from your trip.

    adamnoel: Yeah, more or less. I think. So. Yeah. we're also in the middle of doing a an office move, etc. So lots of activity going on here.
    """
    
    sample_stats = {
        'duration': '00:00:05 to 00:05:00',
        'total_speakers': 2,
        'total_entries': 10,
        'speaker_word_counts': {
            'adamnoel': 45,
            'Misty Pearson, South Carolina': 15
        }
    }
    
    print("\nGenerating test summary...")
    summary = summarizer.summarize_meeting(sample_conversation, sample_stats)
    
    print("\n📝 Generated Summary:")
    print("-" * 30)
    print(summary)


if __name__ == "__main__":
    test_gemini_integration()