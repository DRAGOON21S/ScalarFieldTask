#!/usr/bin/env python3
"""
Test script for SEC Analysis API
"""

import requests
import json
import time

def test_api():
    url = "http://localhost:5000/api/analyze"
    
    # Test query
    test_query = "What are Apple's main business segments?"
    
    print(f"🧪 Testing API with query: {test_query}")
    print("=" * 60)
    
    try:
        # Send request
        response = requests.post(url, json={"query": test_query}, timeout=180)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ API Response Structure:")
            print(f"  - Query: {data.get('query', 'N/A')}")
            print(f"  - Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"  - Analysis Directory: {data.get('analysis_directory', 'N/A')}")
            print(f"  - Combined Analysis Length: {len(data.get('combined_analysis', ''))}")
            print(f"  - Individual Analyses: {list(data.get('individual_analyses', {}).keys())}")
            print(f"  - Sources Count: {len(data.get('sources', []))}")
            print(f"  - Analysis Files: {len(data.get('analysis_files', []))}")
            
            # Show preview of combined analysis
            combined = data.get('combined_analysis', '')
            if combined:
                print("\n📄 Combined Analysis Preview:")
                print(combined[:500] + "..." if len(combined) > 500 else combined)
            else:
                print("\n❌ No combined analysis content!")
                
            # Show individual analyses status
            individual = data.get('individual_analyses', {})
            print(f"\n📊 Individual Analyses Status:")
            for analysis_type, content in individual.items():
                content_length = len(content) if content else 0
                status = "✅ Has content" if content_length > 50 else "❌ Empty/minimal"
                print(f"  - {analysis_type}: {status} ({content_length} chars)")
            
        else:
            print(f"❌ API Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 3 minutes")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 SEC Analysis API Test")
    test_api()
