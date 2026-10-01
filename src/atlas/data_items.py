# -*- coding: utf-8 -*-
"""Single source of truth for the AI Investment Atlas.

Amounts are US$ billions as announced (headline). None = not disclosed.
cat:  compute = data centers & power, chips = chips & manufacturing, funding = AI company funding
kind: site (a specific place), program (multi-site pledge or company-wide plan, shown at HQ/flagship),
      funding (equity raised, shown at HQ)
prec: how exact the pin is -> site | city | region | hq | country
"""

S = {}  # source registry: key -> (label, url)
def src(key, label, url):
    S[key] = (label, url)
    return key

# ---------- sources ----------
src("stargate_epoch", "Epoch AI - OpenAI Stargate: where the US sites stand (2026)", "https://epoch.ai/publications/openai-stargate-where-the-us-sites-stand")
src("stargate_oai_jul25", "OpenAI - Stargate advances with 4.5 GW partnership with Oracle (Jul 2025)", "https://openai.com/index/stargate-advances-with-partnership-with-oracle/")
src("stargate_5sites", "AI Business - Five AI data centers confirmed as part of Stargate (Sep 2025)", "https://aibusiness.com/data-centers/five-ai-data-centers-confirmed-stargate-project")
src("stargate_sw", "MediaJustice - Stargate Project Southwest fact sheet (Dec 2025)", "https://mediajustice.org/wp-content/uploads/2025/12/Stargate-Project-SW-Fact-Sheet-FINAL.pdf")
src("vantage_frontier", "Converge Digest - Vantage commits $25B to 1.4 GW campus in Texas (Aug 2025)", "https://convergedigest.com/vantage-data-centers-commits-25b-to-1-4gw-campus-in-texas/")
src("jupiter", "Global Trade - Dona Ana County approves $165B IRB for Project Jupiter (Sep 2025)", "https://www.globaltrademag.com/dona-ana-county-approves-165-billion-irb-for-project-jupiter-a-transformative-leap-for-the-new-mexico-borderplex/")
src("nvda_ports", "NVIDIA 8-K - PORTS-Pike Technology Campus release (Aug 17, 2026)", "https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000069/sbeoainvidia-portsrelease.htm")
src("cnbc_ports", "CNBC - Nvidia backing $105B in financing for OpenAI data center in Ohio (Aug 2026)", "https://www.cnbc.com/2026/08/17/nvidia-financing-open-ai-data-center-ohio.html")
src("oai_ports", "OpenAI - OpenAI joins PORTS-Pike project (Aug 2026)", "https://openai.com/index/openai-joins-ports-pike-project/")
src("meta_hyperion", "CNBC - Meta's Louisiana data center investment to reach $50 billion (Jul 13, 2026)", "https://www.cnbc.com/2026/07/13/meta-louisiana-data-center-investment-reaches-50-billion-amid-ai-push.html")
src("meta_nuclear", "CNBC - Meta signs nuclear energy deals to power Prometheus (Jan 9, 2026)", "https://www.cnbc.com/2026/01/09/meta-signs-nuclear-energy-deals-to-power-prometheus-ai-supercluster.html")
src("wnn_meta", "World Nuclear News - Meta announces landmark agreements for new nuclear (Jan 2026)", "https://www.world-nuclear-news.org/articles/meta-announces-landmark-agreements-for-new-nuclear")
src("meta_elpaso", "Forbes - BlackRock will own 80% of Meta's El Paso AI data center (Jul 28, 2026)", "https://www.forbes.com/sites/maryroeloffs/2026/07/28/blackrock-will-own-80-of-metas-massive-new-ai-data-center-in-el-paso/")
src("meta_10q", "Meta 10-Q, quarter ended Jun 30, 2026 (El Paso venture)", "https://www.sec.gov/Archives/edgar/data/0001326801/000162828026050705/meta-20260630.htm")
src("axios_meta", "Axios - Meta unveils nuclear deals with Vistra, TerraPower, Oklo (Jan 2026)", "https://www.axios.com/2026/01/09/meta-nuclear-deal-vistra-terrapower-oklo")
src("msft_fairwater_wi", "GuruFocus/TradingView - Microsoft invests $7 billion in Wisconsin AI data centers (Sep 2025)", "https://tr.tradingview.com/news/gurufocus:d5b1e6b1a094b:0-microsoft-invests-7-billion-in-wisconsin-ai-data-centers")
src("fairwater_live", "The Energy Mag - Microsoft's $3.3B Fairwater AI data center goes live (Apr 2026)", "https://theenergymag.com/news/2026-04-20/microsoft-fairwater-ai")
src("fairwater_atl", "Microsoft Source - From Wisconsin to Atlanta: Microsoft's first AI superfactory (Nov 2025)", "https://news.microsoft.com/source/features/ai/from-wisconsin-to-atlanta-microsoft-connects-datacenters-to-build-its-first-ai-superfactory/")
src("nebius", "DCD - Microsoft to use Nebius GPU data centers in deal worth $17.4bn (Sep 2025)", "https://datacenterdynamics.com/en/news/microsoft-to-use-nebius-gpu-data-centers-in-deal-worth-174bn-over-five-years")
src("smr_deals", "SMR Intel - Every nuclear-powered data center deal (2026)", "https://smrintel.com/nuclear-data-center-deals/")
src("explainx_nuclear", "ExplainX - Hyperscaler nuclear deals for AI: GW, providers, dates (2026)", "https://www.explainx.ai/blog/hyperscaler-nuclear-deals-ai-data-centers-2026")
src("google_tx", "Reuters via Yahoo Finance - Google plans $40 billion Texas data center investment (Nov 2025)", "https://finance.yahoo.com/news/google-invest-40-billion-data-211425756.html")
src("amzn_pa", "DCD - Amazon to invest $20bn in data centers in Pennsylvania (Jun 2025)", "https://www.datacenterdynamics.com/en/news/amazon-to-invest-20bn-in-data-centers-in-pennsylvania/")
src("amzn_nc", "CNBC - Amazon to invest $10 billion in North Carolina data centers (Jun 2025)", "https://www.cnbc.com/2025/06/04/amazon-data-centers-ai.html")
src("amzn_impact", "Amazon - Record $340 billion U.S. investment in 2025 (economic impact report)", "https://www.aboutamazon.com/news/job-creation-and-investment/amazon-economic-impact-report-2025")
src("amzn_rainier", "CNBC - Anthropic to spend $50B on US AI infrastructure; Amazon's $11B Indiana campus is live (Nov 2025)", "https://www.cnbc.com/2025/11/12/anthropic-ai-data-centers-texas-new-york.html")
src("aws_ms", "SiliconANGLE - AWS to invest $10B in two new data centers in Mississippi (Jan 2024)", "https://siliconangle.com/2024/01/28/aws-invest-10b-build-two-new-data-centers-mississippi/")
src("anthropic_50b", "Anthropic - Anthropic invests $50 billion in American AI infrastructure (Nov 2025)", "https://www.anthropic.com/news/anthropic-invests-50-billion-in-american-ai-infrastructure")
src("xai_baxtel", "Baxtel - SpaceX's first earnings call was mostly a data center call (Aug 2026)", "https://baxtel.com/news/spacex-s-first-earnings-call-was-mostly-a-data-center-call")
src("spacex_q2", "CNBC - SpaceX earnings: soaring AI costs outweigh revenue beat (Aug 4, 2026)", "https://www.cnbc.com/2026/08/04/spacex-spcx-earnings-live-updates-q2-2026.html")
src("crwv_q2", "CNBC - CoreWeave stock pops as revenue doubles (Aug 11, 2026)", "https://www.cnbc.com/2026/08/11/coreweave-crwv-q2-earnings-report-2026.html")
src("crwv_dcd", "DCD - Neocloud results Q2 2026: CoreWeave, Nebius, Cerebras (Sep 2026)", "https://www.datacenterdynamics.com/en/news/neocloud-results-q2-2026-coreweave-nebius-cerebras/")
src("crwv_fy25", "CoreWeave - Q4 2025 earnings call transcript (Feb 26, 2026)", "https://s205.q4cdn.com/133937190/files/doc_financials/2025/q4/CORRECTED-TRANSCRIPT-CoreWeave-Inc-CRWV-US-Q4-2025-Earnings-Call-26-February-2026-5-00-PM-ET.pdf")
src("uae_stargate", "The National - Stargate UAE data centre to cost more than $30bn (Jan 2026)", "https://www.thenationalnews.com/future/technology/2026/01/26/stargate-uae-data-centre-to-cost-more-than-30bn-ai-minister-says/")
src("oai_uae", "OpenAI - Introducing Stargate UAE (May 2025)", "https://openai.com/index/introducing-stargate-uae/")
src("msft_uae", "Microsoft On the Issues - Microsoft's $15.2 billion investment in the UAE (Nov 2025)", "https://blogs.microsoft.com/on-the-issues/2025/11/03/microsofts-15-2-billion-usd-investment-in-the-uae/")
src("row_aws", "Rest of World - Gulf war: drone strikes on AWS data centers and AI investment risk (Mar 2026)", "https://restofworld.org/2026/gulf-war-aws-data-center-attack-ai-investment-risk/")
src("tnw_stargate", "The Next Web - Iran's IRGC threatens Stargate UAE (3 Apr 2026)", "https://thenextweb.com/news/iran-threatens-stargate-openai-abu-dhabi")
src("fp_gulf", "Foreign Policy - War, AI and the Gulf: war-risk insurance up about 1,900% (10 Apr 2026)", "https://foreignpolicy.com/2026/04/10/war-ai-gulf-uae-saudi-qatar-iran/")
src("saudi_leap", "Global Data Center Hub - Saudi Arabia's LEAP 2026 (AWS region Dec 2026)", "https://www.globaldatacenterhub.com/p/saudi-arabias-leap-2026-15-billion")
src("humain_cnbc", "CNBC - Saudi AI firm Humain is pouring billions into data centers (Aug 2025)", "https://www.cnbc.com/2025/08/27/saudi-arabia-wants-to-be-worlds-third-largest-ai-provider-humain.html")
src("stargate_intl", "IntuitionLabs - Stargate Project: OpenAI's $500B AI data center plan (2026)", "https://intuitionlabs.ai/articles/openai-stargate-datacenter-details")
src("skh_f1", "SK hynix F-1/A (2026) - Indiana plant operations from 2H 2028", "https://www.sec.gov/Archives/edgar/data/0002120882/000119312526289345/d32785df1a.htm")
src("googl_fcf", "MLQ.ai - Alphabet Q2 capex hits record $44.9B; first negative free cash flow", "https://mlq.ai/news/alphabet-q2-capex-hits-record-449b-full-year-guidance-raised-to-195-205b/")
src("orcl_q4fy26", "Oracle 8-K - Q4 FY2026 results ($40B FY27 financing plan)", "https://www.sec.gov/Archives/edgar/data/0001341439/000119312526265848/orcl-ex99_1.htm")
src("humain_dcd", "DCD - Humain breaks ground on two data centers (2025)", "https://www.datacenterdynamics.com/en/news/humain-breaks-ground-two-data-centers-with-first-facilities-expected-to-go-live-in-q2-2026/")
src("humain_amd", "DCD - AMD and Humain agree 500MW compute deal across the Kingdom and US", "https://www.datacenterdynamics.com/en/news/amd-and-saudi-arabias-humain-agree-500mw-compute-deal-across-the-kingdom-and-us/")
src("humain_v2030", "Vision2030.ai - HUMAIN: 600K GPUs, $77B, 6.6GW pipeline (2026)", "https://vision2030.ai/analysis/humain-ai-infrastructure/")
src("google_vizag", "Reuters via Yahoo Finance - Google to invest $15 billion in AI data centre in India (Oct 2025)", "https://finance.yahoo.com/news/google-invest-15-billion-ai-070904414.html")
src("india_big3", "Analytics Insight - Amazon, Google, Microsoft bet $80.5B on India's AI boom (Sep 2026)", "https://www.analyticsinsight.net/news/amazon-google-microsoft-bet-usd-805b-on-indias-ai-boom")
src("msft_india", "AP via Yahoo Finance - India eyes $200B in data center investments (Dec 2025)", "https://finance.yahoo.com/news/india-eyes-200b-data-center-064556704.html")
src("amzn_india", "Amazon - Amazon will invest $48 billion in India by 2030 (2026)", "https://www.aboutamazon.com/news/company-news/amazon-india-investment")
src("reliance", "Blackridge Research - Upcoming data center projects in India 2026", "https://www.blackridgeresearch.com/blog/latest-list-of-new-upcoming-data-center-projects-in-india")
src("uk_futurum", "Futurum - UK AI sector boosted by $40bn+ investments from Microsoft, NVIDIA & others (Sep 2025)", "https://futurumgroup.com/insights/uk-ai-sector-boosted-by-40bn-investments-from-microsoft-nvidia-others/")
src("uk_fortune", "Fortune - Big Tech's billions in UK investments during Trump visit (Sep 2025)", "https://www.fortune.com/2025/09/17/big-tech-billions-uk-investments-donald-trump-visit-microsoft-nvidia-google")
src("uk_dci", "Data Centre Insight - UK AI infrastructure at Data Centre World 2026", "https://datacentreinsight.co.uk/2026/02/24/scaling-responsibly-for-the-future-of-uk-ai-infrastructure-at-data-centre-world/")
src("uk_substack", "Digital Infrastructure (Substack) - What I read last week, Sep 21, 2025", "https://digitalinfrastructure.substack.com/p/09212025-what-i-read-last-week")
src("narvik", "W.Media - Stargate pulls out of Norway data center deal as Microsoft takes over (2026)", "https://w.media/after-uk-exit-stargate-pulls-out-of-norway-data-center-deal-as-microsoft-takes-over/")
src("eu_gf", "European Commission - EU launches AI Gigafactories call (Jul 30, 2026)", "https://digital-strategy.ec.europa.eu/en/news/eu-launches-ai-gigafactories-call-boost-europes-computing-capacity-and-unlock-more-eu30-billion")
src("eu_polytech", "Polytechnique Insights - European AI gigafactories: the true, the false and the uncertain (2026)", "https://www.polytechnique-insights.com/en/columns/digital/european-ai-gigafactories-the-true-the-false-and-the-uncertain/")
src("france_109", "Euronews - EU to mobilise EUR200 billion for AI; Macron's EUR109bn plan (Feb 2025)", "https://www.euronews.com/business/2025/02/11/eu-to-mobilise-200-billion-for-ai-investment")
src("msft_japan", "Tech Insider - Microsoft's $10B Japan AI investment (2026)", "https://tech-insider.org/microsoft-10-billion-japan-ai-investment-sovereign-cloud-2026/")
src("softbank_jp", "DCD - SoftBank Corp. to launch AI Data Center GPU Cloud in Japan (2026)", "https://www.datacenterdynamics.com/en/news/softbank-corp-to-launch-ai-data-center-gpu-cloud-offering-in-japan/")
src("korea_nvda", "AI Business - Nvidia, South Korea partner on 260,000-GPU AI push (Oct 2025)", "https://aibusiness.com/data-centers/nvidia-south-korea-government-partner-ai")
src("korea_oai", "TechWire Asia - OpenAI, Samsung and SK move ahead with Korea data centre build (Feb 2026)", "https://techwireasia.com/2026/02/openai-samsung-and-sk-move-ahead-with-korea-data-centre-build/")
src("argentina", "TechRepublic - OpenAI to build $25 billion data center in Argentina (Oct 2025)", "https://www.techrepublic.com/article/news-openai-data-center-argentina/")
src("alibaba", "SCMP - Alibaba, Tencent present a tale of two strategies for AI spending (May 2026)", "https://www.scmp.com/tech/big-tech/article/3353573/alibaba-tencent-signal-ai-spending-surge-despite-earnings-pressure-china-chips-ramp")
src("alibaba_dcd", "DCD - Alibaba considers increasing AI capex to $69bn over three years (Feb 2026)", "https://www.datacenterdynamics.com/en/news/alibaba-considers-increasing-ai-data-center-capex-spend-to-69bn-over-three-years-report/")
src("bytedance", "BigGo Finance - ByteDance boosts 2026 capex to over 200 billion yuan (May 2026)", "https://finance.biggo.com/news/lfE0EZ4BYH_ypPqOu9ei")
src("bytedance_bm", "BusinessMirror (Bloomberg) - ByteDance weighs capex of as much as $70B (May 2026)", "https://businessmirror.com.ph/2026/05/27/bytedance-weighs-capex-of-as-much-as-70b-in-ai-push/")
src("rhodium_china", "Rhodium Group - Examining China's AI financing (Sep 2026)", "https://rhg.com/research/examining-chinas-ai-financing/")
src("tsmc_265", "Reuters via Yahoo Finance - TSMC to invest another $100 billion in US (Jul 16, 2026)", "https://finance.yahoo.com/technology/ai/articles/tsmc-invest-another-100-billion-100633089.html")
src("tsmc_165", "TSMC - Intends to expand U.S. investment to US$165 billion (Mar 4, 2025)", "https://pr.tsmc.com/english/news/3210")
src("nvda_500", "Bloomberg - Nvidia says it will build up to $500 billion of AI gear in US (Apr 14, 2025)", "https://www.bloomberg.com/news/articles/2025-04-14/nvidia-says-it-will-build-up-to-500-billion-of-ai-gear-in-us")
src("nvda_mfg26", "ChannelLife - NVIDIA expands US AI manufacturing with partner network (2026)", "https://channellife.news/story/nvidia-expands-us-ai-manufacturing-with-partner-network")
src("apple_600", "Apple Newsroom - Apple increases U.S. commitment to $600 billion (Aug 2025)", "https://www.apple.com/newsroom/2025/08/apple-increases-us-commitment-to-600-billion-usd-announces-ambitious-program/")
src("apple_houston", "CNBC - Apple begins shipping American-made AI servers from Texas (Oct 2025)", "https://www.cnbc.com/2025/10/23/apple-american-made-ai-servers-texas.html")
src("micron_200", "U.S. Department of Commerce - Micron $200B investment (Jun 2025)", "https://www.commerce.gov/news/press-releases/2025/06/president-trump-secures-200b-investment-micron-technology-memory-chip")
src("micron_10q", "Micron 10-Q, quarter ended May 28, 2026 (New York groundbreaking)", "https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000015/mu-20260528.htm")
src("skh_y2", "CNBC - SK Hynix to invest $38 billion building new memory chip plants (Aug 7, 2026)", "https://www.cnbc.com/2026/08/07/sk-hynix-memory-chips-ai-prices.html")
src("skh_indiana", "DCD - SK hynix confirms $3.87bn Indiana advanced packaging facility (Apr 2024)", "https://datacenterdynamics.com/en/news/sk-hynix-confirms-387-billion-investment-in-indiana-advanced-chip-packaging-facility")
src("samsung_tesla", "SamMobile - Samsung's Texas fab begins production early for Tesla chips (Sep 2026)", "https://www.sammobile.com/news/push-to-make-tesla-chips-sees-samsungs-texas-fab-begin-production-early")
src("samsung_p5", "Digitimes - Samsung expands AI chip push with Pyeongtaek P5 and Texas foundry ramp (Mar 2026)", "https://www.digitimes.com/news/a20260304VL206/samsung-expansion-texas-ai-chip-production-infrastructure.html")
src("terafab", "Startup Fortune - Musk and Intel are building a chip factory bigger than the Pentagon (Sep 2026)", "https://startupfortune.com/musk-and-intel-are-building-a-chip-factory-bigger-than-the-pentagon-apple-park-and-mall-of-america-combined/")
src("terafab_247", "24/7 Wall St. - Intel lands Musk's Terafab (Apr 2026)", "https://247wallst.com/investing/2026/04/07/intel-lands-musks-25-billion-terafab-a-billion-dollar-foundry-win-in-the-making/")
src("intel_usg", "Yahoo Finance - Intel announces $8.9 billion investment from US government (Aug 2025)", "https://finance.yahoo.com/news/intel-announces-89-billion-investment-from-us-government-which-will-own-99-of-chipmaker-180452175.html")
src("intel_proxy", "Intel DEF 14A 2026 proxy (SoftBank $2B, NVIDIA $5B placements)", "https://www.sec.gov/Archives/edgar/data/50863/000005086326000061/intc_courtesy-pdfa.pdf")
src("oai_122", "Bloomberg - OpenAI valued at $852 billion after completing $122 billion round (Mar 31, 2026)", "https://www.bloomberg.com/news/articles/2026-03-31/openai-valued-at-852-billion-after-completing-122-billion-round")
src("oai_122_cnbc", "CNBC - OpenAI closes record-breaking $122 billion funding round (Mar 31, 2026)", "https://www.cnbc.com/2026/03/31/openai-funding-round-ipo.html")
src("funding_hist", "Pinggy - Racing to a trillion: OpenAI and Anthropic's funding history (2026)", "https://pinggy.io/blog/openai_anthropic_funding_history/")
src("oai_66", "W.Media - OpenAI raises $6.6 billion, valuation soars to $157 billion (Oct 2024)", "https://w.media/openai-raises-6-6-billion-valuation-soars-to-157-billion/")
src("ant_h", "CNBC - Anthropic tops OpenAI as most valuable AI startup (May 28, 2026)", "https://www.cnbc.com/2026/05/28/anthropic-open-ai-startup-value.html")
src("ant_hist", "Digital Applied - Anthropic's $65B Series H at $965B (2026)", "https://www.digitalapplied.com/blog/anthropic-65b-series-h-965b-valuation-frontier-market-2026")
src("ant_msnv", "Introl - Anthropic's $50 billion data center plan ($30B Azure, $15B MSFT/NVDA) (2025)", "https://introl.com/blog/anthropic-50-billion-data-center-plan-december-2025")
src("amzn_ant4", "NBC News - Amazon to invest another $4 billion in Anthropic (Nov 2024)", "https://www.nbcnews.com/business/business-news/amazon-invest-another-4-billion-anthropic-openais-biggest-rival-rcna181360")
src("xai_e", "AI2.work - SpaceX absorbs xAI as Colossus 2 becomes first gigawatt cluster (2026)", "https://ai2.work/blog/spacex-absorbs-xai-as-colossus-2-becomes-world-s-first-gigawatt-ai-cluster")
src("xai_c", "xAI - Series C announcement (Dec 2024)", "https://x.ai/news/series-c")
src("xai_hist", "Longterm Wiki - xAI funding history", "https://www.longtermwiki.com/organizations/xai/funding")
src("spacex_ipo", "CNBC - SpaceX IPO takeaways: SPCX closes at $161 after record debut (Jun 12, 2026)", "https://www.cnbc.com/2026/06/12/spacex-ipo-spcx-live-updates.html")
src("meta_scale", "Economy Middle East - Meta invests $14.3 billion for 49% of Scale AI (Jun 2025)", "https://economymiddleeast.com/news/meta-invests-14-3-billion-for-49-percent-in-scale-ai-to-develop-superintelligence-lab")
src("mistral", "TechRepublic - Mistral AI Series C, ASML invests EUR1.3 billion (Sep 2025)", "https://www.techrepublic.com/article/news-mistral-ai-asml-series-c-funding/")
src("ssi", "Built In SF - Safe Superintelligence raises $2B at $32B valuation (Apr 2025)", "https://www.builtinsf.com/articles/safe-superintelligence-raises-2b-32b-valuation-20250415")
src("tml", "Pulse 2.0 - Thinking Machines Lab raises $2B at $12B valuation (Jul 2025)", "https://pulse2.com/thinking-machines-lab-2-billion-raised-at-12-billion-valuation-for-ai-technology")
src("nscale", "Wikipedia - Nscale (Series C, Mar 2026)", "https://en.wikipedia.org/wiki/Nscale")
# company financials
src("msft_q4fy26", "Microsoft FY26 Q4 earnings call (Jul 29, 2026)", "https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4")
src("msft_8k", "Microsoft 8-K - FY26 Q4 press release (Jul 29, 2026)", "https://www.sec.gov/Archives/edgar/data/0000789019/000119312526323632/msft-ex99_1.htm")
src("msft_cnbc_q3", "CNBC - Microsoft calls for $190 billion in 2026 capital spending (Apr 29, 2026)", "https://www.cnbc.com/2026/04/29/microsoft-msft-q3-earnings-report-2026.html")
src("msft_ai37", "GeekWire - Microsoft reports $37B AI run rate (Apr 2026)", "https://www.geekwire.com/2026/microsoft-tops-wall-street-expectations-reports-accelerating-azure-growth-and-37b-ai-run-rate/")
src("msft_beancount", "Beancount.io - Microsoft FY2026 earnings analysis (OCF $182.9B)", "https://beancount.io/blog/2026/07/29/microsoft-fy2026-earnings-analysis")
src("msft_capex_q", "Beancount.io - Microsoft FY2026 Q3 capex by quarter", "https://beancount.io/blog/2026/07/12/microsoft-fy2026-q3-earnings-analysis")
src("msft_openai_rpo", "The Register - Microsoft investors sweat OpenAI exposure (45% of RPO) (Jan 2026)", "https://www.theregister.com/2026/01/29/microsoft_earnings_q2_2026/")
src("googl_q2", "Alphabet Q2 2026 earnings call transcript (Jul 22, 2026)", "https://finance.yahoo.com/quote/GOOG/earnings/GOOG-Q2-2026-earnings_call-657320.html")
src("googl_ars", "Alphabet 2025 annual report (capex 2024 $52.5B, 2025 $91.4B)", "https://www.sec.gov/Archives/edgar/data/0001652044/000130817926000344/goog014907-ars.pdf")
src("googl_equity", "Alphabet 8-K - $80 billion equity capital raise (Jun 1, 2026)", "https://www.sec.gov/Archives/edgar/data/0001652044/000119312526257724/d83560dex991.htm")
src("amzn_q2", "Amazon - Q2 2026 results (Jul 30, 2026)", "https://www.aboutamazon.com/news/company-news/amazon-earnings-q2-2026-report")
src("amzn_fy25", "sec-api.io - Financial analysis of Amazon FY2025 and H1 2026", "https://sec-api.io/insights/financial-analysis-of-amazon-fy2025-and-the-first-half-of-2026")
src("amzn_capex_q2", "Yahoo Finance - Amazon Q2 2026 earnings call ($220B capex)", "https://finance.yahoo.com/quote/AMZN/earnings/AMZN-Q2-2026-earnings_call-657334.html")
src("meta_q2", "The Next Web - Meta lifts the floor on its AI spending (Jul 2026)", "https://thenextweb.com/news/meta-q2-2026-capex-ai-buildout")
src("meta_fcf", "FourWeekMBA - Meta Q2 2026: $60.8B revenue, $784M free cash flow", "https://fourweekmba.com/ai-meta-q2-2026-capex-free-cash-flow-ai-infrastructure/")
src("capex_2025", "Platformonomics - Follow the capex: 2025 retrospective (Feb 2026)", "https://platformonomics.com/2026/02/follow-the-capex-2025-retrospective/")
src("orcl_q1fy27", "Oracle 8-K - Q1 FY2027 results (Sep 10, 2026)", "https://www.sec.gov/Archives/edgar/data/0001341439/000119312526387905/orcl-ex99_1.htm")
src("orcl_10k", "Oracle 10-K FY2026 (capex $55.7B; FY25 $21.2B)", "https://www.sec.gov/Archives/edgar/data/0001341439/000119312526277521/orcl-20260531.htm")
src("orcl_capex", "TIKR - Oracle's AI boom has $664 billion in backlog (Sep 2026)", "https://www.tikr.com/blog/oracles-ai-boom-has-664-billion-in-backlog-can-its-cash-flow-catch-up-heres-what-its-numbers-are-saying")
src("orcl_fy24", "Oracle - Q4 FY2024 results (Jun 11, 2024)", "https://www.oracle.com/news/announcement/q4fy24-earnings-release-2024-06-11/")
src("spacex_s1", "SpaceX S-1/A (2026)", "https://www.sec.gov/Archives/edgar/data/0001181412/000162828026039276/spaceexplorationtechnologi.htm")
src("spacex_tunguz", "Tomasz Tunguz - The newest hyperscaler (SpaceXAI capex, Aug 2026)", "https://tomtunguz.com/the-newest-hyperscaler/")
src("spacex_capex25", "Tech Market Briefs - SpaceX IPO profile (2025 capex $20.74B, AI 61%)", "https://techmarketbriefs.com/pre-ipo/spacex/")
src("crwv_tl", "TickerLeague - CoreWeave capital expenditures", "https://tickerleague.com/companies/CRWV/financials/capex")
src("oai_600", "Reuters via Yahoo Finance - OpenAI expects compute spend of around $600 billion through 2030 (Feb 20, 2026)", "https://finance.yahoo.com/news/openai-sees-compute-spend-around-223950561.html")
src("oai_70", "Techstrong.ai - OpenAI's revenue run rate nears $70 billion (Sep 2026)", "https://techstrong.ai/articles/openais-revenue-run-rate-nears-70-billion-on-enterprise-growth-report/")
src("ant_65", "Axios - Anthropic's revenue run rate reportedly surpasses $65 billion (Aug 17, 2026)", "https://www.axios.com/2026/08/17/anthropic-revenue-run-rate-ipo-openai")
src("ant_518", "93.3 The Drive (Reuters) - Anthropic's $518 billion buildout hinges on non-cancelable deals (Sep 29, 2026)", "https://www.933thedrive.com/2026/09/29/anthropics-518-billion-ai-buildout-hinges-largely-on-deals-that-cannot-be-canceled-filing-shows/")
src("ant_518b", "Yahoo Finance - Anthropic's S-1 is here: the $518 billion commitment (Sep 2026)", "https://finance.yahoo.com/technology/ai/articles/anthropic-1-518-billion-commitment-165731037.html")
src("ant_gross", "Digital Applied - Anthropic files for IPO (gross-basis revenue note) (2026)", "https://www.digitalapplied.com/blog/anthropic-ipo-filing-2026-claude-stack-analysis")
src("ant_gb", "Anthropic - Expanded partnership with Google and Broadcom (Apr 6, 2026)", "https://www.anthropic.com/news/google-broadcom-partnership-compute")
src("oai_deals", "Sacra - OpenAI revenue, valuation & funding (compute agreements)", "https://sacra.com/c/openai/")
src("oai_fierce", "Fierce Network - Encyclopedia of AI deals (AMD, Broadcom, CoreWeave, Oracle)", "https://www.fierce-network.com/cloud/fierce-networks-encyclopedia-ai-deals")
src("oai_cerebras", "CNBC - OpenAI chip deal with Cerebras (Jan 16, 2026)", "https://www.cnbc.com/2026/01/16/openai-chip-deal-with-cerebras-adds-to-roster-of-nvidia-amd-broadcom.html")
src("oai_oracle", "IntuitionLabs - Oracle-OpenAI $300B deal explained (2026)", "https://intuitionlabs.ai/articles/oracle-openai-300b-deal-analysis")
src("oai_burn", "Techstrong.ai - OpenAI cash burn of ~$278 billion 2026-2030 (Reuters) (Sep 2026)", "https://techstrong.ai/articles/openais-revenue-run-rate-nears-70-billion-on-enterprise-growth-report/")
src("nvda_q2", "NVIDIA - Q2 fiscal 2027 results (Aug 26, 2026)", "https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx")
src("nvda_10q", "NVIDIA 10-Q, quarter ended Jul 26, 2026 (equity investments, guarantees)", "https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm")
src("nvda_call", "Motley Fool - NVIDIA Q2 FY2027 earnings call transcript (FY28 +70% outlook)", "https://www.fool.com/earnings/call-transcripts/2026/08/31/nvidia-nvda-q2-2027-earnings-call-transcript/")
src("tsmc_q2", "BigGo Finance - TSMC Q2 2026 earnings call", "https://finance.biggo.com/news/TW_2330.TW_2026-07-16")
src("mu_fq2", "Micron 8-K - fiscal Q2 2026 results (Mar 18, 2026)", "https://www.sec.gov/Archives/edgar/data/723125/000072312526000004/a2026q2ex991-pressrelease.htm")
src("jpm_650", "Tom's Hardware - J.P. Morgan: $650 billion in annual revenue required for a 10% return", "https://www.tomshardware.com/tech-industry/artificial-intelligence/usd650-billion-in-annual-revenue-required-to-deliver-10-percent-return-on-ai-buildout-investment-j-p-morgan-claims-equivalent-to-usd35-payment-from-every-iphone-user-or-usd180-from-every-netflix-subscriber-in-perpetuity")
src("bain_2t", "Bain & Company - $2 trillion in new revenue needed to fund AI's scaling trend (Sep 2025)", "https://www.prnewswire.com/news-releases/2-trillion-in-new-revenue-needed-to-fund-ais-scaling-trend---bain--companys-6th-annual-global-technology-report-302563362.html")
src("gs_12t", "Briefs - Goldman says hyperscaler AI spend could jump to $1.2 trillion next year (Sep 2026)", "https://www.briefs.co/news/goldman-says-hyperscaler-ai-spend-could-jump-to-1-2-trillion/")
src("jpm_consensus", "J.P. Morgan AM - Charting an earnings surge, powered by AI capex (Sep 2026)", "https://am.jpmorgan.com/ca/en/asset-management/institutional/insights/portfolio-insights/research-report/charting-an-earnings-surge-powered-by-ai-capex/")
src("meta_600", "DCD - Meta to spend $600bn on US data centers by 2028 (2025)", "https://www.datacenterdynamics.com/en/news/meta-to-spend-600bn-on-us-data-centers-by-2028/")
src("crwv_meta", "Investing Engineer - CoreWeave Q2 2026 (OpenAI, Meta, Anthropic commitments)", "https://investingengineer.com/coreweave-earnings-ai-infrastructure-boom/")

# ---------- investments ----------
# helper
def it(id, title, who, cat, kind, amount, date, place, country, lat, lon, prec, status, note, srcs,
       gw=None, amount_note=None, partners=None):
    return dict(id=id, title=title, who=who, cat=cat, kind=kind, amount=amount, amountNote=amount_note,
                gw=gw, date=date, place=place, country=country, lat=lat, lon=lon, prec=prec,
                status=status, note=note, src=srcs, partners=partners)

ITEMS = [
 # ---------------- Data centers & power: United States ----------------
 it("stargate-program", "Stargate program", "OpenAI", "compute", "program", 500, "2025-01",
    "Abilene, Texas (flagship; sites in TX, NM, OH, WI, MI)", "United States", 32.52, -99.73, "site",
    "~7 GW of US sites in development",
    "OpenAI's pledge to invest $500B in 10 GW of US AI data centers over four years, with Oracle, SoftBank and MGX. The pin sits at the Abilene flagship; the individual sites are mapped separately.",
    ["stargate_oai_jul25", "stargate_epoch"], gw=10, amount_note="4-year pledge", partners="Oracle, SoftBank, MGX"),
 it("stargate-abilene", "Stargate I campus", "Oracle / OpenAI", "compute", "site", None, "2025-01",
    "Abilene, Texas", "United States", 32.47, -99.80, "site", "Operating (partial)",
    "The first Stargate campus. About 0.3 GW was running in early 2026 and training OpenAI models; 1.2 GW is planned.",
    ["stargate_epoch", "stargate_oai_jul25"], gw=1.2, partners="Crusoe"),
 it("frontier-shackelford", "Frontier campus (Stargate site)", "Vantage Data Centers", "compute", "site", 25, "2025-08",
    "Shackelford County, Texas", "United States", 32.72, -99.30, "site", "Under construction",
    "Ten-building, 1.4 GW campus on 1,200 acres; one of the five Stargate sites named in September 2025.",
    ["vantage_frontier", "stargate_epoch"], gw=1.4, amount_note="$25B+", partners="Oracle / OpenAI"),
 it("stargate-milam", "Stargate Milam County campus", "SB Energy (SoftBank)", "compute", "site", None, "2025-09",
    "Milam County, Texas", "United States", 30.66, -97.00, "site", "Under construction",
    "SoftBank-led Stargate site. OpenAI said Milam County and Lordstown could reach 1.5 GW combined within about 18 months.",
    ["stargate_5sites", "stargate_epoch"], partners="OpenAI"),
 it("stargate-lordstown", "Stargate Lordstown site", "SoftBank", "compute", "site", None, "2025-09",
    "Lordstown, Ohio", "United States", 41.165, -80.857, "site", "Under construction",
    "SoftBank-led Stargate data center in a former auto-industry town; paired with Milam County for 1.5 GW.",
    ["stargate_5sites", "stargate_epoch"], partners="OpenAI"),
 it("project-jupiter", "Project Jupiter (Stargate site)", "STACK Infrastructure / BorderPlex Digital", "compute", "site", 165, "2025-09",
    "Santa Teresa, Dona Ana County, New Mexico", "United States", 31.86, -106.66, "site", "Approved; facing lawsuits",
    "Four-building campus with an on-site microgrid. The county approved up to $165B in industrial revenue bonds, the largest private investment in New Mexico's history. Two lawsuits seek to stop it.",
    ["jupiter", "stargate_sw"], amount_note="bond authorization, up to", partners="Oracle / OpenAI"),
 it("stargate-portwash", "Stargate Port Washington", "Vantage Data Centers", "compute", "site", None, "2025-10",
    "Port Washington, Wisconsin", "United States", 43.387, -87.875, "site", "Under construction; due Q4 2028",
    "Oracle/OpenAI Stargate site planned at about 1.3 GW.", ["stargate_epoch"], gw=1.3, partners="Oracle / OpenAI"),
 it("stargate-saline", "Stargate Saline Township", "Related Digital", "compute", "site", None, "2025-10",
    "Saline Township, Michigan", "United States", 42.15, -83.80, "site", "Planned",
    "Oracle/OpenAI Stargate site in southeast Michigan.", ["stargate_sw"], partners="Oracle / OpenAI"),
 it("ports-pike", "PORTS-Pike Technology Campus", "SB Energy / NVIDIA / OpenAI", "compute", "site", 105, "2026-08",
    "Pike County, Ohio", "United States", 39.01, -83.00, "site", "Announced; first halls ready in NVIDIA FY2029",
    "8 GW of IT capacity leased to OpenAI for 20 years, exclusively on NVIDIA systems. NVIDIA guarantees up to $105B of the land, power and shell obligations; SB Energy will build 10 GW of generation and $4.2B of grid upgrades. NVIDIA says each hardware generation here is worth $150-200B of its revenue.",
    ["nvda_ports", "cnbc_ports", "oai_ports"], gw=8, amount_note="NVIDIA credit-support cap"),
 it("meta-hyperion", "Hyperion AI supercluster", "Meta", "compute", "site", 50, "2026-07",
    "Richland Parish, Louisiana", "United States", 32.47, -91.62, "site", "Under construction; 2 GW by 2030",
    "Expanded in July 2026 to 5 GW and more than $50B, up from $10B when announced in December 2024. Financed through a joint venture with Blue Owl; Entergy is building gas plants and 240 miles of transmission for it.",
    ["meta_hyperion"], gw=5, amount_note="more than", partners="Blue Owl Capital"),
 it("meta-prometheus", "Prometheus AI supercluster", "Meta", "compute", "site", None, "2025-07",
    "New Albany, Ohio", "United States", 40.08, -82.81, "site", "Coming online 2026",
    "1 GW cluster spanning several buildings; Meta's nuclear deals with Vistra, TerraPower and Oklo were signed to power it.",
    ["meta_nuclear"], gw=1),
 it("meta-elpaso", "El Paso AI data center campus", "Meta / BlackRock", "compute", "site", 14, "2026-07",
    "El Paso, Texas", "United States", 31.78, -106.27, "city", "Under construction",
    "1 GW, 1,000-acre campus. BlackRock funds will own 80%; Meta keeps 20%, leases the buildings back and guarantees up to about $13B of residual value.",
    ["meta_elpaso", "meta_10q"], gw=1, partners="BlackRock"),
 it("msft-fairwater-wi", "Fairwater AI datacenters", "Microsoft", "compute", "site", 7.3, "2025-09",
    "Mount Pleasant, Wisconsin", "United States", 42.70, -87.93, "site", "First site live (2026)",
    "Two identical AI datacenters: $3.3B for the first, which Microsoft calls the world's most powerful AI datacenter, plus $4B for a second.",
    ["msft_fairwater_wi", "fairwater_live"]),
 it("msft-fairwater-atl", "Fairwater Atlanta", "Microsoft", "compute", "site", None, "2025-11",
    "Atlanta metro, Georgia", "United States", 33.62, -84.50, "city", "Operating",
    "Second Fairwater site, linked to Wisconsin by a dedicated AI network so the two act as one 'AI superfactory'.",
    ["fairwater_atl"], partners="QTS (landlord)"),
 it("nebius-vineland", "Nebius Vineland campus for Microsoft", "Nebius", "compute", "site", 17.4, "2025-09",
    "Vineland, New Jersey", "United States", 39.486, -75.026, "site", "Delivering capacity",
    "Five-year GPU capacity contract worth $17.4B (up to $19.4B) for Microsoft; the campus starts at 300 MW with room for 400 MW more.",
    ["nebius"], gw=0.3, amount_note="5-year contract", partners="Microsoft (customer)"),
 it("msft-tmi", "Crane Clean Energy Center (Three Mile Island) restart", "Constellation / Microsoft", "compute", "site", None, "2024-09",
    "Londonderry Township, Pennsylvania", "United States", 40.153, -76.725, "site", "Restart under way",
    "20-year power purchase agreement to restart an 835 MW reactor for Microsoft's data centers.",
    ["smr_deals", "explainx_nuclear"], gw=0.835),
 it("google-texas", "Texas AI data center campuses", "Google", "compute", "site", 40, "2025-11",
    "Haskell & Armstrong counties, Texas", "United States", 33.16, -99.73, "region", "Under construction",
    "Three new campuses through 2027, Google's largest investment in any state; one Haskell County site is paired with new solar and batteries.",
    ["google_tx"], amount_note="through 2027"),
 it("amzn-pa", "Pennsylvania AI campuses", "Amazon (AWS)", "compute", "site", 20, "2025-06",
    "Salem Twp (Luzerne Co.) & Falls Twp (Bucks Co.), Pennsylvania", "United States", 41.09, -76.15, "region", "Permitting / construction",
    "Largest private investment in Pennsylvania's history. The Salem site sits beside the Susquehanna nuclear plant, where Amazon bought Talen's 960 MW data center campus.",
    ["amzn_pa", "smr_deals"]),
 it("amzn-nc", "North Carolina data centers", "Amazon (AWS)", "compute", "site", 10, "2025-06",
    "Richmond County, North Carolina", "United States", 34.99, -79.75, "region", "Under construction",
    "AI and cloud campus creating at least 500 jobs.", ["amzn_nc"]),
 it("amzn-ga", "Georgia data centers", "Amazon (AWS)", "compute", "site", 11, "2025-01",
    "Butts & Douglas counties, Georgia", "United States", 33.29, -83.96, "region", "Under construction",
    "At least $11B for AI and cloud data centers.", ["amzn_nc", "amzn_impact"]),
 it("amzn-in", "Project Rainier & northern Indiana expansion", "Amazon (AWS)", "compute", "site", 26, "2024-04",
    "New Carlisle, Indiana", "United States", 41.70, -86.51, "site", "Operating (Rainier); expanding",
    "$11B campus built for Anthropic's models (live since late 2025, hundreds of thousands of Trainium2 chips) plus a further $15B announced for northern Indiana in 2025.",
    ["amzn_rainier", "amzn_impact", "ant_msnv"], partners="Anthropic (tenant)"),
 it("amzn-ms", "Mississippi data center complexes", "Amazon (AWS)", "compute", "site", 13, "2024-01",
    "Madison & Warren counties, Mississippi", "United States", 32.62, -90.04, "region", "Under construction",
    "$10B announced in January 2024, the largest project in state history, plus $3B more in 2025.",
    ["aws_ms", "amzn_impact"]),
 it("colossus", "Colossus 1 & 2 supercomputers", "SpaceXAI (xAI)", "compute", "site", None, "2024-09",
    "Memphis, Tennessee & Southaven, Mississippi", "United States", 35.06, -90.14, "site", "Operating: 1.4 GW (Q2 2026)",
    "Colossus 2 became the first gigawatt-scale training cluster in January 2026. Nameplate capacity was 1.4 GW in Q2 2026, guided above 2 GW by year-end and about 10 GW by end-2027. Colossus 1 is now leased to Anthropic.",
    ["xai_baxtel", "xai_e"], gw=1.4),
 it("anthropic-fluidstack", "Custom data centers with Fluidstack", "Anthropic", "compute", "program", 50, "2025-11",
    "Texas & New York (sites undisclosed; shown at HQ)", "United States", 37.789, -122.396, "hq", "Sites coming online through 2026",
    "Anthropic's first self-directed build: facilities in Texas and New York, with more sites to come; about 800 permanent and 2,400 construction jobs.",
    ["anthropic_50b"], partners="Fluidstack"),
 it("crwv-2026", "CoreWeave 2026 build-out", "CoreWeave", "compute", "program", 37, "2026-08",
    "Company-wide (HQ Livingston, New Jersey)", "United States", 40.79, -74.32, "hq", "In progress",
    "2026 capex guided to $35-39B, roughly three times revenue. 1.5 GW active and 4.2 GW contracted power; backlog $104B plus $25B signed in early Q3.",
    ["crwv_dcd", "crwv_q2"], gw=4.2, amount_note="2026 capex guide, midpoint"),
 # Power
 it("meta-nuclear", "Nuclear power portfolio (Vistra, TerraPower, Oklo)", "Meta", "compute", "program", None, "2026-01",
    "Perry & Davis-Besse (Ohio), Beaver Valley (Pennsylvania), Pike County (Ohio)", "United States", 41.80, -81.14, "region", "Signed",
    "Up to 6.6 GW of new and existing nuclear by 2035: 20-year PPAs for 2.1 GW from Vistra's Ohio plants plus uprates, TerraPower Natrium units, and prepaid power for Oklo's 1.2 GW Pike County campus.",
    ["meta_nuclear", "wnn_meta"], gw=6.6),
 it("meta-clinton", "Clinton nuclear plant PPA", "Meta / Constellation", "compute", "site", None, "2025-06",
    "Clinton, Illinois", "United States", 40.17, -88.83, "site", "Signed",
    "20-year deal for about 1.1 GW from Constellation's Clinton plant.", ["axios_meta"], gw=1.1),
 it("google-kairos", "Kairos Power small-reactor fleet", "Google", "compute", "program", None, "2024-10",
    "Oak Ridge, Tennessee (Hermes 2) and TVA grid", "United States", 35.93, -84.31, "region", "First unit targeted 2030",
    "Agreement for up to 500 MW of small modular reactors supplying grids that serve Google.", ["explainx_nuclear", "smr_deals"], gw=0.5),
 it("amzn-xenergy", "X-energy small-reactor program", "Amazon", "compute", "program", None, "2024-10",
    "Richland, Washington (Energy Northwest)", "United States", 46.29, -119.28, "region", "Development",
    "Amazon invested about $700M in X-energy toward up to 5 GW of Xe-100 reactors, starting with Energy Northwest in Washington.",
    ["smr_deals", "explainx_nuclear"], gw=5),

 # ---------------- Data centers: rest of world ----------------
 it("uae-campus", "UAE-US AI Campus & Stargate UAE", "G42 / OpenAI", "compute", "site", 30, "2025-05",
    "Abu Dhabi, UAE", "United Arab Emirates", 24.42, 54.58, "city", "At risk: named as a target by Iran (Apr 2026)",
    "5 GW campus built by G42; the 1 GW Stargate UAE cluster inside it is backed by OpenAI, Oracle, NVIDIA, Cisco and SoftBank. The UAE's AI minister put the cost above $30B. Since the Iran war began on 28 Feb 2026 the site sits in a strike zone: drones knocked out two of AWS's three UAE availability zones on 1 Mar, Iran's IRGC threatened Stargate UAE by name on 3 Apr, and war-risk insurance for Gulf data centers is up about 1,900%. The 200 MW first phase was due in 2026; treat that date as uncertain.",
    ["uae_stargate", "oai_uae", "tnw_stargate", "row_aws", "fp_gulf"], gw=5, amount_note="more than", partners="Oracle, NVIDIA, Cisco, SoftBank"),
 it("msft-uae", "Microsoft UAE investment", "Microsoft", "compute", "program", 15.2, "2025-11",
    "Abu Dhabi, UAE", "United Arab Emirates", 24.47, 54.37, "city", "Under way; in the war's strike zone since Mar 2026",
    "Includes a $1.5B stake in G42, $10B+ of datacenter capex and a 200 MW Khazna expansion due by end-2026. The UAE has been inside the Iran war's strike zone since March 2026, when drones hit AWS data centers in the country; Gulf data-center war-risk insurance is up about 1,900%, which raises the cost and risk of the build.",
    ["msft_uae", "row_aws", "fp_gulf"], amount_note="2023-2029", partners="G42"),
 it("aws-humain", "AWS-HUMAIN AI Zone", "Amazon (AWS) / HUMAIN", "compute", "site", 5, "2025-05",
    "Riyadh, Saudi Arabia", "Saudi Arabia", 24.71, 46.68, "city", "Building; Gulf war risk",
    "Joint AI zone with up to 150,000 accelerators (NVIDIA GB300 and Trainium); AWS's first Saudi region is due in December 2026. On 1 Mar 2026 Iranian drones knocked out two of the three availability zones of AWS's UAE region and damaged its Bahrain facility, so the Gulf build-out now carries war risk and higher insurance costs.",
    ["humain_v2030", "humain_dcd", "saudi_leap", "row_aws", "fp_gulf"], amount_note="$5B+"),
 it("amd-humain", "AMD-HUMAIN compute venture", "AMD / HUMAIN", "compute", "program", 10, "2025-05",
    "Saudi Arabia & United States (shown at Riyadh)", "Saudi Arabia", 24.80, 46.80, "city", "Deploying",
    "$10B joint effort for 500 MW of AMD-based AI data centers over five years in Saudi Arabia and the US.",
    ["humain_amd"], gw=0.5),
 it("humain-dcs", "HUMAIN Riyadh & Dammam data centers", "HUMAIN (PIF)", "compute", "site", None, "2025-05",
    "Dammam & Riyadh, Saudi Arabia", "Saudi Arabia", 26.43, 50.10, "city", "First sites live 2026",
    "Two 100 MW sites to start, on 18,000 NVIDIA GB300s with several hundred thousand more planned; HUMAIN targets 1.9 GW by 2030 and 6.6 GW by 2034.",
    ["humain_dcd", "humain_cnbc"], gw=0.2),
 it("google-vizag", "India AI hub", "Google", "compute", "site", 15, "2025-10",
    "Visakhapatnam, Andhra Pradesh", "India", 17.69, 83.22, "city", "Broke ground Apr 2026",
    "Gigawatt-scale campus with AdaniConneX and Airtel plus a new subsea cable landing; Google's largest investment in India.",
    ["google_vizag", "india_big3"], gw=1, amount_note="2026-2030"),
 it("msft-india", "Microsoft India cloud & AI", "Microsoft", "compute", "program", 17.5, "2025-12",
    "Hyderabad (new region) and across India", "India", 17.39, 78.49, "city", "Under way (2026-2029)",
    "Microsoft's largest-ever Asia commitment: datacenters including a new Hyderabad region, plus AI skilling.",
    ["msft_india", "india_big3"], amount_note="2026-2029"),
 it("amzn-india", "AWS India expansion", "Amazon (AWS)", "compute", "program", 13, "2026-06",
    "Mumbai & Hyderabad", "India", 19.08, 72.88, "city", "Planned (to 2030)",
    "An extra $13B for AWS AI and cloud capacity, lifting Amazon's total India plan for 2026-2030 to $48B across all businesses.",
    ["amzn_india"], amount_note="AWS portion of $48B"),
 it("reliance-jamnagar", "Jamnagar AI data center", "Reliance Industries", "compute", "site", None, "2025-01",
    "Jamnagar, Gujarat", "India", 22.47, 70.06, "site", "Development",
    "1 GW to start with a goal of 3 GW; Meta will lease capacity here.", ["reliance", "india_big3"], gw=1),
 it("msft-uk", "Microsoft UK investment & Loughton supercomputer", "Microsoft", "compute", "program", 30, "2025-09",
    "Loughton, Essex (and across the UK)", "United Kingdom", 51.65, 0.07, "city", "Under way (2025-2028)",
    "$30B through 2028, $15B of it capex, including the UK's largest supercomputer (23,000+ GPUs) with Nscale.",
    ["uk_futurum", "uk_fortune"], partners="Nscale"),
 it("google-uk", "Google UK investment", "Google", "compute", "program", 6.8, "2025-09",
    "Waltham Cross, Hertfordshire", "United Kingdom", 51.69, -0.03, "city", "Data center opened Sep 2025",
    "GBP5B for AI infrastructure and DeepMind research, including a new data center in Waltham Cross.",
    ["uk_fortune"]),
 it("stargate-uk", "Stargate UK", "Nscale / OpenAI / NVIDIA", "compute", "site", None, "2025-09",
    "Cobalt Park, North Tyneside", "United Kingdom", 55.02, -1.52, "site", "Planned",
    "Sovereign compute in the North East's AI Growth Zone.", ["uk_futurum"]),
 it("blyth", "Blyth AI campus", "Blackstone", "compute", "site", 13.5, "2025-09",
    "Blyth, Northumberland", "United Kingdom", 55.13, -1.51, "site", "Under construction",
    "GBP10B AI campus led by Blackstone.", ["uk_dci"], amount_note="GBP10B"),
 it("nvda-uk", "NVIDIA UK AI infrastructure rollout", "NVIDIA", "compute", "program", 15, "2025-09",
    "United Kingdom (shown at London)", "United Kingdom", 51.51, -0.13, "country", "Deploying",
    "Up to GBP11B of GPUs for UK projects, including the Microsoft-Nscale supercomputer and Stargate UK.",
    ["uk_fortune"], amount_note="up to GBP11B"),
 it("crwv-uk", "CoreWeave UK data centers", "CoreWeave", "compute", "program", 3.4, "2025-09",
    "Airdrie, Scotland (DataVita) and England", "United Kingdom", 55.87, -3.98, "region", "Expanding",
    "A further GBP1.5B takes CoreWeave's UK commitment to GBP2.5B.", ["uk_substack", "uk_dci"], amount_note="GBP2.5B total"),
 it("narvik", "Narvik AI campus (ex-Stargate Norway)", "Nscale / Aker / Microsoft", "compute", "site", None, "2025-07",
    "Narvik, Norway", "Norway", 68.44, 17.43, "site", "Microsoft took over OpenAI's slot (Feb 2026)",
    "230 MW hydro-powered site first announced as Stargate Norway; OpenAI stepped back and Microsoft took the capacity.",
    ["narvik"], gw=0.23),
 it("msft-portugal", "Sines data center investment", "Microsoft", "compute", "site", 10, "2025-11",
    "Sines, Portugal", "Portugal", 37.95, -8.87, "city", "Planned",
    "About $10B for an AI data center in Portugal.", ["eu_polytech"]),
 it("france-plan", "France national AI investment plan", "France (public & private)", "compute", "program", 113, "2025-02",
    "France (shown at Paris)", "France", 48.86, 2.35, "country", "Pledged",
    "EUR109B of AI investment announced by President Macron, who called it France's equivalent of Stargate.",
    ["france_109"], amount_note="EUR109B"),
 it("eu-gigafactories", "EU AI Gigafactories", "European Commission & member states", "compute", "program", 34.5, "2026-07",
    "Up to 7 sites across the EU (shown at Brussels)", "Belgium", 50.85, 4.35, "country", "Call for tenders open",
    "Up to EUR10B of EU and national money meant to unlock at least EUR20B of private capital for seven sites with 100,000+ AI chips each.",
    ["eu_gf"], amount_note="EUR30B target"),
 it("google-germany", "Google Germany infrastructure", "Google", "compute", "program", 6.4, "2025-11",
    "Germany (shown at Frankfurt)", "Germany", 50.11, 8.68, "country", "Under way",
    "EUR5.5B for data center capacity and infrastructure in Germany.", ["google_tx"], amount_note="EUR5.5B"),
 it("vantage-zaragoza", "Zaragoza hyperscale campus", "Vantage Data Centers", "compute", "site", 3.8, "2025-09",
    "Villanueva de Gallego, Aragon", "Spain", 41.77, -0.83, "site", "Planned",
    "EUR3.2B campus marking Vantage's entry into Spain.", ["uk_substack"], amount_note="EUR3.2B"),
 it("msft-japan", "Microsoft Japan AI investment", "Microsoft", "compute", "program", 10, "2026-04",
    "Tokyo & Osaka regions", "Japan", 35.68, 139.69, "city", "Under way (2026-2029)",
    "Azure GPU capacity with Sakura Internet and SoftBank, sovereign-cloud controls and AI training for 1 million people.",
    ["msft_japan"], amount_note="2026-2029"),
 it("softbank-sakai", "Sakai AI data center & GPU cloud", "SoftBank Corp.", "compute", "site", None, "2026-05",
    "Sakai, Osaka (former Sharp LCD plant)", "Japan", 34.57, 135.47, "site", "GPU cloud launches Oct 2026",
    "150 MW data center on a closed LCD factory site; SoftBank's GPU cloud runs on NVIDIA GB200 NVL72.",
    ["softbank_jp"], gw=0.15),
 it("korea-nvda", "Korea sovereign AI: 260,000 NVIDIA GPUs", "Korean government, Samsung, SK, Hyundai, Naver", "compute", "program", None, "2025-10",
    "South Korea (shown at Seoul)", "South Korea", 37.57, 126.98, "country", "Deploying",
    "More than 260,000 Blackwell-class GPUs across a national AI computing center and factory 'AI factories' at Samsung, SK and Hyundai.",
    ["korea_nvda"]),
 it("korea-oai", "OpenAI data centers in Korea", "OpenAI / Samsung / SK", "compute", "site", None, "2025-10",
    "South Korea (sites not disclosed)", "South Korea", 35.90, 127.60, "country", "Construction from Mar 2026",
    "Joint AI data centers with Samsung and SK; both also agreed to supply memory for Stargate.", ["korea_oai", "stargate_intl"]),
 it("stargate-argentina", "Stargate Argentina", "Sur Energy / OpenAI", "compute", "site", 25, "2025-10",
    "Patagonia, Argentina", "Argentina", -39.5, -68.5, "region", "Letter of intent",
    "Up to $25B for a 500 MW AI campus under Argentina's RIGI incentive regime; the builder and funding are not yet named.",
    ["argentina"], gw=0.5, amount_note="up to"),
 it("alibaba", "Alibaba AI & cloud infrastructure plan", "Alibaba", "compute", "program", 53, "2025-02",
    "China (shown at Hangzhou)", "China", 30.27, 120.16, "hq", "Under way; likely to overshoot",
    "RMB380B over three years; management expects to exceed it and a RMB480B ($69B) plan has been reported.",
    ["alibaba", "alibaba_dcd"], amount_note="RMB380B, 3 years"),
 it("bytedance", "ByteDance 2026 AI capex", "ByteDance", "compute", "program", 29.4, "2026-05",
    "China (shown at Beijing)", "China", 39.99, 116.31, "hq", "Under way",
    "2026 capex raised to more than RMB200B, with talks of up to $70B; China's 13 largest listed AI spenders are set to double AI capex to RMB932B ($139B) this year.",
    ["bytedance", "bytedance_bm", "rhodium_china"], amount_note="RMB200B+"),
 it("tencent", "Tencent AI capex", "Tencent", "compute", "program", 11, "2026-03",
    "China (shown at Shenzhen)", "China", 22.54, 113.93, "hq", "Rising in 2026",
    "RMB79.2B of capex in 2025, with a 'substantial increase' promised for 2026 as domestic chips arrive.",
    ["bytedance_bm", "alibaba"], amount_note="2025 capex, RMB79.2B"),

 # ---------------- Chips & manufacturing ----------------
 it("tsmc-az", "TSMC Arizona fabs & packaging", "TSMC", "chips", "site", 265, "2026-07",
    "Phoenix, Arizona", "United States", 33.745, -112.08, "site", "Fab 1 producing; more under construction",
    "Raised from $165B (March 2025) with another $100B in July 2026 for 2nm-and-below fabs and advanced packaging. NVIDIA Blackwell wafers are already made here.",
    ["tsmc_265", "tsmc_165"]),
 it("nvda-us", "NVIDIA US AI supercomputer manufacturing", "NVIDIA", "chips", "program", 500, "2025-04",
    "Houston & Fort Worth, Texas; Phoenix, Arizona", "United States", 29.76, -95.37, "city", "Ramping",
    "NVIDIA plans to produce up to $500B of AI infrastructure in the US over four years with TSMC, Foxconn (Houston), Wistron (Fort Worth), Amkor and SPIL. The figure is the value of hardware produced, not NVIDIA's own spending.",
    ["nvda_500", "nvda_mfg26"], amount_note="value of output, 4 years"),
 it("apple-us", "Apple US commitment & Houston AI server plant", "Apple", "chips", "program", 600, "2025-08",
    "Houston, Texas (servers) and across the US", "United States", 29.88, -95.55, "city", "Shipping servers since Oct 2025",
    "Raised from $500B to $600B over four years. It covers suppliers, R&D and more; the AI part includes a 250,000 sq ft Houston factory building servers for Apple Intelligence.",
    ["apple_600", "apple_houston"], amount_note="broad 4-year pledge"),
 it("micron-us", "Micron US memory expansion", "Micron", "chips", "program", 200, "2025-06",
    "Boise, Idaho; Clay, New York; Manassas, Virginia", "United States", 43.53, -116.15, "hq", "Under way",
    "About $150B for manufacturing (two Idaho fabs, up to four in New York, a Virginia upgrade) plus $50B of R&D, with HBM packaging to follow.",
    ["micron_200", "micron_10q"]),
 it("micron-ny", "Micron New York megafab", "Micron", "chips", "site", None, "2026-01",
    "Clay, New York", "United States", 43.18, -76.18, "site", "Broke ground Jan 2026",
    "First of up to four DRAM fabs; supply from 2030. Part of the $200B plan.", ["micron_10q"]),
 it("skh-yongin", "Yongin Y2 & Cheongju M17 fabs", "SK hynix", "chips", "site", 38.1, "2026-08",
    "Yongin & Cheongju, South Korea", "South Korea", 37.16, 127.29, "site", "Approved; Y2 ground-breaking Jul 2027",
    "KRW54T for two new memory fabs, part of a KRW600T long-range plan for the Yongin cluster; Y2 is dedicated to DRAM including HBM.",
    ["skh_y2"], amount_note="KRW54T"),
 it("skh-indiana", "HBM advanced packaging plant", "SK hynix", "chips", "site", 3.87, "2024-04",
    "West Lafayette, Indiana", "United States", 40.43, -86.91, "site", "Construction; operations 2H 2028",
    "First US plant for high-bandwidth memory packaging, with Purdue research ties.", ["skh_indiana", "skh_f1"]),
 it("samsung-taylor", "Taylor 2nm fab (Tesla AI chips)", "Samsung", "chips", "site", 16.5, "2025-07",
    "Taylor, Texas", "United States", 30.57, -97.41, "site", "Production started (Sep 2026)",
    "Tesla's $16.5B contract for AI5/AI6 chips revived the fab; output began ahead of schedule at about 30% utilization.",
    ["samsung_tesla"], amount_note="Tesla contract"),
 it("samsung-p5", "Pyeongtaek P5 memory fab", "Samsung", "chips", "site", None, "2026-03",
    "Pyeongtaek, South Korea", "South Korea", 37.02, 127.05, "site", "Under construction",
    "Fifth Pyeongtaek fab aimed at HBM and advanced DRAM for AI servers.", ["samsung_p5"]),
 it("terafab", "Terafab (Intel 14A foundry)", "Tesla / SpaceX / Intel", "chips", "site", 16.8, "2026-08",
    "Grimes County, Texas", "United States", 30.40, -96.00, "site", "Construction from Dec 2026",
    "Musk's chip complex, confirmed in August 2026 with a $16.8B first phase and 3,000 jobs; Intel is the foundry partner on its unproven 14A process.",
    ["terafab", "terafab_247"], amount_note="first phase"),
 it("intel-recap", "Intel recapitalization", "US government, NVIDIA, SoftBank", "chips", "program", 15.9, "2025-08",
    "Santa Clara, California", "United States", 37.388, -121.963, "hq", "Closed",
    "US government stake of $8.9B (9.9%), NVIDIA $5B with joint x86/NVLink products, SoftBank $2B.",
    ["intel_usg", "intel_proxy"]),

 # ---------------- AI company funding ----------------
 it("oai-122", "OpenAI funding round", "OpenAI", "funding", "funding", 122, "2026-03",
    "San Francisco", "United States", 37.769, -122.389, "hq", "Closed at $852B valuation",
    "Largest private round ever: Amazon up to $50B ($35B contingent on an IPO or AGI), NVIDIA $30B, SoftBank $30B, plus $3B from individual investors.",
    ["oai_122", "oai_122_cnbc"]),
 it("oai-40", "OpenAI funding round", "OpenAI", "funding", "funding", 40, "2025-03",
    "San Francisco", "United States", 37.769, -122.389, "hq", "Closed at $300B valuation",
    "SoftBank-led round, then the largest private raise in history.", ["funding_hist"]),
 it("oai-66", "OpenAI funding round", "OpenAI", "funding", "funding", 6.6, "2024-10",
    "San Francisco", "United States", 37.769, -122.389, "hq", "Closed at $157B valuation",
    "", ["oai_66"]),
 it("ant-h", "Anthropic Series H", "Anthropic", "funding", "funding", 65, "2026-05",
    "San Francisco", "United States", 37.789, -122.396, "hq", "Closed at $965B valuation",
    "Led by Altimeter, Dragoneer, Greenoaks and Sequoia; made Anthropic the most valuable private AI company.",
    ["ant_h"]),
 it("ant-g", "Anthropic Series G", "Anthropic", "funding", "funding", 30, "2026-02",
    "San Francisco", "United States", 37.789, -122.396, "hq", "Closed at $380B valuation", "", ["ant_hist", "funding_hist"]),
 it("ant-f", "Anthropic Series F", "Anthropic", "funding", "funding", 13, "2025-09",
    "San Francisco", "United States", 37.789, -122.396, "hq", "Closed at $183B valuation", "", ["ant_hist"]),
 it("ant-msnv", "Microsoft & NVIDIA investment in Anthropic", "Microsoft / NVIDIA", "funding", "funding", 15, "2025-11",
    "San Francisco", "United States", 37.789, -122.396, "hq", "Committed",
    "NVIDIA up to $10B and Microsoft up to $5B, alongside Anthropic's $30B Azure purchase commitment.",
    ["ant_msnv"], amount_note="up to"),
 it("ant-amzn", "Amazon investment in Anthropic", "Amazon", "funding", "funding", 4, "2024-11",
    "San Francisco", "United States", 37.789, -122.396, "hq", "Closed",
    "Took Amazon's total investment to $8B.", ["amzn_ant4"]),
 it("xai-e", "xAI Series E", "xAI", "funding", "funding", 20, "2026-01",
    "Palo Alto, California", "United States", 37.44, -122.14, "hq", "Closed; xAI merged into SpaceX Feb 2026",
    "Backers included NVIDIA, Cisco, Valor, Fidelity, Qatar's QIA, MGX and Saudi Arabia's HUMAIN ($3B).",
    ["xai_e", "humain_v2030"]),
 it("xai-bc", "xAI Series B & C", "xAI", "funding", "funding", 12, "2024-12",
    "Palo Alto, California", "United States", 37.44, -122.14, "hq", "Closed",
    "Two $6B rounds, in May and December 2024.", ["xai_c", "xai_hist"]),
 it("spacex-ipo", "SpaceX IPO (funds SpaceXAI build-out)", "SpaceX", "funding", "funding", 75, "2026-06",
    "Starbase, Texas", "United States", 25.99, -97.16, "hq", "Listed Jun 12, 2026",
    "Largest IPO ever, at a $1.75T valuation, four months after SpaceX absorbed xAI. With a $25B bond, SpaceX held about $100B of cash at mid-year; 86% of its Q2 capex went to AI.",
    ["spacex_ipo", "spacex_tunguz"]),
 it("meta-scale", "Meta stake in Scale AI", "Meta", "funding", "funding", 14.3, "2025-06",
    "San Francisco", "United States", 37.770, -122.404, "hq", "Closed",
    "49% stake; Scale's CEO Alexandr Wang joined to lead Meta Superintelligence Labs.", ["meta_scale"]),
 it("tml", "Thinking Machines Lab seed round", "Thinking Machines Lab", "funding", "funding", 2, "2025-07",
    "San Francisco", "United States", 37.776, -122.417, "hq", "Closed at $12B valuation",
    "Mira Murati's lab.", ["tml"]),
 it("ssi", "Safe Superintelligence round", "Safe Superintelligence", "funding", "funding", 2, "2025-04",
    "Palo Alto, California", "United States", 37.44, -122.16, "hq", "Closed at $32B valuation",
    "Ilya Sutskever's lab.", ["ssi"]),
 it("mistral", "Mistral AI Series C", "Mistral AI", "funding", "funding", 2.0, "2025-09",
    "Paris", "France", 48.87, 2.33, "hq", "Closed at EUR11.7B valuation",
    "EUR1.7B round led by ASML's EUR1.3B.", ["mistral"], amount_note="EUR1.7B"),
 it("nscale", "Nscale Series C", "Nscale", "funding", "funding", 2, "2026-03",
    "London", "United Kingdom", 51.52, -0.10, "hq", "Closed",
    "UK AI cloud behind Stargate UK and Microsoft's Loughton supercomputer; reportedly seeking about $3.5B more before an IPO.",
    ["nscale"]),
]

# ---------- compute and equity deal flow (not mapped) ----------
FLOWS = [
 # payer, payee, amount $B (None = unpriced), type, term, note, sources
 ("OpenAI", "Oracle", 300, "Compute", "5 yrs from 2027", "4.5 GW of Stargate capacity", ["oai_oracle", "oai_fierce"]),
 ("OpenAI", "Microsoft Azure", 250, "Compute", "Multi-year", "Commitment made with the Oct 2025 restructuring", ["oai_deals"]),
 ("OpenAI", "Amazon (AWS)", 38, "Compute", "7 yrs", "NVIDIA-based capacity; reportedly expanded with Trainium", ["oai_deals"]),
 ("OpenAI", "CoreWeave", 22.4, "Compute", "~5 yrs", "Three contracts in 2025", ["oai_fierce"]),
 ("OpenAI", "Cerebras", 10, "Compute", "Through 2028", "750 MW of low-latency inference; 'more than' $10B", ["oai_cerebras"]),
 ("OpenAI", "AMD", None, "Chips", "From H2 2026", "6 GW of Instinct GPUs; OpenAI got warrants for up to 160M AMD shares", ["oai_fierce"]),
 ("OpenAI", "Broadcom", None, "Chips", "From H2 2026", "10 GW of OpenAI-designed accelerators", ["oai_fierce"]),
 ("OpenAI", "SB Energy (PORTS-Pike)", None, "Lease", "20 yrs", "8 GW IT; NVIDIA guarantees up to $105B", ["nvda_ports"]),
 ("Anthropic", "Broadcom", 161.2, "Chips", "From 2027", "TPU equipment leases (~3.5 GW)", ["ant_518", "ant_gb"]),
 ("Anthropic", "Google Cloud", 111.1, "Compute", "Apr 2026 - Jul 2033", "TPU capacity", ["ant_518"]),
 ("Anthropic", "Amazon (AWS)", 110, "Compute", "May 2026 - Apr 2036", "Trainium capacity", ["ant_518"]),
 ("Anthropic", "SpaceX (xAI)", 84.5, "Compute", "Through 2029", "Colossus capacity; largely cancelable on 90 days' notice", ["ant_518"]),
 ("Anthropic", "Microsoft Azure", 31.4, "Compute", "Nov 2026 - May 2033", "NVIDIA-based capacity", ["ant_518"]),
 ("Anthropic", "AMD", 20, "Chips", "Multi-year", "'Over' $20B expected supply", ["ant_518"]),
 ("Meta", "CoreWeave", 35, "Compute", "Multi-year", "$14.2B (2025) + $21B (2026)", ["crwv_q2", "crwv_meta"]),
 ("Google", "SpaceX (xAI)", 30, "Compute", "Oct 2026 - Jun 2029", "~$920M a month for ~110,000 GPUs", ["xai_baxtel"]),
 ("Microsoft", "Nebius", 17.4, "Compute", "5 yrs", "Up to $19.4B; Vineland, NJ", ["nebius"]),
 ("Tesla", "Samsung", 16.5, "Chips", "Multi-year", "AI5/AI6 chips from Taylor, TX", ["samsung_tesla"]),
 ("Amazon", "OpenAI", 50, "Equity", "Mar 2026", "$35B contingent on IPO or AGI", ["oai_122"]),
 ("NVIDIA", "OpenAI", 30, "Equity", "Mar 2026", "Part of the $122B round", ["oai_122"]),
 ("SoftBank", "OpenAI", 30, "Equity", "Mar 2026", "After ~$41B in the 2025 round", ["oai_122", "oai_oracle"]),
 ("NVIDIA", "Anthropic", 10, "Equity", "Nov 2025", "Up to", ["ant_msnv"]),
 ("NVIDIA", "SB Energy / OpenAI", 105, "Guarantee", "20 yrs", "Credit support for PORTS-Pike; plus $1.5B equity in SB Energy", ["nvda_10q"]),
]

# ---------- builders: company-level capex and revenue ----------
# capex: [2024, 2025, 2026] in $B (calendar unless noted). share: portion of capex that serves the AI-exposed revenue line.
BUILDERS = [
 dict(id="msft", name="Microsoft", ticker="MSFT", capex=[75.6, 118.0, 190.0], capexNote="Calendar years incl. finance leases; 2026 is the ~$190B plan before a lease reclassification lowered the reported figure to ~$175B",
      share=0.95, rev_now=237.2, rev_2023=111.6, revLine="Microsoft Cloud revenue (Q4 FY26 x4) minus FY2023",
      ocf=182.9, spend26=190.0, backlog="Commercial RPO $678B (+84%); 45% tied to OpenAI as of Jan 2026",
      extra="Disclosed AI run-rate: $37B (Apr 2026, +123%). Copilot: 30M+ paid seats. Stays free-cash-flow positive in FY27 (CFO).",
      src=["msft_cnbc_q3", "msft_q4fy26", "msft_8k", "msft_ai37", "msft_beancount", "msft_capex_q", "msft_openai_rpo"]),
 dict(id="googl", name="Alphabet", ticker="GOOGL", capex=[52.5, 91.4, 200.0], capexNote="2026 = midpoint of $195-205B guidance; 2027 to 'significantly increase'",
      share=0.90, rev_now=479.2, rev_2023=307.4, revLine="Total revenue (Search, YouTube, Cloud; Q2 2026 x4) minus 2023",
      ocf=185.7, spend26=200.0, backlog="Google Cloud backlog $514B",
      extra="Revenue added since 2023 includes Search and YouTube growth, which Alphabet credits partly to AI. Cloud revenue +82% y/y in Q2 2026. First negative quarterly free cash flow (-$5.9B), buybacks paused, $80B equity raise (incl. $10B from Berkshire).",
      src=["googl_q2", "googl_ars", "googl_equity", "googl_fcf"]),
 dict(id="amzn", name="Amazon", ticker="AMZN", capex=[83.0, 131.8, 220.0], capexNote="Cash capex; AWS was ~68% of 2025 property additions",
      share=0.70, rev_now=168.8, rev_2023=90.8, revLine="AWS revenue (Q2 2026 x4) minus 2023",
      ocf=161.4, spend26=220.0, backlog="AWS backlog $496B, growing triple digits",
      extra="AWS +37% y/y in Q2 2026, its fastest in 18 quarters, with a 39% operating margin. Capacity short of demand through 2027.",
      src=["amzn_q2", "amzn_fy25", "amzn_capex_q2"]),
 dict(id="meta", name="Meta", ticker="META", capex=[39.2, 72.2, 137.5], capexNote="Incl. finance-lease principal; 2026 = midpoint of $130-145B",
      share=0.95, rev_now=243.2, rev_2023=134.9, revLine="Total revenue (Q2 2026 x4) minus 2023; no cloud business to rent capacity",
      ocf=130.3, spend26=137.5, backlog="No external backlog; off-balance-sheet leases for Hyperion (Blue Owl JV) and El Paso (BlackRock, ~$13B guarantee)",
      extra="Leads on the revenue it has added so far, but 2027 capex and off-balance-sheet leases are not in this capital figure. Q2 2026 free cash flow fell 91% to $784M; pledged $600B+ of US spending through 2028.",
      src=["meta_q2", "meta_fcf", "capex_2025", "meta_600", "meta_10q"]),
 dict(id="orcl", name="Oracle", ticker="ORCL", capex=[21.2, 55.7, 92.5], capexNote="Fiscal years ending May (FY25, FY26, FY27 guide of $90-95B; no more than $70B net cash)",
      share=1.0, rev_now=29.6, rev_2023=6.9, revLine="Oracle Cloud Infrastructure revenue (Q1 FY27 x4) minus FY2024",
      ocf=46.9, spend26=92.5, backlog="RPO $664B; about half expected to convert within 36 months, largely OpenAI's $300B",
      extra="Free cash flow -$23.7B in FY26; raising ~$40B of debt and equity in FY27, incl. a $20B at-the-market share sale.",
      src=["orcl_q1fy27", "orcl_10k", "orcl_capex", "orcl_fy24", "orcl_q4fy26"]),
 dict(id="crwv", name="CoreWeave", ticker="CRWV", capex=[8.7, 14.9, 37.0], capexNote="2026 = midpoint of $35-39B guidance",
      share=1.0, rev_now=14.1, rev_2023=0.23, revLine="Revenue (Q3 2026 guidance x4) minus 2023",
      ocf=4.4, ocfLabel="adj. EBITDA (TTM)", spend26=37.0, backlog="Backlog $104B at Jun 30 plus $25B+ signed in early Q3",
      extra="About $35B of debt; Q3 interest expense guided up to $940M. Customers include Microsoft, OpenAI, Meta, Anthropic and Jane Street.",
      src=["crwv_q2", "crwv_dcd", "crwv_fy25", "crwv_tl", "crwv_meta"]),
 dict(id="spcx", name="SpaceXAI (xAI)", ticker="SPCX", capex=[0, 12.7, 55.2], capexNote="AI capex only. 2024 not disclosed; 2025 = 61% of $20.7B; 2026 = Q1 $7.7B + Q2 $15.8B + two more quarters at Q2's level",
      share=1.0, rev_now=10.2, rev_2023=0.0, revLine="AI segment revenue (Q2 2026 x4)",
      ocf=6.6, ocfLabel="SpaceX adj. EBITDA (2025)", spend26=55.2, backlog="Leases: Anthropic up to $84.5B through 2029 (largely cancelable), Google ~$30B through Jun 2029",
      extra="AI segment lost $1.26B in Q2 2026 but turned EBITDA-positive. About $100B of cash after the IPO and a $25B bond.",
      src=["spacex_q2", "spacex_tunguz", "spacex_capex25", "xai_baxtel", "spacex_s1"]),
]

# ---------- renters: frontier labs paying for compute ----------
LABS = [
 dict(id="oai", name="OpenAI", ticker="private", commit=600, commitNote="~$600B of compute through 2030 (company target, Feb 2026), spread over 2026-2030",
      annual=120.0, rev_now=70.0, revLine="Annualized revenue, late Sep 2026 (reported)",
      extra="2025 revenue about $13B. Targets $280B+ revenue by 2030 and expects ~$278B of cash burn in 2026-2030. Signed deals: Microsoft $250B, Oracle $300B, AWS $38B+, CoreWeave $22.4B, plus AMD, Broadcom and PORTS-Pike.",
      src=["oai_600", "oai_70", "oai_burn", "oai_deals"]),
 dict(id="ant", name="Anthropic", ticker="private", commit=518.2, commitNote="$518B of cloud and compute commitments in its IPO filing; each contract spread over its stated term (Broadcom assumed 2027-2033, AMD 2027-2030)",
      annual=None, rev_now=65.0, revLine="Annualized revenue, end of Jul 2026 (partly gross basis)",
      extra="2025 revenue $4.6B; first operating profit in Q2 2026 on $11.5B of revenue. About 80% of commitments are non-cancelable.",
      src=["ant_518", "ant_518b", "ant_65", "ant_gross"]),
]

# Anthropic commitment schedule: (amount, start_year_fraction, end_year_fraction)
ANT_SCHEDULE = [
 ("Google", 111.1, 2026 + 3/12, 2033 + 7/12),
 ("Amazon", 110.0, 2026 + 4/12, 2036 + 4/12),
 ("Microsoft", 31.4, 2026 + 10/12, 2033 + 5/12),
 ("Broadcom", 161.2, 2027.0, 2034.0),
 ("xAI", 84.5, 2026 + 5/12, 2030.0),
 ("AMD", 20.0, 2027.0, 2031.0),
]

COLLECTORS = [
 dict(name="NVIDIA", stat="$89.0B", label="data-center revenue, Q2 FY27 (+117% y/y)", sub="Guides Q3 revenue to $108B and ~70% growth next fiscal year", src="nvda_q2"),
 dict(name="TSMC", stat="$40.2B", label="Q2 2026 revenue; profit +77% y/y", sub="2026 growth now 'slightly above 40%'; capex raised to $60-64B", src="tsmc_q2"),
 dict(name="Micron", stat="$23.9B", label="fiscal Q2 2026 revenue (vs $8.1B a year earlier)", sub="$13.8B net income in one quarter as HBM prices soar", src="mu_fq2"),
 dict(name="NVIDIA as financier", stat="$99B", label="equity stakes in AI companies, plus $25B committed", sub="And up to $105B of guarantees on OpenAI's Ohio leases", src="nvda_10q"),
]
