from django.core.management.base import BaseCommand
import google.generativeai as genai
import os
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Check Gemini AI API connection'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("🔄 Checking Gemini API configuration...")
            
            # Load environment variables
            load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                self.stdout.write(self.style.ERROR("❌ GEMINI_API_KEY not found in .env file"))
                return
                
            # Configure Gemini with the experimental model
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            
            # Simple test prompt
            test_response = model.generate_content("Say 'Connection successful!'")
            
            if test_response and test_response.text:
                self.stdout.write(self.style.SUCCESS(f"\n✅ Gemini API connection successful!"))
                self.stdout.write(f"Response: {test_response.text}")
                self.stdout.write(self.style.SUCCESS(f"\nModel: gemini-2.0-pro-exp-02-05"))
                models = genai.list_models()
                self.stdout.write("\nAvailable models:")
                for model in models:
                    self.stdout.write(f"- {model.name}")
            else:
                self.stdout.write(self.style.WARNING("⚠️ Connected but no response received"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection failed: {str(e)}"))
            self.stdout.write("\nTrying to list available models...")
            try:
                models = genai.list_models()
                self.stdout.write("\nAvailable models:")
                for model in models:
                    self.stdout.write(f"- {model.name}")
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f"Could not list models: {str(e2)}"))