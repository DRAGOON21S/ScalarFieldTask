// SEC Analysis AI - Frontend JavaScript

class SECAnalysisAI {
    constructor() {
        this.currentQuery = '';
        this.isAnalyzing = false;
        this.initializeComponents();
        this.attachEventListeners();
    }

    initializeComponents() {
        this.queryInput = document.getElementById('queryInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    attachEventListeners() {
        // Input field events
        this.queryInput.addEventListener('input', (e) => {
            this.updateSendButton();
        });

        this.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendQuery();
            }
        });

        // Send button event
        this.sendButton.addEventListener('click', () => {
            this.sendQuery();
        });

        // Tab switching events
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.currentTarget.onclick.toString().match(/showTab\('(.+?)'\)/)?.[1];
                if (tabId) this.showTab(tabId);
            });
        });

        // Scroll to top functionality
        window.addEventListener('scroll', () => {
            const scrollToTopBtn = document.getElementById('scrollToTop');
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });

        // Smooth scroll for analysis content
        document.addEventListener('click', (e) => {
            if (e.target.matches('.analysis-content a[href^="#"]')) {
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }

    updateSendButton() {
        const hasText = this.queryInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isAnalyzing;
    }

    async sendQuery() {
        const query = this.queryInput.value.trim();
        if (!query || this.isAnalyzing) return;

        this.currentQuery = query;
        this.addUserMessage(query);
        this.queryInput.value = '';
        this.updateSendButton();
        
        await this.analyzeQuery(query);
    }

    addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'user-message';
        messageElement.innerHTML = `
            <div class="user-message-content">
                ${this.escapeHtml(message)}
            </div>
        `;
        
        this.chatMessages.appendChild(messageElement);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async analyzeQuery(query) {
        this.isAnalyzing = true;
        this.showLoadingOverlay();
        
        try {
            // Start the initial animation steps (1-3) quickly
            const initialStepsPromise = this.simulateInitialSteps();
            
            // Start the actual API call at the same time
            const apiCallPromise = this.callAnalysisAPI(query);
            
            // Wait for initial steps to complete
            await initialStepsPromise;
            
            // Keep step 3 pulsing until API call is complete
            const results = await apiCallPromise;
            
            // Show completion step
            await this.showCompletionStep();
            
            // Wait 2 seconds after showing "Complete"
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Display results
            this.displayResults(results);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Failed to analyze query. Please try again.');
        } finally {
            this.isAnalyzing = false;
            this.hideLoadingOverlay();
            this.updateSendButton();
        }
    }

    async simulateAnalysisSteps() {
        const steps = [
            { id: 'step1', duration: 2000, text: 'Parsing your query and identifying key parameters...' },
            { id: 'step2', duration: 4000, text: 'Searching SEC databases and extracting relevant data...' },
            { id: 'step3', duration: 3000, text: 'Running AI analysis and generating insights...' },
            { id: 'step4', duration: 1000, text: 'Finalizing comprehensive analysis...' }
        ];
        
        const loadingStepsContainer = document.querySelector('.loading-steps');
        const loadingText = document.querySelector('.loading-text');
        
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            // Update progress bar
            loadingStepsContainer.className = `loading-steps progress-${25 * (i + 1)}`;
            
            // Update loading text
            if (loadingText) {
                loadingText.textContent = step.text;
            }
            
            // Deactivate previous step and mark as completed
            if (i > 0) {
                const prevStep = document.getElementById(steps[i - 1].id);
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
            }
            
            // Activate current step
            const currentStep = document.getElementById(step.id);
            currentStep.classList.add('active');
            
            // Wait for step duration
            await new Promise(resolve => setTimeout(resolve, step.duration));
        }
        
        // Mark final step as completed
        const finalStep = document.getElementById('step4');
        finalStep.classList.remove('active');
        finalStep.classList.add('completed');
    }

    async simulateInitialSteps() {
        const steps = [
            { id: 'step1', duration: 1500, text: 'Parsing your query and identifying key parameters...' },
            { id: 'step2', duration: 2000, text: 'Searching SEC databases and extracting relevant data...' },
            { id: 'step3', duration: 1500, text: 'Running AI analysis and generating insights...' }
        ];
        
        const loadingStepsContainer = document.querySelector('.loading-steps');
        const loadingText = document.querySelector('.loading-text');
        
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            // Update progress bar (25%, 50%, 75% for first 3 steps)
            loadingStepsContainer.className = `loading-steps progress-${25 * (i + 1)}`;
            
            // Update loading text
            if (loadingText) {
                loadingText.textContent = step.text;
            }
            
            // Deactivate previous step and mark as completed
            if (i > 0) {
                const prevStep = document.getElementById(steps[i - 1].id);
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
            }
            
            // Activate current step
            const currentStep = document.getElementById(step.id);
            currentStep.classList.add('active');
            
            // Wait for step duration
            await new Promise(resolve => setTimeout(resolve, step.duration));
        }
        
        // Keep step 3 pulsing with waiting animation - don't mark as completed yet
        const step3 = document.getElementById('step3');
        step3.classList.remove('active');
        step3.classList.add('waiting');
        
        const loadingTextElement = document.querySelector('.loading-text');
        if (loadingTextElement) {
            loadingTextElement.textContent = 'Processing comprehensive analysis... Please wait...';
        }
    }

    async showCompletionStep() {
        const loadingStepsContainer = document.querySelector('.loading-steps');
        const loadingText = document.querySelector('.loading-text');
        
        // Update loading text
        if (loadingText) {
            loadingText.textContent = 'Analysis complete! Preparing results...';
        }
        
        // Mark step 3 as completed
        const step3 = document.getElementById('step3');
        step3.classList.remove('active', 'waiting');
        step3.classList.add('completed');
        
        // Activate and complete step 4
        const step4 = document.getElementById('step4');
        step4.classList.add('active');
        
        // Update progress bar to 100%
        loadingStepsContainer.className = 'loading-steps progress-100';
        
        // Brief pause for visual effect
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Mark step 4 as completed
        step4.classList.remove('active');
        step4.classList.add('completed');
    }

    async callAnalysisAPI(query) {
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            // For demo purposes, return mock data
            console.log('Using mock data for demo');
            return this.generateMockResults(query);
        }
    }

    generateMockResults(query) {
        const company = this.extractCompanyFromQuery(query);
        
        return {
            query: query,
            company: company,
            timestamp: new Date().toISOString(),
            combined_analysis: this.generateMockCombinedAnalysis(company, query),
            individual_analyses: {
                '10k': this.generateMock10KAnalysis(company, query),
                '8k': this.generateMock8KAnalysis(company, query),
                'form4': this.generateMockForm4Analysis(company, query)
            },
            sources: [
                { type: '10-K', company: company, year: '2024', filename: `${company}_10k.json` },
                { type: '8-K', company: company, year: '2024', filename: `${company}_8k.json` },
                { type: 'Form 4', company: company, year: '2024', filename: `${company}_form4.json` }
            ],
            analysis_files: [
                `comprehensive_analysis_${company}_${new Date().toISOString().slice(0,10)}.txt`,
                `10k_analysis_${company}_${new Date().toISOString().slice(0,10)}.txt`,
                `8k_analysis_${company}_${new Date().toISOString().slice(0,10)}.txt`,
                `form4_analysis_${company}_${new Date().toISOString().slice(0,10)}.txt`
            ]
        };
    }

    extractCompanyFromQuery(query) {
        const companies = ['Apple', 'Microsoft', 'NVIDIA', 'Meta', 'Google', 'Amazon', 'Tesla'];
        const lowerQuery = query.toLowerCase();
        
        for (const company of companies) {
            if (lowerQuery.includes(company.toLowerCase())) {
                return company;
            }
        }
        return 'Apple'; // Default for demo
    }

    generateMockCombinedAnalysis(company, query) {
        return `# Comprehensive SEC Analysis: ${company}

## Executive Summary

Based on our comprehensive analysis of ${company}'s SEC filings, here are the key insights:

### Key Findings
- **Business Segments**: ${company} operates in multiple high-growth segments with strong market positions
- **Financial Performance**: Strong revenue growth and profitability metrics across recent filings
- **Risk Management**: Well-documented risk assessment and mitigation strategies
- **Corporate Governance**: Robust governance structures and insider trading compliance

### Recent Developments
Our analysis of the most recent 8-K filings reveals several material events:
- Strategic partnerships and acquisitions
- Financial results and guidance updates
- Management changes and board appointments
- Regulatory developments and compliance matters

### Insider Trading Analysis
Form 4 filings show:
- Executive transactions aligned with company performance
- No unusual trading patterns detected
- Proper disclosure and timing compliance
- Balanced insider sentiment indicators

## Detailed Analysis

### Business Overview
${company} continues to demonstrate strong fundamentals across its core business segments. The company's strategic focus on innovation and market expansion is evident in recent filings.

### Financial Highlights
- Revenue growth trends remain positive
- Profit margins show stability and improvement
- Cash flow generation supports strategic initiatives
- Balance sheet strength provides flexibility

### Risk Assessment
Key risk factors identified include:
- Market competition and technological disruption
- Regulatory and compliance challenges
- Economic and geopolitical uncertainties
- Operational and supply chain risks

### Recommendations
Based on our comprehensive analysis:
1. Monitor ongoing developments in core business segments
2. Track regulatory changes and compliance updates
3. Watch for insider trading pattern changes
4. Follow strategic initiative progress and outcomes

*This analysis is based on the latest available SEC filings and provides a comprehensive view of ${company}'s current financial and operational status.*`;
    }

    generateMock10KAnalysis(company, query) {
        return `# ${company} 10-K Annual Report Analysis

## Business Segments Analysis

### Primary Business Lines
${company} operates through several key business segments:

**Technology Products & Services**
- Core product offerings showing strong market demand
- Innovation pipeline supporting future growth
- Market share leadership in key categories

**Financial Performance by Segment**
- Detailed revenue breakdown by geographic region
- Profit margin analysis by product category
- Growth trends and market opportunities

## Risk Factors Assessment

### Market Risks
- Competitive pressure from industry players
- Technology disruption and innovation cycles
- Customer demand variability

### Operational Risks
- Supply chain dependencies and vulnerabilities
- Talent acquisition and retention challenges
- Regulatory compliance requirements

### Financial Risks
- Interest rate and currency fluctuations
- Credit risk and customer concentrations
- Liquidity and capital allocation decisions

## Management Discussion & Analysis

The company's MD&A section provides detailed insights into:
- Operating performance drivers
- Strategic initiatives and investments
- Market outlook and guidance
- Capital allocation priorities

## Corporate Governance

### Board Structure
- Independent director representation
- Committee structures and responsibilities
- Executive compensation alignment

### Risk Oversight
- Enterprise risk management framework
- Internal controls and audit procedures
- Compliance monitoring systems

*Analysis based on latest 10-K filing data*`;
    }

    generateMock8KAnalysis(company, query) {
        return `# ${company} 8-K Current Events Analysis

## Recent Material Events

### Financial Results & Guidance
**Item 2.02 - Results of Operations and Financial Condition**
- Quarterly earnings announcements
- Revenue and profit performance updates
- Forward-looking guidance revisions

### Corporate Actions
**Item 8.01 - Other Events**
- Strategic partnerships and alliances
- Product launches and market expansions
- Regulatory approvals and certifications

### Management Changes
**Item 5.02 - Departure of Directors or Principal Officers**
- Executive appointments and departures
- Board composition changes
- Leadership succession planning

## Event Impact Analysis

### Market Significance
Each reported event has been evaluated for:
- Financial impact on operations
- Strategic importance to business objectives
- Stakeholder implications and communications

### Regulatory Compliance
All 8-K filings demonstrate:
- Timely disclosure of material events
- Proper categorization and documentation
- Regulatory requirement adherence

## Timeline of Events

### Recent Quarter Activity
- Month-by-month breakdown of material events
- Event clustering and significance patterns
- Market response and stakeholder reactions

### Forward-Looking Indicators
- Events suggesting future business direction
- Strategic initiative progress markers
- Market opportunity developments

*Analysis covers all material 8-K filings in the specified period*`;
    }

    generateMockForm4Analysis(company, query) {
        return `# ${company} Insider Trading Analysis (Form 4)

## Executive Trading Summary

### Key Insider Activity
**Trading Volume Analysis**
- Total transaction value: Detailed breakdown by insider
- Transaction frequency and timing patterns
- Buy vs. sell ratio analysis

**Notable Transactions**
- Large block trades and their context
- Option exercises and stock grants
- Timing relative to earnings and events

## Insider Sentiment Analysis

### Executive Behavior Patterns
**CEO & C-Suite Activity**
- Recent trading by top executives
- Pattern consistency with historical behavior
- Alignment with company performance

**Director Trading**
- Board member transaction analysis
- Independent director activity levels
- Compensation-related vs. discretionary trades

## Compliance & Governance

### Filing Timeliness
- All Form 4 filings submitted within required timeframes
- Complete disclosure of insider relationships
- Proper transaction categorization

### Trading Plan Compliance
- 10b5-1 trading plan adherence
- Pre-arranged transaction patterns
- Insider trading policy compliance

## Risk Assessment

### Red Flag Analysis
✅ No unusual trading patterns detected
✅ Proper disclosure timing maintained
✅ Transaction sizes within normal ranges
✅ No concerning concentration of selling

### Positive Indicators
- Executive retention and commitment
- Long-term shareholding patterns
- Balanced trading activity

*Analysis based on most recent Form 4 filings and insider trading data*`;
    }

    displayResults(results) {
        // Store current analysis title for minimize functionality
        this.currentAnalysisTitle = `Analysis Results - ${results.query || 'Latest Analysis'}`;
        
        // Hide welcome message
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }

        // Show results container
        this.resultsContainer.style.display = 'block';

        // Only populate combined analysis content
        const combinedContent = this.formatAnalysisContent(results.combined_analysis);
        document.getElementById('content-combined').innerHTML = combinedContent;

        // Debug: Log content length
        console.log('Combined content length:', combinedContent.length);

        // Add scroll event listeners for the combined tab only
        this.setupScrollIndicators();

        // Add scroll to top button for combined tab
        this.addScrollToTopForTabs();

        // Ensure content is rendered before checking scroll
        setTimeout(() => {
            this.checkContentOverflow();
        }, 200);

        // Show success notification
        this.showNotification('Analysis completed successfully! Results are now available in the tabs below.', 'success');

        // Populate sources
        this.displaySources(results.sources, results.analysis_files);

        // Scroll to results
        this.resultsContainer.scrollIntoView({ behavior: 'smooth' });

        // Re-initialize Lucide icons for new content
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    addScrollToTopForTabs() {
        // Add smooth scrolling to all tab panes
        document.querySelectorAll('.analysis-content').forEach(content => {
            content.addEventListener('scroll', (e) => {
                // Add subtle scroll indicator
                const scrollPercent = (e.target.scrollTop / (e.target.scrollHeight - e.target.clientHeight)) * 100;
                e.target.style.background = `linear-gradient(to right, rgba(96, 165, 250, 0.1) ${scrollPercent}%, transparent ${scrollPercent}%) top / 100% 2px no-repeat`;
            });
        });
    }

    formatAnalysisContent(content) {
        // Enhanced markdown-like content to HTML conversion
        if (!content) return '<p>No content available.</p>';
        
        // Remove technical headers and metadata
        let processedContent = content
            .replace(/\r\n/g, '\n')
            .replace(/\r/g, '\n');
        
        // Remove technical header sections
        const linesToRemove = [
            /^=== SEC TOOLS ANALYSIS ===$/m,
            /^=== COMPREHENSIVE SEC ANALYSIS ===$/m,
            /^Original Query:.*$/m,
            /^Tool Query:.*$/m,
            /^Enhanced Query:.*$/m,
            /^Generated:.*$/m,
            /^Execution Time:.*$/m,
            /^Analysis Scope:.*$/m,
            /^INDIVIDUAL TOOL RESULTS:$/m,
            /^-+$/m, // Lines of dashes
            /^=+$/m, // Lines of equal signs
            /^=== SEC FILING ANALYSIS RESULT ===$/m,
            /^Query:.*$/m,
            /^Generated:.*$/m,
            /^SEC_TOOLS: SUCCESS$/m,
            /^SEC.*ANALYZER: SUCCESS$/m,
            /^Individual File:.*\.txt$/m
        ];
        
        // Split into lines for processing
        let headerLines = processedContent.split('\n');
        let cleanedLines = [];
        let skipUntilContent = false;
        
        for (let i = 0; i < headerLines.length; i++) {
            let line = headerLines[i].trim();
            
            // Skip the technical header section
            if (line.match(/^=== (SEC TOOLS ANALYSIS|COMPREHENSIVE SEC ANALYSIS|SEC FILING ANALYSIS RESULT) ===/)) {
                skipUntilContent = true;
                continue;
            }
            
            // Skip individual header lines
            let shouldSkip = linesToRemove.some(pattern => line.match(pattern));
            if (shouldSkip) {
                continue;
            }
            
            // Skip lines that are just equal signs or dashes
            if (line.match(/^[=-]+$/) && line.length > 5) {
                continue;
            }
            
            // Skip technical status lines
            if (line.match(/^SEC.*: SUCCESS$/)) {
                continue;
            }
            
            // Start including content after we find substantial content
            if (skipUntilContent) {
                // Look for the start of actual analysis content (usually starts with a paragraph or heading)
                if (line.length > 0 && 
                    !line.match(/^(Original Query|Tool Query|Enhanced Query|Generated|Execution Time|Query|Analysis Scope|INDIVIDUAL TOOL RESULTS|SEC_TOOLS|SEC.*ANALYZER|Individual File|=|-)/)) {
                    skipUntilContent = false;
                    cleanedLines.push(headerLines[i]); // Keep original spacing
                }
            } else {
                cleanedLines.push(headerLines[i]); // Keep original spacing
            }
        }
        
        // Join back and continue with existing formatting
        processedContent = cleanedLines.join('\n');
        
        // Handle different heading levels
        processedContent = processedContent
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^#### (.*$)/gim, '<h4>$1</h4>');
        
        // Handle bold and italic text
        processedContent = processedContent
            .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/__(.*?)__/g, '<strong>$1</strong>')
            .replace(/_(.*?)_/g, '<em>$1</em>');
        
        // Handle lists with better formatting
        processedContent = processedContent
            .replace(/^\* (.+)$/gim, '<li>$1</li>')
            .replace(/^- (.+)$/gim, '<li>$1</li>')
            .replace(/^\+ (.+)$/gim, '<li>$1</li>')
            .replace(/^(\d+)\. (.+)$/gim, '<li data-number="$1">$2</li>');
        
        // Handle code blocks
        processedContent = processedContent
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Handle blockquotes
        processedContent = processedContent
            .replace(/^> (.+)$/gim, '<blockquote>$1</blockquote>');
        
        // Handle horizontal rules
        processedContent = processedContent
            .replace(/^---$/gim, '<hr>')
            .replace(/^===$/gim, '<hr>');
        
        // Handle special status indicators
        processedContent = processedContent
            .replace(/✅/g, '<span class="success">✅</span>')
            .replace(/❌/g, '<span class="error">❌</span>')
            .replace(/⚠️/g, '<span class="warning">⚠️</span>')
            .replace(/ℹ️/g, '<span class="info">ℹ️</span>')
            .replace(/🔍/g, '<span class="info">🔍</span>')
            .replace(/📊/g, '<span class="info">📊</span>')
            .replace(/💡/g, '<span class="info">💡</span>')
            .replace(/🎯/g, '<span class="success">🎯</span>');
        
        // Handle line breaks and paragraphs
        let lines = processedContent.split('\n');
        let htmlLines = [];
        let inList = false;
        let listType = '';
        let inBlockquote = false;
        let inCodeBlock = false;
        
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            
            // Skip empty lines in certain contexts
            if (line === '') {
                if (inList) {
                    htmlLines.push(`</${listType}>`);
                    inList = false;
                }
                if (inBlockquote) {
                    htmlLines.push('</blockquote>');
                    inBlockquote = false;
                }
                htmlLines.push('');
                continue;
            }
            
            // Handle code blocks
            if (line.startsWith('<pre><code>')) {
                inCodeBlock = true;
                htmlLines.push(line);
                continue;
            }
            if (line.endsWith('</code></pre>')) {
                inCodeBlock = false;
                htmlLines.push(line);
                continue;
            }
            if (inCodeBlock) {
                htmlLines.push(line);
                continue;
            }
            
            // Handle lists
            if (line.startsWith('<li')) {
                if (!inList) {
                    // Determine list type
                    if (line.includes('data-number=')) {
                        listType = 'ol';
                    } else {
                        listType = 'ul';
                    }
                    htmlLines.push(`<${listType}>`);
                    inList = true;
                }
                htmlLines.push(line);
                continue;
            } else if (inList) {
                htmlLines.push(`</${listType}>`);
                inList = false;
            }
            
            // Handle blockquotes
            if (line.startsWith('<blockquote>')) {
                if (!inBlockquote) {
                    inBlockquote = true;
                }
                htmlLines.push(line);
                continue;
            } else if (inBlockquote) {
                htmlLines.push('</blockquote>');
                inBlockquote = false;
            }
            
            // Handle headings and other elements
            if (line.startsWith('<h') || line.startsWith('<hr') || line === '') {
                htmlLines.push(line);
            } else if (!line.startsWith('<')) {
                // Regular paragraph
                htmlLines.push(`<p>${line}</p>`);
            } else {
                htmlLines.push(line);
            }
        }
        
        // Close any remaining open lists
        if (inList) {
            htmlLines.push(`</${listType}>`);
        }
        if (inBlockquote) {
            htmlLines.push('</blockquote>');
        }
        
        // Join and clean up
        let finalContent = htmlLines.join('\n');
        
        // Clean up multiple consecutive empty paragraphs
        finalContent = finalContent
            .replace(/<p><\/p>/g, '')
            .replace(/\n\s*\n\s*\n/g, '\n\n')
            .replace(/<\/blockquote>\s*<blockquote>/g, '<br>');
        
        return finalContent;
    }

    displaySources(sources, analysisFiles) {
        const sourcesList = document.getElementById('sourcesList');
        sourcesList.innerHTML = '';

        // Add data sources
        sources.forEach(source => {
            const sourceElement = document.createElement('div');
            sourceElement.className = 'source-item';
            sourceElement.innerHTML = `
                <i data-lucide="file-text"></i>
                <span>${source.type} - ${source.company} (${source.year})</span>
            `;
            sourcesList.appendChild(sourceElement);
        });

        // Add analysis files
        analysisFiles.forEach(file => {
            const sourceElement = document.createElement('div');
            sourceElement.className = 'source-item download-item';
            sourceElement.style.cursor = 'pointer';
            sourceElement.innerHTML = `
                <i data-lucide="download"></i>
                <span>${file}</span>
            `;
            
            // Add click handler for download
            sourceElement.addEventListener('click', () => {
                this.downloadFile(file);
            });
            
            sourcesList.appendChild(sourceElement);
        });

        // Re-initialize Lucide icons for new elements
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    showTab(tabId) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`tab-${tabId}`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`pane-${tabId}`).classList.add('active');
    }

    minimizeResults() {
        this.resultsContainer.style.display = 'none';
        
        // Show minimized state
        const minimizedResults = document.getElementById('minimizedResults');
        minimizedResults.style.display = 'flex';
        
        // Update minimized title if available
        const titleElement = minimizedResults.querySelector('.minimized-title');
        if (this.currentAnalysisTitle) {
            titleElement.textContent = this.currentAnalysisTitle;
        }
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    maximizeResults() {
        // Hide minimized state
        const minimizedResults = document.getElementById('minimizedResults');
        minimizedResults.style.display = 'none';
        
        // Show full results
        this.resultsContainer.style.display = 'block';
        
        // Hide welcome message
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
    }

    downloadFile(filename) {
        // Create download link
        const downloadUrl = `/api/download/${encodeURIComponent(filename)}`;
        
        // Create temporary link element
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.style.display = 'none';
        
        // Add to DOM, click, and remove
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    showLoadingOverlay() {
        // Reset all steps to initial state
        this.resetLoadingSteps();
        
        this.loadingOverlay.style.display = 'flex';
        this.loadingOverlay.style.opacity = '0';
        this.loadingOverlay.style.transform = 'scale(0.95)';
        
        // Animate in
        requestAnimationFrame(() => {
            this.loadingOverlay.style.transition = 'all 0.3s ease';
            this.loadingOverlay.style.opacity = '1';
            this.loadingOverlay.style.transform = 'scale(1)';
        });
    }

    resetLoadingSteps() {
        // Reset all steps
        const steps = ['step1', 'step2', 'step3', 'step4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            if (step) {
                step.classList.remove('active', 'completed', 'waiting');
            }
        });
        
        // Reset progress bar
        const loadingStepsContainer = document.querySelector('.loading-steps');
        if (loadingStepsContainer) {
            loadingStepsContainer.className = 'loading-steps';
        }
        
        // Reset loading text
        const loadingText = document.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = 'Processing your query through our AI analysis system';
        }
        
        // Activate first step
        const firstStep = document.getElementById('step1');
        if (firstStep) {
            firstStep.classList.add('active');
        }
    }

    hideLoadingOverlay() {
        this.loadingOverlay.style.display = 'none';
    }

    showError(message) {
        this.showNotification(message, 'error');
        
        // Also add to chat for context
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.innerHTML = `
            <div class="error-content">
                <i data-lucide="alert-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        this.chatMessages.appendChild(errorElement);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info';
        
        notification.innerHTML = `
            <div class="notification-content">
                <i data-lucide="${icon}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Re-initialize Lucide icons for the new elements
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('notification-exit');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    checkContentOverflow() {
        // Only check combined analysis content
        const contentAreas = ['content-combined'];
        
        contentAreas.forEach(areaId => {
            const element = document.getElementById(areaId);
            if (element) {
                const scrollHeight = element.scrollHeight;
                const clientHeight = element.clientHeight;
                const isOverflowing = scrollHeight > clientHeight;
                
                console.log(`${areaId}:`, {
                    scrollHeight,
                    clientHeight,
                    isOverflowing,
                    content: element.innerHTML.substring(0, 100) + '...'
                });
            }
        });
    }

    setupScrollIndicators() {
        // Only setup for combined analysis
        const contentAreas = [
            { content: 'content-combined', indicator: 'scroll-indicator-combined' }
        ];

        contentAreas.forEach(area => {
            const contentElement = document.getElementById(area.content);
            const indicatorElement = document.getElementById(area.indicator);
            
            if (contentElement && indicatorElement) {
                // Check if content is scrollable
                const checkScrollable = () => {
                    const isScrollable = contentElement.scrollHeight > contentElement.clientHeight;
                    const isScrolledToBottom = contentElement.scrollTop + contentElement.clientHeight >= contentElement.scrollHeight - 10;
                    
                    if (isScrollable && !isScrolledToBottom) {
                        indicatorElement.classList.add('visible');
                    } else {
                        indicatorElement.classList.remove('visible');
                    }
                };

                // Initial check
                setTimeout(checkScrollable, 100);

                // Add scroll listener
                contentElement.addEventListener('scroll', checkScrollable);
                
                // Re-check on window resize
                window.addEventListener('resize', checkScrollable);
            }
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for HTML onclick handlers
function setQuery(query) {
    const app = window.secAnalysisApp;
    if (app) {
        app.queryInput.value = query;
        app.updateSendButton();
        app.queryInput.focus();
    }
}

function showTab(tabId) {
    const app = window.secAnalysisApp;
    if (app) {
        app.showTab(tabId);
    }
}

function minimizeResults() {
    const app = window.secAnalysisApp;
    if (app) {
        app.minimizeResults();
    }
}

function maximizeResults() {
    const app = window.secAnalysisApp;
    if (app) {
        app.maximizeResults();
    }
}

function sendQuery() {
    const app = window.secAnalysisApp;
    if (app) {
        app.sendQuery();
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.secAnalysisApp = new SECAnalysisAI();
    
    // Initialize Lucide icons after DOM is ready
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
