import os
import json
import google.generativeai as genai
from pathlib import Path
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Tuple
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InsiderTradingAnalyzer:
    def __init__(self, api_key=None, json_folder="gemini_form4"):
        """
        Initialize Insider Trading Analyzer with Gemini API
        
        Args:
            api_key (str): Google Gemini API key
            json_folder (str): Path to folder containing Form 4 JSON files
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("API key must be provided either as parameter or GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.json_folder = Path(json_folder)

    def extract_company_and_dates(self, user_query: str) -> Dict:
        """
        Extract company name and dates from user query using LLM
        """
        extraction_prompt = """You are an expert SEC Form 4 insider trading analyst. Extract company name and dates from user queries using EXACT reference mappings.

## EXACT COMPANY NAMES (use these exact formats for JSON matching):
- Apple_Inc (Apple Inc → Apple_Inc in JSON files)
- MICROSOFT_CORP (Microsoft Corporation → MICROSOFT_CORP in JSON files)
- NVIDIA_CORP (NVIDIA Corporation → NVIDIA_CORP in JSON files)
- Meta_Platforms_Inc (Meta Platforms Inc → Meta_Platforms_Inc in JSON files)
- JPMORGAN_CHASE_&_CO (JPMorgan Chase & Co → JPMORGAN_CHASE_&_CO in JSON files)
- JOHNSON_&_JOHNSON (Johnson & Johnson → JOHNSON_&_JOHNSON in JSON files)
- DoorDash_Inc (DoorDash Inc → DoorDash_Inc in JSON files)
- ROKU_INC (Roku Inc → ROKU_INC in JSON files)
- Zoom_Communications_Inc (Zoom Communications Inc → Zoom_Communications_Inc in JSON files)
- UNITEDHEALTH_GROUP_INC (UnitedHealth Group Inc → UNITEDHEALTH_GROUP_INC in JSON files)

## COMPANY KEYWORDS FOR DETECTION:
- Apple: ["Apple", "AAPL", "iPhone", "Mac", "iPad", "Tim Cook"] → Apple_Inc
- Microsoft: ["Microsoft", "MSFT", "Windows", "Azure", "Office", "Satya Nadella"] → MICROSOFT_CORP
- NVIDIA: ["NVIDIA", "NVDA", "GPU", "AI chips", "Jensen Huang"] → NVIDIA_CORP
- Meta: ["Meta", "Facebook", "META", "Instagram", "WhatsApp", "Mark Zuckerberg"] → Meta_Platforms_Inc
- JPMorgan: ["JPMorgan", "Chase", "JPM", "banking", "Jamie Dimon"] → JPMORGAN_CHASE_&_CO
- Johnson & Johnson: ["J&J", "JNJ", "pharmaceutical", "healthcare", "medical devices"] → JOHNSON_&_JOHNSON
- DoorDash: ["DoorDash", "DASH", "food delivery", "gig economy"] → DoorDash_Inc
- Roku: ["Roku", "streaming", "TV platform"] → ROKU_INC
- Zoom: ["Zoom", "video conferencing", "ZM", "remote work"] → Zoom_Communications_Inc
- UnitedHealth: ["UnitedHealth", "UNH", "health insurance", "healthcare"] → UNITEDHEALTH_GROUP_INC

## ANALYSIS TYPES:
- executive_transactions: CEO, CFO, COO level transactions
- director_activity: Board member transactions
- insider_sentiment: Overall buying vs selling patterns
- large_transactions: Transactions above certain threshold
- stock_options: Option exercises and grants
- recent_activity: Transactions within specific timeframe
- all: All insider transactions

## VALID YEARS: 2020, 2021, 2022, 2023, 2024, 2025

## TIME PERIOD KEYWORDS:
- "latest": most recent available data
- "recent": last 6 months or current year
- Specific months: "January 2024", "March 2023", etc.
- Quarters: "Q1 2024", "fourth quarter 2023", etc.
- Years: "2024", "2023", etc.

Return ONLY JSON with EXACT company name format for JSON matching:

{
  "company": "Exact company name with underscores as shown above",
  "date_range": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  },
  "analysis_type": "specific analysis type from options above",
  "confidence": "high/medium/low"
}

Examples:
"Apple insider trading in February 2021" → {"company": "Apple_Inc", "date_range": {"start_date": "2021-02-01", "end_date": "2021-02-28"}, "analysis_type": "all", "confidence": "high"}
"Microsoft executive transactions in 2024" → {"company": "MICROSOFT_CORP", "date_range": {"start_date": "2024-01-01", "end_date": "2024-12-31"}, "analysis_type": "executive_transactions", "confidence": "high"}
"NVIDIA director activity recent" → {"company": "NVIDIA_CORP", "date_range": {"start_date": "2024-01-01", "end_date": "2024-12-31"}, "analysis_type": "director_activity", "confidence": "medium"}

Query: """
        
        try:
            response = self.model.generate_content(extraction_prompt + user_query)
            if response.text:
                # Clean and parse JSON
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text.split('```json')[1].split('```')[0]
                elif text.startswith('```'):
                    text = text.split('```')[1].split('```')[0]
                    
                result = json.loads(text)
                print(f"✓ Extracted: {result['company']}, dates: {result['date_range']['start_date']} to {result['date_range']['end_date']}")
                return result
        except Exception as e:
            print(f"⚠️ Extraction error: {e}")
        
        # Fallback extraction
        return self._fallback_extraction(user_query)

    def _fallback_extraction(self, user_query: str) -> Dict:
        """Simple regex-based fallback extraction with correct naming format"""
        companies = {
            "apple": "Apple_Inc",
            "microsoft": "MICROSOFT_CORP", 
            "nvidia": "NVIDIA_CORP",
            "meta": "Meta_Platforms_Inc",
            "facebook": "Meta_Platforms_Inc",
            "jpmorgan": "JPMORGAN_CHASE_&_CO",
            "chase": "JPMORGAN_CHASE_&_CO",
            "johnson": "JOHNSON_&_JOHNSON",
            "j&j": "JOHNSON_&_JOHNSON",
            "doordash": "DoorDash_Inc",
            "roku": "ROKU_INC",
            "zoom": "Zoom_Communications_Inc",
            "unitedhealth": "UNITEDHEALTH_GROUP_INC"
        }
        
        query_lower = user_query.lower()
        company = None
        
        for key, name in companies.items():
            if key in query_lower:
                company = name
                break
        
        # Extract year/month patterns
        import re
        dates = re.findall(r'(\w+)\s+(\d{4})', user_query)
        if dates:
            month_name, year = dates[0]
            month_map = {"january": 1, "february": 2, "march": 3, "april": 4, 
                        "may": 5, "june": 6, "july": 7, "august": 8,
                        "september": 9, "october": 10, "november": 11, "december": 12}
            
            month_num = month_map.get(month_name.lower(), 1)
            start_date = f"{year}-{month_num:02d}-01"
            
            # Calculate end date (last day of month)
            if month_num == 12:
                next_month = f"{int(year)+1}-01-01"
            else:
                next_month = f"{year}-{month_num+1:02d}-01"
            
            from datetime import datetime, timedelta
            end_date = (datetime.strptime(next_month, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            start_date = "2021-01-01"
            end_date = "2021-12-31"
        
        return {
            "company": company or "Unknown Company",
            "date_range": {"start_date": start_date, "end_date": end_date},
            "confidence": "medium" if company else "low"
        }

    def find_company_file(self, company_name: str) -> Optional[Path]:
        """Find JSON file for company"""
        if not self.json_folder.exists():
            print(f"❌ Folder not found: {self.json_folder}")
            return None
        
        json_files = list(self.json_folder.glob("*.json"))
        print(f"📁 Available files: {[f.stem for f in json_files]}")
        
        # Normalize and search
        normalized_company = company_name.lower().replace(" ", "").replace("inc", "").replace("corp", "").replace(".", "")
        
        for file in json_files:
            normalized_file = file.stem.lower().replace("_", "").replace("form4", "")
            if normalized_company[:5] in normalized_file or normalized_file[:5] in normalized_company:
                print(f"✓ Found match: {file}")
                return file
        
        print(f"❌ No file found for: {company_name}")
        return None

    def analyze_filings(self, json_file: Path, start_date: str, end_date: str, query: str) -> str:
        """Analyze the Form 4 filings"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            relevant_filings = []
            
            # Extract relevant filings within date range - handle the nested structure
            for company_key, company_data in data.items():
                if isinstance(company_data, dict):
                    for year_key, year_data in company_data.items():
                        if isinstance(year_data, list):  # Year contains list of filings
                            for filing in year_data:
                                if isinstance(filing, dict):
                                    filing_date = filing.get('FILING_DATE', '')
                                    if self._is_date_in_range(filing_date, start_date, end_date):
                                        relevant_filings.append(filing)
                                        print(f"✓ Found relevant filing dated: {filing_date}")
            
            print(f"📊 Found {len(relevant_filings)} relevant filings")
            
            if not relevant_filings:
                return f"No insider trading filings found in the specified date range ({start_date} to {end_date})"
            
            # Analyze with Gemini
            analysis_prompt = f"""Analyze these SEC Form 4 insider trading filings and answer the user's query.

User Query: {query}
Date Range: {start_date} to {end_date}

Form 4 Data:
{json.dumps(relevant_filings[:10], indent=2)}  # Limit to avoid token limits

Provide a comprehensive analysis including:
1. Summary of filing activity
2. Key insiders involved (names, titles, relationships)  
3. Transaction details (if any transactions exist)
4. Notable patterns or trends
5. Any significant observations

Be specific about dates, names, titles, and transaction amounts. If no actual trades occurred, explain what the filings show."""
            
            response = self.model.generate_content(analysis_prompt)
            return response.text if response.text else "Analysis failed"
            
        except Exception as e:
            return f"Error analyzing filings: {str(e)}"

    def _is_date_in_range(self, date_str: str, start_date: str, end_date: str) -> bool:
        """Check if date string falls within range"""
        try:
            # Handle various date formats
            if len(date_str) == 10 and '-' in date_str:  # YYYY-MM-DD
                return start_date <= date_str <= end_date
            elif len(date_str) == 8:  # YYYYMMDD
                formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                return start_date <= formatted <= end_date
            return False
        except:
            return False

    def process_query(self, user_query: str) -> str:
        """Main processing pipeline"""
        print(f"🚀 Processing: {user_query}")
        
        # Step 1: Extract company and dates
        extraction = self.extract_company_and_dates(user_query)
        
        if extraction['confidence'] == 'low':
            return "❌ Could not identify company in query. Please specify a company name."
        
        # Step 2: Find company file
        json_file = self.find_company_file(extraction['company'])
        if not json_file:
            return f"❌ No data file found for {extraction['company']}"
        
        # Step 3: Analyze filings
        start_date = extraction['date_range']['start_date']
        end_date = extraction['date_range']['end_date']
        
        result = self.analyze_filings(json_file, start_date, end_date, user_query)
        
        # Step 4: Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"insider_analysis_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"=== INSIDER TRADING ANALYSIS ===\n")
            f.write(f"Query: {user_query}\n")
            f.write(f"Company: {extraction['company']}\n")
            f.write(f"Date Range: {start_date} to {end_date}\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result)
        
        print(f"✅ Analysis complete! Saved to: {filename}")
        return result


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Analyze insider trading from Form 4 data')
    parser.add_argument('query', help='Your question about insider trading')
    parser.add_argument('-f', '--folder', default='gemini_form4', help='Folder containing JSON files')
    parser.add_argument('-k', '--api-key', help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        analyzer = InsiderTradingAnalyzer(api_key=args.api_key, json_folder=args.folder)
        result = analyzer.process_query(args.query)
        print("\n" + "="*50)
        print("ANALYSIS RESULT:")
        print("="*50)
        print(result[:1000] + "..." if len(result) > 1000 else result)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

# Usage Examples:
"""
python sec_insider_analyzer.py "Show me Apple insider trading in February 2021"
python sec_insider_analyzer.py "What Microsoft insider activity happened in March 2021?"
python sec_insider_analyzer.py "NVIDIA insider trades between January and March 2021"
"""
