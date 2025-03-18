from django.core.management.base import BaseCommand
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import time

class Command(BaseCommand):
    help = 'Test Gemini AI connectivity and chat functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='chat',
            choices=['chat', 'parse', 'list'],
            help='Test mode: chat for conversation, parse for warehouse details, list for available models'
        )

    def list_available_models(self):
        """List all available Gemini models"""
        try:
            self.stdout.write("📋 Listing available Gemini models...")
            models = genai.list_models()
            for model in models:
                self.stdout.write(f"- {model.name}")
                self.stdout.write(f"  Supported generation methods: {', '.join(model.supported_generation_methods)}")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to list models: {str(e)}"))
            return False

    def test_connectivity(self):
        """Test basic connectivity with Gemini AI"""
        try:
            self.stdout.write("🔄 Testing Gemini AI connectivity...")
            
            # Load environment variables
            load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                self.stdout.write(self.style.ERROR("❌ GEMINI_API_KEY not found in .env file"))
                return False, None, None
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # List available models first
            self.list_available_models()
            
            # Try models in order of preference
            model_names = [
                'models/gemini-1.5-pro',  # Latest stable pro model
                'models/gemini-pro',      # Fallback
                'models/gemini-1.5-pro-latest'  # Another option
            ]
            
            model = None
            errors = []
            
            for model_name in model_names:
                try:
                    self.stdout.write(f"🔄 Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    break
                except Exception as e:
                    errors.append(f"{model_name}: {str(e)}")
                    continue
            
            if not model:
                self.stdout.write(self.style.ERROR(f"❌ Failed to initialize any model:\n" + "\n".join(errors)))
                return False, None, None
            
            try:
                chat = model.start_chat(history=[])
            except AttributeError:
                # If start_chat is not available, we'll use generate_content instead
                self.stdout.write(self.style.WARNING("⚠️ Chat functionality not available, falling back to basic generation"))
                chat = None
            
            # Test with a simple message
            test_message = "Hello! Are you working?"
            if chat:
                response = chat.send_message(test_message)
            else:
                response = model.generate_content(test_message)
            
            if response and response.text:
                self.stdout.write(self.style.SUCCESS("✅ Gemini AI connection successful"))
                self.stdout.write(f"🤖 AI Response: {response.text}")
                return True, model, chat
            else:
                self.stdout.write(self.style.ERROR("❌ No response received from Gemini AI"))
                return False, None, None
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection test failed: {str(e)}"))
            return False, None, None

    def handle_chat_mode(self):
        """Handle interactive chat mode with Gemini AI"""
        success, model, chat = self.test_connectivity()
        if not success:
            return
        
        self.stdout.write("\n📝 Starting chat mode (type 'exit' to quit)")
        self.stdout.write("You can test warehouse-related queries like:")
        self.stdout.write("- 'My warehouse is 30 feet long and 20 feet wide'")
        self.stdout.write("- 'The rental price is $500 per month'")
        self.stdout.write("- 'It has CCTV and parking facilities'\n")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                    
                if not user_input:
                    continue
                
                # Send message and get response
                try:
                    if chat:
                        response = chat.send_message(user_input)
                    else:
                        response = model.generate_content(user_input)
                    
                    if response and response.text:
                        self.stdout.write(f"\n🤖 AI: {response.text}")
                    else:
                        self.stdout.write(self.style.WARNING("\n⚠️ No response received"))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
                    
            except KeyboardInterrupt:
                self.stdout.write("\n👋 Chat session ended by user")
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
                break
        
        self.stdout.write("\n✨ Chat session ended")

    def parse_warehouse_details(self, model):
        """Parse warehouse details mode"""
        self.stdout.write("\n📝 Warehouse Details Parser (type 'exit' to return to chat)")
        
        while True:
            try:
                user_input = input("\nDescribe your warehouse: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    self.stdout.write("Returning to chat mode...")
                    break
                
                # Build the prompt
                prompt = """Extract warehouse details from this text and return ONLY a valid JSON object:
                {
                    "length": (number in feet),
                    "breadth": (number in feet),
                    "height": (number in feet),
                    "area": (calculated length * breadth),
                    "landmarks": "location details",
                    "terms_cond": "terms and conditions",
                    "facilities": ["list of available facilities"],
                    "missing_info": ["list any missing required details"]
                }
                
                Text to parse: {input}"""
                
                self.stdout.write("\n🔄 Processing warehouse details...")
                response = model.generate_content(prompt.format(input=user_input))
                
                if response and response.text:
                    # Clean and parse the response
                    text = response.text.strip()
                    if '```json' in text:
                        text = text.split('```json')[1].split('```')[0].strip()
                    elif '```' in text:
                        text = text.split('```')[1].strip()
                    
                    # Parse and display JSON
                    data = json.loads(text)
                    self.stdout.write("\n📋 Parsed Details:")
                    self.stdout.write(json.dumps(data, indent=2))
                    
                    # Show missing fields
                    if data.get('missing_info'):
                        self.stdout.write(self.style.WARNING(
                            f"\n⚠️ Missing information: {', '.join(data['missing_info'])}"
                        ))
                else:
                    self.stdout.write(self.style.WARNING("⚠️ No response received"))
                    
            except KeyboardInterrupt:
                self.stdout.write("\nReturning to chat mode...")
                break
            except json.JSONDecodeError as je:
                self.stdout.write(self.style.ERROR(f"\n❌ Invalid JSON response: {str(je)}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
                time.sleep(1)

    def handle(self, *args, **options):
        if options['mode'] == 'list':
            # Just list models and exit
            self.list_available_models()
            return
            
        # Test connectivity first
        success, model, chat = self.test_connectivity()
        
        if not success:
            return
        
        # Start requested mode
        if options['mode'] == 'chat':
            self.handle_chat_mode()
        else:
            self.parse_warehouse_details(model)