import os
import json
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SECMasterAnalyzer:
    def __init__(self, api_key=None):
        """
        Initialize SEC Master Analyzer that orchestrates all SEC analysis tools
        
        Args:
            api_key (str): Google Gemini API key
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("API key must be provided either as parameter or GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Define tool configurations
        self.tools = {
            'sec_tools': {
                'script': 'sec_tools.py',
                'description': '10-K Annual Reports - Business segments, risk factors, financial information',
                'data_type': 'Annual comprehensive business analysis'
            },
            'sec_8k_analyzer': {
                'script': 'sec_8k_analyzer.py', 
                'description': '8-K Current Events - Material events, acquisitions, earnings releases',
                'data_type': 'Current events and material changes'
            },
            'sec_insider_analyzer': {
                'script': 'sec_insider_analyzer.py',
                'description': 'Form 4 Insider Trading - Executive and director transactions',
                'data_type': 'Insider trading activity'
            }
        }

    def enhance_user_query(self, user_query: str) -> Dict:
        """
        Enhance user query and determine which tools to use
        """
        enhancement_prompt = """You are an expert SEC filing analyst. Analyze the user's query and enhance it for comprehensive SEC analysis across different filing types.

## TASK
1. Enhance the user query to be more specific and analytical
2. Determine which SEC filing types would be most relevant
3. Create optimized queries for each relevant tool

## AVAILABLE TOOLS & DATA:
- **10-K Tool**: Annual reports, business segments, risk factors, financial information, governance
- **8-K Tool**: Current events, material changes, acquisitions, earnings releases, legal matters
- **Form 4 Tool**: Insider trading, executive transactions, director activity

## RESPONSE FORMAT
Return ONLY valid JSON:

{
  "enhanced_query": "Enhanced and more specific version of the user query",
  "analysis_scope": "comprehensive description of what analysis should cover",
  "tools_to_use": [
    {
      "tool": "sec_tools",
      "query": "Specific enhanced query for 10-K analysis",
      "rationale": "Why this tool is needed"
    },
    {
      "tool": "sec_8k_analyzer", 
      "query": "Specific enhanced query for 8-K analysis",
      "rationale": "Why this tool is needed"
    },
    {
      "tool": "sec_insider_analyzer",
      "query": "Specific enhanced query for Form 4 analysis", 
      "rationale": "Why this tool is needed"
    }
  ],
  "expected_insights": "What key insights should emerge from combined analysis"
}

## EXAMPLES

User: "Tell me about Apple"
{
  "enhanced_query": "Provide comprehensive analysis of Apple Inc.'s business fundamentals, recent material events, and insider trading patterns to understand the company's current position and trajectory",
  "analysis_scope": "Complete corporate analysis covering business model, recent developments, and management activity",
  "tools_to_use": [
    {
      "tool": "sec_tools",
      "query": "What are Apple's main business segments, revenue streams, and key risk factors?",
      "rationale": "10-K provides foundational business understanding"
    },
    {
      "tool": "sec_8k_analyzer",
      "query": "What material events and current developments has Apple reported recently?",
      "rationale": "8-K shows recent material changes and events"
    },
    {
      "tool": "sec_insider_analyzer", 
      "query": "Show me recent Apple insider trading activity and executive transactions",
      "rationale": "Form 4 reveals management sentiment and activity"
    }
  ],
  "expected_insights": "Integrated view of Apple's business model, recent strategic moves, and management confidence levels"
}

User Query: """
        
        try:
            full_prompt = enhancement_prompt + user_query
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                # Clean and parse JSON
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text.split('```json')[1].split('```')[0]
                elif text.startswith('```'):
                    text = text.split('```')[1].split('```')[0]
                    
                result = json.loads(text)
                print(f"✓ Query enhanced successfully")
                print(f"📋 Analysis scope: {result['analysis_scope']}")
                print(f"🔧 Tools to use: {len(result['tools_to_use'])}")
                return result
                
        except Exception as e:
            print(f"⚠️ Query enhancement error: {e}")
        
        # Fallback enhancement
        return self._fallback_enhancement(user_query)

    def _fallback_enhancement(self, user_query: str) -> Dict:
        """Fallback query enhancement using basic logic"""
        print("🔄 Using fallback query enhancement...")
        
        # Basic enhancement logic
        enhanced_query = f"Provide comprehensive SEC analysis of: {user_query}"
        
        # Determine tools based on keywords
        tools_to_use = []
        
        # Always include 10-K for business fundamentals
        tools_to_use.append({
            "tool": "sec_tools",
            "query": f"Analyze business segments and fundamentals related to: {user_query}",
            "rationale": "10-K provides business foundation"
        })
        
        # Include 8-K for material events
        if any(word in user_query.lower() for word in ['event', 'news', 'acquisition', 'earnings', 'recent']):
            tools_to_use.append({
                "tool": "sec_8k_analyzer",
                "query": f"Show material events and current developments related to: {user_query}",
                "rationale": "8-K provides current events context"
            })
        
        # Include Form 4 for insider activity
        if any(word in user_query.lower() for word in ['insider', 'trading', 'executive', 'management']):
            tools_to_use.append({
                "tool": "sec_insider_analyzer",
                "query": f"Show insider trading activity related to: {user_query}",
                "rationale": "Form 4 provides insider activity insights"
            })
        
        # If no specific triggers, use all tools
        if len(tools_to_use) == 1:  # Only had 10-K
            tools_to_use.extend([
                {
                    "tool": "sec_8k_analyzer",
                    "query": f"Show material events related to: {user_query}",
                    "rationale": "8-K provides material events context"
                },
                {
                    "tool": "sec_insider_analyzer",
                    "query": f"Show insider activity related to: {user_query}",
                    "rationale": "Form 4 provides management activity insights"
                }
            ])
        
        return {
            "enhanced_query": enhanced_query,
            "analysis_scope": f"Comprehensive SEC analysis covering: {user_query}",
            "tools_to_use": tools_to_use,
            "expected_insights": f"Multi-dimensional analysis of {user_query} across different SEC filing types"
        }

    def run_analysis_tool(self, tool_config: Dict) -> Dict:
        """
        Run individual analysis tool and capture results
        """
        tool_name = tool_config['tool']
        query = tool_config['query']
        
        print(f"🔍 Running {tool_name}: {query[:60]}...")
        
        try:
            # Build command - ensure proper quote handling and encoding for Windows
            script_path = self.tools[tool_name]['script']
            
            # For Windows, we need to handle quotes carefully and set UTF-8 encoding
            if os.name == 'nt':  # Windows
                # Set environment variables for UTF-8 encoding
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONLEGACYWINDOWSSTDIO'] = '1'
                
                cmd = f'python "{script_path}" "{query}"'
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd(), 
                                      shell=True, env=env, encoding='utf-8', errors='replace')
            else:  # Unix/Linux
                cmd = [sys.executable, script_path, query]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            # Run the tool
            start_time = datetime.now()
            end_time = datetime.now()
            
            if result.returncode == 0:
                # Parse output to find generated file
                output_lines = result.stdout.split('\n')
                generated_file = None
                
                # Look for different patterns in the output
                for line in output_lines:
                    line = line.strip()
                    if 'saved to:' in line.lower() or 'result saved to:' in line.lower() or 'analysis saved to:' in line.lower():
                        # Extract filename from output - look for .txt files
                        parts = line.split()
                        for part in parts:
                            if part.endswith('.txt'):
                                generated_file = part
                                break
                    elif line.startswith('📄') and '.txt' in line:
                        # Pattern: 📄 Result saved to: filename.txt
                        parts = line.split()
                        for part in parts:
                            if part.endswith('.txt'):
                                generated_file = part
                                break
                    
                    if generated_file:
                        break
                
                if generated_file and os.path.exists(generated_file):
                    # Read the generated analysis
                    with open(generated_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    print(f"✅ {tool_name} completed successfully")
                    return {
                        'success': True,
                        'tool': tool_name,
                        'query': query,
                        'file_path': generated_file,
                        'content': content,
                        'execution_time': (end_time - start_time).total_seconds()
                    }
                else:
                    print(f"⚠️ {tool_name} completed but no output file found")
                    print(f"STDOUT: {result.stdout}")
                    print(f"STDERR: {result.stderr}")
                    return {
                        'success': False,
                        'tool': tool_name,
                        'query': query,
                        'error': 'No output file generated',
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                print(f"❌ {tool_name} failed with error code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return {
                    'success': False,
                    'tool': tool_name,
                    'query': query,
                    'error': f'Tool failed with code {result.returncode}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except Exception as e:
            print(f"❌ Error running {tool_name}: {str(e)}")
            return {
                'success': False,
                'tool': tool_name,
                'query': query,
                'error': str(e)
            }

    def combine_analyses(self, original_query: str, enhanced_query: str, analysis_results: List[Dict]) -> str:
        """
        Combine and synthesize all analysis results using Gemini
        """
        print("🔄 Combining analyses with Gemini...")
        
        # Filter successful results
        successful_results = [r for r in analysis_results if r.get('success', False)]
        
        if not successful_results:
            return "❌ No successful analyses to combine."
        
        combination_prompt = f"""You are a senior SEC analyst tasked with synthesizing comprehensive corporate analysis from multiple SEC filing sources.

## ORIGINAL USER QUERY
{original_query}

## ENHANCED ANALYSIS SCOPE  
{enhanced_query}

## SOURCE ANALYSES
You have been provided with analysis results from three specialized SEC tools:

"""
        
        # Add each successful analysis
        for i, result in enumerate(successful_results, 1):
            tool_desc = self.tools[result['tool']]['description']
            data_type = self.tools[result['tool']]['data_type']
            
            combination_prompt += f"""
### SOURCE {i}: {result['tool'].upper().replace('_', ' ')} 
**Data Type**: {data_type}
**Tool Focus**: {tool_desc}
**Query Used**: {result['query']}

**ANALYSIS CONTENT**:
{result['content'][:4000]}  # Limit content to avoid token limits

---
"""
        
        combination_prompt += f"""

## SYNTHESIS REQUIREMENTS

### 1. EXECUTIVE SUMMARY
Create a comprehensive executive summary that integrates insights from all sources, addressing the user's original query: "{original_query}"

### 2. KEY FINDINGS INTEGRATION
Synthesize findings across different filing types:
- **Business Fundamentals** (from 10-K analysis)
- **Recent Material Events** (from 8-K analysis)  
- **Management Activity** (from Form 4 analysis)

### 3. CROSS-REFERENCE INSIGHTS
Identify connections and correlations between:
- Business strategy and recent material events
- Material events and insider trading patterns
- Risk factors and management actions
- Financial performance and strategic moves

### 4. COMPREHENSIVE TIMELINE
If applicable, create a timeline showing:
- Key business developments (10-K insights)
- Material events and announcements (8-K events)
- Insider trading activity (Form 4 transactions)

### 5. STRATEGIC IMPLICATIONS
Provide integrated analysis of:
- What the combined data reveals about company direction
- How different filing types support or contradict each other
- Overall corporate health and trajectory
- Key risks and opportunities identified across sources

### 6. DATA QUALITY NOTES
Acknowledge any limitations:
- Data gaps between different filing types
- Time period mismatches
- Areas where additional analysis would be beneficial

## RESPONSE FORMAT
Structure your response professionally for executive consumption:

# COMPREHENSIVE SEC ANALYSIS: [COMPANY/TOPIC]

## Executive Summary
[Integrated overview addressing the original query]

## Key Findings by Source
### Business Fundamentals (10-K Analysis)
[Key insights from annual report analysis]

### Material Events (8-K Analysis)  
[Key insights from current events analysis]

### Insider Activity (Form 4 Analysis)
[Key insights from insider trading analysis]

## Cross-Filing Insights
[Connections and correlations across filing types]

## Strategic Timeline
[Chronological integration if applicable]

## Implications and Conclusions
[Strategic implications and overall assessment]

## Analysis Notes
[Data limitations and recommendations]

RESPOND WITH COMPREHENSIVE SYNTHESIS:
"""
        
        try:
            response = self.model.generate_content(combination_prompt)
            return response.text if response.text else "Failed to generate combined analysis"
            
        except Exception as e:
            return f"Error combining analyses: {str(e)}"

    def process_comprehensive_query(self, user_query: str) -> Dict:
        """
        Main processing pipeline that orchestrates all tools
        """
        print(f"🚀 Starting comprehensive SEC analysis: {user_query}")
        print("="*80)
        
        # Step 1: Enhance query and determine tools
        enhancement = self.enhance_user_query(user_query)
        
        # Step 2: Run each tool
        analysis_results = []
        for tool_config in enhancement['tools_to_use']:
            result = self.run_analysis_tool(tool_config)
            analysis_results.append(result)
        
        print("\n" + "="*80)
        print("📊 INDIVIDUAL ANALYSIS SUMMARY:")
        for result in analysis_results:
            status = "✅" if result.get('success') else "❌"
            tool = result['tool'].replace('_', ' ').title()
            print(f"  {status} {tool}")
        
        # Step 3: Combine all analyses
        print("\n" + "="*80)
        combined_analysis = self.combine_analyses(
            user_query, 
            enhancement['enhanced_query'], 
            analysis_results
        )
        
        # Step 4: Save individual analyses and comprehensive result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^\w\s-]', '', user_query)[:40]
        safe_query = re.sub(r'[-\s]+', '_', safe_query)
        
        # Create a directory for this comprehensive analysis
        analysis_dir = f"comprehensive_analysis_{safe_query}_{timestamp}"
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Save individual analysis files in the directory
        individual_files = {}
        successful_results = [r for r in analysis_results if r.get('success', False)]
        
        for result in successful_results:
            if result.get('content'):
                tool_name = result['tool']
                individual_file = os.path.join(analysis_dir, f"{tool_name}_analysis_{timestamp}.txt")
                
                with open(individual_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== {tool_name.upper().replace('_', ' ')} ANALYSIS ===\n")
                    f.write(f"Original Query: {user_query}\n")
                    f.write(f"Tool Query: {result['query']}\n")
                    f.write(f"Generated: {datetime.now()}\n")
                    f.write(f"Execution Time: {result.get('execution_time', 0):.2f} seconds\n")
                    f.write("="*80 + "\n\n")
                    f.write(result['content'])
                
                individual_files[tool_name] = individual_file
                print(f"💾 Saved {tool_name} analysis: {individual_file}")
        
        # Save comprehensive combined analysis
        comprehensive_file = os.path.join(analysis_dir, f"comprehensive_analysis_{timestamp}.txt")
        
        with open(comprehensive_file, 'w', encoding='utf-8') as f:
            f.write(f"=== COMPREHENSIVE SEC ANALYSIS ===\n")
            f.write(f"Original Query: {user_query}\n")
            f.write(f"Enhanced Query: {enhancement['enhanced_query']}\n")
            f.write(f"Analysis Scope: {enhancement['analysis_scope']}\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("="*80 + "\n\n")
            
            f.write("INDIVIDUAL TOOL RESULTS:\n")
            f.write("-" * 40 + "\n")
            for result in analysis_results:
                status = "SUCCESS" if result.get('success') else "FAILED"
                tool_name = result['tool']
                f.write(f"{tool_name.upper()}: {status}\n")
                if result.get('success') and tool_name in individual_files:
                    f.write(f"  Individual File: {individual_files[tool_name]}\n")
                elif result.get('file_path'):
                    f.write(f"  Original Output: {result['file_path']}\n")
                if result.get('error'):
                    f.write(f"  Error: {result['error']}\n")
            f.write("\n" + "="*80 + "\n\n")
            
            f.write("COMPREHENSIVE COMBINED ANALYSIS:\n")
            f.write("="*80 + "\n")
            f.write(combined_analysis)
            
            # Add individual analysis sections for reference
            if successful_results:
                f.write("\n\n" + "="*80 + "\n")
                f.write("INDIVIDUAL ANALYSIS DETAILS:\n")
                f.write("="*80 + "\n")
                
                for result in successful_results:
                    tool_desc = self.tools[result['tool']]['description']
                    f.write(f"\n### {result['tool'].upper().replace('_', ' ')} ANALYSIS\n")
                    f.write(f"**Tool Focus**: {tool_desc}\n")
                    f.write(f"**Query Used**: {result['query']}\n")
                    f.write("-" * 60 + "\n")
                    f.write(result['content'][:3000])  # First 3000 chars
                    if len(result['content']) > 3000:
                        f.write("\n\n[... See individual file for complete analysis ...]\n")
                    f.write("\n" + "-" * 60 + "\n")
        
        # Also create a summary index file
        index_file = os.path.join(analysis_dir, "analysis_index.txt")
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"=== SEC ANALYSIS INDEX ===\n")
            f.write(f"Query: {user_query}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Analysis Directory: {analysis_dir}\n")
            f.write("="*50 + "\n\n")
            
            f.write("FILES CREATED:\n")
            f.write(f"📋 Master Report: {os.path.basename(comprehensive_file)}\n")
            f.write(f"📇 This Index: {os.path.basename(index_file)}\n")
            f.write("\nIndividual Analysis Files:\n")
            for tool_name, file_path in individual_files.items():
                f.write(f"📄 {tool_name.replace('_', ' ').title()}: {os.path.basename(file_path)}\n")
            
            f.write(f"\nTotal Files: {len(individual_files) + 2}\n")
            f.write(f"Successful Analyses: {len(successful_results)}/{len(analysis_results)}\n")
        
        print(f"\n✅ Comprehensive analysis complete!")
        print(f"� Analysis directory: {analysis_dir}")
        print(f"�📄 Master report: {os.path.basename(comprehensive_file)}")
        print(f"📇 Analysis index: analysis_index.txt")
        if individual_files:
            print(f"📄 Individual files: {len(individual_files)} saved")
        
        return {
            'success': True,
            'original_query': user_query,
            'enhanced_query': enhancement['enhanced_query'],
            'tools_used': len(enhancement['tools_to_use']),
            'successful_analyses': len([r for r in analysis_results if r.get('success')]),
            'analysis_results': analysis_results,
            'combined_analysis': combined_analysis,
            'analysis_directory': analysis_dir,
            'output_file': comprehensive_file,
            'individual_files': individual_files,
            'index_file': index_file
        }


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive SEC Analysis Master Tool')
    parser.add_argument('query', help='Your comprehensive question about SEC filings and corporate analysis')
    parser.add_argument('-k', '--api-key', help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        analyzer = SECMasterAnalyzer(api_key=args.api_key)
        result = analyzer.process_comprehensive_query(args.query)
        
        if result['success']:
            print("\n" + "="*80)
            print("🎯 COMPREHENSIVE ANALYSIS SUMMARY:")
            print("="*80)
            print(f"✓ Analysis directory: {result['analysis_directory']}")
            print(f"✓ Tools used: {result['tools_used']}")
            print(f"✓ Successful analyses: {result['successful_analyses']}")
            print(f"✓ Master report: {os.path.basename(result['output_file'])}")
            if result.get('individual_files'):
                print(f"✓ Individual files: {len(result['individual_files'])}")
                for tool_name, file_path in result['individual_files'].items():
                    print(f"   - {tool_name.replace('_', ' ').title()}: {os.path.basename(file_path)}")
            
            # Show preview of combined analysis
            preview = result['combined_analysis'][:1000]
            print(f"\n📋 PREVIEW:\n{preview}...")
            
        else:
            print("❌ Comprehensive analysis failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

# Usage Examples:
"""
python sec_master_analyzer.py "Tell me about Apple's business and recent developments"
python sec_master_analyzer.py "Analyze Microsoft's strategic position and insider activity"
python sec_master_analyzer.py "What's happening with NVIDIA - business, events, and management actions?"
python sec_master_analyzer.py "Comprehensive analysis of Meta's corporate situation"
python sec_master_analyzer.py "Give me a complete picture of Johnson & Johnson"
"""
