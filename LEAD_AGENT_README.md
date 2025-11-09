# CauSelf Lead Response Agent - Phase 1

AI-powered sales response generator for CauSelf's FMCG supply chain forecasting platform.

## Overview

Automatically generates personalized, on-brand sales responses for leads at scale. Uses Claude AI to:
- Classify lead intent (high/medium/low intent, objections, questions)
- Generate personalized responses matching CauSelf's proven messaging
- Recommend next actions (immediate call, discovery meeting, resources, etc.)

## Features

### Intent Classification
- **HIGH_INTENT**: Meeting requests, pricing questions, specific challenges
- **MEDIUM_INTENT**: General interest, "tell me more"
- **LOW_INTENT**: Vague inquiries
- **OBJECTION**: Already have system, too expensive, timing issues
- **QUESTION**: Specific questions about features, implementation, pricing

### Lead Temperature Handling
- **HOT** (8 nuclear leads): Skip intro, get to specifics quickly
- **WARM** (576 engaged): Brief CauSelf reminder, then specifics
- **COLD** (new outreach): Full value prop, social proof

### Next Action Recommendations
- **IMMEDIATE_CALL**: Hot lead + high intent
- **SCHEDULE_DISCOVERY_30**: Qualified + medium/high intent
- **SCHEDULE_INTRO_15**: Objections or busy executives
- **SEND_RESOURCES**: Not qualified, nurture approach
- **FOLLOW_UP_1_WEEK**: Low intent but qualified

### CauSelf Messaging (Always Included)
- 25% forecast accuracy improvement
- 40% planning time reduction
- 90-120 day implementation (vs 12-18 months for SAP/Oracle)
- Enterprise-grade AI at mid-market prices
- Purpose-built for FMCG

## Installation

```bash
# Install dependencies
pip install -r requirements_lead_agent.txt

# Set Anthropic API key
export ANTHROPIC_API_KEY='your-key-here'
```

## Usage

### Interactive Mode (Recommended)
```bash
python lead_response_agent.py
```

Prompts you for:
- Sender name, company
- Lead temperature (hot/warm/cold)
- Message source (email/LinkedIn/etc.)
- Message content
- Optional: company revenue, sender role, engagement context

Then generates:
- Personalized response text
- Next action recommendation
- Reasoning and confidence score

### Quick Test Mode
```bash
python lead_response_agent.py test
```

Runs 3 pre-configured test leads:
1. **Sarah Chen** (BrightFood) - Warm lead, high intent, manual planning pain
2. **Mike Thompson** (GlobalBev) - Cold lead, objection (already has SAP)
3. **Jennifer Martinez** (PureFood) - Hot lead, took assessment, wants demo

## Example Usage

### Input
```
Sender: Sarah Chen
Company: BrightFood Corp
Temperature: WARM (clicked email 2x)
Source: Email
Message: "Hi Brett, I saw your email about AI forecasting. We're currently
using Excel for our demand planning and it's killing us - so many hours of
manual work. What kind of accuracy improvements have you seen with FMCG
companies our size ($150M revenue)? Would love to learn more."
```

### Output
```
GENERATED RESPONSE:
================================================================================
Hi Sarah,

Great to hear from you! Many of our FMCG clients were in a similar position -
evaluating options to move beyond Excel-based forecasting.

What they typically see with CauSelf:
- 25% forecast accuracy improvement (reducing both stockouts and excess inventory)
- 40% reduction in planning time (freeing up your team for strategic work)
- 90-120 day implementation (vs 12-18 months for SAP/Oracle)

For a $150M company like BrightFood, implementation usually involves:
- Week 1-4: Data integration and baseline setup
- Week 5-8: Model training and validation
- Week 9-12: User training and production rollout

Our clients in your revenue range typically invest $100K-$150K annually, which
includes platform license, implementation, training, and ongoing support. Most
see ROI within 6-12 months through reduced inventory carrying costs.

Would it make sense to schedule a 30-minute discovery call to discuss your
specific forecasting challenges? I'm available Tuesday or Thursday if either works.

Best regards,
Brett

NEXT ACTION RECOMMENDATION:
================================================================================
Action: SCHEDULE DISCOVERY 30
Details: Propose 30-minute discovery call with 2-3 specific time options.

Reasoning: Qualified lead with medium_intent. Standard discovery flow.
```

## Architecture

### Data Models
- **LeadMessage**: Raw input (sender, company, message, source, temperature)
- **LeadProfile**: Analyzed characteristics (intent, qualification, pain points)
- **ResponsePackage**: Generated response + next action + reasoning

### Core Methods
- `analyze_and_respond()`: Main workflow orchestrator
- `_analyze_lead()`: Intent classification using Claude
- `_generate_response()`: Personalized response generation
- `_recommend_next_action()`: Next step logic

### Qualification Criteria
- ✅ FMCG or adjacent industry
- ✅ $50M-$700M revenue range
- ✅ Decision maker/influencer role (VP Supply Chain, COO, CFO)
- ✅ Expressed specific pain point or need

## Pricing Ranges (Auto-Included in Responses)
- **$50M-$100M revenue**: $75K-$100K annually
- **$100M-$300M revenue**: $100K-$150K annually
- **$300M-$700M revenue**: $150K-$200K annually

Includes: platform license, implementation, training, support

## Phase 2 Roadmap (Tomorrow)
- [ ] Pipedrive API integration
- [ ] Automatic activity logging
- [ ] Lead status updates
- [ ] Follow-up reminder creation
- [ ] Batch processing mode
- [ ] Response quality scoring

## Technical Details
- **Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Temperature**: 0.3 for analysis, 0.5 for response generation
- **Max Tokens**: 1024 for analysis, 2048 for responses
- **Python**: 3.11+

## Tips for Best Results

1. **Be Specific with Context**: Include company revenue, sender role, engagement history
2. **Set Correct Temperature**: HOT for multi-click engaged, WARM for some engagement, COLD for new
3. **Provide Source**: Different channels (email vs LinkedIn) affect tone
4. **Review Before Sending**: AI generates draft, you add final personal touch
5. **Update Messaging**: Edit prompts in code as CauSelf messaging evolves

## Support
Questions? Check the code comments or reach out to Brett.
