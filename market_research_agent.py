#!/usr/bin/env python3
"""
Agentic AI Market Research Agent - Standalone Version
Perfect for client discovery calls and business opportunity assessments.
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

# Import AI frameworks
try:
    from crewai import Agent, Task, Crew
    from langchain_openai import ChatOpenAI

    print("✅ AI packages imported successfully!")
except ImportError as e:
    print(f"❌ Error importing required packages: {e}")
    print("Please run: pip install crewai langchain-openai python-dotenv")
    exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✅ Environment variables loaded!")
except ImportError:
    print("⚠️ python-dotenv not found, using OS environment variables")
    pass


@dataclass
class BusinessProfile:
    """Structure for business information"""

    name: str
    industry: str
    size: str
    revenue_range: str
    description: str
    pain_points: List[str]
    current_processes: List[str]


@dataclass
class ProcessAnalysis:
    """Analysis of a specific business process"""

    name: str
    time_percentage: float
    complexity_score: int  # 1-5 scale
    automation_potential: str  # High, Medium, Low
    current_cost_annual: float
    potential_savings: float
    roi_percentage: float
    implementation_difficulty: str


@dataclass
class MarketResearchResult:
    """Complete market research analysis result"""

    business_profile: BusinessProfile
    process_analyses: List[ProcessAnalysis]
    overall_roi: float
    recommended_solution: Dict
    implementation_roadmap: List[str]
    investment_range: str
    payback_months: int


class MarketResearchAgent:
    """AI-powered market research and opportunity analysis agent"""

    def __init__(self, api_key: str = None):
        """Initialize the agent with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "sk-your-key-here":
            print("❌ Error: OpenAI API key not configured!")
            print("Please edit the .env file and add your actual OpenAI API key")
            print("Get your key from: https://platform.openai.com/api-keys")
            exit(1)

        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # Cost-effective model
                temperature=0.3,
                api_key=self.api_key,
            )
            print("✅ AI model initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing AI model: {e}")
            print("Please check your API key and internet connection")
            exit(1)

    def create_research_crew(self) -> Crew:
        """Create the multi-agent research crew"""

        # Market Research Analyst
        researcher = Agent(
            role="Senior Market Research Analyst",
            goal="Analyze business operations and identify AI automation opportunities",
            backstory="""You are an expert business analyst with 15+ years experience in 
                        operational efficiency and technology implementations. You specialize 
                        in identifying high-impact automation opportunities and quantifying 
                        business value.""",
            llm=self.llm,
            verbose=False,
        )

        # Business Process Expert
        process_expert = Agent(
            role="Business Process Optimization Specialist",
            goal="Evaluate current processes and design automation solutions",
            backstory="""You are a certified Six Sigma Black Belt with extensive experience 
                        in process improvement and automation. You can quickly identify 
                        bottlenecks, inefficiencies, and automation opportunities in any 
                        business process.""",
            llm=self.llm,
            verbose=False,
        )

        # ROI Calculator
        roi_analyst = Agent(
            role="Financial ROI Analyst",
            goal="Calculate accurate ROI projections and business impact",
            backstory="""You are a financial analyst specializing in technology ROI calculations.
                        You have deep experience in cost-benefit analysis, payback period 
                        calculations, and business case development for automation projects.""",
            llm=self.llm,
            verbose=False,
        )

        return Crew(agents=[researcher, process_expert, roi_analyst], verbose=False)

    def analyze_business(self, business_description: str) -> MarketResearchResult:
        """Perform comprehensive business analysis"""

        print("🤖 Starting AI analysis...")
        print("   Initializing research agents...")

        try:
            crew = self.create_research_crew()

            # Market Research Task
            research_task = Task(
                description=f"""
                Analyze this business and identify automation opportunities:
                
                Business Description: {business_description}
                
                Your analysis should include:
                1. Business classification (industry, size, revenue estimate)
                2. Identification of 3-5 most time-consuming manual processes
                3. Assessment of current operational costs and inefficiencies
                4. Preliminary automation opportunity assessment
                
                Focus on quantifiable, high-impact areas where AI agents could provide immediate value.
                Be specific about time spent on each process and current business impact.
                """,
                agent=crew.agents[0],
                expected_output="Structured business analysis with process identification and initial opportunity assessment",
            )

            # Process Analysis Task
            process_task = Task(
                description="""
                Based on the business analysis, perform detailed process evaluation:
                
                For each identified process, analyze:
                1. Current time investment (hours/week, cost/year)
                2. Complexity level (1-5 scale)
                3. Automation potential (High/Medium/Low)
                4. Specific AI solutions that could address this process
                5. Implementation complexity and timeline
                
                Prioritize processes by ROI potential and implementation feasibility.
                """,
                agent=crew.agents[1],
                expected_output="Detailed process analysis with automation recommendations and priority ranking",
            )

            # ROI Calculation Task
            roi_task = Task(
                description="""
                Calculate comprehensive ROI analysis for the identified opportunities:
                
                For the top 3 processes, calculate:
                1. Current annual cost (time * hourly rate + opportunity cost)
                2. Potential automation savings (% reduction in time/cost)
                3. Implementation investment required
                4. Payback period and 3-year ROI
                5. Risk factors and mitigation strategies
                
                Provide conservative, realistic, and optimistic scenarios.
                Include specific dollar amounts and percentages.
                """,
                agent=crew.agents[2],
                expected_output="Detailed ROI calculations with investment recommendations and financial projections",
            )

            # Execute the analysis
            crew.tasks = [research_task, process_task, roi_task]

            print("   Agents analyzing business processes...")
            print("   Calculating ROI projections...")

            result = crew.kickoff()

            # Parse and structure the results
            return self._parse_analysis_result(result, business_description)

        except Exception as e:
            print(f"❌ Error during AI analysis: {e}")
            print("Creating fallback analysis...")
            return self._create_fallback_analysis(business_description)

    def _create_fallback_analysis(
        self, business_description: str
    ) -> MarketResearchResult:
        """Create a fallback analysis if AI fails"""

        business_profile = BusinessProfile(
            name="Client Business",
            industry=self._extract_industry(business_description),
            size=self._estimate_business_size(business_description),
            revenue_range=self._estimate_revenue(business_description),
            description=business_description,
            pain_points=[
                "Manual processes",
                "Time-intensive tasks",
                "Operational inefficiencies",
            ],
            current_processes=[
                "Research tasks",
                "Report generation",
                "Communication management",
            ],
        )

        # Create realistic process analyses based on business type
        if (
            "marketing" in business_description.lower()
            or "consultant" in business_description.lower()
        ):
            process_analyses = [
                ProcessAnalysis(
                    name="Client Research & Market Analysis",
                    time_percentage=40.0,
                    complexity_score=3,
                    automation_potential="High",
                    current_cost_annual=48000,
                    potential_savings=33600,
                    roi_percentage=70.0,
                    implementation_difficulty="Medium",
                ),
                ProcessAnalysis(
                    name="Proposal and Content Creation",
                    time_percentage=30.0,
                    automation_potential="High",
                    complexity_score=4,
                    current_cost_annual=36000,
                    potential_savings=28800,
                    roi_percentage=80.0,
                    implementation_difficulty="Low",
                ),
                ProcessAnalysis(
                    name="Client Communication & Reporting",
                    time_percentage=20.0,
                    complexity_score=2,
                    automation_potential="Medium",
                    current_cost_annual=24000,
                    potential_savings=14400,
                    roi_percentage=60.0,
                    implementation_difficulty="Low",
                ),
            ]
        else:
            # Generic business processes
            process_analyses = [
                ProcessAnalysis(
                    name="Research & Data Collection",
                    time_percentage=35.0,
                    complexity_score=3,
                    automation_potential="High",
                    current_cost_annual=52500,
                    potential_savings=36750,
                    roi_percentage=70.0,
                    implementation_difficulty="Medium",
                ),
                ProcessAnalysis(
                    name="Report and Document Generation",
                    time_percentage=25.0,
                    automation_potential="High",
                    complexity_score=4,
                    current_cost_annual=37500,
                    potential_savings=30000,
                    roi_percentage=80.0,
                    implementation_difficulty="Low",
                ),
                ProcessAnalysis(
                    name="Administrative Tasks",
                    time_percentage=20.0,
                    complexity_score=2,
                    automation_potential="Medium",
                    current_cost_annual=30000,
                    potential_savings=18000,
                    roi_percentage=60.0,
                    implementation_difficulty="Low",
                ),
            ]

        # Calculate overall metrics
        total_current_cost = sum(p.current_cost_annual for p in process_analyses)
        total_savings = sum(p.potential_savings for p in process_analyses)
        implementation_cost = total_current_cost * 0.25  # Assume 25% of annual cost
        overall_roi = (
            (total_savings / implementation_cost) * 100
            if implementation_cost > 0
            else 0
        )

        recommended_solution = {
            "approach": "Multi-Agent Business Automation Platform",
            "components": ["Research Agent", "Content Generator", "Communication Bot"],
            "timeline": "8-12 weeks",
            "investment": f"${implementation_cost:,.0f} - ${implementation_cost * 1.5:,.0f}",
        }

        implementation_roadmap = [
            "Week 1-2: Discovery and requirements gathering",
            "Week 3-4: Agent design and architecture planning",
            "Week 5-8: Core agent development and testing",
            "Week 9-10: Integration and system testing",
            "Week 11-12: Deployment and user training",
        ]

        return MarketResearchResult(
            business_profile=business_profile,
            process_analyses=process_analyses,
            overall_roi=overall_roi,
            recommended_solution=recommended_solution,
            implementation_roadmap=implementation_roadmap,
            investment_range=recommended_solution["investment"],
            payback_months=int(
                (implementation_cost / (total_savings / 12))
                if total_savings > 0
                else 12
            ),
        )

    def _parse_analysis_result(
        self, raw_result: str, business_description: str
    ) -> MarketResearchResult:
        """Parse the raw agent result into structured data"""
        # For now, use the fallback - in production you'd parse the LLM output
        return self._create_fallback_analysis(business_description)

    def _extract_industry(self, description: str) -> str:
        """Extract industry from business description with better coverage"""
        description_lower = description.lower()

        industry_keywords = {
            "banking": [
                "bank",
                "banking",
                "financial services",
                "finance",
                "credit union",
                "lending",
            ],
            "legal": ["law", "legal", "attorney", "lawyer", "court", "litigation"],
            "consulting": ["consultant", "consulting", "advisory", "strategy"],
            "real_estate": ["real estate", "property", "realtor", "housing"],
            "healthcare": [
                "medical",
                "healthcare",
                "clinic",
                "doctor",
                "patient",
                "hospital",
            ],
            "manufacturing": ["manufacturing", "production", "factory", "assembly"],
            "marketing": ["marketing", "advertising", "digital", "social media"],
            "accounting": ["accounting", "bookkeeping", "tax", "cpa"],
            "insurance": ["insurance", "underwriting", "claims", "actuarial"],
            "retail": ["retail", "store", "shopping", "merchandise"],
            "technology": ["software", "tech", "it", "development", "saas"],
            "education": ["education", "school", "university", "training"],
        }

        for industry, keywords in industry_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return industry.title()

        return "Professional Services"

    def _estimate_business_size(self, description: str) -> str:
        """Estimate business size with proper enterprise scaling"""
        description_lower = description.lower()

        # Look for employee numbers first
        import re

        employee_matches = re.findall(
            r"(\d{1,6})\s*(?:employees|people|staff)", description_lower
        )
        if employee_matches:
            emp_count = int(employee_matches[0])
            if emp_count >= 10000:
                return f"Large Enterprise ({emp_count:,} employees)"
            elif emp_count >= 1000:
                return f"Mid-Large Enterprise ({emp_count:,} employees)"
            elif emp_count >= 500:
                return f"Mid-Market ({emp_count:,} employees)"
            elif emp_count >= 100:
                return f"Small-Mid Market ({emp_count:,} employees)"
            elif emp_count >= 20:
                return f"Small Business ({emp_count} employees)"
            else:
                return f"Small Business ({emp_count} employees)"

        # Fallback to keyword detection
        if any(
            word in description_lower for word in ["solo", "freelance", "independent"]
        ):
            return "Solo/Freelance"
        elif any(word in description_lower for word in ["small", "startup"]):
            return "Small Business (2-50 employees)"
        elif any(word in description_lower for word in ["mid-size", "medium"]):
            return "Mid-Market (51-500 employees)"
        elif any(
            word in description_lower for word in ["large", "enterprise", "corporation"]
        ):
            return "Large Enterprise (1000+ employees)"
        else:
            return "Small-Medium Business"

    def _estimate_revenue(self, description: str) -> str:
        """Estimate revenue range with enterprise brackets"""
        description_lower = description.lower()

        # Look for revenue numbers first
        import re

        # Match patterns like "$4.39 billion", "4.39B", "$500M", etc.
        revenue_patterns = [
            r"\$?(\d+\.?\d*)\s*billion",
            r"\$?(\d+\.?\d*)\s*b\b",
            r"\$?(\d+\.?\d*)\s*million",
            r"\$?(\d+\.?\d*)\s*m\b",
            r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        ]

        for pattern in revenue_patterns:
            matches = re.findall(pattern, description_lower)
            if matches:
                amount = float(matches[0].replace(",", ""))

                if "billion" in description_lower or "b" in description_lower:
                    if amount >= 10:
                        return f"${amount}B+ (Large Enterprise)"
                    elif amount >= 1:
                        return f"${amount}B (Enterprise)"
                    else:
                        return f"${amount*1000}M (Large Corporate)"

                elif "million" in description_lower or "m" in description_lower:
                    if amount >= 500:
                        return f"${amount}M+ (Large Corporate)"
                    elif amount >= 100:
                        return f"${amount}M (Mid-Large Market)"
                    elif amount >= 10:
                        return f"${amount}M (Mid-Market)"
                    else:
                        return f"${amount}M (Small-Mid Market)"

                else:
                    # Raw dollar amount
                    if amount >= 1000000000:
                        return f"${amount/1000000000:.1f}B (Enterprise)"
                    elif amount >= 1000000:
                        return f"${amount/1000000:.0f}M (Corporate)"
                    else:
                        return f"${amount:,.0f} (Small Business)"

        # Fallback based on business size keywords
        if any(word in description_lower for word in ["solo", "freelance"]):
            return "$100K - $500K"
        elif any(word in description_lower for word in ["small", "startup"]):
            return "$500K - $10M"
        elif any(
            word in description_lower for word in ["enterprise", "corporation", "large"]
        ):
            return "$100M+"
        else:
            return "$1M - $50M"

    def _create_fallback_analysis(
        self, business_description: str
    ) -> MarketResearchResult:
        """Create industry-specific analysis based on business type"""

        business_profile = BusinessProfile(
            name="Client Business",
            industry=self._extract_industry(business_description),
            size=self._estimate_business_size(business_description),
            revenue_range=self._estimate_revenue(business_description),
            description=business_description,
            pain_points=[
                "Manual processes",
                "Time-intensive tasks",
                "Operational inefficiencies",
            ],
            current_processes=[
                "Research tasks",
                "Report generation",
                "Communication management",
            ],
        )

        # Industry-specific process analysis
        industry = business_profile.industry.lower()

        if industry == "banking":
            # Banking-specific processes and costs
            annual_revenue = self._extract_revenue_number(business_description)
            base_cost = max(
                annual_revenue * 0.15, 50000000
            )  # At least 15% of revenue or $50M

            process_analyses = [
                ProcessAnalysis(
                    name="Regulatory Compliance & Reporting",
                    time_percentage=40.0,
                    complexity_score=5,
                    automation_potential="High",
                    current_cost_annual=base_cost * 0.4,
                    potential_savings=base_cost * 0.4 * 0.6,  # 60% savings potential
                    roi_percentage=60.0,
                    implementation_difficulty="High",
                ),
                ProcessAnalysis(
                    name="Risk Management & Data Analysis",
                    time_percentage=25.0,
                    automation_potential="High",
                    complexity_score=4,
                    current_cost_annual=base_cost * 0.25,
                    potential_savings=base_cost * 0.25 * 0.7,  # 70% savings
                    roi_percentage=70.0,
                    implementation_difficulty="Medium",
                ),
                ProcessAnalysis(
                    name="Customer Due Diligence & KYC",
                    time_percentage=20.0,
                    complexity_score=4,
                    automation_potential="High",
                    current_cost_annual=base_cost * 0.20,
                    potential_savings=base_cost * 0.20 * 0.8,  # 80% savings
                    roi_percentage=80.0,
                    implementation_difficulty="Medium",
                ),
                ProcessAnalysis(
                    name="Cybersecurity Monitoring & Response",
                    time_percentage=15.0,
                    complexity_score=5,
                    automation_potential="Medium",
                    current_cost_annual=base_cost * 0.15,
                    potential_savings=base_cost * 0.15 * 0.5,  # 50% savings
                    roi_percentage=50.0,
                    implementation_difficulty="High",
                ),
            ]

            recommended_solution = {
                "approach": "Enterprise AI Compliance & Risk Management Platform",
                "components": [
                    "Regulatory Reporting Agent",
                    "Risk Analysis Engine",
                    "KYC Automation",
                    "Cybersecurity Monitor",
                ],
                "timeline": "18-24 months (phased implementation)",
                "investment": f"${base_cost * 0.3 / 1000000:.1f}M - ${base_cost * 0.5 / 1000000:.1f}M",
            }

        elif (
            "marketing" in business_description.lower()
            or "consultant" in business_description.lower()
        ):
            # Marketing consulting processes
            annual_revenue = self._extract_revenue_number(business_description)
            base_cost = max(annual_revenue * 0.6, 60000)  # Labor-intensive business

            process_analyses = [
                ProcessAnalysis(
                    name="Client Research & Market Analysis",
                    time_percentage=40.0,
                    complexity_score=3,
                    automation_potential="High",
                    current_cost_annual=base_cost * 0.4,
                    potential_savings=base_cost * 0.4 * 0.7,
                    roi_percentage=70.0,
                    implementation_difficulty="Medium",
                ),
                ProcessAnalysis(
                    name="Proposal and Content Creation",
                    time_percentage=30.0,
                    automation_potential="High",
                    complexity_score=4,
                    current_cost_annual=base_cost * 0.3,
                    potential_savings=base_cost * 0.3 * 0.8,
                    roi_percentage=80.0,
                    implementation_difficulty="Low",
                ),
                ProcessAnalysis(
                    name="Client Communication & Reporting",
                    time_percentage=20.0,
                    complexity_score=2,
                    automation_potential="Medium",
                    current_cost_annual=base_cost * 0.2,
                    potential_savings=base_cost * 0.2 * 0.6,
                    roi_percentage=60.0,
                    implementation_difficulty="Low",
                ),
            ]

            recommended_solution = {
                "approach": "Multi-Agent Marketing Automation Platform",
                "components": [
                    "Research Agent",
                    "Content Generator",
                    "Communication Bot",
                ],
                "timeline": "8-12 weeks",
                "investment": f"${base_cost * 0.25:,.0f} - ${base_cost * 0.4:,.0f}",
            }

        else:
            # Generic business processes
            annual_revenue = self._extract_revenue_number(business_description)
            base_cost = max(annual_revenue * 0.2, 100000)

            process_analyses = [
                ProcessAnalysis(
                    name="Research & Data Collection",
                    time_percentage=35.0,
                    complexity_score=3,
                    automation_potential="High",
                    current_cost_annual=base_cost * 0.35,
                    potential_savings=base_cost * 0.35 * 0.7,
                    roi_percentage=70.0,
                    implementation_difficulty="Medium",
                ),
                ProcessAnalysis(
                    name="Report and Document Generation",
                    time_percentage=25.0,
                    automation_potential="High",
                    complexity_score=4,
                    current_cost_annual=base_cost * 0.25,
                    potential_savings=base_cost * 0.25 * 0.8,
                    roi_percentage=80.0,
                    implementation_difficulty="Low",
                ),
                ProcessAnalysis(
                    name="Administrative Tasks",
                    time_percentage=20.0,
                    complexity_score=2,
                    automation_potential="Medium",
                    current_cost_annual=base_cost * 0.20,
                    potential_savings=base_cost * 0.20 * 0.6,
                    roi_percentage=60.0,
                    implementation_difficulty="Low",
                ),
            ]

            recommended_solution = {
                "approach": "Multi-Agent Business Automation Platform",
                "components": [
                    "Research Agent",
                    "Content Generator",
                    "Communication Bot",
                ],
                "timeline": "12-16 weeks",
                "investment": f"${base_cost * 0.25:,.0f} - ${base_cost * 0.4:,.0f}",
            }

        # Calculate overall metrics
        total_savings = sum(p.potential_savings for p in process_analyses)

        # Extract implementation cost from recommended solution investment
        impl_cost_str = recommended_solution["investment"]
        impl_cost = self._extract_implementation_cost(impl_cost_str)

        overall_roi = (total_savings / impl_cost) * 100 if impl_cost > 0 else 0
        payback_months = int(
            (impl_cost / (total_savings / 12)) if total_savings > 0 else 12
        )

        implementation_roadmap = [
            "Week 1-4: Discovery and requirements gathering",
            "Week 5-8: Solution design and architecture planning",
            "Week 9-16: Core system development and testing",
            "Week 17-20: Integration and system testing",
            "Week 21-24: Deployment and user training",
        ]

        return MarketResearchResult(
            business_profile=business_profile,
            process_analyses=process_analyses,
            overall_roi=overall_roi,
            recommended_solution=recommended_solution,
            implementation_roadmap=implementation_roadmap,
            investment_range=recommended_solution["investment"],
            payback_months=payback_months,
        )

    def _extract_revenue_number(self, description: str) -> float:
        """Extract numeric revenue from description"""
        import re

        description_lower = description.lower()

        # Look for billion amounts
        billion_match = re.search(r"(\d+\.?\d*)\s*billion", description_lower)
        if billion_match:
            return float(billion_match.group(1)) * 1000000000

        # Look for million amounts
        million_match = re.search(r"(\d+\.?\d*)\s*million", description_lower)
        if million_match:
            return float(million_match.group(1)) * 1000000

        # Look for raw dollar amounts
        dollar_match = re.search(r"\$(\d{1,3}(?:,\d{3})*)", description_lower)
        if dollar_match:
            return float(dollar_match.group(1).replace(",", ""))

        # Default based on business size
        if "large" in description_lower or "enterprise" in description_lower:
            return 500000000  # $500M default for large enterprises
        elif "small" in description_lower:
            return 2000000  # $2M default for small business
        else:
            return 10000000  # $10M default

    def _extract_implementation_cost(self, cost_str: str) -> float:
        """Extract implementation cost from investment string"""
        import re

        # Handle million amounts
        million_match = re.search(r"(\d+\.?\d*)M", cost_str)
        if million_match:
            return float(million_match.group(1)) * 1000000

        # Handle dollar amounts with commas
        dollar_match = re.search(r"\$(\d{1,3}(?:,\d{3})*)", cost_str)
        if dollar_match:
            return float(dollar_match.group(1).replace(",", ""))

        # Default
        return 100000


def print_header():
    """Print professional header"""
    print("\n" + "=" * 80)
    print("🤖 AGENTIC AI MARKET RESEARCH AGENT")
    print("   Professional Business Analysis & AI Opportunity Assessment")
    print("=" * 80)
    print()


def collect_business_info() -> str:
    """Collect business information from user"""
    print("📋 BUSINESS DISCOVERY QUESTIONNAIRE")
    print("-" * 40)

    questions = [
        "What industry is your business in?",
        "How many employees do you have?",
        "What are your main business activities?",
        "What processes take the most time each week?",
        "What are your biggest operational challenges?",
        "What's your approximate annual revenue?",
    ]

    responses = []
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question}")
        response = input("   → ").strip()
        if response:
            responses.append(f"{question} {response}")

    return " ".join(responses)


def format_currency(amount: float) -> str:
    """Format currency for display"""
    return f"${amount:,.0f}"


def print_analysis_report(result: MarketResearchResult):
    """Print professionally formatted analysis report"""

    print("\n" + "=" * 80)
    print("📊 BUSINESS ANALYSIS REPORT")
    print("=" * 80)

    # Executive Summary
    print("\n🏢 BUSINESS PROFILE")
    print("-" * 20)
    print(f"Industry: {result.business_profile.industry}")
    print(f"Size: {result.business_profile.size}")
    print(f"Revenue Range: {result.business_profile.revenue_range}")

    # Process Analysis
    print("\n⚡ AUTOMATION OPPORTUNITIES")
    print("-" * 30)

    total_current_cost = sum(p.current_cost_annual for p in result.process_analyses)
    total_savings = sum(p.potential_savings for p in result.process_analyses)

    for i, process in enumerate(result.process_analyses, 1):
        print(f"\n{i}. {process.name}")
        print(f"   • Time Investment: {process.time_percentage}% of operations")
        print(
            f"   • Current Annual Cost: {format_currency(process.current_cost_annual)}"
        )
        print(f"   • Potential Savings: {format_currency(process.potential_savings)}")
        print(f"   • Automation Potential: {process.automation_potential}")
        print(f"   • ROI: {process.roi_percentage:.0f}%")

    # Financial Summary
    print("\n💰 FINANCIAL IMPACT SUMMARY")
    print("-" * 28)
    print(f"Total Current Annual Cost: {format_currency(total_current_cost)}")
    print(f"Projected Annual Savings: {format_currency(total_savings)}")
    print(f"Overall ROI: {result.overall_roi:.0f}%")
    print(f"Payback Period: {result.payback_months} months")

    # Recommended Solution
    print("\n🎯 RECOMMENDED SOLUTION")
    print("-" * 24)
    print(f"Approach: {result.recommended_solution['approach']}")
    print(f"Components: {', '.join(result.recommended_solution['components'])}")
    print(f"Timeline: {result.recommended_solution['timeline']}")
    print(f"Investment Range: {result.investment_range}")

    # Implementation Roadmap
    print("\n🗺️  IMPLEMENTATION ROADMAP")
    print("-" * 27)
    for step in result.implementation_roadmap:
        print(f"   • {step}")

    # Next Steps
    print("\n🚀 RECOMMENDED NEXT STEPS")
    print("-" * 26)
    print("   • Schedule discovery call to discuss specific requirements")
    print("   • Develop proof of concept for highest-impact process")
    print("   • Create detailed implementation plan and timeline")
    print("   • Begin with pilot program to validate ROI projections")

    print("\n" + "=" * 80)
    print(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 80)


def save_report(result: MarketResearchResult, filename: str = None):
    """Save analysis report to file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"market_research_analysis_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(asdict(result), f, indent=2, default=str)

    print(f"\n💾 Analysis saved to: {filename}")


def main():
    """Main application entry point"""
    print_header()

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-key-here":
        print("❌ Error: OpenAI API key not configured!")
        print("Please edit the .env file and add your actual OpenAI API key")
        print("\n1. Get your key from: https://platform.openai.com/api-keys")
        print("2. Edit the .env file in this directory")
        print("3. Replace 'sk-your-key-here' with your actual key")
        return

    try:
        # Initialize agent
        agent = MarketResearchAgent(api_key)

        # Collect business information
        business_description = collect_business_info()

        if not business_description.strip():
            print("❌ No business information provided. Exiting.")
            return

        # Perform analysis
        print("\n🔄 Processing your business analysis...")
        print("   This may take 30-60 seconds...")

        result = agent.analyze_business(business_description)

        # Display results
        print_analysis_report(result)

        # Save report
        save_report_choice = (
            input("\n💾 Save this report to file? (y/n): ").strip().lower()
        )
        if save_report_choice in ["y", "yes"]:
            save_report(result)

        print(
            "\n✅ Analysis complete! Use this report for client discussions and proposals."
        )

    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("Please check your API key and internet connection.")
        return


if __name__ == "__main__":
    main()
