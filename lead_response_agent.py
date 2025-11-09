#!/usr/bin/env python3
"""
CauSelf Lead Response Agent - Phase 1
Generates personalized sales responses for FMCG supply chain leads.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from anthropic import Anthropic


# ============================================================================
# ENUMS
# ============================================================================

class IntentType(Enum):
    """Classification of lead's message intent"""
    HIGH_INTENT = "high_intent"  # Meeting request, pricing, specific challenge
    MEDIUM_INTENT = "medium_intent"  # General interest, "tell me more"
    LOW_INTENT = "low_intent"  # Vague inquiry
    OBJECTION = "objection"  # Already have system, too expensive, timing
    QUESTION = "question"  # Specific about features, implementation, pricing


class LeadTemperature(Enum):
    """Lead's familiarity with CauSelf"""
    HOT = "hot"  # Nuclear 8 - high engagement, clicked multiple times
    WARM = "warm"  # 576 engaged - opened emails, clicked content
    COLD = "cold"  # New outreach, zero context


class NextAction(Enum):
    """Recommended next step for the lead"""
    IMMEDIATE_CALL = "immediate_call"  # Hot + high intent
    SCHEDULE_DISCOVERY_30 = "schedule_discovery_30"  # Qualified + medium/high intent
    SCHEDULE_INTRO_15 = "schedule_intro_15"  # Objection or busy exec
    SEND_RESOURCES = "send_resources"  # Not qualified
    FOLLOW_UP_1_WEEK = "follow_up_1_week"  # Low intent but qualified


class MessageSource(Enum):
    """Where the message came from"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WEBSITE_FORM = "website_form"
    ASSESSMENT_TOOL = "assessment_tool"
    REFERRAL = "referral"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class LeadMessage:
    """Raw input from lead"""
    sender_name: str
    company_name: Optional[str]
    message_content: str
    source: MessageSource
    lead_temperature: LeadTemperature

    # Optional enrichment data
    company_revenue: Optional[str] = None  # e.g., "$200M", "$50M-$100M"
    industry: Optional[str] = "FMCG"
    sender_role: Optional[str] = None  # e.g., "VP Supply Chain", "COO"
    engagement_context: Optional[str] = None  # e.g., "Clicked email 2x, took assessment"


@dataclass
class LeadProfile:
    """Analyzed lead characteristics"""
    intent: IntentType
    temperature: LeadTemperature
    is_qualified: bool
    qualification_reasons: List[str]

    # Extracted details
    company_name: Optional[str]
    company_revenue: Optional[str]
    industry: str
    sender_role: Optional[str]

    # Key insights from message
    pain_points_mentioned: List[str] = field(default_factory=list)
    specific_questions: List[str] = field(default_factory=list)
    objections_raised: List[str] = field(default_factory=list)
    current_system_mentioned: Optional[str] = None


@dataclass
class ResponsePackage:
    """Generated response and recommended action"""
    response_text: str
    next_action: NextAction
    next_action_details: str
    reasoning: str

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0  # 0-1 scale


# ============================================================================
# CAUSELF MESSAGING CONSTANTS
# ============================================================================

CAUSELF_VALUE_PROPS = {
    "accuracy": "25% forecast accuracy improvement",
    "time_savings": "40% planning time reduction",
    "implementation_speed": "90-120 days",
    "legacy_comparison": "12-18 months for SAP/Oracle",
    "cost_savings": "50-70% lower TCO than enterprise systems",
    "positioning": "Enterprise-grade AI at mid-market prices",
    "target": "Purpose-built for FMCG"
}

PAIN_POINT_SOLUTIONS = {
    "forecast accuracy": "AI/ML models improve accuracy by 25%",
    "manual planning": "Automation reduces planning time by 40%",
    "disconnected systems": "Integrated platform connects ERP/WMS/TMS",
    "enterprise cost": "50-70% lower TCO than SAP/Oracle",
    "long implementation": "90-120 days vs 12-18+ months for legacy systems"
}

PRICING_RANGES = {
    "small": {"revenue": "$50M-$100M", "price": "$75K-$100K"},
    "medium": {"revenue": "$100M-$300M", "price": "$100K-$150K"},
    "large": {"revenue": "$300M-$700M", "price": "$150K-$200K"}
}

QUALIFICATION_CRITERIA = {
    "industry": ["FMCG", "Food", "Beverage", "Consumer Goods", "CPG"],
    "revenue_min": 50_000_000,
    "revenue_max": 700_000_000,
    "decision_makers": ["VP Supply Chain", "COO", "CFO", "Director", "VP Operations"]
}


# ============================================================================
# LEAD RESPONSE AGENT
# ============================================================================

class LeadResponseAgent:
    """
    Generates personalized sales responses for CauSelf leads.
    Uses Anthropic API for intelligent response generation.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent with Anthropic API"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def analyze_and_respond(self, lead_message: LeadMessage) -> ResponsePackage:
        """
        Main workflow: analyze lead message and generate response.

        Steps:
        1. Classify intent and extract key information
        2. Determine qualification status
        3. Generate personalized response
        4. Recommend next action
        """
        # Step 1: Analyze the lead
        lead_profile = self._analyze_lead(lead_message)

        # Step 2: Generate response
        response_text = self._generate_response(lead_message, lead_profile)

        # Step 3: Recommend next action
        next_action, action_details, reasoning = self._recommend_next_action(
            lead_profile, lead_message
        )

        return ResponsePackage(
            response_text=response_text,
            next_action=next_action,
            next_action_details=action_details,
            reasoning=reasoning,
            confidence_score=0.85  # Placeholder for future ML confidence
        )

    def _analyze_lead(self, lead_message: LeadMessage) -> LeadProfile:
        """Use Claude to analyze lead message and classify intent"""

        analysis_prompt = f"""You are analyzing a sales lead message for CauSelf, an AI-powered supply chain forecasting platform for FMCG companies.

LEAD MESSAGE:
From: {lead_message.sender_name}
Company: {lead_message.company_name or "Unknown"}
Source: {lead_message.source.value}
Temperature: {lead_message.temperature.value}
Message: {lead_message.message_content}

CONTEXT:
- CauSelf is an AI forecasting platform for FMCG companies ($50M-$700M revenue)
- Target decision makers: VP Supply Chain, COO, CFO
- Qualified leads: FMCG industry, mid-market size, decision maker/influencer

ANALYSIS TASKS:
1. Classify the INTENT of this message:
   - HIGH_INTENT: Meeting request, pricing question, specific challenge/pain point
   - MEDIUM_INTENT: General interest, "tell me more", exploring options
   - LOW_INTENT: Vague inquiry, minimal engagement
   - OBJECTION: Already have system, too expensive, bad timing
   - QUESTION: Specific question about features, implementation, pricing

2. Determine if lead is QUALIFIED:
   - ✅ FMCG or adjacent industry
   - ✅ Mid-market size ($50M-$700M revenue range)
   - ✅ Decision maker or influencer role
   - ✅ Expressed specific pain point or need

3. Extract KEY INFORMATION:
   - Pain points mentioned (forecast accuracy, manual processes, etc.)
   - Specific questions asked
   - Objections raised
   - Current system mentioned (SAP, Oracle, etc.)

RESPONSE FORMAT (JSON):
{{
    "intent": "HIGH_INTENT|MEDIUM_INTENT|LOW_INTENT|OBJECTION|QUESTION",
    "is_qualified": true|false,
    "qualification_reasons": ["reason 1", "reason 2"],
    "pain_points_mentioned": ["pain point 1", "pain point 2"],
    "specific_questions": ["question 1", "question 2"],
    "objections_raised": ["objection 1"],
    "current_system_mentioned": "system name or null"
}}

Provide ONLY the JSON response, no additional text."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.3,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        # Parse Claude's response
        analysis_text = response.content[0].text
        analysis_data = self._parse_json_response(analysis_text)

        return LeadProfile(
            intent=IntentType(analysis_data.get("intent", "MEDIUM_INTENT").lower()),
            temperature=lead_message.lead_temperature,
            is_qualified=analysis_data.get("is_qualified", False),
            qualification_reasons=analysis_data.get("qualification_reasons", []),
            company_name=lead_message.company_name,
            company_revenue=lead_message.company_revenue,
            industry=lead_message.industry,
            sender_role=lead_message.sender_role,
            pain_points_mentioned=analysis_data.get("pain_points_mentioned", []),
            specific_questions=analysis_data.get("specific_questions", []),
            objections_raised=analysis_data.get("objections_raised", []),
            current_system_mentioned=analysis_data.get("current_system_mentioned")
        )

    def _generate_response(
        self,
        lead_message: LeadMessage,
        lead_profile: LeadProfile
    ) -> str:
        """Generate personalized response using Claude"""

        # Build context for response generation
        context_parts = []

        # Lead temperature context
        if lead_profile.temperature == LeadTemperature.HOT:
            context_parts.append("This is a HOT lead (high engagement). Skip introduction, get to specifics quickly.")
        elif lead_profile.temperature == LeadTemperature.WARM:
            context_parts.append("This is a WARM lead (some engagement). Brief reminder of CauSelf, then specifics.")
        else:
            context_parts.append("This is a COLD lead (no prior context). Full value prop, social proof, soft CTA.")

        # Intent context
        intent_guidance = {
            IntentType.HIGH_INTENT: "High intent - be direct, propose meeting with specific times",
            IntentType.MEDIUM_INTENT: "Medium intent - educate on value, soft CTA for discovery call",
            IntentType.LOW_INTENT: "Low intent - build interest, offer resources",
            IntentType.OBJECTION: "Objection handling - empathize, reframe, offer low-pressure 15-min call",
            IntentType.QUESTION: "Answer specific question, then pivot to discovery"
        }
        context_parts.append(intent_guidance[lead_profile.intent])

        # Qualification context
        if lead_profile.is_qualified:
            context_parts.append("Lead IS qualified - offer 30-min discovery call")
        else:
            context_parts.append("Lead NOT fully qualified - offer resources, nurture approach")

        generation_prompt = f"""You are Brett Podolsky, founder of CauSelf, responding to a sales lead.

LEAD INFORMATION:
Name: {lead_message.sender_name}
Company: {lead_message.company_name or "their company"}
Role: {lead_message.sender_role or "role unknown"}
Industry: {lead_profile.industry}
Revenue: {lead_message.company_revenue or "unknown"}
Source: {lead_message.source.value}
Engagement Context: {lead_message.engagement_context or "None"}

THEIR MESSAGE:
{lead_message.message_content}

ANALYSIS:
Intent: {lead_profile.intent.value}
Qualified: {"Yes" if lead_profile.is_qualified else "No"}
Pain Points Mentioned: {", ".join(lead_profile.pain_points_mentioned) if lead_profile.pain_points_mentioned else "None"}
Questions: {", ".join(lead_profile.specific_questions) if lead_profile.specific_questions else "None"}
Objections: {", ".join(lead_profile.objections_raised) if lead_profile.objections_raised else "None"}
Current System: {lead_profile.current_system_mentioned or "None"}

RESPONSE GUIDELINES:
{chr(10).join(f"- {part}" for part in context_parts)}

CAUSELF VALUE PROPS (ALWAYS include these numbers):
- 25% forecast accuracy improvement
- 40% planning time reduction
- 90-120 day implementation (vs 12-18 months for SAP/Oracle)
- Enterprise-grade AI at mid-market prices
- Purpose-built for FMCG

TONE & STYLE:
- Consultative, not salesy
- Confident but humble
- Data-driven (use specific numbers)
- Empathetic to their challenges
- Direct with clear CTAs
- Match their tone (formal vs casual)

PRICING GUIDANCE (if relevant):
- $50M-$100M revenue: $75K-$100K annually
- $100M-$300M revenue: $100K-$150K annually
- $300M-$700M revenue: $150K-$200K annually
- Include: platform license, implementation, training, support

EXAMPLE STRUCTURES:

HIGH INTENT (Hot Lead):
"Great to hear from you! [Reference their engagement].

What they typically see with CauSelf:
- 25% forecast accuracy improvement
- 40% reduction in planning time
- 90-120 day implementation

[Address specific question/pain point]

Would it make sense to schedule a 30-minute discovery call? I'm available [Day] or [Day].

Best regards,
Brett"

OBJECTION (Already Have System):
"That's great - many of our best clients had existing systems when they came to us. What's working well with [Their System]? And what would you improve?

CauSelf often sits alongside existing ERPs, enhancing forecasting capabilities. We're right-sized for mid-market complexity - the 'Goldilocks zone' between point solutions and SAP.

Would it make sense to have a 15-minute conversation to see if there's a fit? No pressure if there isn't.

Best regards,
Brett"

Generate a personalized response to {lead_message.sender_name}. Output ONLY the email/message text, no additional commentary."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0.5,  # Slightly higher for more natural variation
            messages=[{"role": "user", "content": generation_prompt}]
        )

        return response.content[0].text.strip()

    def _recommend_next_action(
        self,
        lead_profile: LeadProfile,
        lead_message: LeadMessage
    ) -> tuple[NextAction, str, str]:
        """Determine recommended next action based on lead profile"""

        # Hot lead + high intent = immediate call
        if (lead_profile.temperature == LeadTemperature.HOT and
            lead_profile.intent == IntentType.HIGH_INTENT):
            return (
                NextAction.IMMEDIATE_CALL,
                "Call this lead TODAY. High intent + high engagement = immediate opportunity.",
                f"Hot lead ({lead_message.engagement_context}) with high intent. Strike while hot."
            )

        # Qualified + high/medium intent = 30-min discovery
        if (lead_profile.is_qualified and
            lead_profile.intent in [IntentType.HIGH_INTENT, IntentType.MEDIUM_INTENT, IntentType.QUESTION]):
            return (
                NextAction.SCHEDULE_DISCOVERY_30,
                "Propose 30-minute discovery call with 2-3 specific time options.",
                f"Qualified lead with {lead_profile.intent.value}. Standard discovery flow."
            )

        # Objection = 15-min low-pressure conversation
        if lead_profile.intent == IntentType.OBJECTION:
            return (
                NextAction.SCHEDULE_INTRO_15,
                "Offer 15-minute no-pressure conversation to explore fit.",
                f"Objection raised: {', '.join(lead_profile.objections_raised)}. Low-pressure approach."
            )

        # Not qualified = send resources
        if not lead_profile.is_qualified:
            return (
                NextAction.SEND_RESOURCES,
                "Send case study/whitepaper, add to nurture campaign.",
                f"Not qualified: {', '.join(lead_profile.qualification_reasons)}"
            )

        # Low intent but qualified = follow up in 1 week
        if lead_profile.intent == IntentType.LOW_INTENT and lead_profile.is_qualified:
            return (
                NextAction.FOLLOW_UP_1_WEEK,
                "Set reminder to follow up in 1 week with additional value/insight.",
                "Qualified but low intent. Give them space, follow up with value."
            )

        # Default: discovery call
        return (
            NextAction.SCHEDULE_DISCOVERY_30,
            "Propose 30-minute discovery call.",
            "Default action for unclear situation."
        )

    def _parse_json_response(self, text: str) -> dict:
        """Extract JSON from Claude's response"""
        import json

        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback to defaults
        return {
            "intent": "MEDIUM_INTENT",
            "is_qualified": False,
            "qualification_reasons": ["Unable to parse analysis"],
            "pain_points_mentioned": [],
            "specific_questions": [],
            "objections_raised": [],
            "current_system_mentioned": None
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_header(text: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_response_package(package: ResponsePackage, lead_message: LeadMessage):
    """Display the generated response package"""

    print_header("GENERATED RESPONSE")
    print(package.response_text)

    print_header("NEXT ACTION RECOMMENDATION")
    print(f"Action: {package.next_action.value.upper().replace('_', ' ')}")
    print(f"Details: {package.next_action_details}")
    print(f"\nReasoning: {package.reasoning}")

    print_header("METADATA")
    print(f"Generated: {package.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Confidence: {package.confidence_score:.0%}")
    print()


def interactive_mode():
    """Interactive CLI for testing lead responses"""

    print_header("CauSelf Lead Response Agent - Phase 1")
    print("Generate personalized sales responses for your leads.\n")

    # Initialize agent
    try:
        agent = LeadResponseAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nSet your Anthropic API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return

    print("✅ Agent initialized successfully\n")

    while True:
        print("\n" + "-"*80)
        print("Enter lead information (or 'quit' to exit):")
        print("-"*80 + "\n")

        # Collect lead info
        sender_name = input("Sender Name: ").strip()
        if sender_name.lower() == 'quit':
            break

        company_name = input("Company Name (optional): ").strip() or None

        print("\nLead Temperature:")
        print("  1. HOT (nuclear 8 - high engagement)")
        print("  2. WARM (576 engaged - some clicks)")
        print("  3. COLD (new outreach)")
        temp_choice = input("Choose (1-3): ").strip()
        temperature_map = {
            "1": LeadTemperature.HOT,
            "2": LeadTemperature.WARM,
            "3": LeadTemperature.COLD
        }
        lead_temperature = temperature_map.get(temp_choice, LeadTemperature.WARM)

        print("\nMessage Source:")
        print("  1. Email")
        print("  2. LinkedIn")
        print("  3. Website Form")
        print("  4. Assessment Tool")
        print("  5. Referral")
        source_choice = input("Choose (1-5): ").strip()
        source_map = {
            "1": MessageSource.EMAIL,
            "2": MessageSource.LINKEDIN,
            "3": MessageSource.WEBSITE_FORM,
            "4": MessageSource.ASSESSMENT_TOOL,
            "5": MessageSource.REFERRAL
        }
        message_source = source_map.get(source_choice, MessageSource.EMAIL)

        print("\nLead's Message:")
        print("(Enter message, then press Ctrl+D or Ctrl+Z when done)")
        message_lines = []
        try:
            while True:
                line = input()
                message_lines.append(line)
        except EOFError:
            pass
        message_content = "\n".join(message_lines).strip()

        if not message_content:
            print("❌ No message entered. Try again.")
            continue

        # Optional enrichment
        company_revenue = input("\nCompany Revenue (optional, e.g., $200M): ").strip() or None
        sender_role = input("Sender Role (optional, e.g., VP Supply Chain): ").strip() or None
        engagement_context = input("Engagement Context (optional, e.g., clicked email 2x): ").strip() or None

        # Create lead message
        lead_message = LeadMessage(
            sender_name=sender_name,
            company_name=company_name,
            message_content=message_content,
            source=message_source,
            lead_temperature=lead_temperature,
            company_revenue=company_revenue,
            sender_role=sender_role,
            engagement_context=engagement_context
        )

        # Generate response
        print("\n🤖 Analyzing lead and generating response...\n")
        try:
            response_package = agent.analyze_and_respond(lead_message)
            print_response_package(response_package, lead_message)
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()

    print("\n👋 Thanks for using CauSelf Lead Response Agent!")


def quick_test_mode():
    """Quick test with sample leads"""

    print_header("CauSelf Lead Response Agent - Quick Test Mode")

    # Initialize agent
    try:
        agent = LeadResponseAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return

    # Sample leads
    test_leads = [
        LeadMessage(
            sender_name="Sarah Chen",
            company_name="BrightFood Corp",
            message_content="Hi Brett, I saw your email about AI forecasting. We're currently using Excel for our demand planning and it's killing us - so many hours of manual work. What kind of accuracy improvements have you seen with FMCG companies our size ($150M revenue)? Would love to learn more.",
            source=MessageSource.EMAIL,
            lead_temperature=LeadTemperature.WARM,
            company_revenue="$150M",
            sender_role="VP Supply Chain",
            engagement_context="Clicked email 2x"
        ),
        LeadMessage(
            sender_name="Mike Thompson",
            company_name="GlobalBev Inc",
            message_content="We already have SAP IBP. Why would we need another system?",
            source=MessageSource.LINKEDIN,
            lead_temperature=LeadTemperature.COLD,
            company_revenue="$400M",
            sender_role="Director of Planning"
        ),
        LeadMessage(
            sender_name="Jennifer Martinez",
            company_name="PureFood Products",
            message_content="Just took your supply chain assessment - scored 42%. Our forecast accuracy is terrible and we're constantly dealing with stockouts. Can we schedule a demo?",
            source=MessageSource.ASSESSMENT_TOOL,
            lead_temperature=LeadTemperature.HOT,
            company_revenue="$80M",
            sender_role="COO",
            engagement_context="Took assessment, clicked email 3x"
        )
    ]

    for i, lead in enumerate(test_leads, 1):
        print(f"\n{'='*80}")
        print(f"  TEST LEAD #{i}: {lead.sender_name} - {lead.company_name}")
        print(f"{'='*80}")
        print(f"Message: {lead.message_content}")
        print(f"Temperature: {lead.lead_temperature.value}")
        print(f"Source: {lead.source.value}")

        print("\n🤖 Generating response...\n")
        try:
            response_package = agent.analyze_and_respond(lead)
            print_response_package(response_package, lead)
        except Exception as e:
            print(f"❌ Error: {e}")

        if i < len(test_leads):
            input("\n[Press Enter for next test lead...]")


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
