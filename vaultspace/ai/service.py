import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import re

load_dotenv()

class GeminiService:
    def __init__(self):
        
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def parse_warehouse_details(self, user_input):
        prompt = """You are a helpful warehouse assistant. Extract warehouse details from the user's message and return a valid JSON object.
        Be natural and conversational in understanding the context.

        Example inputs and their interpretations:
        - "My warehouse is 30 feet long, 20 feet wide, and 15 feet high" -> {"length": 30, "breadth": 20, "height": 15}
        - "I want to rent it for ₹15,000 monthly" -> {"rental_price": 15000}
        - "It's near the bus stand" -> {"landmarks": "bus stand"}
        - "The warehouse has loading docks and security cameras" -> {"facilities": ["Loading Docks", "Surveillance cameras"]}
        - "Minimum lease period is 6 months" -> {"terms_cond": "Minimum lease period is 6 months"}
        
        Return this exact format (and ONLY this format - no explanation text, just the JSON):
        {
            "length": <number or null>,
            "breadth": <number or null>,
            "height": <number or null>,
            "area": <calculated or null>,
            "landmarks": "<text or empty string>",
            "rental_price": <number or null>,
            "terms_cond": "<text or empty string>",
            "facilities": ["facility1", "facility2"],
            "missing_fields": ["field1", "field2"]
        }

        Rules for natural language understanding:
        1. Understand various ways of expressing dimensions:
           - "30 feet long" or "length is 30 feet" or "30 ft in length"
           - "20 feet wide" or "width of 20 feet" or "20 ft breadth"
           - "15 feet high" or "height is 15 feet" or "15 ft tall"
        
        2. Understand price expressions:
           - "₹15,000 per month" or "15k monthly" or "rent is 15000"
           - Remove currency symbols and commas before converting to number
        
        3. Understand location descriptions:
           - "near X" or "located at X" or "landmark: X"
           - "close to X" or "adjacent to X" or "beside X"
        
        4. Understand facilities:
           - Match against standard list: Loading Docks, Racking Systems, Lighting and Climate Control, Climate control, Surveillance cameras, Security personnel, Restrooms and break areas, Office spaces, First aid stations
           - Handle variations like "security guards" -> "Security personnel"
        
        5. Understand terms and conditions:
           - Look for phrases about lease period, payment terms, maintenance
           - Extract complete sentences for clarity
        
        6. Context awareness:
           - If user mentions only one dimension, add others to missing_fields
           - If user mentions price without currency, assume ₹
           - If user mentions facilities without standard names, match to closest standard facility

        User input: {text}"""

        try:
            # Check for simple landmark input first
            landmark_match = re.search(r'landmark\s*(?::|is|=)\s*(.+?)(?:$|\.|\n)', user_input, re.IGNORECASE)
            if landmark_match:
                landmark_text = landmark_match.group(1).strip()
                return {
                    "length": None,
                    "breadth": None,
                    "height": None, 
                    "area": None,
                    "landmarks": landmark_text,
                    "rental_price": None,
                    "terms_cond": "",
                    "facilities": [],
                    "missing_fields": []
                }
            
            # Handle common dimension patterns directly before sending to the AI
            simple_dimension_pattern = r"(\d+)\s*(?:feet|foot|ft|f)?\s*(long|length|wide|width|breadth|high|height|tall)"
            dimensions = {
                "length": None,
                "breadth": None,
                "height": None
            }
            
            # Try to directly extract dimensions with regex
            dimension_matches = re.findall(simple_dimension_pattern, user_input.lower())
            for value, dim_type in dimension_matches:
                if "long" in dim_type or "length" in dim_type:
                    dimensions["length"] = float(value)
                elif "wide" in dim_type or "width" in dim_type or "breadth" in dim_type:
                    dimensions["breadth"] = float(value)
                elif "high" in dim_type or "height" in dim_type or "tall" in dim_type:
                    dimensions["height"] = float(value)
            
            # Handle format like "30×20×15" or "30x20x15"
            combined_dimension_pattern = r"(\d+)\s*(?:×|x)\s*(\d+)\s*(?:×|x)\s*(\d+)"
            combined_match = re.search(combined_dimension_pattern, user_input)
            if combined_match:
                dimensions["length"] = float(combined_match.group(1))
                dimensions["breadth"] = float(combined_match.group(2))
                dimensions["height"] = float(combined_match.group(3))
            
            # Extract landmarks
            landmarks = ""
            if "near" in user_input.lower() or "landmark" in user_input.lower() or "located" in user_input.lower():
                # First try to match "landmark: X" pattern
                landmark_colon_match = re.search(r'landmark\s*(?::|is|=)\s*(.+?)(?:$|\.|\n)', user_input, re.IGNORECASE)
                if landmark_colon_match:
                    landmarks = landmark_colon_match.group(1).strip()
                else:
                    # Try location indicators
                    location_indicators = ["near", "at", "in", "by", "close to", "adjacent to", "beside", "located"]
                    for indicator in location_indicators:
                        if indicator in user_input.lower():
                            parts = user_input.lower().split(indicator)
                            if len(parts) > 1:
                                # Take the text after the indicator until the next punctuation
                                location_text = parts[1].strip()
                                end_idx = next((i for i, c in enumerate(location_text) if c in '.,;:!?'), len(location_text))
                                landmarks = location_text[:end_idx].strip().capitalize()
                                break
            
            # If we only found landmark, return it
            if landmarks and not any(dimensions.values()):
                return {
                    "length": None,
                    "breadth": None,
                    "height": None,
                    "area": None,
                    "landmarks": landmarks,
                    "rental_price": None,
                    "terms_cond": "",
                    "facilities": [],
                    "missing_fields": []
                }
            
            # If we found at least one dimension directly, create a simplified result
            if any(dimensions.values()):
                # Check if the input contains terms
                terms_cond = ""
                if "terms" in user_input.lower() or "condition" in user_input.lower():
                    # Extract quoted text as terms
                    terms_match = re.search(r"['\"]([^'\"]+)['\"]", user_input)
                    if terms_match:
                        terms_cond = terms_match.group(1)
                
                # Extract facilities
                facilities = []
                facility_keywords = {
                    "loading dock": "Loading Docks",
                    "rack": "Racking Systems",
                    "light": "Lighting and Climate Control", 
                    "climate": "Climate control",
                    "surveillance": "Surveillance cameras",
                    "camera": "Surveillance cameras",
                    "security": "Security personnel",
                    "guard": "Security personnel",
                    "personnel": "Security personnel",
                    "restroom": "Restrooms and break areas",
                    "toilet": "Restrooms and break areas",
                    "washroom": "Restrooms and break areas",
                    "break area": "Restrooms and break areas", 
                    "break room": "Restrooms and break areas",
                    "office space": "Office spaces",
                    "office room": "Office spaces",
                    "workspace": "Office spaces",
                    "first aid": "First aid stations",
                    "medical": "First aid stations"
                }
                
                for keyword, standard_facility in facility_keywords.items():
                    if keyword in user_input.lower() and standard_facility not in facilities:
                        facilities.append(standard_facility)
                
                # Also check for facility mentions using "has" or "with" patterns
                facility_patterns = [
                    r'(?:has|with|having|contains|includes?)\s+([^,.;]+)(?:and|,|\.|$)',
                    r'facilities\s*(?::|include|are)\s*([^,.;]+)(?:and|,|\.|$)'
                ]
                
                for pattern in facility_patterns:
                    facility_matches = re.finditer(pattern, user_input.lower())
                    for match in facility_matches:
                        facility_text = match.group(1).strip()
                        # Check each facility text against our keywords
                        for keyword, standard_facility in facility_keywords.items():
                            if keyword in facility_text and standard_facility not in facilities:
                                facilities.append(standard_facility)
                
                # Extract rental price
                rental_price = None
                price_match = re.search(r'(?:₹|rs\.?|inr|price|rent|cost)[^\d]*(\d+(?:,\d+)*(?:\.\d+)?)', 
                                        user_input.lower(), re.IGNORECASE)
                if price_match:
                    # Remove commas from the price
                    price_str = price_match.group(1).replace(',', '')
                    rental_price = float(price_str)
                
                # Handle shorthand price formats like "15k" (meaning 15,000)
                if not rental_price:
                    k_price_match = re.search(r'(\d+)k', user_input.lower())
                    if k_price_match:
                        k_price = float(k_price_match.group(1))
                        rental_price = k_price * 1000
                
                # Try to find any number followed by "per month" or "monthly"
                if not rental_price:
                    monthly_price_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:per month|monthly)', user_input.lower())
                    if monthly_price_match:
                        price_str = monthly_price_match.group(1).replace(',', '')
                        rental_price = float(price_str)
                
                # Try to find just plain numbers that might be prices
                if not rental_price and "price" in user_input.lower():
                    plain_price_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', user_input.lower())
                    if plain_price_match:
                        price_str = plain_price_match.group(1).replace(',', '')
                        rental_price = float(price_str)
                
                # Calculate area if both dimensions are available
                area = None
                if dimensions["length"] and dimensions["breadth"]:
                    area = dimensions["length"] * dimensions["breadth"]
                
                # Determine missing fields
                missing_fields = []
                if dimensions["length"] is None:
                    missing_fields.append("length")
                if dimensions["breadth"] is None:
                    missing_fields.append("breadth")
                if dimensions["height"] is None:
                    missing_fields.append("height")
                
                result = {
                    "length": dimensions["length"],
                    "breadth": dimensions["breadth"],
                    "height": dimensions["height"],
                    "area": area,
                    "landmarks": landmarks,
                    "rental_price": rental_price,
                    "terms_cond": terms_cond,
                    "facilities": facilities,
                    "missing_fields": missing_fields
                }
                
                print(f"Direct extraction result: {result}")
                return result
            
            # If we couldn't extract dimensions directly, try the AI
            response = self.model.generate_content(prompt.format(text=user_input))
            cleaned_text = response.text.strip()
            
            # Remove code block markers if present
            if '```json' in cleaned_text:
                cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
            elif '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```')[1].strip()
            
            # Print the cleaned text for debugging
            print(f"Cleaned AI response: {cleaned_text}")

            # Parse the JSON response
            data = json.loads(cleaned_text)
            
            # Ensure we have the expected structure
            if not isinstance(data, dict):
                raise ValueError("Invalid response format")
            
            # Create a normalized result with all required fields
            result = {
                "length": data.get("length"),
                "breadth": data.get("breadth"),
                "height": data.get("height"),
                "area": data.get("area"),
                "landmarks": data.get("landmarks", ""),
                "rental_price": data.get("rental_price"),
                "terms_cond": data.get("terms_cond", ""),
                "facilities": data.get("facilities", []),
                "missing_fields": data.get("missing_fields", [])
            }
            
            # Handle field name variations
            if "landmark" in data and not result["landmarks"]:
                result["landmarks"] = data["landmark"]
            
            if "width" in data and not result["breadth"]:
                result["breadth"] = data["width"]
            
            # Calculate area if possible
            if result["length"] and result["breadth"]:
                result["area"] = float(result["length"]) * float(result["breadth"])
            
            # Handle simple inputs like "20 feet long"
            if result["length"] and not result["breadth"] and not result["height"]:
                missing = result["missing_fields"]
                if "breadth" not in missing:
                    missing.append("breadth")
                if "height" not in missing:
                    missing.append("height")
                result["missing_fields"] = missing
            
            print(f"AI processed result: {result}")
            return result

        except Exception as e:
            print(f"Error processing input '{user_input}': {str(e)}")
            
            # Attempt basic extraction as a fallback
            try:
                # Extract dimensions with a simpler pattern
                length_match = re.search(r'(\d+)\s*(?:feet|foot|ft|f)?\s*(?:long|length)', user_input.lower())
                breadth_match = re.search(r'(\d+)\s*(?:feet|foot|ft|f)?\s*(?:wide|width|breadth)', user_input.lower())
                height_match = re.search(r'(\d+)\s*(?:feet|foot|ft|f)?\s*(?:high|height|tall)', user_input.lower())
                
                length = float(length_match.group(1)) if length_match else None
                breadth = float(breadth_match.group(1)) if breadth_match else None
                height = float(height_match.group(1)) if height_match else None
                
                # Try to extract landmark as a last resort
                landmark = None
                landmark_match = re.search(r'landmark\s*(?::|is|=)\s*(.+?)(?:$|\.|\n)', user_input, re.IGNORECASE)
                if landmark_match:
                    landmark = landmark_match.group(1).strip()
                
                # If we found any information, return it
                if any([length, breadth, height, landmark]):
                    # Calculate area if possible
                    area = None
                    if length and breadth:
                        area = length * breadth
                        
                    # Determine missing fields
                    missing_fields = []
                    if length is None:
                        missing_fields.append("length")
                    if breadth is None:
                        missing_fields.append("breadth")
                    if height is None:
                        missing_fields.append("height")
                        
                    return {
                        "length": length,
                        "breadth": breadth,
                        "height": height,
                        "area": area,
                        "landmarks": landmark or "",
                        "rental_price": None,
                        "terms_cond": "",
                        "facilities": [],
                        "missing_fields": missing_fields
                    }
                
                # Check for terms and conditions specifically
                if "terms" in user_input.lower() or "condition" in user_input.lower() or "leasable" in user_input.lower():
                    terms_match = re.search(r"['\"]([^'\"]+)['\"]", user_input)
                    if terms_match:
                        return {
                            "length": None,
                            "breadth": None,
                            "height": None,
                            "area": None,
                            "landmarks": "",
                            "rental_price": None,
                            "terms_cond": terms_match.group(1),
                            "facilities": [],
                            "missing_fields": []
                        }
            except Exception as inner_e:
                print(f"Fallback extraction failed: {str(inner_e)}")
            
            # Default error response if all else fails
            return {
                "message": "I'm having trouble understanding your warehouse details. Could you describe it more clearly? For example: 'My warehouse is 30 feet long, 20 feet wide, and 15 feet high'",
                "data": None
            }