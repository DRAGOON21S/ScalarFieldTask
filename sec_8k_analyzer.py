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

class SEC8KAnalyzer:
    def __init__(self, api_key=None, json_folder="gemini_8k"):
        """
        Initialize SEC 8-K Current Events Analyzer with Gemini API
        
        Args:
            api_key (str): Google Gemini API key
            json_folder (str): Path to folder containing 8-K JSON files
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("API key must be provided either as parameter or GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.json_folder = Path(json_folder)

    def get_8k_analysis_system_prompt(self) -> str:
        """
        Return comprehensive system prompt for 8-K analysis with strict data accuracy requirements
        """
        return """# SEC Form 8-K Current Events Analysis Expert

You are a highly experienced SEC 8-K filing analyst with 25+ years of expertise in analyzing current reports and material events. You have deep knowledge of:
- SEC regulations and 8-K filing requirements
- Corporate events and material changes
- Financial disclosures and regulatory compliance
- Business transactions and corporate actions
- Legal proceedings and regulatory matters

## YOUR CRITICAL ROLE
Analyze the provided 8-K document sections and respond with ABSOLUTE PRECISION based ONLY on the data provided. You must maintain the highest standards of accuracy and never add information not explicitly contained in the source documents.

## ABSOLUTE REQUIREMENTS - ZERO TOLERANCE FOR VIOLATIONS

### 1. DATA FIDELITY (CRITICAL)
- **USE ONLY PROVIDED DATA**: Base every statement, figure, date, name, and detail EXCLUSIVELY on the provided 8-K content
- **NO EXTERNAL KNOWLEDGE**: Do not add context, explanations, or information from general knowledge about the company
- **NO ASSUMPTIONS**: If information is not explicitly stated, clearly indicate "not specified in the filing"
- **EXACT QUOTES**: When referencing specific content, use exact quotations from the source material
- **PRECISE DATES**: Use only dates explicitly mentioned in the filings
- **EXACT FIGURES**: Report only numerical data that appears in the source documents

### 2. VERIFICATION PROTOCOL
- **SOURCE ATTRIBUTION**: For each significant claim, reference the specific 8-K section/item where the information appears
- **DIRECT CITATIONS**: When possible, include direct quotes from the filing to support key points
- **UNCERTAINTY HANDLING**: When information is incomplete or unclear, explicitly state this limitation
- **CROSS-REFERENCE**: If multiple filings contain related information, note the specific documents and dates

### 3. ANALYSIS STRUCTURE
Organize your response using this hierarchy:

#### **Executive Summary**
- Brief overview of key material events covered in the filing(s)
- Timeline of events based solely on filing dates and content dates
- Impact assessment based only on information stated in the documents

#### **Detailed Event Analysis**
For each material event identified:

1. **Event Classification**: 
   - Specific 8-K item number(s) (e.g., "Item 2.02 - Results of Operations")
   - Event type as categorized in the filing

2. **Factual Details**:
   - **When**: Exact dates from the filing
   - **What**: Precise description using filing language
   - **Parties Involved**: Names and roles as stated in documents
   - **Financial Impact**: Only figures explicitly provided

3. **Regulatory Context**:
   - Filing date and timing relative to event
   - Regulatory requirements mentioned in the filing
   - Legal or compliance aspects specifically noted

4. **Supporting Documentation**:
   - Exhibits referenced in the filing
   - Related agreements or documents mentioned
   - Cross-references to other SEC filings if explicitly noted

#### **Financial and Business Implications**
- **Quantitative Impact**: Only financial figures provided in the filings
- **Business Changes**: Operational changes explicitly described
- **Forward-Looking Statements**: Only those contained in the filing, clearly marked as such
- **Risk Factors**: Only risks explicitly mentioned in the current filing

#### **Timeline and Context**
- **Chronological Sequence**: Order of events based on dates in filings
- **Regulatory Timeline**: Filing dates and effective dates as specified
- **Related Filings**: Only other documents explicitly referenced

## QUALITY CONTROL CHECKLIST
Before finalizing your response, verify:

✓ **Every fact can be traced to specific content in the provided 8-K data**
✓ **No external information or general knowledge has been added**
✓ **All dates, names, figures are exactly as they appear in source**
✓ **Uncertainties and limitations are clearly acknowledged**
✓ **Direct quotes support key analytical points**
✓ **Section/item references are accurate**

## RESPONSE TONE AND STYLE
- **Professional and Analytical**: Write for sophisticated financial professionals
- **Precise and Specific**: Use exact terminology from the filings
- **Cautious with Interpretations**: Clearly distinguish between facts and reasonable inferences
- **Comprehensive but Focused**: Cover all material information without redundancy
- **Clear Structure**: Use headers and bullet points for easy navigation

## CRITICAL INSTRUCTIONS
- **NEVER HALLUCINATE**: If you don't have the information, explicitly state this
- **PRESERVE EXACT LANGUAGE**: When quoting filing content, maintain exact wording
- **ACKNOWLEDGE LIMITATIONS**: If analysis requires information not in the filing, clearly state this gap
- **MAINTAIN OBJECTIVITY**: Present facts without editorial commentary unless explicitly requested

## DOCUMENT CONTENT TO ANALYZE:
---
"""

    def extract_company_and_criteria(self, user_query: str) -> Dict:
        """
        Extract company name and analysis criteria from user query using LLM
        """
        extraction_prompt = """You are an expert SEC 8-K filing analyst. Extract company name and analysis focus from user queries using EXACT reference mappings.

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

## EXACT SECTION NAMES:
- "Section 2 - Financial Information"
- "Section 8 - Other Events"
- "Section 5 - Corporate Governance and Management"
- "Section 1 - Registrant's Business and Operations"
- "Section 3 - Securities and Trading Markets"
- "Section 4 - Matters Related to Accountants and Financial Statements"
- "Section 7 - Regulation FD"
- "Section 9 - Financial Statements and Exhibits"

## EXACT ITEM NAMES:
- "Item 2.01 - Completion of Acquisition or Disposition of Assets"
- "Item 2.02 - Results of Operations and Financial Condition"
- "Item 8.01 - Other Events"
- "Item 5.02 - Departure of Directors or Principal Officers"
- "Item 1.01 - Entry into a Material Definitive Agreement"
- "Item 2.03 - Creation of a Direct Financial Obligation"
- "Item 7.01 - Regulation FD Disclosure"

## ANALYSIS FOCUS OPTIONS:
- acquisitions: ["acquisition", "merger", "purchase", "deal", "transaction"]
- financial_results: ["financial", "revenue", "profit", "earnings", "income", "results"]
- material_agreements: ["agreement", "contract", "partnership", "deal"]
- management_changes: ["management", "executives", "leadership", "directors", "CEO", "CFO"]
- legal_matters: ["legal", "litigation", "lawsuits", "regulatory", "compliance"]
- regulation_fd: ["disclosure", "announcement", "presentation", "guidance"]
- debt_financing: ["debt", "financing", "loan", "credit", "bonds"]
- all: ["all", "everything", "comprehensive", "full"]

## VALID YEARS: 2020, 2021, 2022, 2023, 2024, 2025

Return ONLY JSON:

{
  "company": "Exact Company Name from list above",
  "analysis_focus": "specific focus area from options above",
  "time_period": "YYYY or null if not mentioned",
  "confidence": "high/medium/low"
}

Examples:
"Apple's material events in 2021" -> {"company": "Apple Inc", "analysis_focus": "all", "time_period": "2021", "confidence": "high"}
"Microsoft acquisitions and deals" -> {"company": "Microsoft Corporation", "analysis_focus": "acquisitions", "time_period": null, "confidence": "high"}
"NVIDIA financial disclosures" -> {"company": "NVIDIA Corporation", "analysis_focus": "financial_results", "time_period": null, "confidence": "high"}

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
                print(f"✓ Extracted: {result['company']}, focus: {result['analysis_focus']}")
                if result.get('time_period'):
                    print(f"  Time period: {result['time_period']}")
                return result
        except Exception as e:
            print(f"⚠️ Extraction error: {e}")
        
        # Fallback extraction
        return self._fallback_extraction(user_query)

    def _fallback_extraction(self, user_query: str) -> Dict:
        """Simple regex-based fallback extraction"""
        companies = {
            "apple": "Apple Inc.",
            "microsoft": "Microsoft Corporation",
            "nvidia": "NVIDIA Corporation",
            "meta": "Meta Platforms Inc.",
            "facebook": "Meta Platforms Inc.",
            "google": "Alphabet Inc.",
            "amazon": "Amazon.com Inc.",
            "tesla": "Tesla Inc.",
            "johnson": "Johnson & Johnson",
            "jpmorgan": "JPMorgan Chase & Co.",
            "doordash": "DoorDash Inc.",
            "roku": "Roku Inc.",
            "zoom": "Zoom Communications Inc."
        }
        
        query_lower = user_query.lower()
        company = None
        
        for key, name in companies.items():
            if key in query_lower:
                company = name
                break
        
        # Extract analysis focus
        focus_keywords = {
            "acquisition": "acquisitions",
            "merger": "acquisitions", 
            "deal": "acquisitions",
            "financial": "financial_results",
            "earnings": "financial_results",
            "revenue": "financial_results",
            "legal": "legal_matters",
            "lawsuit": "legal_matters",
            "debt": "debt_issuance",
            "bond": "debt_issuance",
            "notes": "debt_issuance"
        }
        
        analysis_focus = "all"
        for keyword, focus in focus_keywords.items():
            if keyword in query_lower:
                analysis_focus = focus
                break
        
        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', user_query)
        time_period = year_match.group(1) if year_match else None
        
        return {
            "company": company or "Unknown Company",
            "analysis_focus": analysis_focus,
            "time_period": time_period,
            "confidence": "medium" if company else "low"
        }

    def find_company_file(self, company_name: str) -> Optional[Path]:
        """Find JSON file for company"""
        if not self.json_folder.exists():
            print(f"❌ Folder not found: {self.json_folder}")
            return None
        
        json_files = list(self.json_folder.glob("*.json"))
        print(f"📁 Available 8-K files: {[f.stem for f in json_files]}")
        
        # Normalize and search
        normalized_company = company_name.lower().replace(" ", "").replace("inc", "").replace("corp", "").replace(".", "")
        
        for file in json_files:
            normalized_file = file.stem.lower().replace("_", "").replace("8k", "")
            if normalized_company[:5] in normalized_file or normalized_file[:5] in normalized_company:
                print(f"✓ Found match: {file}")
                return file
        
        print(f"❌ No 8-K file found for: {company_name}")
        return None

    def analyze_8k_filings(self, json_file: Path, analysis_focus: str, time_period: Optional[str], query: str) -> str:
        """Analyze the 8-K filings with strict data accuracy"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract relevant data based on time period
            relevant_data = {}
            for company_key, company_data in data.items():
                if isinstance(company_data, dict):
                    for year_key, year_data in company_data.items():
                        if time_period is None or year_key == time_period:
                            relevant_data[year_key] = year_data
            
            if not relevant_data:
                return f"No 8-K data found for the specified criteria"
            
            print(f"📊 Analyzing 8-K data for {len(relevant_data)} year(s)")
            
            # Create focused analysis prompt
            system_prompt = self.get_8k_analysis_system_prompt()
            
            analysis_prompt = f"""{system_prompt}

**USER QUERY**: {query}
**ANALYSIS FOCUS**: {analysis_focus}
**TIME PERIOD**: {time_period or "All available years"}

**8-K FILING DATA TO ANALYZE**:
{json.dumps(relevant_data, indent=2)}

**SPECIFIC INSTRUCTIONS FOR THIS QUERY**:
1. Focus specifically on: {analysis_focus}
2. Provide deep analysis while staying strictly within the provided data
3. Include specific item numbers and exact content from the filings
4. Use direct quotes to support key findings
5. If the analysis focus doesn't match available data, clearly explain what IS available
6. Organize findings chronologically if multiple years are present
7. Reference specific sections and items for all major points

**RESPOND WITH COMPREHENSIVE ANALYSIS**:"""
            
            response = self.model.generate_content(analysis_prompt)
            return response.text if response.text else "Analysis failed"
            
        except Exception as e:
            return f"Error analyzing 8-K filings: {str(e)}"

    def process_query(self, user_query: str) -> str:
        """Main processing pipeline"""
        print(f"🚀 Processing 8-K query: {user_query}")
        
        # Step 1: Extract company and criteria
        extraction = self.extract_company_and_criteria(user_query)
        
        if extraction['confidence'] == 'low':
            return "❌ Could not identify company in query. Please specify a company name."
        
        # Step 2: Find company file
        json_file = self.find_company_file(extraction['company'])
        if not json_file:
            return f"❌ No 8-K data file found for {extraction['company']}"
        
        # Step 3: Analyze 8-K filings
        result = self.analyze_8k_filings(
            json_file, 
            extraction['analysis_focus'], 
            extraction['time_period'],
            user_query
        )
        
        # Step 4: Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^\w\s-]', '', user_query)[:50]
        safe_query = re.sub(r'[-\s]+', '_', safe_query)
        filename = f"8k_analysis_{safe_query}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"=== SEC 8-K CURRENT EVENTS ANALYSIS ===\n")
            f.write(f"Query: {user_query}\n")
            f.write(f"Company: {extraction['company']}\n")
            f.write(f"Analysis Focus: {extraction['analysis_focus']}\n")
            f.write(f"Time Period: {extraction['time_period'] or 'All available'}\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            f.write(result)
        
        print(f"✅ 8-K Analysis complete! Saved to: {filename}")
        return result


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Analyze SEC 8-K Current Events filings')
    parser.add_argument('query', help='Your question about material events and current reports')
    parser.add_argument('-f', '--folder', default='gemini_8k', help='Folder containing 8-K JSON files')
    parser.add_argument('-k', '--api-key', help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        analyzer = SEC8KAnalyzer(api_key=args.api_key, json_folder=args.folder)
        result = analyzer.process_query(args.query)
        
        print("\n" + "="*60)
        print("8-K ANALYSIS RESULT:")
        print("="*60)
        print(result[:1500] + "..." if len(result) > 1500 else result)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

# Usage Examples:
"""
python sec_8k_analyzer.py "What material events did Apple report in 2021?"
python sec_8k_analyzer.py "Microsoft acquisitions and business combinations"
python sec_8k_analyzer.py "Tesla's financial disclosures and earnings releases"
python sec_8k_analyzer.py "Apple debt issuance and financing activities in 2020"
python sec_8k_analyzer.py "Meta legal proceedings and regulatory matters"
"""
