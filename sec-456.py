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

class DateBasedSECAnalyzer:
    def __init__(self, api_key=None, json_folder_path=None, json_file_path=None):
        """
        Initialize Date-Based SEC Forms Analyzer with Gemini API
        
        Args:
            api_key (str): Google Gemini API key
            json_folder_path (str): Path to folder containing SEC forms JSON files
            json_file_path (str): Path to specific JSON file (deprecated, use json_folder_path)
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("API key must be provided either as parameter or GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Handle both folder and single file paths for backward compatibility
        if json_folder_path:
            self.json_folder_path = Path(json_folder_path)
            self.json_file_path = None
        elif json_file_path:
            self.json_file_path = Path(json_file_path) 
            self.json_folder_path = None
        else:
            self.json_folder_path = None
            self.json_file_path = None
        
        # Supported SEC forms for insider trading
        self.supported_forms = ["3", "4", "5"]

    def find_company_json_file(self, company_name: str) -> Optional[Path]:
        """
        Find JSON file for the specified company in folder
        
        Args:
            company_name (str): Company name to search for
            
        Returns:
            Optional[Path]: Path to the JSON file if found
        """
        if not self.json_folder_path or not self.json_folder_path.exists():
            print(f"❌ JSON folder not found: {self.json_folder_path}")
            return None
            
        print(f"🔍 Searching for JSON file for: {company_name}")
        
        # List all available JSON files for debugging
        json_files = list(self.json_folder_path.glob("*.json"))
        print(f"📁 Available JSON files: {[f.stem for f in json_files]}")
        
        # Normalize company name for matching
        normalized_search = self._normalize_company_name(company_name)
        
        # Try different matching strategies
        for json_file in json_files:
            file_stem = json_file.stem
            normalized_file = self._normalize_company_name(file_stem)
            
            # Strategy 1: Exact match after normalization
            if normalized_search == normalized_file:
                print(f"✓ Found exact match: {json_file}")
                return json_file
            
            # Strategy 2: Check if search term is in filename
            if normalized_search in normalized_file or normalized_file in normalized_search:
                print(f"✓ Found partial match: {json_file}")
                return json_file
            
            # Strategy 3: Check core company name (first word)
            search_core = normalized_search.split()[0] if normalized_search else ""
            file_core = normalized_file.split()[0] if normalized_file else ""
            if search_core and file_core and (search_core == file_core or len(search_core) > 3 and search_core in file_core):
                print(f"✓ Found core name match: {json_file}")
                return json_file
        
        print(f"❌ No matching file found for: {company_name}")
        return None
    
    def _normalize_company_name(self, name: str) -> str:
        """
        Normalize company name for matching
        """
        if not name:
            return ""
        
        # Convert to lowercase and remove common suffixes/prefixes
        normalized = name.lower()
        
        # Remove common corporate suffixes
        suffixes = [
            " inc.", " inc", " corporation", " corp.", " corp", " company", " co.", " co",
            " ltd.", " ltd", " limited", " llc", " l.l.c.", " plc", " form4", "_form4"
        ]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        
        # Remove extra whitespace and special characters
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized

    def extract_dates_and_company_from_query(self, user_query: str) -> Dict:
        """
        Extract dates and company name from user query using LLM
        
        Args:
            user_query (str): User's query
            
        Returns:
            Dict: Extracted dates, company, and processed query
        """
        extraction_prompt = """You are an expert at extracting dates and company names from SEC-related queries. Your task is to identify and extract ALL dates AND company names mentioned in the user's query.

## TASK
Extract both dates and company information from the following query. Look for:

### DATES:
- Specific dates (e.g., "February 3, 2021", "2021-02-03", "Feb 3 2021")
- Date ranges (e.g., "between January and March 2021", "from 2020 to 2022")
- Relative dates (e.g., "last month", "this year", "Q1 2021")
- Partial dates (e.g., "February 2021", "2021")

### COMPANIES:
- Full company names (e.g., "Apple Inc.", "Microsoft Corporation", "Meta Platforms Inc.")
- Common names (e.g., "Apple", "Microsoft", "Google", "Facebook", "Tesla")
- Stock tickers if mentioned (e.g., "AAPL", "MSFT", "GOOGL")

## OUTPUT FORMAT
Return ONLY a JSON object with this exact structure:

{
  "dates_found": [
    {
      "original_text": "text as found in query",
      "standardized_date": "YYYY-MM-DD format",
      "date_type": "specific/range_start/range_end/partial"
    }
  ],
  "date_range": {
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
  },
  "company": {
    "original_text": "company name as found in query",
    "standardized_name": "standardized company name",
    "confidence": "high/medium/low"
  },
  "processed_query": "user query with dates and company highlighted or cleaned for analysis"
}

## EXAMPLES

Query: "Show me Apple insider trading activity in February 2021"
{
  "dates_found": [
    {
      "original_text": "February 2021",
      "standardized_date": "2021-02-01",
      "date_type": "partial"
    }
  ],
  "date_range": {
    "start_date": "2021-02-01",
    "end_date": "2021-02-28"
  },
  "company": {
    "original_text": "Apple",
    "standardized_name": "Apple Inc.",
    "confidence": "high"
  },
  "processed_query": "Show me [COMPANY: Apple] insider trading activity in [DATE: February 2021]"
}

Now extract dates and company from this query:
"""
        
        try:
            full_prompt = extraction_prompt + f"\nUser Query: {user_query}"
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                response_text = response.text.strip()
                json_result = self._extract_json_from_response(response_text)
                
                if json_result:
                    print(f"✓ Dates and company extracted from query")
                    return json_result
                else:
                    print("⚠️ Could not extract valid JSON from extraction")
                    return self._fallback_extraction(user_query)
            else:
                raise Exception("Empty response from extraction")
                
        except Exception as e:
            print(f"⚠️ Error in extraction: {str(e)}")
            return self._fallback_extraction(user_query)

    def _fallback_extraction(self, user_query: str) -> Dict:
        """
        Fallback method for date and company extraction using regex
        """
        print("🔄 Using fallback extraction...")
        
        # Extract company names (more comprehensive list)
        company_mapping = {
            "apple": "Apple Inc.",
            "microsoft": "Microsoft Corporation", 
            "google": "Alphabet Inc.",
            "amazon": "Amazon.com Inc.",
            "tesla": "Tesla Inc.",
            "meta": "Meta Platforms Inc.",
            "facebook": "Meta Platforms Inc.",
            "nvidia": "NVIDIA Corporation",
            "intel": "Intel Corporation",
            "amd": "Advanced Micro Devices Inc.",
            "johnson": "Johnson & Johnson",
            "jpmorgan": "JPMorgan Chase & Co.",
            "doordash": "DoorDash Inc.",
            "roku": "Roku Inc.",
            "zoom": "Zoom Communications Inc.",
            "unitedhealth": "UnitedHealth Group Inc."
        }
        
        query_lower = user_query.lower()
        company = None
        company_original = ""
        
        for keyword, full_name in company_mapping.items():
            if keyword in query_lower:
                company = full_name
                company_original = keyword.title()
                break
        
        # Extract dates using existing fallback logic
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY
            r'\b(\w+ \d{1,2}, \d{4})\b',  # Month DD, YYYY
            r'\b(\w+ \d{4})\b',  # Month YYYY
            r'\b(\d{4})\b',  # Just year
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, user_query)
            for match in matches:
                standardized = self._standardize_date(match)
                if standardized:
                    dates_found.append({
                        "original_text": match,
                        "standardized_date": standardized,
                        "date_type": "partial"
                    })
        
        date_range = None
        if dates_found:
            sorted_dates = sorted([d["standardized_date"] for d in dates_found if d["standardized_date"]])
            date_range = {
                "start_date": sorted_dates[0] if sorted_dates else None,
                "end_date": sorted_dates[-1] if sorted_dates else None
            }
        else:
            date_range = {"start_date": None, "end_date": None}
        
        result = {
            "dates_found": dates_found,
            "date_range": date_range,
            "processed_query": user_query
        }
        
        if company:
            result["company"] = {
                "original_text": company_original,
                "standardized_name": company,
                "confidence": "medium"
            }
        
        return result
        """
        Extract dates and company name from user query using LLM
        
        Args:
            user_query (str): User's query
            
        Returns:
            Dict: Extracted dates, company, and processed query
        """
        extraction_prompt = """You are an expert at extracting dates and company names from SEC-related queries. Your task is to identify and extract ALL dates AND company names mentioned in the user's query.

## TASK
Extract both dates and company information from the following query. Look for:

### DATES:
- Specific dates (e.g., "February 3, 2021", "2021-02-03", "Feb 3 2021")
- Date ranges (e.g., "between January and March 2021", "from 2020 to 2022")
- Relative dates (e.g., "last month", "this year", "Q1 2021")
- Partial dates (e.g., "February 2021", "2021")

### COMPANIES:
- Full company names (e.g., "Apple Inc.", "Microsoft Corporation", "Meta Platforms Inc.")
- Common names (e.g., "Apple", "Microsoft", "Google", "Facebook", "Tesla")
- Stock tickers if mentioned (e.g., "AAPL", "MSFT", "GOOGL")

## OUTPUT FORMAT
Return ONLY a JSON object with this exact structure:

{
  "dates_found": [
    {
      "original_text": "text as found in query",
      "standardized_date": "YYYY-MM-DD format",
      "date_type": "specific/range_start/range_end/partial"
    }
  ],
  "date_range": {
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
  },
  "company": {
    "original_text": "company name as found in query",
    "standardized_name": "standardized company name",
    "confidence": "high/medium/low"
  },
  "processed_query": "user query with dates and company highlighted or cleaned for analysis"
}

## EXAMPLES

Query: "Show me Apple insider trading activity in February 2021"
{
  "dates_found": [
    {
      "original_text": "February 2021",
      "standardized_date": "2021-02-01",
      "date_type": "partial"
    }
  ],
  "date_range": {
    "start_date": "2021-02-01",
    "end_date": "2021-02-28"
  },
  "company": {
    "original_text": "Apple",
    "standardized_name": "Apple Inc.",
    "confidence": "high"
  },
  "processed_query": "Show me [COMPANY: Apple] insider trading activity in [DATE: February 2021]"
}

Query: "What happened at Microsoft between January and March 2021?"
{
  "dates_found": [
    {
      "original_text": "January 2021",
      "standardized_date": "2021-01-01",
      "date_type": "range_start"
    },
    {
      "original_text": "March 2021", 
      "standardized_date": "2021-03-31",
      "date_type": "range_end"
    }
  ],
  "date_range": {
    "start_date": "2021-01-01",
    "end_date": "2021-03-31"
  },
  "company": {
    "original_text": "Microsoft",
    "standardized_name": "Microsoft Corporation",
    "confidence": "high"
  },
  "processed_query": "What happened at [COMPANY: Microsoft] between [DATE RANGE: January and March 2021]?"
}

Now extract dates and company from this query:
"""
  "date_range": {
    "start_date": "2021-02-03",
    "end_date": "2021-02-03"
  },
  "processed_query": "Show me insider trading activity on [DATE: February 3, 2021]"
}

Query: "What happened between January and March 2021?"
{
  "dates_found": [
    {
      "original_text": "January 2021",
      "standardized_date": "2021-01-01",
      "date_type": "range_start"
    },
    {
      "original_text": "March 2021", 
      "standardized_date": "2021-03-31",
      "date_type": "range_end"
    }
  ],
  "date_range": {
    "start_date": "2021-01-01",
    "end_date": "2021-03-31"
  },
  "processed_query": "What happened between [DATE RANGE: January and March 2021]?"
}
"""
        
        try:
            full_prompt = extraction_prompt + f"\nUser Query: {user_query}"
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                response_text = response.text.strip()
                json_result = self._extract_json_from_response(response_text)
                
                if json_result:
                    print(f"✓ Dates and company extracted from query")
                    return json_result
                else:
                    print("⚠️ Could not extract valid JSON from extraction")
                    return self._fallback_extraction(user_query)
            else:
                raise Exception("Empty response from extraction")
                
        except Exception as e:
            print(f"⚠️ Error in extraction: {str(e)}")
            return self._fallback_extraction(user_query)

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        json_patterns = [
            r'\{.*\}',
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        return None

    def _fallback_date_extraction(self, user_query: str) -> Dict:
        """
        Fallback method for date extraction using regex
        """
        print("🔄 Using fallback date extraction...")
        
        # Common date patterns
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY
            r'\b(\w+ \d{1,2}, \d{4})\b',  # Month DD, YYYY
            r'\b(\d{4})\b',  # Just year
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, user_query)
            for match in matches:
                dates_found.append({
                    "original_text": match,
                    "standardized_date": self._standardize_date(match),
                    "date_type": "specific"
                })
        
        date_range = None
        if dates_found:
            sorted_dates = sorted([d["standardized_date"] for d in dates_found if d["standardized_date"]])
            date_range = {
                "start_date": sorted_dates[0] if sorted_dates else None,
                "end_date": sorted_dates[-1] if sorted_dates else None
            }
        else:
            date_range = {"start_date": None, "end_date": None}
        
        return {
            "dates_found": dates_found,
            "date_range": date_range,
            "processed_query": user_query
        }

    def _standardize_date(self, date_str: str) -> Optional[str]:
        """
        Standardize date string to YYYY-MM-DD format
        """
        try:
            # Try different date formats
            formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%Y"
            ]
            
            for fmt in formats:
                try:
                    if fmt == "%Y":
                        dt = datetime.strptime(date_str, fmt)
                        return f"{dt.year}-01-01"  # Use January 1st for year-only dates
                    else:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            return None
        except:
            return None

    def find_relevant_sections_by_date(self, dates_data: Dict) -> Dict:
        """
        Find relevant sections in JSON file based on extracted dates
        Handles JSON structure with arrays of filings under year keys
        
        Args:
            dates_data (Dict): Result from date extraction
            
        Returns:
            Dict: Relevant sections from JSON file
        """
        if not self.json_file_path or not self.json_file_path.exists():
            return {"error": f"JSON file not found: {self.json_file_path}"}
        
        try:
            print(f"📖 Reading JSON file: {self.json_file_path}")
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            date_range = dates_data.get("date_range", {})
            start_date = date_range.get("start_date")
            end_date = date_range.get("end_date")
            
            print(f"🔍 Searching for data between {start_date} and {end_date}")
            
            relevant_sections = {}
            
            # Navigate through JSON structure to find date-based entries
            for company, company_data in data.items():
                print(f"📊 Analyzing company: {company}")
                company_filings = []
                
                # Handle different JSON structures
                if isinstance(company_data, dict):
                    # Structure: {year: [filings]} or {year: {data}}
                    for year_key, year_data in company_data.items():
                        if isinstance(year_data, list):
                            # Array of filings under year key
                            for filing in year_data:
                                if self._is_filing_in_date_range(filing, start_date, end_date):
                                    company_filings.append(filing)
                                    filing_date = filing.get("FILING_DATE", "unknown")
                                    print(f"✓ Found relevant filing dated: {filing_date}")
                        elif isinstance(year_data, dict):
                            # Single filing or other structure
                            if self._is_filing_in_date_range(year_data, start_date, end_date):
                                company_filings.append(year_data)
                                filing_date = year_data.get("FILING_DATE", year_key)
                                print(f"✓ Found relevant entry for: {filing_date}")
                elif isinstance(company_data, list):
                    # Direct array of filings
                    for filing in company_data:
                        if self._is_filing_in_date_range(filing, start_date, end_date):
                            company_filings.append(filing)
                            filing_date = filing.get("FILING_DATE", "unknown")
                            print(f"✓ Found relevant filing dated: {filing_date}")
                
                if company_filings:
                    relevant_sections[company] = {
                        "filings": company_filings,
                        "total_filings": len(company_filings)
                    }
            
            if not relevant_sections:
                print("⚠️ No relevant sections found for the specified dates")
                # Let's show what dates we actually found for debugging
                self._debug_available_dates(data)
                return {"error": "No data found for the specified date range"}
            
            print(f"📋 Found {len(relevant_sections)} companies with relevant data")
            total_filings = sum(section["total_filings"] for section in relevant_sections.values())
            print(f"📄 Total relevant filings: {total_filings}")
            
            return {"sections": relevant_sections, "date_info": dates_data}
            
        except Exception as e:
            print(f"❌ Error reading JSON file: {str(e)}")
            return {"error": f"Error reading JSON file: {str(e)}"}

    def _is_filing_in_date_range(self, filing: Dict, start_date: str, end_date: str) -> bool:
        """
        Check if a filing falls within the specified date range
        """
        if not start_date or not end_date:
            return True  # If no date range specified, include all
        
        if not isinstance(filing, dict):
            return False
        
        # Get filing date
        filing_date = filing.get("FILING_DATE")
        if not filing_date:
            return False
        
        # Standardize the filing date
        standardized_date = self._standardize_date(filing_date)
        if not standardized_date:
            return False
        
        # Check if it falls within range
        return start_date <= standardized_date <= end_date

    def _debug_available_dates(self, data: Dict):
        """
        Debug function to show available dates in the JSON for troubleshooting
        """
        print("🔍 Debug: Available dates in JSON:")
        
        for company, company_data in data.items():
            print(f"  Company: {company}")
            dates_found = []
            
            if isinstance(company_data, dict):
                for year_key, year_data in company_data.items():
                    if isinstance(year_data, list):
                        for filing in year_data:
                            if isinstance(filing, dict) and "FILING_DATE" in filing:
                                dates_found.append(filing["FILING_DATE"])
                    elif isinstance(year_data, dict) and "FILING_DATE" in year_data:
                        dates_found.append(year_data["FILING_DATE"])
            elif isinstance(company_data, list):
                for filing in company_data:
                    if isinstance(filing, dict) and "FILING_DATE" in filing:
                        dates_found.append(filing["FILING_DATE"])
            
            if dates_found:
                print(f"    Available filing dates: {sorted(set(dates_found))}")
            else:
                print(f"    No FILING_DATE fields found")

    def _extract_date_from_key_or_entry(self, key: str, entry_data: Dict) -> Optional[str]:
        """
        Extract date from key or entry data (legacy method for compatibility)
        """
        # Try to parse the key as a date
        standardized_key_date = self._standardize_date(key)
        if standardized_key_date:
            return standardized_key_date
        
        # Look for FILING_DATE in entry data
        if isinstance(entry_data, dict):
            filing_date = entry_data.get("FILING_DATE")
            if filing_date:
                return self._standardize_date(filing_date)
        
        return None

    def analyze_sec_forms(self, processed_query: str, relevant_sections: Dict) -> str:
        """
        Analyze SEC forms data using specialized system prompt
        Handles the new structure with arrays of filings
        
        Args:
            processed_query (str): Processed user query
            relevant_sections (Dict): Relevant sections from JSON
            
        Returns:
            str: Analysis results
        """
        analysis_prompt = """# SEC Forms 3/4/5 Analysis Expert

You are a highly experienced SEC filing expert specializing in insider trading forms (Forms 3, 4, and 5). You have deep expertise in:
- SEC insider trading regulations and requirements
- Forms 3, 4, and 5 structure and content
- Insider trading patterns and analysis
- Corporate governance and insider relationships
- Securities law and compliance requirements

## YOUR ROLE
Analyze the provided SEC Forms data and respond to the user's query with comprehensive, accurate insights based STRICTLY on the information provided in the JSON data.

## DATA STRUCTURE
The JSON contains companies with arrays of filings. Each filing has:
- FORM: The type of SEC form (3, 4, or 5)
- INSIDER_INFO: Details about the insider (name, title, relationship)
- FILING_DATE: When the form was filed
- TRADING_TABLES: Transaction details (if any)

## CRITICAL INSTRUCTIONS
- **NO HALLUCINATION**: Use ONLY information present in the provided JSON data
- **NO EXTERNAL INFORMATION**: Do not add information not found in the JSON
- **PRESERVE ACCURACY**: Maintain exact dates, names, titles, and numbers as provided
- **COMPREHENSIVE STRUCTURE**: Organize the information in a clear, professional manner
- **COMPLETE COVERAGE**: Address all aspects of the user's query using available data
- **COUNT ACCURATELY**: When summarizing, count actual filings in the data

## ANALYSIS GUIDELINES

### Content Analysis Approach
1. **Thorough Examination**: Carefully analyze all provided JSON sections and filings
2. **Date-Focused Analysis**: Pay special attention to filing dates and transaction dates
3. **Insider Information**: Extract and present insider details (names, titles, relationships)
4. **Transaction Details**: Analyze trading tables and transaction information
5. **Pattern Recognition**: Identify trends or patterns in the filing data
6. **Compliance Focus**: Note any compliance-related information

### Response Structure
1. **Executive Summary**: Brief overview of key findings and filing counts
2. **Filing Overview**: Summary of forms found (types, dates, count)
3. **Insider Analysis**: Details about the individuals who filed
4. **Transaction Summary**: Analysis of any trading activity found
5. **Key Observations**: Important patterns or notable information from the data
6. **Detailed Breakdown**: Filing-by-filing analysis if relevant

### Response Quality Standards
- **Accuracy**: Base all analysis strictly on provided JSON data
- **Clarity**: Use professional, accessible language
- **Completeness**: Cover all relevant aspects found in the data
- **Organization**: Present information in logical, scannable format
- **Specificity**: Include exact dates, names, and figures from the JSON
- **Quantification**: Count and summarize filings, insiders, transactions

## EXAMPLE ANALYSIS STRUCTURE
```
# Executive Summary
Found [X] SEC Form [types] filings from [date range] for [companies].

# Filing Overview  
- Total filings: [count]
- Form types: [list]
- Date range: [start] to [end]
- Companies: [list]

# Insider Analysis
[Details about each insider who filed]

# Transaction Activity
[Summary of any trading tables/transactions found]

# Key Observations
[Notable patterns or insights from the data]
```

## JSON DATA TO ANALYZE:
---
"""
        
        try:
            # Format the sections for better analysis
            sections_json = json.dumps(relevant_sections, indent=2)
            full_prompt = analysis_prompt + sections_json + f"\n\n## USER QUERY TO ANALYZE:\n{processed_query}"
            
            print("🔍 Analyzing SEC forms data with Gemini...")
            
            # Add some stats for the user
            total_filings = sum(section.get("total_filings", 0) for section in relevant_sections.values())
            companies_count = len(relevant_sections)
            print(f"📊 Sending {total_filings} filings from {companies_count} companies for analysis")
            
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                print("✓ SEC forms analysis completed")
                return response.text
            else:
                return "Error: Empty response from analysis"
                
        except Exception as e:
            return f"Error during SEC forms analysis: {str(e)}"

    def save_analysis_result(self, result: str, query: str, dates_info: Dict) -> str:
        """
        Save analysis result to txt file
        
        Args:
            result (str): Analysis result
            query (str): Original query
            dates_info (Dict): Date extraction information
            
        Returns:
            str: Path to saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create safe filename from query
            safe_query = re.sub(r'[^\w\s-]', '', query)[:50]
            safe_query = re.sub(r'[-\s]+', '_', safe_query)
            
            filename = f"sec_forms_analysis_{safe_query}_{timestamp}.txt"
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"=== SEC FORMS ANALYSIS RESULT ===\n")
                file.write(f"Query: {query}\n")
                file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"JSON File: {self.json_file_path}\n")
                
                # Add date information
                if dates_info.get("dates_found"):
                    file.write(f"Dates Analyzed: ")
                    for date_item in dates_info["dates_found"]:
                        file.write(f"{date_item['original_text']} ")
                    file.write("\n")
                
                date_range = dates_info.get("date_range", {})
                if date_range.get("start_date"):
                    file.write(f"Date Range: {date_range['start_date']} to {date_range['end_date']}\n")
                
                file.write("="*60 + "\n\n")
                file.write(result)
            
            print(f"✓ Analysis saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error saving result: {str(e)}")
            return ""

    def process_date_based_query(self, user_query: str) -> Dict:
        """
        Complete date-based SEC forms query processing pipeline
        
        Args:
            user_query (str): User's original query
            
        Returns:
            Dict: Processing results and file paths
        """
        try:
            print(f"🚀 Processing date-based SEC query: {user_query}")
            
            # Step 1: Extract dates and company from query
            extraction_data = self.extract_dates_and_company_from_query(user_query)
            processed_query = extraction_data.get("processed_query", user_query)
            
            print(f"📅 Date extraction results:")
            if extraction_data.get("dates_found"):
                for date_item in extraction_data["dates_found"]:
                    print(f"  Found: {date_item['original_text']} -> {date_item['standardized_date']}")
            
            date_range = extraction_data.get("date_range", {})
            if date_range.get("start_date"):
                print(f"  Date range: {date_range['start_date']} to {date_range['end_date']}")
            
            # Step 2: Handle company detection and JSON file selection
            if self.json_folder_path and extraction_data.get("company"):
                company_info = extraction_data["company"]
                print(f"🏢 Company detected: {company_info['standardized_name']}")
                
                # Find the JSON file for this company
                json_file = self.find_company_json_file(company_info["standardized_name"])
                if not json_file:
                    return {
                        "success": False,
                        "error": f"No JSON file found for company: {company_info['standardized_name']}"
                    }
                
                # Temporarily set the JSON file path
                original_json_file = self.json_file_path
                self.json_file_path = json_file
            elif not self.json_file_path:
                return {
                    "success": False,
                    "error": "No company detected in query and no JSON file specified. Please mention a company name."
                }
            
            # Step 3: Find relevant sections in JSON file
            sections_result = self.find_relevant_sections_by_date(extraction_data)
            
            if "error" in sections_result:
                return {
                    "success": False,
                    "error": sections_result["error"]
                }
            
            relevant_sections = sections_result["sections"]
            print(f"📋 Found relevant data for {len(relevant_sections)} companies")
            
            # Step 4: Analyze SEC forms data
            analysis_result = self.analyze_sec_forms(processed_query, relevant_sections)
            
            # Step 5: Save result to file
            output_file = self.save_analysis_result(analysis_result, user_query, extraction_data)
            
            # Restore original JSON file path if we temporarily changed it
            if self.json_folder_path and extraction_data.get("company"):
                self.json_file_path = original_json_file
            
            return {
                "success": True,
                "dates_extracted": extraction_data,
                "processed_query": processed_query,
                "relevant_sections": relevant_sections,
                "analysis_result": analysis_result,
                "output_file": output_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }

    def test_setup(self) -> Dict:
        """
        Test the setup to ensure everything is working
        """
        print("🧪 Testing Date-Based SEC Analyzer setup...")
        
        results = {
            "api_connection": False,
            "json_file_access": False,
            "date_extraction_test": False
        }
        
        # Test 1: API Connection
        try:
            test_response = self.model.generate_content("Hello, respond with just 'OK'")
            if test_response.text and "OK" in test_response.text:
                results["api_connection"] = True
                print("✅ API connection successful")
            else:
                print("❌ API connection failed - unexpected response")
        except Exception as e:
            print(f"❌ API connection failed: {str(e)}")
        
        # Test 2: JSON file access
        if self.json_file_path and self.json_file_path.exists():
            try:
                with open(self.json_file_path, 'r') as f:
                    json.load(f)
                results["json_file_access"] = True
                print(f"✅ JSON file accessible: {self.json_file_path}")
            except Exception as e:
                print(f"❌ JSON file error: {str(e)}")
        else:
            print(f"❌ JSON file not found: {self.json_file_path}")
        
        # Test 3: Date extraction
        try:
            test_query = "Show me activity on February 3, 2021"
            dates_result = self.extract_dates_from_query(test_query)
            if dates_result and dates_result.get("dates_found"):
                results["date_extraction_test"] = True
                print("✅ Date extraction working correctly")
            else:
                print("❌ Date extraction failed")
        except Exception as e:
            print(f"❌ Date extraction test failed: {str(e)}")
        
        # Summary
        print("\n📊 Setup Test Results:")
        for test, result in results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test}: {result}")
        
        return results


def main():
    """
    Command line interface for Date-Based SEC Analyzer
    """
    parser = argparse.ArgumentParser(description='Analyze SEC Forms by Date using AI')
    parser.add_argument('query', nargs='?', help='Your date-based question about SEC filings')
    parser.add_argument('-k', '--api-key', help='Google Gemini API key')
    parser.add_argument('-j', '--json-file', help='Path to JSON file containing SEC forms data (deprecated)')
    parser.add_argument('-f', '--folder', default='gemini_form4', help='Path to folder containing SEC forms JSON files')
    parser.add_argument('-t', '--test', action='store_true', help='Run setup test')
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer with folder support
        if args.json_file:
            # Backward compatibility: single file mode
            analyzer = DateBasedSECAnalyzer(api_key=args.api_key, json_file_path=args.json_file)
        else:
            # New mode: folder mode
            analyzer = DateBasedSECAnalyzer(api_key=args.api_key, json_folder_path=args.folder)
        
        # Run test if requested
        if args.test:
            analyzer.test_setup()
            return
        
        # Check if query provided
        if not args.query:
            parser.error("Please provide a query or use --test to test setup")
        
        # Process query
        result = analyzer.process_date_based_query(args.query)
        
        if result["success"]:
            print(f"\n✅ Analysis completed successfully!")
            print(f"📄 Result saved to: {result['output_file']}")
            
            # Show summary of findings
            if result.get("relevant_sections"):
                print(f"📊 Analyzed data from {len(result['relevant_sections'])} companies")
        else:
            print(f"\n❌ Error: {result['error']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()


# Usage Examples:
"""
# Command line usage:
python date_sec_analyzer.py "Show me insider trading on February 3, 2021" -j "path/to/forms_data.json"
python date_sec_analyzer.py "What happened between January and March 2021?" -j "insider_data.json" -k "your_api_key"

# Module usage:
from date_sec_analyzer import DateBasedSECAnalyzer

analyzer = DateBasedSECAnalyzer(json_file_path="forms_data.json")
result = analyzer.process_date_based_query("Show me activity on 2021-02-03")
print(result["analysis_result"])
"""