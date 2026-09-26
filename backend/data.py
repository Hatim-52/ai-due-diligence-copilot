COMPANIES_DATA = {
    "acme": {
        "id": "acme",
        "name": "Acme SaaS Corporation",
        "ticker": "ACME",
        "industry": "Enterprise Cloud & SaaS",
        "summary": "Acme SaaS Corporation is a high-growth provider of cloud-based enterprise resource planning (ERP) software. While revenue growth remains robust at 42% YoY, the company is burning cash rapidly due to heavy sales commissions and rising host infrastructure costs. Acme faces a critical debt wall of $120 million maturing in Q4 2026, alongside a severe intellectual property lawsuit from Sentinel Tech that claims $45 million in damages.",
        "metrics": {
            "years": ["2023", "2024", "2025"],
            "revenue": [45.2, 64.1, 91.0],  # in millions
            "ebitda": [-8.4, -3.1, 4.5],  # in millions
            "debt": [40.0, 85.0, 120.0],  # in millions
            "cash": [25.0, 52.0, 38.0]   # in millions
        },
        "risks": [
            {
                "id": "acme-risk-1",
                "severity": "CRITICAL",
                "category": "Legal & Regulatory",
                "title": "Patent Infringement Lawsuit (Sentinel Tech)",
                "description": "Sentinel Tech has sued Acme claiming infringement on core multi-tenant database synchronization patents, seeking $45 million in damages and an injunction on Acme's primary ERP platform.",
                "sourceRef": "Section: Legal Proceedings & Contingencies"
            },
            {
                "id": "acme-risk-2",
                "severity": "HIGH",
                "category": "Financial / Debt Wall",
                "title": "$120M Debt Maturity in Q4 2026",
                "description": "Acme has $120 million in outstanding senior secured notes maturing in October 2026. Given current cash burn and high interest rate environments, refinancing at favorable terms is highly uncertain.",
                "sourceRef": "Section: Liquidity and Capital Resources"
            },
            {
                "id": "acme-risk-3",
                "severity": "MEDIUM",
                "category": "Operational / Infrastructure",
                "title": "Extreme Cloud Vendor Dependency (AWS)",
                "description": "The platform relies 100% on AWS for hosting. Any service interruptions or price increases in data transit costs directly threaten service level agreements (SLAs) and gross margins.",
                "sourceRef": "Section: Operational Risks & Cloud Hosting"
            }
        ],
        "filings": [
            {
                "section": "Overview & Business Description",
                "content": "Acme SaaS Corporation develops, markets, and operates a suite of cloud-based enterprise resource planning (ERP) software platforms. Our applications automate critical business processes including payroll, financial accounting, inventory management, and customer relationship management (CRM). We sell our platform primarily through direct sales teams and target mid-market enterprise clients. As of December 31, 2025, our active customer base stood at 1,450 enterprises, representing a 35% increase compared to the previous fiscal year. Subscription revenue is recognized ratably over the contract term, which typically ranges from 12 to 36 months."
            },
            {
                "section": "Financial Performance & MD&A",
                "content": "Fiscal year 2025 revenue reached $91.0 million, representing a 42% growth over 2024 revenue of $64.1 million. This growth was driven by strong adoption of our core ERP module and expanding net revenue retention (NRR) of 118%. However, operating expenses increased by 38% to $96.5 million. Sales and marketing expenses accounted for $42.0 million of this total, driven by aggressive representative headcount growth and high initial contract commission rates. Consequently, Net Loss was $5.5 million for the year. Free Cash Flow (FCF) was negative $14.0 million, reducing cash reserves from $52.0 million at the end of 2024 to $38.0 million as of December 31, 2025."
            },
            {
                "section": "Liquidity and Capital Resources",
                "content": "Our primary source of liquidity has been proceeds from equity financing rounds and the issuance of debt. As of December 31, 2025, we had cash and cash equivalents of $38.0 million and outstanding total debt of $120.0 million. This debt is represented by Senior Secured Notes bearing interest at 8.5% per annum, which are set to mature in full on October 15, 2026. We are currently in preliminary discussions with investment banks regarding refinancing alternatives. If credit markets tighten or our operating performance declines, we may be unable to refinance this debt on commercially reasonable terms, which would raise substantial doubt about our ability to continue as a going concern."
            },
            {
                "section": "Legal Proceedings & Contingencies",
                "content": "On August 14, 2025, Sentinel Technologies filed a patent infringement complaint against us in the U.S. District Court for the District of Delaware. The complaint alleges that our database synchronization and caching layer violates US Patents 8,421,902 and 9,102,442. Sentinel seeks damages of $45.0 million for past infringement and a permanent injunction against our ERP platform. We have engaged specialized counsel and intend to vigorously defend ourselves. Discovery is ongoing, and trial is scheduled for early 2027. While we believe we have strong defense positions, an adverse ruling could prevent us from selling our core software platform or result in crippling financial damages."
            },
            {
                "section": "Operational Risks & Cloud Hosting",
                "content": "Our cloud architecture is hosted exclusively on Amazon Web Services (AWS) across two primary regions. While this cloud setup offers high availability and scalability, it makes us vulnerable to single-point infrastructure failures. Any widespread disruption of AWS services could cause substantial downtime for our clients, violating our 99.9% uptime Service Level Agreements (SLAs) and exposing us to significant credit payouts or customer churn. Additionally, cloud hosting fees have risen by 25% due to high database compute and data transfer costs, squeezing our gross subscription margin from 78% in 2024 to 74% in 2025."
            }
        ]
    },
    "solaris": {
        "id": "solaris",
        "name": "Solaris Energy Partners",
        "ticker": "SOLR",
        "industry": "Renewable Utilities & Solar Infrastructure",
        "summary": "Solaris Energy Partners builds and operates utility-scale solar farms. While revenue is stable due to long-term power purchase agreements (PPAs), the company faces capital constraints. Solaris has taken on $350 million in green bond debt to fund active projects, resulting in a high debt-to-equity ratio of 2.1. Operational risks include severe grid interconnection delays of up to 18 months and reliance on federal clean energy tax credits that are vulnerable to political shifts.",
        "metrics": {
            "years": ["2023", "2024", "2025"],
            "revenue": [110.5, 125.0, 138.0],
            "ebitda": [72.0, 81.2, 88.5],
            "debt": [180.0, 260.0, 350.0],
            "cash": [45.0, 30.0, 22.0]
        },
        "risks": [
            {
                "id": "solaris-risk-1",
                "severity": "HIGH",
                "category": "Operational / Supply Chain",
                "title": "18-Month Grid Connection Backlog",
                "description": "Delays in connecting new projects to regional transmission grids (specifically in ERCOT and CAISO) threaten solar project commissioning dates, risking PPA penalties and delayed cash flows.",
                "sourceRef": "Section: Grid Integration & Transmission Constraints"
            },
            {
                "id": "solaris-risk-2",
                "severity": "HIGH",
                "category": "Legal & Regulatory",
                "title": "Federal Subsidy Policy Sunset Risk",
                "description": "Over 35% of project economics rely on Federal Investment Tax Credits (ITC) and Production Tax Credits (PTC). Sunsetting of these credits would drop project IRR by an estimated 4-5%.",
                "sourceRef": "Section: Regulatory Environment & Tax Subsidies"
            },
            {
                "id": "solaris-risk-3",
                "severity": "MEDIUM",
                "category": "Financial / Capital Capex",
                "title": "Extreme Financial Leverage (Debt/Equity: 2.1)",
                "description": "Green bond issuances have pushed total debt to $350 million against cash of $22 million. Solaris is highly leveraged, restricting its ability to secure new construction loans.",
                "sourceRef": "Section: Capital Expenditures & Financing"
            }
        ],
        "filings": [
            {
                "section": "Overview & Utility Assets",
                "content": "Solaris Energy Partners is a master limited partnership (MLP) that owns, operates, and acquires utility-scale solar energy generation facilities. We own 24 operating solar installations across California, Texas, Nevada, and Arizona with a combined nameplate capacity of 1.8 Gigawatts (GW). Approximately 92% of our generated electricity is sold under long-term Power Purchase Agreements (PPAs) to creditworthy utility companies and corporate off-takers. These PPAs have a weighted average remaining contract life of 14.5 years, providing highly predictable and stable operating cash flows."
            },
            {
                "section": "Regulatory Environment & Tax Subsidies",
                "content": "Our business model and the financial feasibility of our utility-scale solar farms are heavily dependent on federal, state, and local support. In particular, the Federal Investment Tax Credit (ITC) allows us to claim a tax credit equal to 30% of the cost of installing solar systems. Additionally, the Production Tax Credit (PTC) provides tax benefits based on kilowatt-hours produced. Changes in political administrations or tax reforms that eliminate, sunset, or retroactively reduce these credits would make future projects uneconomical, lowering expected Project Internal Rates of Return (IRR) from 9% to under 5%."
            },
            {
                "section": "Grid Integration & Transmission Constraints",
                "content": "To sell electricity, our solar projects must connect to regional transmission grids managed by Independent System Operators (ISOs) like ERCOT in Texas and CAISO in California. Currently, these grids face unprecedented interconnection congestion. The queue time to receive final interconnection study approvals and grid linkups has expanded to an average of 18 months. These backlog delays prevent us from turning on completed solar facilities. Under our signed PPAs, failure to deliver power by scheduled commercial operation dates triggers strict financial penalties, ranging from $15,000 to $50,000 per day."
            },
            {
                "section": "Capital Expenditures & Financing",
                "content": "The construction of solar projects requires massive upfront capital expenditures. During the fiscal year ended December 31, 2025, our CapEx was $142.0 million. To fund these projects, we issued $90.0 million in Green Bonds in Q2 2025, bringing our total outstanding long-term debt to $350.0 million. This has elevated our Debt-to-Equity ratio to 2.1. Cash flow from operations was $55.0 million, but distribution payouts to unitholders consumed $38.0 million, leaving our cash reserves constrained at $22.0 million. This high debt level may limit our capacity to secure new project-level construction financing."
            },
            {
                "section": "Supply Chain & Solar Panels",
                "content": "Solar PV modules are manufactured using high-purity polysilicon wafers, the supply of which is highly concentrated in East Asia. Trade disputes, tariffs under the Uyghur Forced Labor Prevention Act (UFLPA), and shipping disruptions have delayed panel shipments to our construction sites by up to six months. In response, we have signed forward-procurement agreements to purchase modules at fixed prices, but this ties up capital and exposes us to inventory risk if market prices for solar panels decline."
            }
        ]
    },
    "biohealth": {
        "id": "biohealth",
        "name": "BioHealth Labs Inc.",
        "ticker": "BHLA",
        "industry": "Biotech & Clinical Therapeutics",
        "summary": "BioHealth Labs Inc. is a clinical-stage biotechnology company developing gene therapies for cardiovascular diseases. Its lead drug candidate, CardioVax, is currently in Phase III clinical trials. Despite promising primary efficacy metrics, 12% of patients experienced adverse side effects, threatening FDA approval timelines. BioHealth has a short cash runway of 14 months ($45M cash against a $3.2M monthly burn) and key oncology patent expirations looming in 2028.",
        "metrics": {
            "years": ["2023", "2024", "2025"],
            "revenue": [0.0, 0.0, 0.0],  # Clinical stage, zero revenue
            "ebitda": [-28.2, -34.5, -38.4],  # Operating cash burn
            "debt": [0.0, 0.0, 10.0],  # Small convertible debt
            "cash": [65.0, 58.0, 45.0]
        },
        "risks": [
            {
                "id": "biohealth-risk-1",
                "severity": "CRITICAL",
                "category": "Clinical & FDA Regulatory",
                "title": "CardioVax Phase III Side Effect Signals",
                "description": "12% of clinical trial participants reported moderate-to-severe adverse cardiovascular side effects (nausea, heart rate spikes). This raises the likelihood of an FDA clinical hold or extended review cycles.",
                "sourceRef": "Section: Clinical Development & CardioVax Trials"
            },
            {
                "id": "biohealth-risk-2",
                "severity": "CRITICAL",
                "category": "Financial / Cash Runway",
                "title": "14-Month Cash Runway ($3.2M Monthly Burn)",
                "description": "With $45 million in cash and cash equivalents and an active monthly burn rate of $3.2 million, BioHealth will run out of capital by Q1 2027, requiring dilutive equity financing.",
                "sourceRef": "Section: Capital Runway & R&D Burn"
            },
            {
                "id": "biohealth-risk-3",
                "severity": "HIGH",
                "category": "Intellectual Property",
                "title": "Oncology Platform Patent Expirations (2028)",
                "description": "Two foundational patents covering their secondary oncology delivery platform are set to expire in mid-2028, exposing them to immediate generic competition in the cancer treatment market.",
                "sourceRef": "Section: Intellectual Property & Patents"
            }
        ],
        "filings": [
            {
                "section": "Overview & Clinical Pipeline",
                "content": "BioHealth Labs Inc. is a clinical-stage biotechnology company focused on discovering, developing, and commercializing novel gene therapies for patients suffering from severe cardiovascular diseases. Our lead product candidate, CardioVax-200, is a therapeutic agent designed to stimulate cellular repair of cardiac tissue post-myocardial infarction. We currently generate zero revenue from commercial product sales, as all of our compounds are in pre-clinical or clinical trial phases. Our long-term viability depends on successfully achieving positive clinical outcomes, obtaining regulatory approvals from the US FDA, and commercializing our pipeline."
            },
            {
                "section": "Clinical Development & CardioVax Trials",
                "content": "During 2025, we advanced the CardioVax-200 Phase III clinical trial to its final enrollment phase of 450 patients. Preliminary primary efficacy endpoints met statistical significance, demonstrating a 22% improvement in Left Ventricular Ejection Fraction (LVEF). However, the safety profile revealed unexpected signals. Approximately 12.4% of patients in the treatment group experienced moderate-to-severe adverse events, including transient sinus tachycardia and severe nausea. The occurrence of these safety signals may prompt the FDA to demand a longer monitoring period, require a larger safety database, or issue a complete response letter (CRL), delaying potential market approval by 12 to 24 months."
            },
            {
                "section": "Capital Runway & R&D Burn",
                "content": "Since our inception, we have incurred significant operating losses and expect to continue to incur losses for the foreseeable future. Our Net Loss for the year ended December 31, 2025 was $38.4 million, driven by clinical trial site fees and laboratory manufacturing expenses. As of December 31, 2025, we had cash and cash equivalents of $45.0 million. Our current monthly net cash burn rate is approximately $3.2 million. Based on this, we estimate our existing cash will only fund operations for approximately 14 months (through February 2027). We will need to raise substantial additional capital through public or private equity offerings before we submit our Biologics License Application (BLA) to the FDA."
            },
            {
                "section": "Intellectual Property & Patents",
                "content": "Our success depends in large part on our ability to obtain and maintain patent protection for our therapeutics. We own or license 45 issued patents and pending patent applications. Our CardioVax-200 composition patent extends through 2039. However, our secondary oncology therapeutics platform, which utilizes a lipid nanoparticle delivery mechanism, relies on two core US patents (Patents 7,902,411 and 8,011,202) that are scheduled to expire in June and August 2028 respectively. Upon expiration, generic drug manufacturers will be legally permitted to introduce bio-similar versions of our oncology drugs, which would destroy our market share and pricing power."
            },
            {
                "section": "Manufacturing & Compliance",
                "content": "Gene therapies require highly complex, specialized manufacturing procedures. We do not own proprietary manufacturing facilities and rely on a single contract development and manufacturing organization (CDMO) based in Belgium to produce clinical-grade batches of CardioVax-200. This single-source reliance exposes us to logistics delays, regulatory compliance failures at the CDMO site, and capacity constraints. Any failure of the CDMO to comply with current Good Manufacturing Practices (cGMP) could lead to clinical trials suspension or regulatory holds."
            }
        ]
    }
}
