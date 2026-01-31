from typing import List, Dict

# Seed List of Historical "Archetypes"
# Ideally, we generate the full semantic summary via LLM once, then store it.
# For the hackathon, we can seed these with pre-generated high-quality summaries.

ARCHETYPES: List[Dict[str, str]] = [
    # --- NVDA Parallels (Infrastructure / Growth Bubbles) ---
    {
        "id": "CSCO_2000",
        "ticker": "CSCO",
        "name": "Dotcom Infrastructure Bubble (Cisco 2000)",
        "period": "2000-03-01_to_2001-03-01",
        "summary": "Parallel to AI Hardware Boom. Cisco was the 'plumbing of the internet'. Massive revenue growth met impossible valuation multiples (200x P/E). When capacity oversupply hit, stock crashed 80% despite company survival.",
        "typical_impact": "Multiple compression, Inventory glut, Crash (-70%)."
    },
    {
        "id": "NVDA_2018",
        "ticker": "NVDA",
        "name": "Crypto Hangover Crash (Nvidia 2018)",
        "period": "2018-09-01_to_2018-12-31",
        "summary": "Self-Parallel. After the 2017 crypto boom, channel inventory flooded with GPUs when crypto prices crashed ('Crypto Winter'). Nvidia missed guidance significantly due to 'excess channel inventory', leading to a 50% drawdown in 3 months.",
        "typical_impact": "Inventory write-downs, Guidance miss, Sharp correction (-50%)."
    },
    {
        "id": "XRX_1972",
        "ticker": "XRX",
        "name": "Nifty Fifty Valuation Bubble (Xerox 1972)",
        "period": "1972-06-01_to_1974-06-01",
        "summary": "Parallel to 'Growth at any Price'. Xerox was a 'One Decision' stock in the 70s, trading at 50x earnings due to photocopy dominance. When the market turned and growth slowed slightly, the valuation premium evaporated, leading to a lost decade.",
        "typical_impact": "Valuation reset, Long-term stagnation."
    },

    # --- AAPL Parallels (Regulation / Maturity / Innovation Lag) ---
    {
        "id": "FB_2018",
        "ticker": "META", # Facebook is now META
        "name": "Big Tech Trust Crisis (Facebook 2018)",
        "period": "2018-03-15_to_2018-07-30",
        "summary": "Parallel to Privacy/Trust issues. Cambridge Analytica scandal caused huge reputational damage and regulatory scrutiny (Congress). Though financials held initially, the 'Trust Discount' compressed the multiple.",
        "typical_impact": "Regulatory overhang, Volatility, P/E contraction."
    },
    {
        "id": "MSFT_1998",
        "ticker": "MSFT",
        "name": "Antitrust & Monopoly Enforcement (Microsoft 1998)",
        "period": "1998-11-01_to_2000-06-01",
        "summary": "Parallel to DOJ vs Apple. Microsoft faced an existential antitrust suit for bundling IE with Windows. The distraction of the trial and threat of breakup weighed on the stock even during the dotcom boom, leading to the 'Lost Decade' of stock performance.",
        "typical_impact": "Legal overhang, Distracted management, Multiple compression."
    },
    {
        "id": "INTC_2012",
        "ticker": "INTC",
        "name": "Missed Platform Shift (Intel 2012)",
        "period": "2012-01-01_to_2013-01-01",
        "summary": "Parallel to AI Innovation Lag. Intel dominated PC chips but failed to pivot to Mobile (iPhone/Android). Revenue peaked as the world shifted to smartphones, causing the stock to stagnate while competitors (ARM/Qualcomm) soared.",
        "typical_impact": "Market share loss, Irrelevance risk, Stagnation."
    },

    # --- JPM Parallels (Banking Scandals / Operational Risk) ---
    {
        "id": "WFC_2016",
        "ticker": "WFC",
        "name": "Reputational Scandal (Wells Fargo 2016)",
        "period": "2016-09-01_to_2017-01-01",
        "summary": "Parallel to Account Closure/Debanking. Fake accounts scandal destroyed WFC's premier reputation. Resulted in massive fines, CEO resignation, and a Fed asset cap that hampered growth for years compared to peers.",
        "typical_impact": "Severe underperformance, Regulatory handcuffs (Asset Cap)."
    },
    {
        "id": "JPM_2012",
        "ticker": "JPM",
        "name": "The London Whale (JPM 2012)",
        "period": "2012-04-01_to_2012-08-01",
        "summary": "Self-Parallel regarding Operational Risk. A failure in internal risk controls led to a $6B trading loss in the CIO office. Jamie Dimon was grilled by Congress. Stock dropped ~25% as competence was questioned, though it recovered quickly.",
        "typical_impact": "Sharp but temporary drop, Management credibility hit."
    },
    {
        "id": "UBS_2011",
        "ticker": "UBS",
        "name": "Rogue Trader Scandal (UBS 2011)",
        "period": "2011-08-01_to_2011-12-01",
        "summary": "Parallel to Compliance Failures. Kweku Adoboli lost $2B in unauthorized trading. CEO Oswald Gruebel resigned. Highlights how single points of failure in compliance can cause massive headline risk for global banks.",
        "typical_impact": "CEO resignation, Regulatory fines, restructuring."
    }
]

def get_archetypes() -> List[Dict[str, str]]:
    return ARCHETYPES
