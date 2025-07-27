import googlemaps
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

class MiamiBusinessScraper:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Please set GOOGLE_MAPS_API_KEY in your .env file")
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.miami_bounds = {
            'north': 25.8557,
            'south': 25.6815,
            'east': -80.1161,
            'west': -80.3198
        }
    
    def search_businesses(self, queries=None, max_results=100):
        """Search for businesses in Miami using multiple queries"""
        if queries is None:
            queries = ["restaurant", "store", "service", "office", "shop", "clinic", "salon", "gym", "hotel", "market"]
        
        all_businesses = []
        seen_places = set()
        
        for i, query in enumerate(queries):
            if len(all_businesses) >= max_results:
                break
                
            print(f"Searching with query '{query}' ({i+1}/{len(queries)})...")
            businesses = self._search_single_query(query, max_results - len(all_businesses))
            
            # Remove duplicates
            for business in businesses:
                business_key = f"{business['business_name']}_{business['phone_number']}"
                if business_key not in seen_places:
                    seen_places.add(business_key)
                    all_businesses.append(business)
            
            print(f"Total unique businesses found: {len(all_businesses)}")
            
            if len(all_businesses) >= max_results:
                break
        
        return all_businesses[:max_results]
    
    def _search_single_query(self, query, max_results):
        """Search for businesses with a single query"""
        businesses = []
        
        try:
            places_result = self.gmaps.places_nearby(
                location=(25.7617, -80.1918),  # Miami coordinates
                radius=50000,  # 50km radius
                keyword=query,
                type='establishment'
            )
            
            for place in places_result.get('results', []):
                if len(businesses) >= max_results:
                    break
                    
                business_data = self._extract_business_info(place)
                if business_data:
                    businesses.append(business_data)
            
            # Handle pagination
            next_page_token = places_result.get('next_page_token')
            while next_page_token and len(businesses) < max_results:
                time.sleep(2)  # Required delay for next page token
                
                try:
                    places_result = self.gmaps.places_nearby(
                        page_token=next_page_token
                    )
                    
                    for place in places_result.get('results', []):
                        if len(businesses) >= max_results:
                            break
                            
                        business_data = self._extract_business_info(place)
                        if business_data:
                            businesses.append(business_data)
                    
                    next_page_token = places_result.get('next_page_token')
                    
                except Exception as e:
                    print(f"Error fetching next page: {e}")
                    break
            
        except Exception as e:
            print(f"Error searching businesses with query '{query}': {e}")
            return []
        
        return businesses
    
    def _extract_business_info(self, place):
        """Extract business name and phone from place data"""
        try:
            place_id = place.get('place_id')
            if not place_id:
                return None
            
            # Get detailed place information
            details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_phone_number', 'international_phone_number']
            )
            
            place_details = details.get('result', {})
            
            business_info = {
                'business_name': place_details.get('name', 'N/A'),
                'phone_number': (
                    place_details.get('formatted_phone_number') or 
                    place_details.get('international_phone_number') or 
                    'N/A'
                )
            }
            
            # Only return if we have both name and phone
            if business_info['business_name'] != 'N/A' and business_info['phone_number'] != 'N/A':
                return business_info
            
        except Exception as e:
            print(f"Error extracting business info: {e}")
        
        return None
    
    def save_to_json(self, businesses, filename="miami_businesses.json"):
        """Save businesses to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(businesses, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved {len(businesses)} businesses to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

def main():
    try:
        scraper = MiamiBusinessScraper()
        
        print("Searching for 10,000 businesses in Miami...")
        print("This will take several minutes due to API rate limits...")
        businesses = scraper.search_businesses(max_results=10000)
        
        if businesses:
            print(f"Found {len(businesses)} businesses with phone numbers")
            
            # Display first few results
            for i, business in enumerate(businesses[:5]):
                print(f"{i+1}. {business['business_name']} - {business['phone_number']}")
            
            if len(businesses) > 5:
                print(f"... and {len(businesses) - 5} more")
            
            # Save to JSON
            scraper.save_to_json(businesses)
        else:
            print("No businesses found")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please create a .env file with your Google Maps API key:")
        print("GOOGLE_MAPS_API_KEY=your_api_key_here")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()