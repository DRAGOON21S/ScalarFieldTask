# SEC JSON STRUCTURE REFERENCE GUIDE

# Complete mappings for sec_tools.py, sec_8k_analyzer.py, and sec_insider_analyzer.py

## EXACT COMPANY NAMES BY FOLDER

### gemini_10k (Annual Reports):

COMPANIES = {
"Apple Inc": "Apple_Inc_10k.json",
"Apple": "Apple_Inc_10k.json",
"AAPL": "Apple_Inc_10k.json",

    "DoorDash Inc": "DoorDash_Inc_10k.json",
    "DoorDash": "DoorDash_Inc_10k.json",
    "DASH": "DoorDash_Inc_10k.json",

    "Johnson & Johnson": "JOHNSON_&_JOHNSON_10k.json",
    "J&J": "JOHNSON_&_JOHNSON_10k.json",
    "JNJ": "JOHNSON_&_JOHNSON_10k.json",

    "JPMorgan Chase & Co": "JPMORGAN_CHASE_&_CO_10k.json",
    "JPMorgan Chase": "JPMORGAN_CHASE_&_CO_10k.json",
    "JPMorgan": "JPMORGAN_CHASE_&_CO_10k.json",
    "Chase": "JPMORGAN_CHASE_&_CO_10k.json",
    "JPM": "JPMORGAN_CHASE_&_CO_10k.json",

    "Meta Platforms Inc": "Meta_Platforms_Inc_10k.json",
    "Meta": "Meta_Platforms_Inc_10k.json",
    "Facebook": "Meta_Platforms_Inc_10k.json",
    "META": "Meta_Platforms_Inc_10k.json",

    "Microsoft Corporation": "MICROSOFT_CORP_10k.json",
    "Microsoft Corp": "MICROSOFT_CORP_10k.json",
    "Microsoft": "MICROSOFT_CORP_10k.json",
    "MSFT": "MICROSOFT_CORP_10k.json",

    "NVIDIA Corporation": "NVIDIA_CORP_10k.json",
    "NVIDIA Corp": "NVIDIA_CORP_10k.json",
    "NVIDIA": "NVIDIA_CORP_10k.json",
    "NVDA": "NVIDIA_CORP_10k.json",

    "Roku Inc": "ROKU_INC_10k.json",
    "Roku": "ROKU_INC_10k.json",
    "ROKU": "ROKU_INC_10k.json",

    "Zoom Communications Inc": "Zoom_Communications_Inc_10k.json",
    "Zoom": "Zoom_Communications_Inc_10k.json",
    "ZM": "Zoom_Communications_Inc_10k.json"

}

### gemini_8k (Current Events):

# Same company names, but with \_8k.json suffix

### gemini_form4 (Insider Trading):

# Same company names, but with \_form4.json suffix

# Plus additional company:

"UnitedHealth Group Inc": "UNITEDHEALTH_GROUP_INC_form4.json",
"UnitedHealth": "UNITEDHEALTH_GROUP_INC_form4.json",
"UNH": "UNITEDHEALTH_GROUP_INC_form4.json"

## JSON STRUCTURE MAPPINGS

### 10-K FILES (sec_tools.py):

JSON_STRUCTURE_10K = {
"root_keys": ["company_name", "years_data"],
"company_name_field": "company_name", # e.g., "Apple_Inc", "MICROSOFT_CORP"

    "years_data": {
        "structure": "years_data.{year}.content",
        "available_years": ["2020", "2021", "2022", "2023", "2024", "2025"],

        "content": {
            "meta_fields": ["company_name", "filing_type", "created_date"],
            "main_data": "parts",

            "parts": [
                {
                    "part_name": "Part I: Business and Risk Factors",
                    "sections": [
                        {"category": "Item 1. Business"},
                        {"category": "Item 1A. Risk Factors"},
                        {"category": "Item 1B. Unresolved Staff Comments"},
                        {"category": "Item 2. Properties"},
                        {"category": "Item 3. Legal Proceedings"}
                    ]
                },
                {
                    "part_name": "Part II: Financial Information",
                    "sections": [
                        {"category": "Item 5. Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities"},
                        {"category": "Item 6. [Reserved]"},  # or "Item 6. Selected Financial Data"
                        {"category": "Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A)"},
                        {"category": "Item 7A. Quantitative and Qualitative Disclosures About Market Risk"},
                        {"category": "Item 8. Financial Statements and Supplementary Data"}
                    ]
                },
                {
                    "part_name": "Part III: Corporate Governance and Executive Compensation",
                    "sections": [
                        {"category": "Item 10. Directors, Executive Officers and Corporate Governance"},
                        {"category": "Item 11. Executive Compensation"},
                        {"category": "Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters"}
                    ]
                }
            ]
        }
    }

}

### 8-K FILES (sec_8k_analyzer.py):

JSON_STRUCTURE_8K = {
"root_key": "company_name", # e.g., "Apple Inc"

    "years": {
        "structure": "{company_name}.{year}",
        "available_years": ["2020", "2021", "2022", "2023", "2024", "2025"],

        "content": {
            "FORM": "8-K",
            "CATEGORIES": {
                "Section 1 - Registrant's Business and Operations": {
                    "ITEMS": [
                        "Item 1.01 - Entry into a Material Definitive Agreement",
                        "Item 1.02 - Termination of a Material Definitive Agreement",
                        "Item 1.03 - Bankruptcy or Receivership"
                    ]
                },
                "Section 2 - Financial Information": {
                    "ITEMS": [
                        "Item 2.01 - Completion of Acquisition or Disposition of Assets",
                        "Item 2.02 - Results of Operations and Financial Condition",
                        "Item 2.03 - Creation of a Direct Financial Obligation",
                        "Item 2.04 - Triggering Events That Accelerate or Increase Direct Financial Obligation",
                        "Item 2.05 - Costs Associated with Exit or Disposal Activities",
                        "Item 2.06 - Material Impairments"
                    ]
                },
                "Section 3 - Securities and Trading Markets": {
                    "ITEMS": [
                        "Item 3.01 - Notice of Delisting or Failure to Satisfy Listing Rule",
                        "Item 3.02 - Unregistered Sales of Equity Securities",
                        "Item 3.03 - Material Modification to Rights of Security Holders"
                    ]
                },
                "Section 4 - Matters Related to Accountants and Financial Statements": {
                    "ITEMS": [
                        "Item 4.01 - Changes in Registrant's Certifying Accountant",
                        "Item 4.02 - Non-Reliance on Previously Issued Financial Statements"
                    ]
                },
                "Section 5 - Corporate Governance and Management": {
                    "ITEMS": [
                        "Item 5.01 - Changes in Control of Registrant",
                        "Item 5.02 - Departure of Directors or Principal Officers",
                        "Item 5.03 - Amendments to Articles of Incorporation or Bylaws",
                        "Item 5.04 - Temporary Suspension of Trading",
                        "Item 5.05 - Amendment to Registrant's Code of Ethics",
                        "Item 5.06 - Change in Shell Company Status",
                        "Item 5.07 - Submission of Matters to a Vote of Security Holders",
                        "Item 5.08 - Shareholder Director Nominations"
                    ]
                },
                "Section 7 - Regulation FD": {
                    "ITEMS": [
                        "Item 7.01 - Regulation FD Disclosure"
                    ]
                },
                "Section 8 - Other Events": {
                    "ITEMS": [
                        "Item 8.01 - Other Events"
                    ]
                },
                "Section 9 - Financial Statements and Exhibits": {
                    "ITEMS": [
                        "Item 9.01 - Financial Statements and Exhibits"
                    ]
                }
            }
        }
    }

}

### FORM 4 FILES (sec_insider_analyzer.py):

JSON_STRUCTURE_FORM4 = {
"root_key": "company_name", # e.g., "Apple_Inc"

    "years": {
        "structure": "{company_name}.{year}",
        "available_years": ["2020", "2021", "2022", "2023", "2024", "2025"],

        "content": [
            {
                "FORM": "4",
                "INSIDER_INFO": {
                    "name": "string",  # e.g., "Timothy D Cook"
                    "title": "string",  # e.g., "Chief Executive Officer"
                    "relationship": "string",
                    "is_director": "boolean",
                    "is_officer": "boolean",
                    "is_ten_percent_owner": "boolean"
                },
                "FILING_DATE": "YYYY-MM-DD",
                "TRADING_TABLES": {
                    "TableI-Non-DerivativeSecurities(CommonStock,PreferredStock,etc.)": {
                        "TRANSACTIONS": [],
                        "table_summary": {
                            "total_transactions": "string",
                            "net_shares_change": "string",
                            "total_transaction_value": "string"
                        }
                    },
                    "TableII-DerivativeSecurities(Options,Warrants,ConvertibleSecurities,etc.)": {
                        "TRANSACTIONS": [],
                        "table_summary": {
                            "total_transactions": "string",
                            "net_shares_change": "string",
                            "total_transaction_value": "string"
                        }
                    }
                }
            }
        ]
    }

}

## ANALYSIS FOCUS CATEGORIES

### 10-K Analysis Categories:

ANALYSIS_CATEGORIES_10K = {
"business_overview": ["Item 1. Business"],
"risk_factors": ["Item 1A. Risk Factors"],
"financial_analysis": ["Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A)"],
"financial_statements": ["Item 8. Financial Statements and Supplementary Data"],
"market_risk": ["Item 7A. Quantitative and Qualitative Disclosures About Market Risk"],
"corporate_governance": ["Item 10. Directors, Executive Officers and Corporate Governance"],
"executive_compensation": ["Item 11. Executive Compensation"],
"legal_proceedings": ["Item 3. Legal Proceedings"],
"properties": ["Item 2. Properties"],
"all": ["all sections"]
}

### 8-K Analysis Focus Areas:

ANALYSIS_FOCUS_8K = {
"acquisitions": ["Item 2.01 - Completion of Acquisition or Disposition of Assets"],
"financial_results": ["Item 2.02 - Results of Operations and Financial Condition"],
"material_agreements": ["Item 1.01 - Entry into a Material Definitive Agreement"],
"debt_financing": ["Item 2.03 - Creation of a Direct Financial Obligation"],
"management_changes": ["Item 5.02 - Departure of Directors or Principal Officers"],
"legal_matters": ["Item 8.01 - Other Events"],
"regulation_fd": ["Item 7.01 - Regulation FD Disclosure"],
"corporate_governance": ["Item 5.03 - Amendments to Articles of Incorporation or Bylaws"],
"all": ["all sections"]
}

### Form 4 Analysis Types:

ANALYSIS_TYPES_FORM4 = {
"executive_transactions": "CEO, CFO, COO level transactions",
"director_activity": "Board member transactions",
"insider_sentiment": "Overall buying vs selling patterns",
"large_transactions": "Transactions above certain threshold",
"stock_options": "Option exercises and grants",
"recent_activity": "Transactions within specific timeframe",
"all": "All insider transactions"
}

## KEYWORD MAPPING FOR AI PARAMETER EXTRACTION

### Company Name Keywords:

COMPANY_KEYWORDS = {
"Apple": ["Apple", "AAPL", "iPhone", "Mac", "iPad", "Tim Cook"],
"Microsoft": ["Microsoft", "MSFT", "Windows", "Azure", "Office", "Satya Nadella"],
"NVIDIA": ["NVIDIA", "NVDA", "GPU", "AI chips", "Jensen Huang"],
"Meta": ["Meta", "Facebook", "META", "Instagram", "WhatsApp", "Mark Zuckerberg"],
"JPMorgan": ["JPMorgan", "Chase", "JPM", "banking", "Jamie Dimon"],
"Johnson & Johnson": ["J&J", "JNJ", "pharmaceutical", "healthcare", "medical devices"],
"DoorDash": ["DoorDash", "DASH", "food delivery", "gig economy"],
"Roku": ["Roku", "streaming", "TV platform"],
"Zoom": ["Zoom", "video conferencing", "ZM", "remote work"],
"UnitedHealth": ["UnitedHealth", "UNH", "health insurance", "healthcare"]
}

### Time Period Keywords:

TIME_KEYWORDS = {
"latest": ["latest", "most recent", "current", "recent"],
"2025": ["2025", "twenty twenty-five", "fiscal 2025"],
"2024": ["2024", "twenty twenty-four", "fiscal 2024"],
"2023": ["2023", "twenty twenty-three", "fiscal 2023"],
"2022": ["2022", "twenty twenty-two", "fiscal 2022"],
"2021": ["2021", "twenty twenty-one", "fiscal 2021"],
"2020": ["2020", "twenty twenty", "fiscal 2020"]
}

### Analysis Focus Keywords:

FOCUS_KEYWORDS = {
"business": ["business", "operations", "segments", "products", "services"],
"risks": ["risks", "risk factors", "challenges", "threats"],
"financial": ["financial", "revenue", "profit", "earnings", "income"],
"acquisitions": ["acquisition", "merger", "purchase", "deal", "transaction"],
"management": ["management", "executives", "leadership", "directors"],
"legal": ["legal", "litigation", "lawsuits", "regulatory"],
"insider": ["insider", "trading", "transactions", "stock sales", "executives"]
}

## SYSTEM PROMPT ENHANCEMENTS

### Enhanced System Prompt for sec_tools.py (10-K):

You are an expert SEC 10-K filing analyst. Use this EXACT reference when extracting parameters:

EXACT COMPANY NAMES: {Apple Inc, Microsoft Corporation, NVIDIA Corporation, Meta Platforms Inc, JPMorgan Chase & Co, Johnson & Johnson, DoorDash Inc, Roku Inc, Zoom Communications Inc}

EXACT PART NAMES:

- "Part I: Business and Risk Factors"
- "Part II: Financial Information"
- "Part III: Corporate Governance and Executive Compensation"

EXACT SECTION NAMES:

- "Item 1. Business"
- "Item 1A. Risk Factors"
- "Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A)"
- "Item 8. Financial Statements and Supplementary Data"
- "Item 10. Directors, Executive Officers and Corporate Governance"
- [etc.]

YEARS: 2020, 2021, 2022, 2023, 2024, 2025 (use "latest" for most recent)

### Enhanced System Prompt for sec_8k_analyzer.py (8-K):

You are an expert SEC 8-K filing analyst. Use this EXACT reference when extracting parameters:

EXACT COMPANY NAMES: {Apple Inc, Microsoft Corporation, NVIDIA Corporation, etc.}

EXACT SECTION NAMES:

- "Section 2 - Financial Information"
- "Section 8 - Other Events"
- "Section 5 - Corporate Governance and Management"

EXACT ITEM NAMES:

- "Item 2.01 - Completion of Acquisition or Disposition of Assets"
- "Item 2.02 - Results of Operations and Financial Condition"
- "Item 8.01 - Other Events"
- [etc.]

ANALYSIS FOCUS OPTIONS: {acquisitions, financial_results, material_agreements, management_changes, legal_matters, all}

### Enhanced System Prompt for sec_insider_analyzer.py (Form 4):

You are an expert SEC Form 4 insider trading analyst. Use this EXACT reference:

EXACT COMPANY NAMES: {Apple_Inc, MICROSOFT_CORP, NVIDIA_CORP, etc.} (note underscore format)

ANALYSIS TYPES: {executive_transactions, director_activity, insider_sentiment, large_transactions, stock_options, recent_activity, all}

INSIDER ROLES: {Chief Executive Officer, Chief Financial Officer, Director, President, etc.}

DATE RANGES: Use YYYY-MM-DD format or relative terms like "last 6 months", "2024", etc.

## USAGE EXAMPLES FOR AI PROMPTS

### Example Queries and Expected Parameters:

Query: "What are Apple's main business segments?"
Expected: company="Apple Inc", year="latest", category="Part I: Business and Risk Factors", subcategory="Item 1. Business"

Query: "Microsoft's recent acquisitions and deals"
Expected: company="Microsoft Corporation", focus="acquisitions", timeframe="recent"

Query: "NVIDIA insider trading by executives in 2024"
Expected: company="NVIDIA_CORP", analysis_type="executive_transactions", date_range="2024"

This reference ensures AI parameter extraction matches EXACT JSON structure field names and values.
