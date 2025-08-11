import os
import json
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SECFormsTools:
    def __init__(self, api_key=None, reports_folder="gemini_10k"):
        """
        Initialize SEC Forms Tools with Gemini API
        
        Args:
            api_key (str): Google Gemini API key
            reports_folder (str): Path to folder containing JSON reports
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("API key must be provided either as parameter or GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.reports_folder = Path(reports_folder)
        
        # Ensure reports folder exists
        self.reports_folder.mkdir(exist_ok=True)
        
        # Define valid categories for each form type
        self.form_categories = {
            "10-K": [
                "Part I: Business and Risk Factors",
                "Part II: Financial Information", 
                "Part III: Governance",
                "Part IV: Exhibits and Schedules"
            ]
            # Add more form types later: "4", "8-K"
        }

    def enhance_query_and_extract_parameters(self, user_query: str) -> Dict:
        """
        Enhance user query and extract parameters using LLM
        
        Args:
            user_query (str): Original user query
            
        Returns:
            Dict: Enhanced query and extracted parameters
        """
        enhancement_prompt = """You are an expert SEC 10-K filing analyst. Your task is to analyze user queries about SEC forms and extract specific parameters while enhancing the query for better analysis.

## EXACT COMPANY NAMES (use these exact formats):
- Apple Inc
- Microsoft Corporation  
- NVIDIA Corporation
- Meta Platforms Inc
- JPMorgan Chase & Co
- Johnson & Johnson
- DoorDash Inc
- Roku Inc
- Zoom Communications Inc

## EXACT PART NAMES (use these exact formats):
- "Part I: Business and Risk Factors"
- "Part II: Financial Information"  
- "Part III: Corporate Governance and Executive Compensation"

## EXACT SECTION NAMES (use these exact formats):
- "Item 1. Business"
- "Item 1A. Risk Factors"
- "Item 1B. Unresolved Staff Comments"
- "Item 2. Properties"
- "Item 3. Legal Proceedings"
- "Item 5. Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities"
- "Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A)"
- "Item 7A. Quantitative and Qualitative Disclosures About Market Risk"
- "Item 8. Financial Statements and Supplementary Data"
- "Item 10. Directors, Executive Officers and Corporate Governance"
- "Item 11. Executive Compensation"
- "Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters"

## VALID YEARS: 2020, 2021, 2022, 2023, 2024, 2025 (use "latest" for most recent)

## COMPANY KEYWORDS FOR DETECTION:
- Apple: ["Apple", "AAPL", "iPhone", "Mac", "iPad", "Tim Cook"]
- Microsoft: ["Microsoft", "MSFT", "Windows", "Azure", "Office", "Satya Nadella"]
- NVIDIA: ["NVIDIA", "NVDA", "GPU", "AI chips", "Jensen Huang"]
- Meta: ["Meta", "Facebook", "META", "Instagram", "WhatsApp", "Mark Zuckerberg"]
- JPMorgan: ["JPMorgan", "Chase", "JPM", "banking", "Jamie Dimon"]
- Johnson & Johnson: ["J&J", "JNJ", "pharmaceutical", "healthcare", "medical devices"]
- DoorDash: ["DoorDash", "DASH", "food delivery", "gig economy"]
- Roku: ["Roku", "streaming", "TV platform"]
- Zoom: ["Zoom", "video conferencing", "ZM", "remote work"]

## TASK
1. Enhance the user query to be more specific and analytical
2. Extract parameters using EXACT names from the reference above

## CRITICAL: RETURN ONLY VALID JSON
Your response must be ONLY the JSON object below, no additional text before or after.

{
  "enhanced_query": "Enhanced and more specific version of the user query",
  "parameters": {
    "year": "YYYY or latest or YYYY,YYYY for comparisons",
    "company": "Exact Company Name from list above",
    "form_type": "10-K",
    "category": "Exact Part Name from list above or all",
    "subcategory": "Exact Section Name from list above or general"
  }
}

## EXAMPLES

User: "What are Apple's main risk factors?"
{
  "enhanced_query": "Identify and analyze the primary business and operational risk factors disclosed by Apple Inc. in their annual 10-K filing, including market risks, competitive risks, and regulatory risks.",
  "parameters": {
    "year": "latest",
    "company": "Apple Inc",
    "form_type": "10-K",
    "category": "Part I: Business and Risk Factors",
    "subcategory": "Item 1A. Risk Factors"
  }
}

User: "How do Microsoft's risk factors compare between 2022 and 2023?"
{
  "enhanced_query": "Conduct a comprehensive comparative analysis of Microsoft Corporation's risk factors between 2022 and 2023, identifying new risks, removed risks, and changes in risk severity or emphasis.",
  "parameters": {
    "year": "2022,2023",
    "company": "Microsoft Corporation",
    "form_type": "10-K",
    "category": "Part I: Business and Risk Factors",
    "subcategory": "Item 1A. Risk Factors"
  }
}

User Query: """
        
        try:
            full_prompt = enhancement_prompt + user_query
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                # Clean the response text
                response_text = response.text.strip()
                
                # Try to extract JSON from response
                json_result = self._extract_json_from_response(response_text)
                
                if json_result:
                    print(f"✓ Query enhanced and parameters extracted")
                    return json_result
                else:
                    print("⚠️ Could not extract valid JSON from response")
                    print(f"Raw response: {response_text[:200]}...")
                    return self._fallback_parameter_extraction(user_query)
            else:
                raise Exception("Empty response from LLM")
                
        except Exception as e:
            print(f"⚠️ Error in query enhancement: {str(e)}")
            return self._fallback_parameter_extraction(user_query)

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response that may contain extra text
        
        Args:
            response_text (str): Raw response from LLM
            
        Returns:
            Optional[Dict]: Parsed JSON if found
        """
        try:
            # First, try parsing the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # If that fails, try to find JSON within the response
        json_patterns = [
            r'\{.*\}',  # Find text between first { and last }
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```',  # JSON in code blocks without language
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try line by line for malformed JSON
        lines = response_text.split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if line.strip().startswith('{'):
                in_json = True
                json_lines = [line]
            elif in_json:
                json_lines.append(line)
                if line.strip().endswith('}'):
                    try:
                        json_text = '\n'.join(json_lines)
                        return json.loads(json_text)
                    except json.JSONDecodeError:
                        in_json = False
                        json_lines = []
        
        return None

    def _fallback_parameter_extraction(self, user_query: str) -> Dict:
        """
        Fallback method for parameter extraction if LLM parsing fails
        """
        print("🔄 Using fallback parameter extraction...")
        
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
            "amd": "Advanced Micro Devices Inc."
        }
        
        query_lower = user_query.lower()
        company = "Unknown Company"
        
        for keyword, full_name in company_mapping.items():
            if keyword in query_lower:
                company = full_name
                break
        
        # Extract year
        year_pattern = r'\b(20\d{2})\b'
        year_match = re.search(year_pattern, user_query)
        year = year_match.group(1) if year_match else "2020"  # Default to 2020 based on user's data
        
        # Determine category based on keywords
        category = "all"
        subcategory = "general"
        
        if any(word in query_lower for word in ["risk", "factor", "business"]):
            category = "Part I: Business and Risk Factors"
            if "risk" in query_lower:
                subcategory = "Item 1A. Risk Factors"
            elif "business" in query_lower:
                subcategory = "Item 1. Business"
        elif any(word in query_lower for word in ["financial", "revenue", "income", "profit", "earnings"]):
            category = "Part II: Financial Information"
            subcategory = "Item 7. Management's Discussion and Analysis"
        elif any(word in query_lower for word in ["governance", "director", "executive", "compensation"]):
            category = "Part III: Governance"
        
        enhanced_query = f"Provide a detailed analysis of {company}'s {category.lower()} information from their {year} 10-K filing, specifically addressing: {user_query}"
        
        result = {
            "enhanced_query": enhanced_query,
            "parameters": {
                "year": year,
                "company": company,
                "form_type": "10-K",
                "category": category,
                "subcategory": subcategory
            }
        }
        
        print(f"📋 Fallback extraction completed:")
        for key, value in result["parameters"].items():
            print(f"  {key}: {value}")
        
        return result

    def get_10k_analysis_system_prompt(self) -> str:
        """
        Return comprehensive system prompt for 10-K analysis including comparison capabilities
        """
        return """# 10-K SEC Filing Analysis Expert

You are a highly experienced SEC filing analyst with 25+ years of expertise in analyzing 10-K forms, financial statements, and corporate disclosures. You have deep knowledge of:
- SEC regulations and filing requirements
- GAAP accounting principles and financial reporting standards
- Corporate governance and risk assessment
- Business analysis and competitive intelligence
- Financial modeling and valuation techniques
- Year-over-year trend analysis and comparisons

## YOUR ROLE
Analyze the provided 10-K document section(s) and respond to the user's enhanced query with comprehensive, professional insights. You excel at both single-year analysis and multi-year comparisons.

## ANALYSIS GUIDELINES

### Content Analysis Approach
1. **Thorough Examination**: Carefully read and analyze all provided content
2. **Multi-Year Comparison**: When provided with multiple years, conduct detailed comparative analysis
3. **Key Insights Extraction**: Identify the most critical information and changes over time
4. **Professional Context**: Provide business context and implications for trends
5. **Quantitative Focus**: Highlight specific numbers, percentages, and financial metrics
6. **Change Analysis**: For comparisons, identify what's new, removed, or modified
7. **Risk Assessment**: Analyze evolution of risks and new emerging threats

### Multi-Year Comparison Structure
When analyzing multiple years, organize your response as follows:
1. **Executive Summary**: Key changes and trends overview
2. **Detailed Year-by-Year Analysis**: 
   - What remained consistent
   - What changed significantly
   - New items introduced
   - Items removed or de-emphasized
3. **Trend Analysis**: Patterns and trajectory over the time period
4. **Implications**: What these changes mean for the company's future
5. **Risk Evolution**: How risk profile has changed

### Single Year Analysis Structure
1. **Executive Summary**: 2-3 sentence overview of key findings
2. **Detailed Analysis**: Comprehensive breakdown of relevant information
3. **Key Metrics/Data**: Specific financial figures, percentages, dates
4. **Business Implications**: What this means for the company and stakeholders
5. **Risk Factors**: Any concerns or red flags identified
6. **Conclusion**: Summary recommendations or outlook

### Response Quality Standards
- **Accuracy**: Base all analysis strictly on provided document content
- **Depth**: Provide detailed, actionable insights
- **Clarity**: Use professional but accessible language
- **Specificity**: Include specific data points and examples
- **Objectivity**: Maintain neutral, analytical perspective
- **Comparison Focus**: For multi-year data, emphasize changes and evolution

## SPECIAL INSTRUCTIONS FOR COMPARISONS
- Always note which years you're comparing
- Highlight specific text or data that differs between years
- Identify emerging themes or new risk factors
- Point out discontinued risks or concerns
- Quantify changes where possible (e.g., "risk factors increased from 15 to 18")

## CRITICAL INSTRUCTIONS
- **NO HALLUCINATION**: Use ONLY information from the provided document
- **CITE SPECIFIC YEARS**: When referencing data, always mention which year it's from
- **QUANTIFY INSIGHTS**: Include numerical data and percentages where available
- **PROFESSIONAL TONE**: Write for sophisticated financial professionals
- **COMPREHENSIVE COVERAGE**: Address all aspects of the enhanced query
- **COMPARISON CLARITY**: For multi-year analysis, make changes crystal clear

## DOCUMENT CONTENT TO ANALYZE:
---
"""

    def find_company_json_file(self, company_name: str) -> Optional[Path]:
        """
        Find JSON file for the specified company in reports folder
        
        Args:
            company_name (str): Company name to search for
            
        Returns:
            Optional[Path]: Path to the JSON file if found
        """
        print(f"🔍 Searching for JSON file for: {company_name}")
        
        # List all available JSON files for debugging
        json_files = list(self.reports_folder.glob("*.json"))
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
            " ltd.", " ltd", " limited", " llc", " l.l.c.", " plc"
        ]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        
        # Remove extra whitespace and special characters
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized

    def extract_category_content(self, json_file_path: Path, year: str, category: str) -> Optional[str]:
        """
        Extract content from specific category in JSON file
        Handles both single years and multi-year comparisons
        
        Args:
            json_file_path (Path): Path to JSON file
            year (str): Year(s) to extract data for (can be "2022, 2023" for comparisons)
            category (str): Category to extract
            
        Returns:
            Optional[str]: Category content as string
        """
        try:
            print(f"📖 Reading JSON file: {json_file_path}")
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            print(f"🔍 JSON structure - Top level keys: {list(data.keys())}")
            
            # Navigate through JSON structure - handle the new format
            if "years_data" in data:
                company_data = data["years_data"]
                company_key = data.get("company_name", "Unknown Company")
            else:
                # Fallback to old format
                company_data = None
                company_key = None
                for key in data.keys():
                    if isinstance(data[key], dict):
                        company_data = data[key]
                        company_key = key
                        break
            
            if not company_data:
                print("❌ No company data found in JSON")
                return None
            
            print(f"📊 Company: {company_key}")
            print(f"📅 Available years: {list(company_data.keys())}")
            
            # Handle multi-year queries (e.g., "2022, 2023")
            years_to_extract = self._parse_years(year, list(company_data.keys()))
            
            if not years_to_extract:
                print(f"❌ No valid years found from: {year}")
                return None
            
            print(f"✓ Extracting data for years: {years_to_extract}")
            
            # Extract data for each year
            multi_year_data = {}
            
            for target_year in years_to_extract:
                year_data = company_data.get(target_year)
                
                if not year_data:
                    print(f"⚠️ No data found for year: {target_year}")
                    continue
                
                # Handle new JSON format with parts/sections structure
                if "content" in year_data and "parts" in year_data["content"]:
                    parts_data = year_data["content"]["parts"]
                    
                    if category == "all":
                        # Convert parts format to categories format
                        categories_data = {}
                        for part in parts_data:
                            part_name = part.get("part_name", "Unknown Part")
                            categories_data[part_name] = {}
                            
                            for section in part.get("sections", []):
                                section_category = section.get("category", "Unknown Category")
                                section_content = section.get("content", "")
                                categories_data[part_name][section_category] = section_content
                        
                        multi_year_data[target_year] = categories_data
                    else:
                        # Find matching category
                        found_category = False
                        for part in parts_data:
                            part_name = part.get("part_name", "")
                            if category in part_name or part_name in category:
                                part_content = {}
                                for section in part.get("sections", []):
                                    section_category = section.get("category", "Unknown Category")
                                    section_content = section.get("content", "")
                                    part_content[section_category] = section_content
                                
                                multi_year_data[target_year] = {category: part_content}
                                found_category = True
                                break
                        
                        if not found_category:
                            print(f"⚠️ Category '{category}' not found in year {target_year}")
                            available_parts = [part.get("part_name", "Unknown") for part in parts_data]
                            print(f"Available parts for {target_year}: {available_parts}")
                
                # Fallback to old format if CATEGORIES exists
                elif "CATEGORIES" in year_data:
                    categories_data = year_data["CATEGORIES"]
                    
                    if category == "all":
                        multi_year_data[target_year] = categories_data
                    else:
                        if category in categories_data:
                            multi_year_data[target_year] = {category: categories_data[category]}
                        else:
                            print(f"⚠️ Category '{category}' not found in year {target_year}")
                            print(f"Available categories for {target_year}: {list(categories_data.keys())}")
                else:
                    print(f"⚠️ No valid content structure found for year: {target_year}")
                    print(f"Available keys in year data: {list(year_data.keys()) if year_data else 'None'}")
            
            if not multi_year_data:
                print(f"❌ No data extracted for any requested years")
                return None
            
            # Format the result
            if len(multi_year_data) == 1:
                # Single year result
                year_key = list(multi_year_data.keys())[0]
                return json.dumps(multi_year_data[year_key], indent=2)
            else:
                # Multi-year comparison result
                comparison_data = {
                    "comparison_type": "multi_year_analysis",
                    "years_compared": list(multi_year_data.keys()),
                    "category": category,
                    "data": multi_year_data
                }
                return json.dumps(comparison_data, indent=2)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error extracting category content: {str(e)}")
            return None

    def _parse_years(self, year_string: str, available_years: List[str]) -> List[str]:
        """
        Parse year string and return list of valid years
        
        Args:
            year_string (str): Year specification (e.g., "2022", "2022, 2023", "latest")
            available_years (List[str]): Available years in the data
            
        Returns:
            List[str]: List of valid years to extract
        """
        if not year_string:
            return []
        
        # Handle "latest" 
        if year_string.strip().lower() == "latest":
            numeric_years = [y for y in available_years if y.isdigit()]
            if numeric_years:
                return [max(numeric_years)]
            return []
        
        # Handle comma-separated years
        if "," in year_string:
            years = [y.strip() for y in year_string.split(",")]
            valid_years = []
            for year in years:
                if year in available_years:
                    valid_years.append(year)
                else:
                    print(f"⚠️ Year {year} not available in data")
            return valid_years
        
        # Handle single year
        clean_year = year_string.strip()
        if clean_year in available_years:
            return [clean_year]
        
        print(f"⚠️ Year {clean_year} not available in data")
        return []

    def analyze_10k_content(self, enhanced_query: str, category_content: str) -> str:
        """
        Analyze 10-K content using LLM with system prompt
        
        Args:
            enhanced_query (str): Enhanced user query
            category_content (str): Content from specific category
            
        Returns:
            str: Analysis results
        """
        try:
            system_prompt = self.get_10k_analysis_system_prompt()
            full_prompt = system_prompt + category_content + f"\n\n## USER QUERY TO ANALYZE:\n{enhanced_query}"
            
            print("🔍 Analyzing content with Gemini...")
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                print("✓ Analysis completed")
                return response.text
            else:
                return "Error: Empty response from analysis"
                
        except Exception as e:
            return f"Error during analysis: {str(e)}"

    def save_analysis_result(self, result: str, query: str) -> str:
        """
        Save analysis result to txt file
        
        Args:
            result (str): Analysis result
            query (str): Original query for filename
            
        Returns:
            str: Path to saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create safe filename from query
            safe_query = re.sub(r'[^\w\s-]', '', query)[:50]
            safe_query = re.sub(r'[-\s]+', '_', safe_query)
            
            filename = f"query_answer_{safe_query}_{timestamp}.txt"
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"=== SEC FILING ANALYSIS RESULT ===\n")
                file.write(f"Query: {query}\n")
                file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("="*50 + "\n\n")
                file.write(result)
            
            print(f"✓ Analysis saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error saving result: {str(e)}")
            return ""

    def process_10k_query(self, user_query: str) -> Dict:
        """
        Complete 10-K query processing pipeline
        
        Args:
            user_query (str): User's original query
            
        Returns:
            Dict: Processing results and file paths
        """
        try:
            print(f"🚀 Processing 10-K query: {user_query}")
            
            # Step 1: Enhance query and extract parameters
            enhanced_data = self.enhance_query_and_extract_parameters(user_query)
            enhanced_query = enhanced_data["enhanced_query"]
            params = enhanced_data["parameters"]
            
            print(f"📊 Extracted parameters:")
            for key, value in params.items():
                print(f"  {key}: {value}")
            
            # Step 2: Find company JSON file
            json_file = self.find_company_json_file(params["company"])
            if not json_file:
                return {
                    "success": False,
                    "error": f"No JSON file found for company: {params['company']}",
                    "available_files": [f.stem for f in self.reports_folder.glob("*.json")]
                }
            
            print(f"📁 Found company file: {json_file}")
            
            # Step 3: Extract category content
            category_content = self.extract_category_content(
                json_file, 
                params["year"], 
                params["category"]
            )
            
            if not category_content:
                return {
                    "success": False,
                    "error": f"No content found for category: {params['category']} in year: {params['year']}"
                }
            
            print(f"📋 Extracted content from category: {params['category']}")
            
            # Step 4: Analyze content with LLM
            analysis_result = self.analyze_10k_content(enhanced_query, category_content)
            
            # Step 5: Save result to file
            output_file = self.save_analysis_result(analysis_result, user_query)
            
            return {
                "success": True,
                "enhanced_query": enhanced_query,
                "parameters": params,
                "json_file_used": str(json_file),
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
        
        Returns:
            Dict: Test results
        """
        print("🧪 Testing SEC Forms Tools setup...")
        
        results = {
            "api_connection": False,
            "reports_folder": False,
            "json_files_found": [],
            "sample_query_test": False
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
        
        # Test 2: Reports folder
        if self.reports_folder.exists():
            results["reports_folder"] = True
            print(f"✅ Reports folder found: {self.reports_folder}")
            
            # Find JSON files
            json_files = list(self.reports_folder.glob("*.json"))
            results["json_files_found"] = [f.stem for f in json_files]
            print(f"📁 JSON files found: {results['json_files_found']}")
        else:
            print(f"❌ Reports folder not found: {self.reports_folder}")
        
        # Test 3: Sample query if we have files
        if results["json_files_found"]:
            try:
                sample_company = results["json_files_found"][0]
                # Test single year query
                sample_query = f"What is {sample_company}'s business overview?"
                print(f"🧪 Testing sample query: {sample_query}")
                
                enhanced_data = self.enhance_query_and_extract_parameters(sample_query)
                if enhanced_data and "enhanced_query" in enhanced_data:
                    results["sample_query_test"] = True
                    print("✅ Sample query processing successful")
                    
                    # Test multi-year parsing
                    test_years = self._parse_years("2022,2023", ["2020", "2021", "2022", "2023"])
                    if test_years == ["2022", "2023"]:
                        print("✅ Multi-year parsing working correctly")
                    else:
                        print("⚠️ Multi-year parsing issue detected")
                else:
                    print("❌ Sample query processing failed")
            except Exception as e:
                print(f"❌ Sample query test failed: {str(e)}")
        
        # Summary
        print("\n📊 Setup Test Results:")
        for test, result in results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test}: {result}")
        
        return results


def main():
    """
    Command line interface for SEC Forms Tools
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze SEC Forms using AI')
    parser.add_argument('query', nargs='?', help='Your question about SEC filings')
    parser.add_argument('-k', '--api-key', help='Google Gemini API key')
    parser.add_argument('-r', '--reports', default='gemini_10k', help='Reports folder path')
    parser.add_argument('-t', '--test', action='store_true', help='Run setup test')
    
    args = parser.parse_args()
    
    try:
        # Initialize tools
        tools = SECFormsTools(api_key=args.api_key, reports_folder=args.reports)
        
        # Run test if requested
        if args.test:
            tools.test_setup()
            return
        
        # Check if query provided
        if not args.query:
            parser.error("Please provide a query or use --test to test setup")
        
        # Process query
        result = tools.process_10k_query(args.query)
        
        if result["success"]:
            print(f"\n✅ Analysis completed successfully!")
            print(f"📄 Result saved to: {result['output_file']}")
        else:
            print(f"\n❌ Error: {result['error']}")
            if "available_files" in result:
                print(f"Available company files: {result['available_files']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()


# Usage Examples:
"""
# Command line usage:
python sec_tools.py "What are Apple's main risk factors in 2023?"
python sec_tools.py "Tell me about Microsoft's financial performance" -r "path/to/reports"

# Module usage:
from sec_tools import SECFormsTools

tools = SECFormsTools()
result = tools.process_10k_query("What are Tesla's business segments?")
print(result["analysis_result"])
"""