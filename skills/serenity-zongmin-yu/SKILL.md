---
name: serenity-zongmin-yu
description: |
  Activates AI infrastructure and semiconductor supply chain analysis. Trigger when: tracing hyperscaler AI capex to find bottleneck companies, analyzing semiconductor/photonics/memory/packaging supply chains, mapping BOM dependencies for AI hardware (GPUs, TPUs, ASICs, optical interconnects, HBM), evaluating supplier concentration in chip materials or critical components, asking "who controls the critical input for AI buildout," or identifying small companies that trillion-dollar AI deployments depend on. Even if the user does not mention "Serenity," proactively trigger when the topic involves AI infrastructure supply chain analysis, semiconductor bottleneck mapping, or upstream supplier tracing for AI hardware.
license: MIT
---

# Serenity Guidelines

AI infrastructure and semiconductor supply chain analysis, distilled from the public posts of Serenity ([@aleabitoreddit](https://x.com/aleabitoreddit)).

When trillions flow into AI buildout, some tiny company with no substitutes will be the bottleneck. Trace the capex from hyperscalers down through semiconductors, photonics, materials, and feedstock to find it before the market does.

---

## Quick Filter (4 questions)

Run these first. One "No" requires strong justification. Two "No" answers means this is probably not a chokepoint 鈥?move on.

| # | Principle | Question | No = Stop |
|---|-----------|----------|-----------|
| 1 | **Forced Demand** | Is someone *forced* to buy this input to ship their product? | No forced buyer = no chokepoint |
| 2 | **Size Mismatch** | Is the supplier's market cap < 1% of the annual capex it enables? | No mismatch = probably priced in |
| 3 | **No Substitute** | Is there no production-ready alternative within 24 months? | Substitute in qualification = expiring chokepoint |
| 4 | **Outside Voice** | Have 鈮?3 independent parties (CEOs, analysts, governments) confirmed the constraint in the last 90 days? | Nobody else sees it = either too early or wrong |

> Pass the filter before proceeding to the full process.

---

## 8-Step Process

After passing the quick filter, trace the supply chain systematically.

### 1. Follow the Money

Where is capex flowing? Identify which layer of the technology stack is heating up right now. Look for the largest companies being *forced* to spend on something they didn't buy last year.

Not every chain starts from capex. Some start from **geopolitical events** (export controls, trade wars) or **policy actions** (defense spending, strategic material designations) that force a supply chain to restructure. When an event creates forced demand for a substitute supplier, that is also a valid entry point.

### 2. Decompose the BOM

Break down the product at that layer into components. Quantify cost share. Which components take the largest portion of the bill of materials?

When the BOM is not public 鈥?as with many hardware OEMs 鈥?use **public supplier relationships, customer disclosures, analyst reports, and community-sourced information** to reconstruct the map. A confirmed multi-hop chain (A supplies B, B supplies C, C supplies the hyperscaler) can be as strong as a published BOM.

### 3. Ask "Who Makes It?"

For each significant component, identify and count the suppliers. How many companies in the world can make this at the required quality and volume?

### 4. Find the Monopoly

Chokepoint signature: supplier count 鈮?3, market cap small relative to downstream demand, switching costs high. A company worth hundreds of millions controlling an input for an industry worth trillions.

If the upstream producers are large oligopolies (too big to be mispriced), keep going 鈥?the alpha often lives **one layer above** in the smaller equipment, testing, metrology, or controller companies that even the oligopoly depends on.

**Red flag:** 10+ suppliers = not a chokepoint. Move on.

### 5. Verify Irreplaceability

Check substitute technologies. How long is the qualification cycle? Can capacity ramp quickly? If every alternative still depends on the same critical input, the chokepoint is structural.

For early-stage architecture transitions (e.g., current generation 鈫?next generation), do not rely on current revenue as the valuation anchor. **Qualification progress, capacity reservations, and foundry partnerships** are more reliable signals than trailing financials when the architecture shift has not yet reached volume production.

### 6. Go One Layer Deeper

Repeat Steps 3-5 on the chokepoint's own inputs. Who supplies the supplier? Where does the raw material come from? Look for the bottleneck within the bottleneck.

**Stop when:** You hit commodity inputs with many global sources.

### 7. Historical Analogies for Pricing

When a critical material becomes scarce, prices can spike 10-100x. Find precedents. What would the buyer pay to avoid a multi-billion dollar project delay?

### 8. Wait for External Validation

Confirm with independent signals: earnings calls mentioning supply constraints, analyst coverage initiating, industry reports quantifying shortages, policy actions flagging strategic materials, or combat/deployment validation for defense supply chains.

---

## Variants

The 8 steps are the core skeleton. Depending on the domain, the entry point, validation method, and chokepoint type shift:

**Architecture Migration** 鈥?When a current-generation technology is maxed out and the next generation requires different components. The chokepoint is not today's supplier but the company that controls the *next* critical input. Evaluate by qualification timeline and capacity reservation, not by trailing revenue.

**Operational Chokepoint** 鈥?Not every bottleneck is a physical material. Sometimes the constraint is who can profitably *monetize* capacity: gross margins matter more than raw gigawatts, software orchestration matters more than cheap power, and financing structure determines whether capacity translates to shareholder value or dilution.

**Event-Driven Entry** 鈥?Start from a geopolitical event, export control, or policy action rather than from capex flows. Decompose the *mission BOM* (what does the military operation / government program / emergency response require?) and find the small Western substitute supplier that a forced restructuring depends on.

**Opaque Supply Chains** 鈥?When OEMs do not publish BOMs, reconstruct the supplier map from public relationships: known customer鈥搒upplier pairs, conference presentations, analyst breadcrumbs, hiring patterns, and community-sourced intelligence. Cross-reference multiple partial clues to build the full picture.

---

## Standard Output Format

**All sections required. Cannot be omitted.** Quick filter may use one sentence per section; full analysis requires expansion.

```
## Conclusion
[Chokepoint confirmed / Not a chokepoint / Needs more data] 鈥?one-sentence rationale

## Quick Filter Results
| Principle | Pass/Fail | Evidence |
|-----------|-----------|----------|
| Forced Demand | | |
| Size Mismatch | | |
| No Substitute | | |
| Outside Voice | | |

## The Chokepoint
- What it is: [component / material / capacity / operational control]
- Who controls it: [company(s)] + [market cap] + [market share]
- Who depends on it: [downstream customers] + [annual capex at stake]
- Size mismatch ratio: [supplier MC / downstream annual spend]
- Variant: [standard / architecture migration / operational / event-driven]

## Supply Chain Map
[Trace from downstream customer 鈫?product 鈫?component 鈫?chokepoint 鈫?upstream inputs]

## Irreplaceability Assessment
- Substitute technologies: [name each + qualification stage + production timeline]
- Qualification cycle for new entrants: [months/years]
- Capacity ramp timeline: [months/years]
- Verdict: [structural / expiring / uncertain]

## External Validation
- [Source 1: who said what, when]
- [Source 2: who said what, when]
- [Source 3: who said what, when]
- Validation strength: [strong / moderate / weak]

## Key Risks (max 3)
[Focus on what could break the chokepoint thesis 鈥?including capital structure risks like dilution, float unlock, or financing overhang]

## Monitoring Indicators
- Check quarterly: [what to watch]
- Thesis-break signals: [what would invalidate this]
```

---

## Data Sources

- **Industry research:** Yole, LightCounting, McKinsey, Gartner 鈥?market sizing and supply/demand gaps
- **Earnings transcripts:** CEOs mentioning "supply-constrained," "allocation," "lead times extending"
- **Trade data:** Commodity price indices (e.g., SMM for metals), import/export databases
- **Company filings:** 10-K supplier disclosures, capex guidance, capacity expansion plans
- **Policy signals:** Export controls, strategic material lists, trade restrictions
- **LinkedIn/hiring:** Companies aggressively hiring for capacity expansion
- **Community intelligence:** Analyst notes, conference presentations, supplier mapping threads

---

## Scope

**Applies to:**
- AI infrastructure: semiconductors, photonics, optical interconnects, HBM, packaging, substrates, feedstock
- Physical supply chains with tangible materials and measurable capacity
- New technology waves or architecture transitions creating demand that outpaces supply
- Industries with qualification barriers and switching costs
- Defense and critical materials supply chains restructured by policy or geopolitics
- Situations where a small upstream company serves a massive downstream market

**Does not apply to:**
- Software and platform businesses 鈥?no physical scarcity, no forced purchasing
- Macro and liquidity trades 鈥?no supply chain to trace, no forced buyer
- Commodities with many fungible suppliers and fast capacity expansion
- Trades where the bottleneck is already widely known and priced in
- Broad sector ETFs or utility-layer plays without drilling to the component level

---

*Distilled from the public posts of Serenity ([@aleabitoreddit](https://x.com/aleabitoreddit)). Not affiliated. Not financial advice.*

