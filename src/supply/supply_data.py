"""AI Supply Chain Atlas: single source of truth for nodes, links, chokepoints, sites, scenarios and quotes.
All figures as researched through 30 Sep 2026. Shares are the cited sources' figures; where a source gives no
number the text says so qualitatively."""

S = {}
def src(key, label, url):
    S[key] = (label, url)
    return key

ATLAS_URL = "https://claude.ai/artifact/4AnG4Rk35RdMEn3aKYr7Pm"

# ---------------------------------------------------------------- sources
src("atlas", "AI Investment Atlas (companion page): capex, lab commitments and financing flows", ATLAS_URL)
src("tf_tsmc_cap", "TrendForce - TSMC targets 2nm/3nm capacity boost by mid-2027; CoWoS to double by 2028 (14 Sep 2026)", "https://www.trendforce.com/news/2026/09/14/news-tsmc-reportedly-targets-22-2nm-16-3nm-capacity-boost-by-mid-2027-cowos-to-double-by-2028/")
src("th_tsmc_az", "Tom's Hardware - TSMC commits another $100B to Arizona for at least four more 2nm fabs", "https://www.tomshardware.com/tech-industry/tsmc-commits-another-100-billion-to-arizona-for-at-least-four-more-2nm-fabs")
src("tf_hbm4", "TrendForce - Samsung, SK hynix tapped as Nvidia Rubin HBM4 suppliers; 2026 HBM shares (9 Mar 2026)", "https://www.trendforce.com/news/2026/03/09/news-samsung-sk%E2%80%AFhynix-reportedly-tapped-as-nvidia-rubin-hbm4-suppliers-shipments-could-start-in-march")
src("tf_mem", "TrendForce - Q3 2026 DRAM and NAND contract price outlook (3 Jul 2026)", "https://www.trendforce.com/presscenter/news/20260703-13134.html")
src("tf_glass", "TrendForce Insights - Glass-fiber cloth (T-glass) shortage", "https://insights.trendforce.com/p/glass-fiber-cloth-shortage")
src("wing_abf", "Wing VC - The ABF substrate bottleneck", "https://www.wing.vc/content/the-abf-substrate-bottleneck")
src("taipei_aspeed", "Taipei Times - ASPEED shifts boards to E-glass amid substrate shortage (4 Jun 2026)", "https://www.taipeitimes.com/News/biz/archives/2026/06/04/2003858478")
src("asml_q2", "MarketBeat - ASML Q2 2026 earnings call highlights (15 Jul 2026)", "https://www.marketbeat.com/instant-alerts/asml-q2-earnings-call-highlights-2026-07-15/")
src("env_test", "Envisioning - Japan's semiconductor test and metrology chokepoints", "https://www.envisioning.com/research/substrate/japan__semiconductor-test-metrology")
src("env_resist", "Envisioning - Japan's EUV photoresist dominance", "https://www.envisioning.com/research/stratum/japan__euv-photoresists")
src("asiae_hanmi", "Asia Economy - Hanmi Semiconductor holds 71.2% of AI TC-bonder market (9 Feb 2026)", "https://view.asiae.co.kr/en/article/2026020908430125470")
src("fx_wafer", "Faxian - Semiconductor silicon wafer market report 2026 (2025 shares)", "https://faxiangongchang.com/en/reports/china-semiconductor-silicon-wafer-2026")
src("nbc_spruce", "NBC - How a tiny town hit by Helene could upend the global chip industry", "https://www.nbcchicago.com/news/business/money-report/how-a-tiny-town-hit-by-helene-could-upend-the-global-semiconductor-chip-industry/3564604/")
src("mt_china", "Mining Technology - China suspends ban on gallium, germanium, antimony exports to US", "https://www.mining-technology.com/news/china-suspends-ban-exports-us/")
src("pillsbury", "Pillsbury - China suspends export controls on certain critical minerals (what stays in force)", "https://pillsburylaw.com/en/news-and-insights/china-suspends-export-controls-certain-critical-minerals-related-items.html")
src("skillings_re", "Skillings - Rare-earth export controls: latest updates and suspension deadlines", "https://skillings.net/rare-earth-export-controls-the-latest-updates-and-what-they-mean-for-supply-chains-2/")
src("tf_inp", "TrendForce - InP shortage emerges as AI optical-interconnect bottleneck (6 Aug 2026)", "https://trendforce.com/news/2026/08/06/news-inp-shortage-emerges-as-ai-optical-interconnect-bottleneck/")
src("dcd_lumentum", "DatacenterDynamics - Nvidia pumps $2B into optical developer Lumentum (Mar 2026)", "https://www.datacenterdynamics.com/en/news/nvidia-pumps-2bn-into-optical-developer-lumentum/")
src("lc_optics", "LightCounting - Optical vendor landscape, May 2026", "https://lightcounting.com/newsletter/en/may-2026-optical-vendor-landscape-376")
src("th_asic", "Tom's Hardware - Custom AI ASICs examined, from Broadcom to MTIA", "https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia")
src("tf_racks", "TrendForce - NVL72 rack output to exceed $710B in 2027 (28 Aug 2026)", "https://www.trendforce.com/presscenter/news/20260828-13204.html")
src("technews_odm", "TechNews - Foxconn leads Quanta and Wistron in AI rack shipments (12 May 2026)", "https://finance.technews.tw/2026/05/12/foxconn-leads-quanta-and-wistron-in-ai-server-shipments/")
src("gev_backlog", "Turbomachinery - GE Vernova gas-turbine backlog hits 116 GW", "https://www.turbomachinerymag.com/view/ge-vernova-gas-turbine-backlog-hits-116-gw-as-power-orders-more-than-double")
src("oilprice_turb", "OilPrice - The gas turbine shortage just became AI's biggest constraint", "https://oilprice.com/Energy/Energy-General/The-Gas-Turbine-Shortage-Just-Became-AIs-Biggest-Constraint.amp.html")
src("pv_transf", "pv magazine USA - US transformer lead times extend to four years (11 May 2026)", "https://pv-magazine-usa.com/2026/05/11/u-s-transformer-market-faces-severe-supply-constraints-as-lead-times-extend-to-four-years/")
src("hoodline_goes", "Hoodline - Cleveland-Cliffs wins $400M sole-source electrical-steel deal (Jul 2026)", "https://hoodline.com/2026/07/cleveland-cliffs-snags-400-million-defense-steel-deal-to-keep-transformers-on/")
src("spg_uranium", "S&P Global - Russia bans enriched-uranium exports to US; US import ban timeline", "https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/111524-russia-temporarily-bans-exports-to-us-of-enriched-uranium-after-us-curbed-imports")
src("bgov_pjm", "Bloomberg Government - AI bumps power cost as PJM misses supply goal (14 Jul 2026)", "https://news.bgov.com/artificial-intelligence/ai-bumps-power-cost-60-as-mega-us-grid-fails-to-hit-supply-goal")
src("fortune_he", "Fortune - Iran war helium shortage hits chip supply chains (21 Mar 2026)", "https://fortune.com/2026/03/21/iran-war-helium-shortage-qatar-chip-supply-chains-ai-boom/")
src("iumi_he", "IUMI - Qatari helium shortages (Jun 2026)", "https://iumi.com/newsletter-june-2026/qatari-helium-shortages/")
src("fool_he", "Motley Fool - The helium shortage exposed AI's weak link (11 May 2026)", "https://www.fool.com/investing/2026/05/11/the-helium-shortage-exposed-the-artificial-intelli/")
src("row_aws", "Rest of World - Gulf war: AWS data-center attack and AI investment risk", "https://restofworld.org/2026/gulf-war-aws-data-center-attack-ai-investment-risk/")
src("fp_gulf", "Foreign Policy - War, AI and the Gulf (10 Apr 2026)", "https://foreignpolicy.com/2026/04/10/war-ai-gulf-uae-saudi-qatar-iran/")
src("tnw_stargate", "The Next Web - Iran threatens Stargate UAE (Apr 2026)", "https://thenextweb.com/news/iran-threatens-stargate-openai-abu-dhabi")
src("aj_hormuz", "Al Jazeera - Iran touts Hormuz attacks as oil flows increase (28 Sep 2026)", "https://aljazeera.com/news/2026/9/28/iran-touts-hormuz-attacks-as-oil-flows-increase-despite-tensions")
src("wiki_ceasefire", "Wikipedia - 2026 Iran war ceasefire", "https://en.wikipedia.org/wiki/2026_Iran_war_ceasefire")
src("ij_taiwan", "Insurance Journal (Bloomberg Economics) - A Taiwan war would cost the world $10 trillion", "https://www.insurancejournal.com/news/international/2024/01/11/755295.htm")
src("samdesk_tw", "Samdesk - Military pressure on Taiwan: PLA drills timeline", "https://www.samdesk.io/briefings/april-7-military-pressure-on-taiwan")
src("tnw_oracle", "The Next Web - S&P cuts Oracle to BBB- on AI spending (Jul 2026)", "https://thenextweb.com/news/oracle-sp-downgrade-ai-spending-junk-risk")
src("webull_crwv", "Webull News - CoreWeave's interest expense hit $640M last quarter", "https://www.webull.com/news/15506452301407232")
src("tr_232", "Thomson Reuters - Section 232 tariff on advanced AI semiconductors (15 Jan 2026)", "https://www.thomsonreuters.com/en-us/help/onesource-global-trade/regulatory-insights/2026/january-15th/trump-admin-tariffs-advanced-ai-chips-232")
src("bern_gw", "Investing.com (Bernstein) - How much does a GW of data-center capacity actually cost", "https://www.investing.com/news/stock-market-news/how-much-does-a-gw-of-data-center-capacity-actually-cost-4314046")
src("epoch_gw", "Epoch AI - AI data-center cost breakdown (14 May 2026)", "https://epoch.ai/data-insights/ai-datacenter-cost-breakdown")
src("sa_all", "Stock Analysis - quotes, analyst consensus and forecasts (accessed 30 Sep 2026; one page per company, linked in the watchlist)", "https://stockanalysis.com/")
src("cmc_semis", "CompaniesMarketCap - largest semiconductor companies by market cap (USD)", "https://companiesmarketcap.com/semiconductors/largest-semiconductor-companies-by-market-cap/")
src("sa_cambricon", "Stock Analysis - Cambricon (SHA:688256) overview and news", "https://stockanalysis.com/quote/sha/688256/")

# ---------------------------------------------------------------- tiers & lanes
TIERS = [
    ("mine", "Mine & extract"), ("refine", "Refine & formulate"), ("mat", "Engineered materials"),
    ("tools", "Tools & gear"), ("fab", "Fabs & power plants"), ("pkg", "Packaging & grid"),
    ("chips", "Chips, optics & plant"), ("sys", "Systems & build"), ("campus", "Campus & capital"),
    ("ops", "Compute sellers"), ("demand", "Models & demand"),
]

# ---------------------------------------------------------------- companies: key -> (name, ticker or None, country)
C = {
 "nvda": ("Nvidia", "NVDA", "US"), "amd": ("AMD", "AMD", "US"), "avgo": ("Broadcom", "AVGO", "US"),
 "mrvl": ("Marvell", "MRVL", "US"), "arm": ("Arm", "ARM", "UK"), "intc": ("Intel", "INTC", "US"),
 "cbrs": ("Cerebras", "CBRS", "US"), "alab": ("Astera Labs", "ALAB", "US"), "crdo": ("Credo", "CRDO", "US"),
 "mtk": ("MediaTek", "2454.TW", "TW"), "alchip": ("Alchip", "3661.TW", "TW"), "guc": ("Global Unichip", "3443.TW", "TW"),
 "cambricon": ("Cambricon", "688256.SS", "CN"), "huawei": ("Huawei (Ascend)", None, "CN"), "aspeed": ("ASPEED", "5274.TWO", "TW"),
 "nuvoton": ("Nuvoton", "4919.TW", "TW"),
 "tsmc": ("TSMC", "TSM", "TW"), "samsung": ("Samsung Electronics", "005930.KS", "KR"), "skhynix": ("SK hynix", "000660.KS", "KR"),
 "mu": ("Micron", "MU", "US"), "sndk": ("SanDisk", "SNDK", "US"), "kioxia": ("Kioxia", "285A.T", "JP"), "stx": ("Seagate", "STX", "US"),
 "smic": ("SMIC", "0981.HK", "CN"), "cxmt": ("CXMT", "688825.SS", "CN"),
 "asml": ("ASML", "ASML", "NL"), "zeiss": ("Carl Zeiss SMT", None, "DE"), "trumpf": ("Trumpf", None, "DE"),
 "amat": ("Applied Materials", "AMAT", "US"), "lrcx": ("Lam Research", "LRCX", "US"), "klac": ("KLA", "KLAC", "US"),
 "tel": ("Tokyo Electron", "8035.T", "JP"), "asmi": ("ASM International", "ASM.AS", "NL"),
 "lasertec": ("Lasertec", "6920.T", "JP"), "advantest": ("Advantest", "6857.T", "JP"), "ter": ("Teradyne", "TER", "US"),
 "disco": ("Disco", "6146.T", "JP"), "accretech": ("Tokyo Seimitsu (Accretech)", "7729.T", "JP"),
 "hanmi": ("Hanmi Semiconductor", "042700.KS", "KR"), "hanwha": ("Hanwha Semitech", None, "KR"),
 "asmpt": ("ASMPT", "0522.HK", "HK"), "besi": ("BE Semiconductor", "BESI.AS", "NL"),
 "snps": ("Synopsys", "SNPS", "US"), "cdns": ("Cadence", "CDNS", "US"), "siemens": ("Siemens (Siemens EDA)", "SIE.DE", "DE"),
 "shinetsu": ("Shin-Etsu Chemical", "4063.T", "JP"), "sumco": ("SUMCO", "3436.T", "JP"), "gwafers": ("GlobalWafers", "6488.TWO", "TW"),
 "siltronic": ("Siltronic", "WAF.DE", "DE"), "sksiltron": ("SK Siltron", None, "KR"),
 "wacker": ("Wacker Chemie", "WCH.DE", "DE"), "hemlock": ("Hemlock Semiconductor", None, "US"), "tokuyama": ("Tokuyama", "4043.T", "JP"),
 "jsr": ("JSR (private)", None, "JP"), "tok": ("Tokyo Ohka Kogyo", "4186.T", "JP"), "fujifilm": ("Fujifilm", "4901.T", "JP"),
 "ajinomoto": ("Ajinomoto", "2802.T", "JP"), "nittobo": ("Nittobo", "3110.T", "JP"), "grace": ("Grace Fabric Technology", None, "CN"),
 "ibiden": ("Ibiden", "4062.T", "JP"), "shinko": ("Shinko Electric (private)", None, "JP"), "unimicron": ("Unimicron", "3037.TW", "TW"),
 "ats": ("AT&S", "ATS.VI", "AT"), "nanyapcb": ("Nan Ya PCB", "8046.TW", "TW"),
 "emc": ("Elite Material", "2383.TW", "TW"), "tuc": ("Taiwan Union Technology", "6274.TWO", "TW"),
 "linde": ("Linde", "LIN", "US"), "airliquide": ("Air Liquide", "AI.PA", "FR"), "apd": ("Air Products", "APD", "US"),
 "entg": ("Entegris", "ENTG", "US"), "axt": ("AXT (Tongmei)", "AXTI", "US"), "sumitomo": ("Sumitomo Electric", "5802.T", "JP"),
 "jx": ("JX Advanced Metals", "5016.T", "JP"), "mp": ("MP Materials", "MP", "US"), "lynas": ("Lynas", "LYC.AX", "AU"),
 "northern_re": ("China Northern Rare Earth", "600111.SS", "CN"), "fcx": ("Freeport-McMoRan", "FCX", "US"), "bhp": ("BHP", "BHP", "AU"),
 "clf": ("Cleveland-Cliffs", "CLF", "US"), "qatarenergy": ("QatarEnergy (state)", None, "QA"),
 "sibelco": ("Sibelco (private)", None, "BE"), "quartzcorp": ("The Quartz Corp (private)", None, "NO"),
 "chalco": ("Chinese alumina refiners (Chalco and others)", "601600.SS", "CN"),
 "ccj": ("Cameco", "CCJ", "CA"), "kap": ("Kazatomprom", "KAP.L", "KZ"), "leu": ("Centrus Energy", "LEU", "US"),
 "urenco": ("Urenco (state-owned)", None, "UK"), "rosatom": ("Rosatom / TENEX (state)", None, "RU"), "orano": ("Orano (state)", None, "FR"),
 "ase": ("ASE Technology", "ASX", "TW"), "amkor": ("Amkor", "AMKR", "US"), "jcet": ("JCET", "600584.SS", "CN"),
 "innolight": ("Zhongji Innolight", "300308.SZ", "CN"), "eoptolink": ("Eoptolink", "300502.SZ", "CN"),
 "cohr": ("Coherent", "COHR", "US"), "lite": ("Lumentum", "LITE", "US"), "fn": ("Fabrinet", "FN", "US"),
 "glw": ("Corning", "GLW", "US"), "fujikura": ("Fujikura", "5803.T", "JP"), "aph": ("Amphenol", "APH", "US"),
 "anet": ("Arista", "ANET", "US"), "csco": ("Cisco", "CSCO", "US"), "prysmian": ("Prysmian", "PRY.MI", "IT"),
 "honhai": ("Hon Hai (Foxconn)", "2317.TW", "TW"), "quanta": ("Quanta Computer", "2382.TW", "TW"), "wistron": ("Wistron", "3231.TW", "TW"),
 "wiwynn": ("Wiwynn", "6669.TW", "TW"), "cls": ("Celestica", "CLS", "CA"), "smci": ("Supermicro", "SMCI", "US"),
 "dell": ("Dell", "DELL", "US"), "hpe": ("HPE", "HPE", "US"),
 "gev": ("GE Vernova", "GEV", "US"), "enr": ("Siemens Energy", "ENR.DE", "DE"), "mhi": ("Mitsubishi Heavy", "7011.T", "JP"),
 "hitachi": ("Hitachi (Hitachi Energy)", "6501.T", "JP"), "hdhe": ("HD Hyundai Electric", "267260.KS", "KR"),
 "etn": ("Eaton", "ETN", "US"), "su": ("Schneider Electric", "SU.PA", "FR"), "vrt": ("Vertiv", "VRT", "US"),
 "delta": ("Delta Electronics", "2308.TW", "TW"), "cat": ("Caterpillar", "CAT", "US"), "be": ("Bloom Energy", "BE", "US"),
 "pwr": ("Quanta Services", "PWR", "US"),
 "ceg": ("Constellation Energy", "CEG", "US"), "vst": ("Vistra", "VST", "US"), "tln": ("Talen Energy", "TLN", "US"),
 "oklo": ("Oklo", "OKLO", "US"), "kairos": ("Kairos Power (private)", None, "US"), "pjm": ("PJM Interconnection", None, "US"),
 "msft": ("Microsoft", "MSFT", "US"), "googl": ("Alphabet", "GOOGL", "US"), "amzn": ("Amazon", "AMZN", "US"),
 "meta": ("Meta", "META", "US"), "orcl": ("Oracle", "ORCL", "US"), "crwv": ("CoreWeave", "CRWV", "US"),
 "nbis": ("Nebius", "NBIS", "NL"), "crusoe": ("Crusoe (private)", None, "US"), "spcx": ("SpaceX (incl. xAI)", "SPCX", "US"),
 "eqix": ("Equinix", "EQIX", "US"), "g42": ("G42 (private)", None, "AE"), "humain": ("HUMAIN (PIF)", None, "SA"),
 "softbank": ("SoftBank Group", "9984.T", "JP"), "openai": ("OpenAI (private)", None, "US"), "anthropic": ("Anthropic (private)", None, "US"),
 "alibaba": ("Alibaba", "BABA", "CN"), "bytedance": ("ByteDance (private)", None, "CN"), "tencent": ("Tencent", "0700.HK", "CN"),
 "baidu": ("Baidu", "BIDU", "CN"),
}

# ---------------------------------------------------------------- nodes
NODES = []
def N(id, tier, lane, short, name, what, why, firms=(), inputs=(), choke=None, exp="med", srcs=()):
    NODES.append(dict(id=id, tier=tier, lane=lane, short=short, name=name, what=what, why=why,
                      firms=[list(f) for f in firms], inputs=[list(i) for i in inputs], choke=choke, exp=exp, src=list(srcs)))

def CH(who, share, where, country, subs, lead, state, status, line):
    return dict(who=who, share=share, where=where, country=country, subs=subs, lead=lead, state=state, status=status, line=line)

# inputs: (input_id, group, weight, passthrough); group None => its own group. weight 0 marks a minor link (drawn, not modeled).
def I(i, p=1.0, g=None, w=1.0):
    return (i, g, w, p)
def M(i):
    return (i, None, 0.0, 0.0)

# ---- tier 0: mine & extract
N("quartz", "mine", "si", "High-purity quartz", "High-purity quartz",
  "Ultra-pure quartz from Spruce Pine, North Carolina, made into the crucibles that hold molten silicon while wafer crystals are grown.",
  "Virtually all of the world's semiconductor-grade high-purity quartz comes from this one town. Hurricane Helene shut its mines on 26 Sep 2024.",
  firms=[("sibelco", None, "Spruce Pine mines"), ("quartzcorp", None, "Spruce Pine mines")],
  choke=CH("Sibelco and The Quartz Corp", "Virtually all", "Spruce Pine, NC", "US",
           "Synthetic quartz and other deposits, at higher cost and not yet proven at scale", "Years to qualify a new deposit",
           "adequate", "warning", "One town supplies the crucible quartz for almost every wafer."),
  exp="low", srcs=["nbc_spruce"])
N("gallium", "mine", "si", "Gallium & germanium", "Gallium and germanium",
  "By-products of alumina and zinc refining, used in compound semiconductors, photodetectors, GaN power chips and the doped cores of optical fiber.",
  "China produces 94% of the world's gallium. Its ban on gallium, germanium and antimony exports to the US is suspended only until 27 Nov 2026.",
  firms=[("chalco", None, "By-product recovery at alumina refineries")],
  choke=CH("China", "94% of gallium", "China", "CN",
           "By-product recovery in Japan, Korea, Germany and North America, small today", "2 to 3 years to add recovery lines",
           "tight", "serious", "China makes almost all of it, and the US ban pause ends 27 Nov 2026."),
  exp="low", srcs=["mt_china", "pillsbury"])
N("indium", "mine", "si", "Indium", "Indium",
  "A by-product of zinc refining and the 'In' in indium phosphide (InP), the wafer material for optical-link lasers.",
  "China produces about 70% of refined indium and keeps it under export control (Announcement No. 10, still in force).",
  firms=[("chalco", None, "Chinese zinc and indium refiners")],
  choke=CH("China", "~70% of refined indium", "China", "CN",
           "Zinc refiners elsewhere can add indium recovery", "1 to 2 years",
           "tight", "serious", "The laser chain starts with a metal China controls."),
  exp="low", srcs=["tf_inp", "pillsbury"])
N("ree", "mine", "si", "Rare earths", "Medium and heavy rare earths",
  "Seven controlled elements, including dysprosium, terbium and yttrium: magnets for fans, pumps, motors and hard drives, and yttria coatings in etch chambers.",
  "China's controls on these seven (Announcement No. 18) remain in force; its wider October 2025 controls are suspended only until 10 Nov 2026.",
  firms=[("northern_re", None, "Largest Chinese producer"), ("mp", None, "US mine and magnet plant"), ("lynas", None, "Australia and Malaysia")],
  choke=CH("China", "Dominant in separation and magnets", "China", "CN",
           "MP Materials (US) and Lynas (Australia, Malaysia) are ramping", "3 to 5 years for new separation and magnet plants",
           "tight", "serious", "Controls on seven elements are live; the broader pause ends 10 Nov 2026."),
  exp="low", srcs=["pillsbury", "skillings_re"])
N("tungsten", "mine", "si", "Tungsten & moly", "Tungsten and molybdenum",
  "Tungsten fills the vertical contacts in chips (deposited from WF6 gas); molybdenum is replacing it at the newest nodes.",
  "Both sit on China's Announcement No. 10 export-control list, which remains in force.",
  firms=[("chalco", None, "Chinese producers")], exp="low", srcs=["pillsbury"])
N("helium", "mine", "si", "Helium", "Helium",
  "Inert gas used to cool wafers during processing, purge tools and test for leaks.",
  "Qatar supplied about a third of the world's helium until Iranian strikes shut Ras Laffan (force majeure 2 Mar 2026; heavy damage 19 to 20 Mar). Russia added helium export controls on 14 Apr. Spot prices doubled; South Korea imports about 65% of its helium from Qatar.",
  firms=[("qatarenergy", "~1/3 of world supply (offline)", "Ras Laffan"), ("linde", None, "Distributor and producer"), ("airliquide", None, "Distributor and producer"), ("apd", None, "Distributor and producer")],
  choke=CH("Qatar (offline), US, Algeria, Russia", "Qatar ~1/3", "Ras Laffan, Qatar", "QA",
           "US and Algerian supply, fab recycling, rationing", "Years to repair Ras Laffan",
           "short", "serious", "A third of supply went offline in March; fabs are running on priority allocations."),
  exp="low", srcs=["fortune_he", "iumi_he", "fool_he"])
N("copper", "mine", "pw", "Copper", "Copper",
  "Windings in transformers and generators, busways and power cables, and the copper foil in chip substrates and boards.",
  "Every megawatt of AI capacity needs copper-heavy power gear; copper and electrical steel are among the constraints behind four-year transformer lead times.",
  firms=[("fcx", None, "Grasberg, Americas"), ("bhp", None, "Escondida")], exp="low", srcs=["pv_transf"])
N("natgas", "mine", "pw", "Natural gas", "Natural gas",
  "Fuel for the gas turbines and engines that power most new US AI campuses with their own generation.",
  "US supply is domestic, but the Iran war has shaken energy markets: Qatar halted LNG at Ras Laffan in March, and Hormuz oil flows were about 7.4M barrels a day in September against about 20M before the war.",
  firms=[], exp="low", srcs=["fortune_he", "aj_hormuz"])
N("uranium", "mine", "pw", "Uranium", "Uranium ore",
  "Mined uranium, the fuel for the nuclear plants AI companies are contracting.",
  "Mining is spread across several countries; the tighter step is enrichment, one tier to the right.",
  firms=[("kap", None, "Kazakhstan"), ("ccj", None, "Canada")], exp="low", srcs=[])

# ---- tier 1: refine & formulate
N("poly", "refine", "si", "Polysilicon", "Semiconductor-grade polysilicon",
  "Silicon refined to eleven-nines purity, the feedstock for wafer crystals.",
  "A handful of firms make chip-grade (not solar-grade) polysilicon; supply is adequate.",
  firms=[("wacker", None, "Germany"), ("hemlock", None, "US"), ("tokuyama", None, "Japan")], exp="low", srcs=[])
N("resist", "refine", "si", "Photoresists", "Photoresists",
  "Light-sensitive polymers that carry each circuit pattern onto the wafer during lithography.",
  "Japanese firms (JSR, Tokyo Ohka Kogyo, Shin-Etsu, Fujifilm) supply 87 to 91% of advanced EUV photoresist.",
  firms=[("jsr", None, "EUV resist"), ("tok", None, "EUV resist"), ("shinetsu", None, "EUV resist"), ("fujifilm", None, "EUV resist")],
  choke=CH("JSR, Tokyo Ohka Kogyo, Shin-Etsu, Fujifilm", "87-91% (Japan)", "Japan", "JP",
           "DuPont, Merck and Korean makers, small at EUV", "2 to 3 years to qualify a resist at a node",
           "adequate", "warning", "Japan makes nearly all EUV resist."),
  exp="med", srcs=["env_resist"])
N("gases", "refine", "si", "Specialty gases", "Bulk and specialty gases",
  "Nitrogen, hydrogen, helium, NF3, WF6 and other gases piped into every fab.",
  "Industrial-gas majors run on long contracts; the helium shock is the live problem.",
  firms=[("linde", None, None), ("airliquide", None, None), ("apd", None, None)],
  inputs=[I("helium", p=0.5), I("tungsten", p=0.4)], exp="low", srcs=["fortune_he"])
N("chems", "refine", "si", "Process chemicals", "Process chemicals, slurries and filters",
  "Ultra-pure acids, solvents, CMP slurries and filtration used between every process step.",
  "Several suppliers per material; qualification, not capacity, is the usual constraint.",
  firms=[("entg", None, "Filters, slurries"), ("fujifilm", None, "Slurries, chemicals")],
  inputs=[M("ree")], exp="med", srcs=[])
N("abf", "refine", "si", "ABF film", "ABF build-up film",
  "Ajinomoto Build-up Film: the insulating layers inside every high-end chip substrate.",
  "Ajinomoto holds 95% of CPU/GPU-grade ABF. Qualifying a new supplier takes 18 to 24 months.",
  firms=[("ajinomoto", "95%", "CPU/GPU-grade ABF")],
  choke=CH("Ajinomoto", "95%", "Japan", "JP", "Sekisui and others at small scale", "18 to 24 months to qualify a new source",
           "tight", "serious", "One food company makes the film inside nearly every AI chip package."),
  exp="med", srcs=["wing_abf"])
N("glasscloth", "refine", "si", "Glass-fiber cloth", "Low-expansion glass-fiber cloth (T-glass)",
  "Low-expansion glass cloth (T-glass, NE-glass) that keeps large substrates and high-speed boards from warping.",
  "Nittobo holds about 90% of T-glass and 60 to 70% of NE-glass; relief is not expected before mid-2027. ASPEED is moving boards to E-glass because substrates are short.",
  firms=[("nittobo", "~90% of T-glass", "60-70% of NE-glass"), ("grace", None, "Qualifying")],
  choke=CH("Nittobo", "~90% of T-glass", "Japan", "JP", "Grace Fabric and others qualifying; E-glass for less demanding parts",
           "Relief not before mid-2027", "short", "critical", "Short now, one maker, no quick fix."),
  exp="high", srcs=["tf_glass", "taipei_aspeed"])
N("goes", "refine", "pw", "Electrical steel", "Grain-oriented electrical steel (GOES)",
  "Specialty steel for transformer cores.",
  "Cleveland-Cliffs is the only US producer meeting DoD and DOE specs for domain-refined GOES; the Defense Logistics Agency signed a $400M sole-source deal in July 2026.",
  firms=[("clf", "Sole qualified US source", "Butler, PA")],
  choke=CH("Cleveland-Cliffs (US)", "Sole US source (DR-GOES)", "US", "US", "Imported steel from Asia and Europe",
           "Years for a new mill", "tight", "serious", "One US mill for the steel inside every transformer core."),
  exp="low", srcs=["hoodline_goes", "pv_transf"])
N("enrich", "refine", "pw", "Uranium enrichment", "Uranium enrichment",
  "Centrifuge plants that turn uranium into reactor fuel.",
  "Russia holds about 44% of world enrichment capacity. US imports of Russian enriched uranium are banned from 2028; waivers run through 2027.",
  firms=[("rosatom", "~44% of capacity", "Russia"), ("urenco", None, "UK/NL/DE/US"), ("orano", None, "France"), ("leu", None, "US, HALEU")],
  inputs=[I("uranium")],
  choke=CH("Rosatom (Russia)", "~44% of capacity", "Russia", "RU", "Urenco, Orano and Centrus expansions",
           "5+ years for new centrifuge halls", "tight", "warning", "The nuclear option for AI runs through Russian enrichment until 2028."),
  exp="low", srcs=["spg_uranium"])

# ---- tier 2: engineered materials
N("wafers", "mat", "si", "300mm wafers", "300mm silicon wafers",
  "Polished single-crystal silicon wafers, the starting canvas for every chip.",
  "Five firms make about 91% (2025): Shin-Etsu 28%, SUMCO 25%, GlobalWafers 15%, Siltronic 12%, SK Siltron 11%.",
  firms=[("shinetsu", "28%", None), ("sumco", "25%", None), ("gwafers", "15%", None), ("siltronic", "12%", None), ("sksiltron", "11%", None)],
  inputs=[I("poly"), I("quartz", p=0.5)],
  choke=CH("Shin-Etsu and SUMCO (Japan) plus three others", "Top two 53%", "Japan", "JP",
           "GlobalWafers, Siltronic, SK Siltron", "2 to 3 years per crystal-growing plant", "adequate", "warning",
           "Two Japanese firms make over half of all wafers."),
  exp="med", srcs=["fx_wafer"])
N("inp", "mat", "si", "InP wafers", "Indium phosphide (InP) wafers",
  "Substrates on which lasers and photodetectors for optical links are grown.",
  "Lumentum's CEO says the InP supply gap now exceeds DRAM's and NAND's. China makes about 70% of refined indium and has tightened controls on InP.",
  firms=[("axt", None, "Wafers made in China"), ("sumitomo", None, "Japan"), ("jx", None, "Japan")],
  inputs=[I("indium", p=0.8)],
  choke=CH("AXT (China-made), Sumitomo Electric, JX Advanced Metals", "Three main makers", "China and Japan", "CN",
           "Few; 6-inch InP capacity is being expanded", "Shortage expected to last beyond 2027", "short", "critical",
           "The scarcest input in AI networking."),
  exp="high", srcs=["tf_inp"])
N("substrate", "mat", "si", "ABF substrates", "FC-BGA (ABF) package substrates",
  "The multilayer boards a GPU, CPU or switch chip is mounted on.",
  "Ibiden about 35%, Shinko 18%, Unimicron 14%, AT&S 10%, Nan Ya PCB 5%. Ibiden is spending ¥500B through FY2028 for 2.5x capacity, in quake-prone Gifu.",
  firms=[("ibiden", "~35%", "Gifu, Japan"), ("shinko", "~18%", "Nagano, Japan"), ("unimicron", "~14%", "Taiwan"), ("ats", "~10%", "Austria, Malaysia"), ("nanyapcb", "~5%", "Taiwan")],
  inputs=[I("abf"), I("glasscloth"), I("copper", p=0.3)],
  choke=CH("Ibiden and Shinko (Japan)", "Top two ~53%", "Japan", "JP",
           "Unimicron, AT&S, Nan Ya; glass-core substrates later this decade", "2 to 3 years for new lines", "short", "serious",
           "Short now, and the leader sits in an earthquake zone."),
  exp="high", srcs=["wing_abf", "taipei_aspeed"])
N("pcb", "mat", "si", "Boards & laminates", "High-speed boards and laminates",
  "Low-loss copper-clad laminates and multilayer boards for server trays and switches.",
  "They use the same scarce low-expansion glass cloth as substrates, so the T-glass squeeze hits boards too.",
  firms=[("emc", None, "Laminates"), ("tuc", None, "Laminates")],
  inputs=[I("glasscloth", p=0.8), I("copper", p=0.3)], exp="high", srcs=["tf_glass"])

# ---- tier 3: tools & design (+ power equipment)
N("litho", "tools", "si", "EUV lithography", "Lithography (EUV and DUV)",
  "Scanners that print circuit patterns: EUV for the finest layers, DUV for the rest.",
  "ASML is the only EUV supplier: 2026 revenue guided at €43-45B, about 65 low-NA EUV tools, EUV capacity +30% in 2027, China about 20% of sales. Zeiss makes the optics and Trumpf the drive lasers.",
  firms=[("asml", "100% of EUV", "Veldhoven"), ("zeiss", None, "EUV optics"), ("trumpf", None, "EUV drive lasers")],
  choke=CH("ASML", "100% of EUV", "Netherlands", "NL", "None for EUV; DUV multi-patterning (as SMIC does) at higher cost and lower yield",
           "EUV capacity +30% in 2027", "adequate", "warning", "A true monopoly, currently delivering."),
  exp="med", srcs=["asml_q2"])
N("depetch", "tools", "si", "Deposition & etch", "Deposition, etch and clean tools",
  "Tools that lay down and carve away the layers of a chip.",
  "Applied Materials, Lam Research, Tokyo Electron and ASM International dominate. Etch chambers use yttria coatings, and yttrium is one of the rare earths China controls.",
  firms=[("amat", None, None), ("lrcx", None, None), ("tel", None, None), ("asmi", None, None)],
  inputs=[M("ree")], exp="med", srcs=["pillsbury"])
N("metrology", "tools", "si", "Inspection", "Inspection and metrology",
  "Tools that find defects and measure layers; EUV masks need actinic (EUV-light) inspection.",
  "Lasertec is the only supplier of actinic EUV mask inspection; KLA leads wafer inspection.",
  firms=[("klac", None, "Wafer inspection"), ("lasertec", "Sole supplier", "Actinic EUV mask inspection")],
  choke=CH("Lasertec", "Sole supplier (actinic mask inspection)", "Japan", "JP", "Partial alternatives with other inspection methods",
           "Months to a year per tool", "adequate", "warning", "Every EUV mask passes through one Japanese firm's tools."),
  exp="med", srcs=["env_test"])
N("eda", "tools", "si", "Design software & IP", "Chip-design software (EDA) and IP",
  "Software and licensed building blocks used to design every chip.",
  "Synopsys and Cadence dominate EDA; Arm licenses the CPU cores in Nvidia's Grace and Vera and in hyperscaler CPUs.",
  firms=[("snps", None, None), ("cdns", None, None), ("siemens", None, None), ("arm", None, "CPU IP")], exp="med", srcs=[])
N("bonders", "tools", "si", "HBM bonders", "HBM stacking bonders",
  "Thermo-compression (TC) and hybrid bonders that stack DRAM dies into HBM.",
  "Hanmi holds 71.2% of TC bonders for AI chips (2025 sales ₩576.7B); BESI leads hybrid bonding for later HBM generations.",
  firms=[("hanmi", "71.2%", "TC bonders"), ("hanwha", None, "TC bonders"), ("asmpt", None, "TC bonders"), ("besi", None, "Hybrid bonding")],
  choke=CH("Hanmi Semiconductor", "71.2%", "Korea", "KR", "Hanwha Semitech, ASMPT; hybrid bonding (BESI) later",
           "Months to a year", "tight", "serious", "One Korean firm builds most of the machines that stack HBM."),
  exp="high", srcs=["asiae_hanmi"])
N("testeq", "tools", "si", "Test equipment", "Automated test equipment (ATE)",
  "Testers that check every die and memory stack.",
  "Advantest controls about 55% of ATE; Teradyne most of the rest.",
  firms=[("advantest", "~55%", None), ("ter", None, None)],
  choke=CH("Advantest", "~55%", "Japan", "JP", "Teradyne", "Months", "tight", "warning", "AI chips need far more test time per unit."),
  exp="high", srcs=["env_test"])
N("dicing", "tools", "si", "Dicing & grinding", "Dicing and grinding",
  "Saws, lasers and grinders that thin wafers and cut them into dies, critical for thin HBM dies.",
  "Disco dominates this niche.",
  firms=[("disco", "Dominant", None), ("accretech", None, None)],
  choke=CH("Disco", "Dominant", "Japan", "JP", "Tokyo Seimitsu (Accretech)", "Months", "adequate", "warning", "Thinner HBM dies mean more grinding per stack."),
  exp="med", srcs=["env_test"])
N("turbines", "tools", "pw", "Gas turbines", "Heavy-duty gas turbines",
  "Large turbines for utility plants and on-site generation at AI campuses.",
  "GE Vernova's backlog is 116 GW plus slot reservations, with 2031 slots on sale; Siemens Energy 69 GW; Mitsubishi Heavy 35 GW. World capacity is about 60 to 70 GW a year against about 110 GW of orders. Combined-cycle plants cost $2,157/kW in 2025, up from under $1,500 in 2023.",
  firms=[("gev", "116 GW backlog", "Capacity 20 to 30 GW/yr"), ("enr", "69 GW backlog", "3+ yr lead times"), ("mhi", "35 GW backlog", "Delivering 2028-30")],
  choke=CH("GE Vernova, Siemens Energy, Mitsubishi Heavy", "Three firms", "US, Germany, Japan", None,
           "Aeroderivatives, reciprocating engines, fuel cells: smaller and costlier", "3+ years; slots sold into 2030-31",
           "short", "critical", "Orders run far ahead of the world's turbine factories."),
  exp="med", srcs=["gev_backlog", "oilprice_turb"])
N("transformers", "tools", "pw", "Transformers", "Large power transformers",
  "Grid, substation and generator step-up transformers that connect campuses and plants to the grid.",
  "Lead times run up to four years. Generator step-up demand is up 274% and substation demand 116% since 2019; prices are up about 80%. Electrical steel and copper are constrained.",
  firms=[("hitachi", None, "Hitachi Energy"), ("enr", None, None), ("hdhe", None, None), ("etn", None, "Distribution"), ("su", None, "Distribution")],
  inputs=[I("goes", p=0.8), I("copper", p=0.5)],
  choke=CH("Hitachi Energy, Siemens Energy, HD Hyundai Electric and a few others", "Few large-unit makers", "Global", None,
           "Refurbished units, mobile substations, on-site generation", "Up to 4 years", "short", "critical",
           "The slowest item to order for any new campus."),
  exp="med", srcs=["pv_transf"])

# ---- tier 4: wafer fabs & generation
FAB_IN = [I("wafers"), I("resist"), I("gases", p=0.2), I("chems", p=0.5), I("litho", p=0.25), I("depetch", p=0.25), I("metrology", p=0.25)]
N("foundry", "fab", "si", "Leading-edge foundry", "Leading-edge logic foundry (3nm, 2nm)",
  "Fabs that make the compute dies inside GPUs and custom accelerators.",
  "TSMC makes the compute dies for Nvidia, AMD, Google's TPU, AWS Trainium and Broadcom's custom chips. 3nm is above 180k wafers a month heading to 210k; 2nm goes from 90k to 110k by mid-2027. Its Arizona plan totals $265B.",
  firms=[("tsmc", "Nearly all AI accelerators", "Taiwan; Arizona ramping"), ("samsung", None, "Samsung Foundry"), ("intc", None, "Intel 18A/14A")],
  inputs=FAB_IN,
  choke=CH("TSMC", "Nearly all AI accelerators", "Taiwan", "TW", "Samsung Foundry, Intel 18A/14A: few AI wins so far",
           "3 to 4 years per fab", "tight", "serious", "The whole AI chip market runs through one company's fabs in Taiwan."),
  exp="high", srcs=["tf_tsmc_cap", "th_tsmc_az"])
N("dram", "fab", "si", "DRAM fabs", "DRAM fabs",
  "Memory fabs making DRAM wafers, for HBM stacks and for server DDR5.",
  "Three makers (Samsung, SK hynix, Micron) plus China's CXMT. DRAM contract prices rose 13 to 18% quarter on quarter in Q3 2026 as HBM soaks up wafers.",
  firms=[("samsung", None, None), ("skhynix", None, None), ("mu", None, None), ("cxmt", None, "China")],
  inputs=FAB_IN,
  choke=CH("Samsung, SK hynix, Micron", "Three firms", "Korea", "KR", "CXMT (China), under US restrictions",
           "2 to 3 years per fab", "short", "serious", "Prices are rising every quarter."),
  exp="high", srcs=["tf_mem"])
N("nand", "fab", "si", "NAND flash", "NAND flash fabs",
  "Flash-memory fabs for the SSDs that hold training data and checkpoints.",
  "NAND contract prices rose 10 to 15% quarter on quarter in Q3 2026.",
  firms=[("samsung", None, None), ("skhynix", None, None), ("kioxia", None, None), ("sndk", None, None), ("mu", None, None)],
  inputs=[I("wafers"), I("resist"), I("gases", p=0.2), I("chems", p=0.5), I("litho", p=0.15), I("depetch", p=0.25)],
  exp="med", srcs=["tf_mem"])
N("china_fab", "fab", "si", "China's fabs", "China's domestic fabs (SMIC, CXMT)",
  "China's logic (SMIC 7nm and 5nm-class on DUV) and memory (CXMT) fabs, cut off from EUV.",
  "They supply Huawei's Ascend and Cambricon chips on tools bought before controls tightened; ASML still earns about 20% of sales in China.",
  firms=[("smic", None, "Logic"), ("cxmt", None, "DRAM and HBM")],
  inputs=[I("wafers"), I("resist"), I("gases", p=0.2), I("chems", p=0.5), I("litho", p=0.25), I("depetch", p=0.25)],
  exp="med", srcs=["asml_q2"])
N("gaspower", "fab", "pw", "Gas-fired plants", "Gas-fired power plants",
  "Utility and on-site combined-cycle and simple-cycle plants.",
  "Built from turbines that are sold out into 2030-31; combined-cycle cost $2,157/kW in 2025.",
  firms=[("vst", None, None), ("ceg", None, None)],
  inputs=[I("turbines"), I("natgas")], exp="med", srcs=["oilprice_turb"])
N("nuclear", "fab", "pw", "Nuclear power", "Nuclear power",
  "Existing reactors under long contracts to AI firms, restarts, uprates and planned small reactors.",
  "Hyperscalers have signed restarts and small-reactor deals (see the Investment Atlas); fuel depends on enrichment, where Russia holds about 44%.",
  firms=[("ceg", None, None), ("vst", None, None), ("tln", None, None), ("oklo", None, None), ("kairos", None, None)],
  inputs=[I("enrich", p=0.5)], exp="med", srcs=["spg_uranium", "atlas"])

# ---- tier 5: package, stack & connect
N("hbm", "pkg", "si", "HBM stacks", "High-bandwidth memory (HBM)",
  "Stacks of 8 to 16 DRAM dies joined by through-silicon vias, placed beside each GPU.",
  "SK hynix has 50% of 2026 HBM bits (down from 59% in 2025), Samsung 28% (up from 20%), Micron the rest. Samsung leads HBM4 supply for Nvidia's Vera Rubin.",
  firms=[("skhynix", "50%", "2026 bits"), ("samsung", "28%", "Leads HBM4 for Rubin"), ("mu", "~22%", "The rest")],
  inputs=[I("dram"), I("bonders", p=0.5), I("testeq", p=0.3), I("dicing", p=0.3)],
  choke=CH("SK hynix, Samsung, Micron", "SK hynix 50%", "Korea", "KR", "None outside the three (CXMT in China)",
           "1 to 2 years per expansion", "short", "serious", "Three suppliers, sold out, prices rising."),
  exp="high", srcs=["tf_hbm4"])
N("cowos", "pkg", "si", "CoWoS packaging", "CoWoS advanced packaging",
  "TSMC's 2.5D packaging that joins compute dies and HBM on a silicon interposer.",
  "About 130k wafers a month by end-2026 and about 260k by end-2028. Every Nvidia data-center GPU and most custom accelerators go through it.",
  firms=[("tsmc", "Dominant", "Taiwan"), ("ase", None, "Overflow"), ("amkor", None, "Overflow, Arizona plans"), ("intc", None, "EMIB alternative")],
  inputs=[I("foundry"), I("hbm"), I("substrate"), I("testeq", p=0.3), I("dicing", p=0.3)],
  choke=CH("TSMC", "Dominant", "Taiwan", "TW", "ASE/SPIL, Amkor, Intel EMIB for part of demand",
           "About two years to double", "short", "critical", "The narrowest point of the chip chain."),
  exp="high", srcs=["tf_tsmc_cap"])
N("osat", "pkg", "si", "Assembly & test", "Outsourced assembly and test (OSAT)",
  "Packaging and test for CPUs, switch chips, NICs and optical DSPs.",
  "ASE (with SPIL), Amkor and JCET lead; much of the capacity is in Taiwan.",
  firms=[("ase", None, None), ("amkor", None, None), ("jcet", None, None)],
  inputs=[I("foundry"), I("substrate"), I("testeq", p=0.3)], exp="med", srcs=[])
N("grid", "pkg", "pw", "Grid & interconnection", "Grid capacity and interconnection",
  "Transmission, substations and the interconnection queue that let a campus draw power.",
  "PJM's July 2026 capacity auction cleared $16.4B, with about $6.3B attributed to data centers, and missed its supply target.",
  firms=[("pjm", None, "Mid-Atlantic grid operator")],
  inputs=[I("transformers"), ("gaspower", "gen", 0.4, 1.0), ("nuclear", "gen", 0.2, 1.0)],
  choke=CH("Regional grid operators and utilities", "Queue-limited", "US", "US", "Behind-the-meter generation",
           "Years", "tight", "serious", "Power prices and queues decide where campuses can go."),
  exp="med", srcs=["bgov_pjm"])
N("onsite", "pkg", "pw", "On-site power", "On-site generation",
  "Generation at the campus: aeroderivative turbines, reciprocating engines, fuel cells, batteries.",
  "Used to skip grid queues, but it draws on the same scarce turbines and on gas.",
  firms=[("be", None, "Fuel cells"), ("cat", None, "Engines and gensets"), ("gev", None, "Aeroderivatives")],
  inputs=[I("natgas"), ("turbines", "equip", 0.5, 1.0)], exp="high", srcs=["oilprice_turb"])

# ---- tier 6: chips, optics & plant gear
N("gpu", "chips", "si", "Merchant GPUs", "Merchant AI accelerators (GPUs)",
  "General-purpose AI accelerators sold on the open market.",
  "Nvidia holds about 70% of the AI chip market; AMD is the second source.",
  firms=[("nvda", "~70% of AI chips", None), ("amd", None, "Second source"), ("intc", None, None), ("cbrs", None, "Wafer-scale")],
  inputs=[I("cowos"), I("eda", p=0.3)],
  choke=CH("Nvidia", "~70% of AI chips", "US (made in Taiwan)", "US", "AMD, custom ASICs",
           "Set by CoWoS and HBM supply", "tight", "warning", "Concentrated, but its limits sit upstream."),
  exp="high", srcs=["th_asic"])
N("asic", "chips", "si", "Custom AI chips", "Custom AI accelerators (ASICs)",
  "Chips designed for one buyer: Google TPU, AWS Trainium, Meta MTIA, OpenAI's Broadcom chip.",
  "Broadcom and Marvell handle about 95% of ASIC co-design; ASIC-based servers are about 27.8% of 2026 AI server shipments.",
  firms=[("avgo", None, "Co-design leader"), ("mrvl", None, "Co-design"), ("alchip", None, None), ("mtk", None, None), ("guc", None, None)],
  inputs=[I("cowos"), I("eda", p=0.3)],
  choke=CH("Broadcom and Marvell", "~95% of co-design", "US", "US", "Alchip, GUC, MediaTek",
           "2 to 3 years per chip", "adequate", "warning", "Two firms design the chips meant to replace Nvidia's."),
  exp="high", srcs=["th_asic"])
N("cpu", "chips", "si", "CPUs", "Server CPUs",
  "Host processors: Nvidia Grace and Vera (Arm), AMD EPYC, Intel Xeon, AWS Graviton, Google Axion.",
  "Several suppliers; packaging and substrates are the shared constraint.",
  firms=[("nvda", None, None), ("amd", None, None), ("intc", None, None), ("arm", None, "IP")],
  inputs=[I("osat"), I("eda", p=0.3)], exp="med", srcs=[])
N("netsi", "chips", "si", "Network silicon", "Network silicon",
  "Switch chips, NICs, retimers and optical DSPs that connect GPUs.",
  "Broadcom and Nvidia lead switch silicon; Marvell makes optical DSPs; Astera Labs and Credo make connectivity chips.",
  firms=[("avgo", None, None), ("nvda", None, None), ("mrvl", None, None), ("alab", None, None), ("crdo", None, None)],
  inputs=[I("osat"), I("eda", p=0.3)], exp="high", srcs=[])
N("bmc", "chips", "si", "Server control chips", "Baseboard management controllers (BMCs)",
  "Small chips that let operators manage each server remotely.",
  "ASPEED is the largest BMC supplier and is moving boards to E-glass because substrates are short.",
  firms=[("aspeed", "Largest supplier", None), ("nuvoton", None, None)],
  inputs=[I("osat")],
  choke=CH("ASPEED", "Largest supplier", "Taiwan", "TW", "Nuvoton and others", "Months", "tight", "warning",
           "A small Taiwanese chip sits in almost every server."),
  exp="high", srcs=["taipei_aspeed"])
N("lasers", "chips", "si", "Lasers", "Lasers and photodetectors",
  "InP laser chips (EMLs, CW lasers) and photodetectors inside optical transceivers.",
  "The InP laser gap is worse than DRAM's, per Lumentum's CEO. Nvidia put $2B each into Lumentum and Coherent in March 2026.",
  firms=[("lite", None, "EMLs"), ("cohr", None, "InP lasers"), ("avgo", None, "EMLs"), ("sumitomo", None, None)],
  inputs=[I("inp"), I("gallium", p=0.4)],
  choke=CH("Lumentum, Coherent, Broadcom and Japanese makers", "A few makers", "US and Japan", "US",
           "Silicon photonics, which still needs a laser source", "Shortage beyond 2027", "short", "critical",
           "Nvidia is financing its own suppliers to get lasers."),
  exp="high", srcs=["tf_inp", "dcd_lumentum"])
N("optics", "chips", "si", "Optical modules", "Optical transceivers",
  "800G and 1.6T pluggable modules that turn electrical signals into light between racks.",
  "Innolight (#1, $5.3B 2025 revenue) and Eoptolink (#2, $3.5B) are both Chinese. The market grew about 58% in 2025.",
  firms=[("innolight", "#1 ($5.3B, 2025)", None), ("eoptolink", "#2 ($3.5B, 2025)", None), ("cohr", None, None), ("fn", None, "Contract manufacturer")],
  inputs=[I("lasers"), I("netsi", p=0.5), I("pcb", p=0.5)],
  choke=CH("Innolight and Eoptolink (China)", "#1 and #2", "China", "CN", "Coherent, Fabrinet-built modules; co-packaged optics later",
           "Months (lasers are the limit)", "tight", "serious", "US AI clusters rely on Chinese optics makers."),
  exp="high", srcs=["lc_optics"])
N("fiber", "chips", "si", "Fiber & cabling", "Fiber, connectors and cables",
  "Optical fiber, connectors and copper cables inside and between halls.",
  "Germanium, one of the minerals China controls, dopes fiber cores.",
  firms=[("glw", None, None), ("fujikura", None, None), ("sumitomo", None, None), ("aph", None, "Copper cables"), ("prysmian", None, None)],
  inputs=[I("gallium", p=0.3), I("copper", p=0.3)], exp="med", srcs=["mt_china"])
N("china_chips", "chips", "si", "China's AI chips", "China's AI chips",
  "Huawei Ascend, Cambricon and others built on SMIC processes.",
  "Shut out of Nvidia's top parts and TSMC's leading nodes; Cambricon's first-half revenue rose 108%.",
  firms=[("huawei", None, None), ("cambricon", None, None)],
  inputs=[I("china_fab")], exp="high", srcs=["sa_cambricon"])
N("electrical", "chips", "pw", "Switchgear & UPS", "Switchgear, UPS and backup power",
  "Medium-voltage switchgear, UPS, busways and backup generators inside each campus.",
  "The same copper and steel constraints as transformers; analysts expect Vertiv's revenue to grow 37% in 2026.",
  firms=[("etn", None, None), ("su", None, None), ("vrt", None, None), ("cat", None, "Gensets")],
  inputs=[I("copper", p=0.3)], exp="high", srcs=["pv_transf", "sa_all"])
N("cooling", "chips", "pw", "Liquid cooling", "Liquid cooling and thermal",
  "Coolant distribution units, cold plates and chillers for racks above 100 kW.",
  "NVL72-class racks need liquid cooling, and rack shipments grow more than 50% in 2027.",
  firms=[("vrt", None, None), ("su", None, None), ("delta", None, None)],
  inputs=[I("copper", p=0.2), M("ree")], exp="high", srcs=["tf_racks"])

# ---- tier 7: systems & build
N("servers", "sys", "si", "AI servers & racks", "AI servers and racks",
  "Integrated GPU or ASIC servers and NVL72-class racks built by ODMs and OEMs.",
  "Rack output will exceed $710B in 2027 with shipments up more than 50%. Foxconn built about 44% of GB-series racks in April 2026; Quanta and Wistron followed.",
  firms=[("honhai", "~44% of GB racks (Apr 2026)", None), ("quanta", "~25%", None), ("wistron", None, None), ("wiwynn", None, None),
         ("dell", None, None), ("smci", None, None), ("hpe", None, None), ("cls", None, None)],
  inputs=[("gpu", "accel", 0.72, 1.0), ("asic", "accel", 0.28, 1.0), I("cpu"), I("dram", p=0.7), I("pcb"), I("bmc"), I("netsi", p=0.8)],
  choke=CH("Foxconn, Quanta, Wistron", "Foxconn ~44%", "Taiwanese firms; plants in Mexico, US, Taiwan", "TW",
           "Dell, Supermicro, HPE, Celestica", "Months", "adequate", "warning", "Assembly is concentrated but can move."),
  exp="high", srcs=["technews_odm", "tf_racks"])
N("netsys", "sys", "si", "Cluster networks", "Cluster networks",
  "Switches, optics and cabling that tie thousands of GPUs into one machine.",
  "Every GPU needs several optical links; optics are now the tightest part of the network bill.",
  firms=[("anet", None, None), ("csco", None, None), ("nvda", None, "InfiniBand and Spectrum-X"), ("cls", None, "White-box switches")],
  inputs=[I("netsi"), I("optics"), I("fiber"), I("pcb", p=0.5)], exp="high", srcs=["lc_optics"])
N("storage", "sys", "si", "Storage", "Storage systems",
  "SSDs and hard drives for training data and checkpoints.",
  "Flash prices are rising with DRAM.",
  firms=[("sndk", None, None), ("stx", None, None), ("samsung", None, None)],
  inputs=[("nand", "flash", 0.7, 1.0)], exp="med", srcs=["tf_mem"])
N("build", "sys", "pw", "Build & shells", "Construction, electrical contracting and shells",
  "Construction, grid and electrical contractors, and colocation shells.",
  "Skilled electricians and grid crews are a practical limit on how fast campuses get built.",
  firms=[("pwr", None, "Grid and electrical contractor"), ("eqix", None, "Colocation")], exp="high", srcs=[])

# ---- tier 8: campus & capital
N("campus", "campus", "mx", "AI campuses", "AI data-center campuses",
  "Where chips, networks, power and cooling meet: gigawatt-scale sites.",
  "A gigawatt costs about $35B by Bernstein's estimate ($50-60B by Nvidia's): about 39% GPUs, 30% mechanical and electrical, 13% networking, 4% thermal. Epoch puts upfront capex near $38B per GW.",
  firms=[], exp="high", srcs=["bern_gw", "epoch_gw"],
  inputs=[I("servers"), I("netsys"), I("storage", p=0.3), I("build"), I("electrical"), I("cooling"),
          ("grid", "power", 0.65, 1.0), ("onsite", "power", 0.35, 1.0)])
N("capital", "campus", "mx", "Capital & financing", "Capital: equity, debt and vendor financing",
  "Money that funds labs, neoclouds and campuses: equity rounds, bonds, private credit, and suppliers financing their customers.",
  "Nvidia has become a major financier of its own customers (about $99B, per the Investment Atlas). S&P cut Oracle to BBB- with $117B of bonds outstanding; CoreWeave carries $35B of debt.",
  firms=[("nvda", None, "Vendor financing"), ("softbank", None, "OpenAI backer"), ("orcl", None, "Bond-funded build-out")],
  exp="high", srcs=["atlas", "tnw_oracle", "webull_crwv"])

# ---- tier 9: compute sellers
N("hyper", "ops", "mx", "Hyperscalers", "Hyperscale clouds",
  "Microsoft, Alphabet, Amazon, Meta and Oracle: the biggest buyers and builders.",
  "2026 capex plans: Amazon $220B, Alphabet $200B, Microsoft $190B, Meta $137.5B, Oracle $92.5B (Investment Atlas).",
  firms=[("msft", None, None), ("googl", None, None), ("amzn", None, None), ("meta", None, None), ("orcl", None, None)],
  inputs=[I("campus")], exp="high", srcs=["atlas"])
N("neo", "ops", "mx", "Neoclouds", "Neoclouds",
  "GPU-rental specialists (CoreWeave, Nebius, Crusoe) and SpaceX's xAI.",
  "Debt-funded: CoreWeave's quarterly interest reached $640M, with $4.4B of principal due by end-2026 and $6.2B in 2027.",
  firms=[("crwv", None, None), ("nbis", None, None), ("crusoe", None, None), ("spcx", None, "xAI")],
  inputs=[I("campus"), I("capital", p=0.8)], exp="high", srcs=["webull_crwv"])
N("sovereign", "ops", "mx", "Gulf & sovereign AI", "Gulf and sovereign AI",
  "State-backed builds: Stargate UAE (G42), HUMAIN in Saudi Arabia, and others.",
  "Inside the Iran war's strike zone: drones knocked out two of three AWS availability zones in the UAE on 1 Mar 2026; Iran's IRGC threatened Stargate UAE on 3 Apr; war-risk insurance for Gulf data centers is up about 1,900%.",
  firms=[("g42", None, None), ("humain", None, None)],
  inputs=[I("campus"), I("capital", p=0.5)], exp="high", srcs=["row_aws", "tnw_stargate", "fp_gulf"])
N("china_cloud", "ops", "mx", "China's AI clouds", "China's AI clouds",
  "Alibaba, ByteDance, Tencent and Baidu, building on domestic chips and whatever Nvidia parts export rules allow.",
  "A parallel chain that shares minerals, DUV tools and optics makers with everyone else.",
  firms=[("alibaba", None, None), ("bytedance", None, None), ("tencent", None, None), ("baidu", None, None)],
  inputs=[I("china_chips")], exp="high", srcs=[])

# ---- tier 10: models & demand
N("labs", "demand", "mx", "Frontier labs", "Frontier AI labs",
  "OpenAI, Anthropic, Google DeepMind, Meta and xAI: the model builders.",
  "OpenAI and Anthropic alone have signed about $1.14T of compute commitments against about $135B of combined annual revenue (Investment Atlas).",
  firms=[("openai", None, None), ("anthropic", None, None), ("googl", None, "DeepMind"), ("meta", None, None), ("spcx", None, "xAI")],
  inputs=[("hyper", "compute", 0.7, 1.0), ("neo", "compute", 0.2, 1.0), ("sovereign", "compute", 0.1, 1.0), I("capital", p=0.6)],
  exp="high", srcs=["atlas"])
N("users", "demand", "mx", "Users & businesses", "End demand: people and businesses paying for AI",
  "Consumers, developers and enterprises paying for AI products and API usage.",
  "This revenue has to pay back everything to its left; the Investment Atlas tests whether it can by 2030.",
  firms=[], inputs=[("labs", "ai", 0.6, 1.0), ("hyper", "ai", 0.4, 1.0)], exp="high", srcs=["atlas"])

# unmodeled share of a substitute group that is always available (e.g. other generation on the grid)
GROUP_OTHER = {("grid", "gen"): 0.4, ("onsite", "equip"): 0.5, ("storage", "flash"): 0.3}

# ---------------------------------------------------------------- key outputs shown in the stress test
OUTPUTS = [
    dict(id="accel", label="AI accelerators", mix=[("gpu", 0.72), ("asic", 0.28)]),
    dict(id="hbm", label="HBM memory", mix=[("hbm", 1.0)]),
    dict(id="optics", label="Optical links", mix=[("optics", 1.0)]),
    dict(id="servers", label="AI servers and racks", mix=[("servers", 1.0)]),
    dict(id="campus", label="New campus capacity", mix=[("campus", 1.0)]),
    dict(id="labs", label="Compute reaching labs", mix=[("labs", 1.0)]),
]

# ---------------------------------------------------------------- scenarios
# shocks: node -> (first 12 months, by year 3), as a share of planned supply lost at that node itself.
SCEN = []
def SC(**k):
    SCEN.append(k)

SC(id="taiwan", name="Taiwan blockade", status="tail", when="Any time; PLA drills rehearse it",
   trigger="China blockades Taiwan. PLA exercise 'Justice Mission 2025' (30 Dec 2025) simulated exactly this.",
   story="Leading-edge wafers, CoWoS packaging, much outsourced test and a share of substrates, DRAM and rack assembly stop leaving the island. TSMC Arizona, Samsung and Intel cover a sliver of compute dies; almost no advanced packaging exists elsewhere yet.",
   shocks={"foundry": (0.85, 0.7), "cowos": (0.9, 0.65), "osat": (0.4, 0.2), "substrate": (0.2, 0.1), "wafers": (0.1, 0.05),
           "dram": (0.15, 0.1), "hbm": (0.05, 0.0), "bmc": (0.3, 0.1), "servers": (0.3, 0.1), "pcb": (0.25, 0.1)},
   exposed=["tsmc", "nvda", "amd", "avgo", "mrvl", "aspeed", "unimicron", "honhai", "quanta", "ase", "mu"],
   winners=["samsung", "intc", "amkor", "smic"],
   recovery="Three years or more. New leading-edge fabs take 3 to 4 years; CoWoS outside Taiwan is a 2027-28 story at best.",
   cost="Bloomberg Economics: about 5% of world GDP for a blockade, $10T (10.2%) for a war.",
   watch=["PLA exercise tempo and any customs 'inspection' regime around Taiwan",
          "TSMC Arizona volume and Amkor's Arizona packaging timeline",
          "Section 232 chip tariff exemptions (25% tariff since 15 Jan 2026)"],
   srcs=["ij_taiwan", "samdesk_tw", "tf_tsmc_cap", "th_tsmc_az", "tr_232"])
SC(id="gulf", name="Gulf war drags on", status="live", when="Since 28 Feb 2026; no ceasefire as of 28 Sep",
   trigger="The US-Israel war with Iran continues. Ceasefires on 8 Apr and 12 Jun broke down; Hormuz oil flows were about 7.4M barrels a day in September against about 20M before the war.",
   story="Ras Laffan's helium (about a third of world supply) stays offline and Russia keeps helium export controls. Gulf AI campuses remain targets after drones hit AWS in the UAE and Bahrain, and insurance costs keep investors away.",
   shocks={"helium": (0.33, 0.25), "sovereign": (0.5, 0.35), "natgas": (0.03, 0.03), "capital": (0.05, 0.03)},
   exposed=["g42", "humain", "amzn", "msft", "orcl", "skhynix", "samsung", "linde"],
   winners=["linde", "apd", "airliquide"],
   recovery="Years for Ras Laffan's helium plant; Gulf AI build-outs slip until insurers return.",
   cost="Helium spot prices doubled; Gulf data-center war-risk insurance up about 1,900%.",
   watch=["Ras Laffan restart date and Hormuz traffic",
          "South Korean fabs' helium inventories (their six-month window closed in July)",
          "Any strike on Stargate UAE or Saudi HUMAIN sites"],
   srcs=["aj_hormuz", "wiki_ceasefire", "fortune_he", "iumi_he", "fool_he", "row_aws", "tnw_stargate", "fp_gulf"])
SC(id="minerals", name="China's minerals switch flips back", status="scheduled", when="Pauses end 10 Nov and 27 Nov 2026",
   trigger="China lets its suspensions lapse: the October 2025 controls return on 10 Nov and the US ban on gallium, germanium and antimony on 27 Nov 2026.",
   story="Gallium, germanium, indium, tungsten and rare earths go back behind licences. The hit lands hardest on optics: indium feeds the InP wafers under every laser, which are already the scarcest input in AI networking.",
   shocks={"gallium": (0.6, 0.3), "ree": (0.5, 0.3), "tungsten": (0.4, 0.2), "indium": (0.4, 0.2)},
   exposed=["cohr", "lite", "axt", "innolight", "eoptolink", "glw", "fujikura", "anet"],
   winners=["mp", "lynas", "sumitomo", "jx"],
   recovery="Two to three years to build recovery and separation capacity outside China.",
   cost="Price spikes for gallium, germanium, indium and dysprosium; licence delays of weeks to months.",
   watch=["MOFCOM notices before 10 Nov and 27 Nov 2026", "InP wafer lead times and laser allocations",
          "US-China trade talks and any extension"],
   srcs=["pillsbury", "skillings_re", "mt_china", "tf_inp"])
SC(id="power", name="Power can't keep up", status="live", when="Now through 2030",
   trigger="Turbines and transformers stay sold out and grid queues stay long.",
   story="Turbine makers can build about 60 to 70 GW a year against about 110 GW of orders; transformers take up to four years. Chips arrive before the power to run them, and campuses slip.",
   shocks={"turbines": (0.35, 0.25), "transformers": (0.3, 0.2), "grid": (0.2, 0.2), "electrical": (0.1, 0.05)},
   exposed=["crwv", "orcl", "spcx", "nbis", "vst", "ceg"],
   winners=["gev", "enr", "mhi", "hitachi", "hdhe", "be", "cat", "etn", "vrt", "pwr"],
   recovery="Turbine capacity reaches about 30 GW a year at GE Vernova by 2030; transformer plants open 2027-28.",
   cost="Combined-cycle plants at $2,157/kW (2025); transformer prices up about 80%; PJM capacity costs at record levels.",
   watch=["GE Vernova quarterly orders and slot reservations", "PJM's next capacity auction",
          "Transformer lead-time surveys"],
   srcs=["oilprice_turb", "gev_backlog", "pv_transf", "bgov_pjm"])
SC(id="inp", name="Laser shortage deepens", status="live", when="Now; relief after 2027",
   trigger="InP wafer and laser capacity keep lagging 1.6T optics demand.",
   story="Each new GPU needs several optical links; without lasers, clusters ship with fewer links or slip. Nvidia is already paying its suppliers to expand.",
   shocks={"inp": (0.25, 0.08), "lasers": (0.05, 0.0)},
   exposed=["innolight", "eoptolink", "fn", "anet", "nvda"],
   winners=["lite", "cohr", "axt"],
   recovery="6-inch InP capacity doubles by end-2027; shortage expected to last beyond 2027.",
   cost="Laser and transceiver prices stay high; co-packaged optics adoption speeds up.",
   watch=["Lumentum and Coherent capacity announcements", "1.6T module shipment guidance from Innolight and Eoptolink"],
   srcs=["tf_inp", "dcd_lumentum", "lc_optics"])
SC(id="hbm", name="HBM falls short", status="plausible", when="2026-27",
   trigger="HBM4 yields or qualification slip while GPU demand keeps rising.",
   story="HBM takes wafers from ordinary DRAM, so a shortfall squeezes both: fewer GPUs can be packaged and server memory gets pricier.",
   shocks={"hbm": (0.25, 0.08), "dram": (0.05, 0.0), "bonders": (0.1, 0.0)},
   exposed=["nvda", "amd", "avgo", "dell", "smci"],
   winners=["skhynix", "samsung", "mu", "hanmi"],
   recovery="One to two years per expansion; new fabs from SK hynix (Yongin, Indiana) and Micron (Idaho, New York) land 2027-30.",
   cost="DRAM contract prices already up 13-18% in Q3 2026.",
   watch=["Samsung HBM4 volumes for Vera Rubin", "Quarterly DRAM contract prices (TrendForce)"],
   srcs=["tf_hbm4", "tf_mem", "asiae_hanmi"])
SC(id="japan", name="Major earthquake in Japan", status="tail", when="Unpredictable",
   trigger="A large quake or tsunami hits the plants of Japan's materials and tool makers.",
   story="Japan is the quiet chokepoint: ABF film, T-glass cloth, the top two substrate makers, most EUV resist, half the wafers, mask inspection, test and dicing. Ibiden's plants sit in seismic Gifu.",
   shocks={"abf": (0.4, 0.1), "glasscloth": (0.5, 0.15), "substrate": (0.3, 0.1), "resist": (0.3, 0.05), "wafers": (0.2, 0.05),
           "testeq": (0.3, 0.05), "dicing": (0.3, 0.05), "metrology": (0.2, 0.05)},
   exposed=["ajinomoto", "nittobo", "ibiden", "tok", "shinetsu", "advantest", "disco", "lasertec", "nvda", "tsmc"],
   winners=["unimicron", "ats", "ter", "gwafers", "siltronic"],
   recovery="Months to a year for most plants; T-glass and ABF have no second source to lean on.",
   cost="The 2011 Tohoku quake showed how single-plant materials can stall chip output for months.",
   watch=["Nittobo T-glass capacity additions (relief not before mid-2027)", "Ibiden's ¥500B expansion",
          "Second-source ABF qualification"],
   srcs=["wing_abf", "tf_glass", "env_test", "env_resist", "fx_wafer"])
SC(id="euv", name="EUV supply stops", status="tail", when="Unlikely, not impossible",
   trigger="ASML, Zeiss or Trumpf is disrupted, or export policy halts EUV shipments and service.",
   story="Installed tools keep running, but no new EUV capacity arrives and servicing gets harder. The planned jump to 2nm (90k to 110k wafers a month) and new memory capacity stall.",
   shocks={"litho": (0.9, 1.0)}, shocks3_extra={"foundry": 0.35, "dram": 0.3},
   exposed=["asml", "tsmc", "samsung", "skhynix", "mu", "intc"],
   winners=[],
   recovery="No substitute. Years.",
   cost="ASML guided 2026 revenue at €43-45B; EUV capacity was due to grow 30% in 2027.",
   watch=["ASML order intake and EUV shipments", "Dutch and US export-licence changes"],
   srcs=["asml_q2", "tf_tsmc_cap"])
SC(id="finance", name="The money stops", status="plausible", when="If AI revenue disappoints",
   kind="demand",
   trigger="AI revenue grows slower than the commitments, credit tightens, and labs and neoclouds cannot raise money.",
   story="This breaks the chain from the other end: orders dry up instead of parts. OpenAI and Anthropic have signed about $1.14T of compute deals against about $135B of revenue; Oracle is one notch above junk; CoreWeave's interest bill is $640M a quarter. Suppliers that financed their customers, like Nvidia, take the hit twice.",
   cut=(0.25, 0.4),
   exposed=["orcl", "crwv", "nbis", "spcx", "nvda", "amd", "avgo", "softbank", "vrt", "gev", "skhynix", "mu"],
   winners=[],
   recovery="Two to three years of digestion; memory and chip prices would fall fast.",
   cost="In the Investment Atlas, OpenAI already needs revenue to grow about 34% a year just to break even on its commitments.",
   watch=["Oracle and CoreWeave credit spreads and refinancing", "Lab funding rounds and revenue run-rates",
          "Hyperscaler capex guidance each quarter"],
   srcs=["atlas", "tnw_oracle", "webull_crwv"])
SC(id="compound", name="Everything at once", status="tail", when="The worst case",
   kind="compound",
   trigger="A Taiwan blockade lands while the Gulf war continues, China's mineral pauses lapse, power stays short and credit dries up.",
   story="Supply collapses at the narrowest points and demand collapses behind it. The AI build-out stops for years, the $1.7T of 2024-26 capex has to be written down against far less revenue, and the payback math in the Investment Atlas fails for everyone except the cash-rich hyperscalers.",
   combine=["taiwan", "gulf", "minerals", "power"], extra={"capital": (0.5, 0.4)}, cut=(0.4, 0.5),
   exposed=["tsmc", "nvda", "orcl", "crwv", "skhynix", "asml", "innolight"],
   winners=[],
   recovery="Five years or more.",
   cost="Bloomberg Economics puts a Taiwan war at $10T, about 10% of world GDP.",
   watch=["All of the above"], srcs=["ij_taiwan", "atlas"])

# ---------------------------------------------------------------- map sites
SITES = []
def ST(id, node, name, who, lat, lon, note, status="normal", srcs=()):
    SITES.append(dict(id=id, node=node, name=name, who=who, lat=lat, lon=lon, note=note, status=status, src=list(srcs)))

ST("spruce", "quartz", "Spruce Pine quartz mines", "Sibelco, The Quartz Corp", 35.915, -82.065, "Virtually all semiconductor-grade high-purity quartz; shut by Hurricane Helene in Sep 2024, since restarted.", "normal", ["nbc_spruce"])
ST("bayanobo", "ree", "Bayan Obo rare-earth district", "China Northern Rare Earth", 41.78, 109.97, "China's main light rare-earth mining district.", "controlled", ["pillsbury"])
ST("ganzhou", "ree", "Ganzhou heavy rare earths and tungsten", "Chinese producers", 25.83, 114.93, "Heavy rare earths and tungsten under export control.", "controlled", ["pillsbury"])
ST("mtnpass", "ree", "Mountain Pass mine", "MP Materials", 35.48, -115.53, "US rare-earth mine and magnet push.", "normal", [])
ST("lynas", "ree", "Lynas processing (Kuantan)", "Lynas", 3.97, 103.43, "Largest rare-earth separation outside China's system.", "normal", [])
ST("gallium_cn", "gallium", "Alumina refineries (gallium)", "Chinese refiners", 36.8, 118.05, "China produces 94% of the world's gallium as an alumina by-product.", "controlled", ["mt_china"])
ST("indium_cn", "indium", "Zinc and indium refining", "Chinese refiners", 24.7, 108.0, "China refines about 70% of the world's indium.", "controlled", ["tf_inp"])
ST("raslaffan", "helium", "Ras Laffan helium and LNG", "QatarEnergy", 25.90, 51.55, "About a third of world helium; offline since Iranian strikes (force majeure 2 Mar 2026, heavy damage 19-20 Mar).", "offline", ["fortune_he", "iumi_he"])
ST("hormuz", "natgas", "Strait of Hormuz", "Shipping lane", 26.57, 56.25, "Oil flows about 7.4M bpd in September vs about 20M before the war; no ceasefire.", "disrupted", ["aj_hormuz"])
ST("escondida", "copper", "Escondida copper mine", "BHP", -24.27, -69.07, "Copper for power gear, cables and substrates.", "normal", [])
ST("grasberg", "copper", "Grasberg copper mine", "Freeport-McMoRan", -4.06, 137.12, "Copper for power gear, cables and substrates.", "normal", [])
ST("mcarthur", "uranium", "Saskatchewan uranium mines", "Cameco", 57.75, -105.05, "Uranium ore.", "normal", [])
ST("kazakh", "uranium", "Kazakh uranium fields", "Kazatomprom", 45.3, 67.5, "Uranium ore.", "normal", [])
ST("novouralsk", "enrich", "Ural enrichment plant", "Rosatom", 57.25, 60.08, "Russia holds about 44% of world enrichment capacity; US import ban from 2028.", "controlled", ["spg_uranium"])
ST("piketon", "enrich", "Piketon enrichment (HALEU)", "Centrus Energy", 39.01, -83.00, "US enrichment for advanced reactors.", "normal", [])
ST("eunice", "enrich", "Urenco USA enrichment", "Urenco", 32.44, -103.13, "US commercial enrichment plant.", "normal", [])
ST("burghausen", "poly", "Burghausen polysilicon and wafers", "Wacker, Siltronic", 48.17, 12.83, "Chip-grade polysilicon and 300mm wafers.", "normal", [])
ST("hemlock", "poly", "Hemlock polysilicon", "Hemlock Semiconductor", 43.41, -84.10, "US chip-grade polysilicon.", "normal", [])
ST("kawasaki", "abf", "ABF film plant (Kawasaki)", "Ajinomoto", 35.53, 139.72, "About 95% of CPU/GPU-grade ABF film.", "tight", ["wing_abf"])
ST("nittobo", "glasscloth", "Glass-fiber cloth plant (Fukushima)", "Nittobo", 37.76, 140.47, "About 90% of T-glass; relief not before mid-2027.", "short", ["tf_glass"])
ST("jsr", "resist", "Photoresist plant (Yokkaichi)", "JSR", 34.97, 136.62, "EUV photoresist.", "normal", ["env_resist"])
ST("tok", "resist", "Photoresist plants (Kanagawa)", "Tokyo Ohka Kogyo", 35.57, 139.66, "EUV photoresist.", "normal", ["env_resist"])
ST("butler", "goes", "Butler Works electrical steel", "Cleveland-Cliffs", 40.86, -79.90, "Only US producer meeting DoD/DOE specs for DR-GOES.", "tight", ["hoodline_goes"])
ST("shirakawa", "wafers", "Shirakawa wafer plant", "Shin-Etsu Handotai", 37.13, 140.21, "Shin-Etsu: 28% of 300mm wafers.", "normal", ["fx_wafer"])
ST("imari", "wafers", "Imari wafer plant", "SUMCO", 33.27, 129.87, "SUMCO: 25% of 300mm wafers.", "normal", ["fx_wafer"])
ST("sherman", "wafers", "Sherman 300mm wafer plant", "GlobalWafers", 33.64, -96.61, "GlobalWafers: 15% of 300mm wafers.", "normal", ["fx_wafer"])
ST("gumi", "wafers", "Gumi wafer plant", "SK Siltron", 36.12, 128.34, "SK Siltron: 11% of 300mm wafers.", "normal", ["fx_wafer"])
ST("tongmei", "inp", "InP wafer plant (Beijing)", "AXT / Tongmei", 39.73, 116.53, "InP substrates made in China.", "short", ["tf_inp"])
ST("itami", "inp", "InP wafers and lasers (Itami)", "Sumitomo Electric", 34.78, 135.40, "InP substrates.", "short", ["tf_inp"])
ST("ogaki", "substrate", "Ogaki substrate plants (Gifu)", "Ibiden", 35.36, 136.61, "About 35% of FC-BGA substrates; ¥500B expansion; seismic zone.", "short", ["wing_abf"])
ST("nagano", "substrate", "Substrate plants (Nagano)", "Shinko Electric", 36.65, 138.19, "About 18% of FC-BGA substrates.", "short", ["wing_abf"])
ST("taoyuan_sub", "substrate", "Substrate plants (Taoyuan)", "Unimicron", 24.99, 121.30, "About 14% of FC-BGA substrates.", "short", ["wing_abf"])
ST("kulim", "substrate", "Substrate plant (Kulim)", "AT&S", 5.42, 100.56, "AT&S: about 10% of FC-BGA substrates.", "short", ["wing_abf"])
ST("veldhoven", "litho", "Veldhoven EUV factory", "ASML", 51.41, 5.41, "The only EUV scanners in the world.", "normal", ["asml_q2"])
ST("oberkochen", "litho", "EUV optics (Oberkochen)", "Carl Zeiss SMT", 48.78, 10.10, "Mirrors and optics for every EUV scanner.", "normal", [])
ST("ditzingen", "litho", "EUV drive lasers (Ditzingen)", "Trumpf", 48.83, 9.07, "CO2 drive lasers for EUV light sources.", "normal", [])
ST("yokohama", "metrology", "Mask inspection (Yokohama)", "Lasertec", 35.52, 139.62, "Only supplier of actinic EUV mask inspection.", "normal", ["env_test"])
ST("gunma", "testeq", "Test-equipment plant (Gunma)", "Advantest", 36.39, 139.06, "About 55% of chip test equipment.", "tight", ["env_test"])
ST("kure", "dicing", "Dicing and grinding plants (Hiroshima)", "Disco", 34.25, 132.57, "Dominant in dicing and grinding.", "normal", ["env_test"])
ST("incheon", "bonders", "TC-bonder plant (Incheon)", "Hanmi Semiconductor", 37.47, 126.66, "71.2% of TC bonders for AI chips.", "tight", ["asiae_hanmi"])
ST("duiven", "bonders", "Hybrid bonders (Duiven)", "BE Semiconductor", 51.95, 6.02, "Hybrid bonding for future HBM.", "normal", [])
ST("siliconvalley", "depetch", "Deposition and etch (Silicon Valley)", "Applied Materials, Lam Research", 37.40, -121.95, "Two of the four big process-tool makers.", "normal", [])
ST("greenville", "turbines", "Gas-turbine plant (Greenville, SC)", "GE Vernova", 34.85, -82.40, "116 GW backlog plus reservations; 2031 slots on sale.", "short", ["gev_backlog"])
ST("berlin", "turbines", "Gas-turbine plant (Berlin)", "Siemens Energy", 52.53, 13.32, "69 GW backlog; lead times of three years or more.", "short", ["oilprice_turb"])
ST("takasago", "turbines", "Gas-turbine works (Takasago)", "Mitsubishi Heavy", 34.75, 134.79, "35 GW backlog; deliveries 2028-30.", "short", ["oilprice_turb"])
ST("southboston", "transformers", "Transformer plant (South Boston, VA)", "Hitachi Energy", 36.70, -78.90, "New large-transformer plant, due 2028.", "short", ["pv_transf"])
ST("ulsan", "transformers", "Transformer works (Ulsan)", "HD Hyundai Electric", 35.51, 129.40, "Major exporter of large transformers to the US.", "short", ["pv_transf"])
ST("hsinchu", "foundry", "Hsinchu fabs and HQ", "TSMC", 24.78, 121.00, "2nm ramp (Baoshan) and headquarters.", "normal", ["tf_tsmc_cap"])
ST("tainan", "foundry", "Tainan fabs (N3, N5)", "TSMC", 23.10, 120.28, "Where most AI compute dies are made.", "normal", ["tf_tsmc_cap"])
ST("kaohsiung", "foundry", "Kaohsiung fabs (N2)", "TSMC", 22.73, 120.33, "2nm capacity.", "normal", ["tf_tsmc_cap"])
ST("phoenix", "foundry", "Arizona fabs", "TSMC", 33.76, -112.13, "$265B plan: more 2nm fabs and two packaging plants.", "ramping", ["th_tsmc_az"])
ST("kumamoto", "foundry", "Kumamoto fab (JASM)", "TSMC", 32.88, 130.84, "TSMC's Japan fab.", "normal", [])
ST("chandler", "foundry", "Ocotillo fabs (18A)", "Intel", 33.27, -111.88, "Intel's leading-edge alternative.", "ramping", [])
ST("taylor", "foundry", "Taylor fab", "Samsung", 30.57, -97.41, "Samsung Foundry's US site.", "ramping", [])
ST("pyeongtaek", "dram", "Pyeongtaek campus", "Samsung", 37.02, 127.05, "DRAM, HBM and foundry.", "normal", ["tf_hbm4"])
ST("icheon", "dram", "Icheon fabs", "SK hynix", 37.27, 127.44, "DRAM and HBM.", "normal", ["tf_hbm4"])
ST("cheongju", "hbm", "Cheongju M15X (HBM)", "SK hynix", 36.64, 127.49, "HBM capacity for Nvidia.", "normal", ["tf_hbm4"])
ST("westlafayette", "hbm", "HBM packaging plant (Indiana)", "SK hynix", 40.43, -86.91, "Planned US HBM packaging plant.", "ramping", [])
ST("boise", "dram", "Boise DRAM fab", "Micron", 43.53, -116.15, "New US DRAM fab.", "ramping", [])
ST("clay", "dram", "Clay, NY megafab", "Micron", 43.19, -76.19, "Planned US memory megafab.", "ramping", [])
ST("taichung", "hbm", "Taichung DRAM and HBM", "Micron", 24.21, 120.62, "Much of Micron's HBM.", "normal", [])
ST("hiroshima", "dram", "Hiroshima DRAM fab", "Micron", 34.43, 132.74, "DRAM.", "normal", [])
ST("kitakami", "nand", "Kitakami NAND fabs", "Kioxia, SanDisk", 39.29, 141.11, "NAND flash.", "normal", ["tf_mem"])
ST("shanghai", "china_fab", "Shanghai fabs", "SMIC", 31.21, 121.60, "China's most advanced logic, on DUV.", "controlled", [])
ST("hefei", "china_fab", "Hefei DRAM fabs", "CXMT", 31.82, 117.23, "China's DRAM and HBM effort.", "controlled", [])
ST("chiayi", "cowos", "CoWoS plant AP7 (Chiayi)", "TSMC", 23.47, 120.44, "CoWoS expansion site.", "short", ["tf_tsmc_cap"])
ST("zhunan", "cowos", "CoWoS plant AP6 (Zhunan)", "TSMC", 24.69, 120.88, "Advanced packaging.", "short", ["tf_tsmc_cap"])
ST("kaohsiung_ase", "osat", "Kaohsiung packaging", "ASE", 22.72, 120.30, "Largest outsourced packager.", "normal", [])
ST("peoria", "osat", "Arizona packaging campus", "Amkor", 33.58, -112.24, "US advanced packaging under construction.", "ramping", [])
ST("pjm", "grid", "PJM grid (Mid-Atlantic)", "PJM Interconnection", 40.12, -75.44, "Capacity auction $16.4B, about $6.3B from data centers (Jul 2026).", "tight", ["bgov_pjm"])
ST("crane", "nuclear", "Crane Clean Energy Center (restart)", "Constellation / Microsoft", 40.15, -76.72, "Restarted reactor contracted to Microsoft.", "ramping", ["atlas"])
ST("susquehanna", "nuclear", "Susquehanna nuclear plant", "Talen / Amazon", 41.09, -76.15, "Nuclear power for an Amazon campus.", "normal", ["atlas"])
ST("newark", "onsite", "Fuel-cell plant (Delaware)", "Bloom Energy", 39.68, -75.75, "On-site power for data centers.", "normal", [])
ST("lafayette", "onsite", "Engine plant (Lafayette, IN)", "Caterpillar", 40.42, -86.87, "Large engines and gensets.", "normal", [])
ST("suzhou", "optics", "Transceiver plants (Suzhou)", "Zhongji Innolight", 31.30, 120.62, "#1 transceiver maker; 2025 revenue $5.3B.", "tight", ["lc_optics"])
ST("chengdu", "optics", "Transceiver plants (Chengdu)", "Eoptolink", 30.66, 104.07, "#2 transceiver maker; 2025 revenue $3.5B.", "tight", ["lc_optics"])
ST("chonburi", "optics", "Optics contract manufacturing (Chonburi)", "Fabrinet", 13.36, 100.98, "Builds optics for US vendors.", "normal", [])
ST("sherman_cohr", "lasers", "InP laser fab (Sherman, TX)", "Coherent", 33.64, -96.61, "InP lasers; Nvidia invested $2B in Coherent.", "short", ["tf_inp"])
ST("sagamihara", "lasers", "Laser fab (Sagamihara)", "Lumentum", 35.57, 139.37, "EML lasers; Nvidia invested $2B in Lumentum.", "short", ["dcd_lumentum"])
ST("wilmington", "fiber", "Fiber plant (Wilmington, NC)", "Corning", 34.24, -77.95, "Optical fiber.", "normal", [])
ST("sakura", "fiber", "Fiber plant (Sakura)", "Fujikura", 35.72, 140.22, "Optical fiber and cables.", "normal", [])
ST("aspeed", "bmc", "ASPEED (Hsinchu)", "ASPEED", 24.80, 121.02, "Largest BMC supplier; moving to E-glass boards.", "tight", ["taipei_aspeed"])
ST("guadalajara", "servers", "Rack assembly (Guadalajara)", "Foxconn", 20.62, -103.40, "Foxconn built about 44% of GB racks in April 2026.", "normal", ["technews_odm"])
ST("houston", "servers", "AI server plant (Houston)", "Foxconn", 29.93, -95.52, "US rack assembly.", "normal", ["technews_odm"])
ST("guishan", "servers", "Server plants (Taoyuan)", "Quanta Computer", 25.03, 121.36, "About 2,100 of 8,300 GB racks in April 2026.", "normal", ["technews_odm"])
ST("columbus", "cooling", "Power and cooling plants (Ohio)", "Vertiv", 39.96, -83.00, "Liquid cooling, UPS and switchgear.", "normal", [])
ST("abudhabi", "sovereign", "Stargate UAE campus", "G42 / OpenAI", 24.42, 54.58, "5 GW campus; Iran's IRGC threatened it on 3 Apr 2026.", "threatened", ["tnw_stargate", "atlas"])
ST("aws_uae", "sovereign", "AWS UAE region", "Amazon", 24.30, 54.45, "Drones knocked out 2 of 3 availability zones on 1 Mar 2026.", "struck", ["row_aws", "fp_gulf"])
ST("aws_bahrain", "sovereign", "AWS Bahrain region", "Amazon", 26.07, 50.56, "Facility damaged on 1 Mar 2026.", "struck", ["row_aws"])
ST("riyadh", "sovereign", "HUMAIN Riyadh campuses", "HUMAIN", 24.71, 46.68, "Saudi build-out with Nvidia, AMD and AWS.", "at risk", ["atlas"])
ST("strait", "foundry", "Taiwan Strait", "Risk zone", 24.2, 119.6, "PLA 'Justice Mission 2025' simulated a blockade (30 Dec 2025).", "at risk", ["samdesk_tw"])

# ---------------------------------------------------------------- quotes (Stock Analysis, as of each date)
# cur: display prefix; px, tgt in local currency; up = % to average target; n = analysts; rating; asof; next = next report date
Q = {}
def QT(k, cur, px, asof, rating=None, n=None, tgt=None, up=None, next=None, proj=None, url=None, flag=None):
    Q[k] = dict(cur=cur, px=px, asof=asof, rating=rating, n=n, tgt=tgt, up=up, next=next, proj=proj, url=url, flag=flag)

US = lambda t: "https://stockanalysis.com/stocks/%s/forecast/" % t.lower()
QT("nvda", "$", 228.26, "2026-09-30", "Strong Buy", 61, 327.70, 43.6, proj="FY27 revenue $411.6B vs $215.9B; EPS $9.31", url=US("nvda"))
QT("amd", "$", 612.07, "2026-09-30", "Strong Buy", 55, 618.51, 1.1, proj="2027 revenue $88.1B vs $50.9B in 2026; EPS $15.58", url=US("amd"))
QT("avgo", "$", 351.11, "2026-09-30", "Strong Buy", 50, 531.85, 51.5, proj="FY27 revenue $173.8B vs $106.0B", url=US("avgo"))
QT("mrvl", "$", 264.13, "2026-09-30", "Strong Buy", 43, 289.11, 9.5, proj="FY27 revenue $12.05B vs $8.19B", url=US("mrvl"))
QT("arm", "$", 287.70, "2026-09-30", "Buy", 43, 288.71, 0.35, url=US("arm"))
QT("intc", "$", 120.12, "2026-09-30", "Buy", 49, 116.37, -3.1, proj="Revenue $72.0B next year vs $63.1B", url=US("intc"))
QT("cbrs", "$", 194.95, "2026-09-29", "Strong Buy", 11, 291.64, 49.6, proj="Revenue $2.95B next year vs $887M", url=US("cbrs"))
QT("alab", "$", 357.84, "2026-09-29", "Buy", 26, 389.95, 9.0, url=US("alab"))
QT("crdo", "$", 192.35, "2026-09-29", "Strong Buy", 19, 280.10, 45.6, url=US("crdo"))
QT("tsmc", "$", 458.39, "2026-09-30", "Strong Buy", 21, 552.26, 20.5, proj="Revenue +42.9% this year, +34.6% next; CoWoS ~130k wafers/mo by end-2026, ~260k by end-2028", url=US("tsm"))
QT("mu", "$", 1072.46, "2026-09-30", "Strong Buy", 49, 1521.00, 41.8, proj="FY26 revenue $130.0B, EPS $73.60; DRAM contract prices +13-18% in Q3", url=US("mu"))
QT("skhynix", "₩", 1862000, "2026-09-23", "Strong Buy", 38, 3202944, 72.0, proj="Revenue ₩534T in 2027 vs ₩346T in 2026; HBM share 50% in 2026", url="https://stockanalysis.com/quote/krx/000660/forecast/")
QT("samsung", "₩", 276500, "2026-09-22", "Strong Buy", 36, 475850, 72.1, proj="Revenue ₩968T in 2027 (+33%); leads HBM4 for Vera Rubin", url="https://stockanalysis.com/quote/krx/005930/forecast/")
QT("sndk", "$", 1740.20, "2026-09-30", "Buy", 25, 2137.00, 22.8, proj="NAND contract prices +10-15% in Q3 2026", url=US("sndk"))
QT("stx", "$", 921.67, "2026-09-30", "Strong Buy", 25, 1125.00, 22.1, url=US("stx"))
QT("smic", "HK$", 63.35, "2026-09-25", "Buy", 24, 94.38, 49.0, next="2026-11-09", url="https://stockanalysis.com/quote/hkg/0981/")
QT("asml", "$", 1834.39, "2026-09-29", "Strong Buy", 42, 2116.00, 15.4, proj="2026 revenue guide €43-45B; consensus sees 2027 revenue 27% higher; EUV capacity +30% in 2027", url=US("asml"))
QT("amat", "$", 511.45, "2026-09-30", "Strong Buy", 40, 638.94, 24.9, url=US("amat"))
QT("lrcx", "$", 326.47, "2026-09-30", "Strong Buy", 35, 373.77, 14.5, proj="FY27 revenue $34.9B (consensus)", url=US("lrcx"))
QT("klac", "$", 196.25, "2026-09-30", "Buy", 29, 233.77, 19.1, url=US("klac"))
QT("ter", "$", 403.02, "2026-09-29", "Buy", 17, 446.47, 10.8, url=US("ter"))
QT("tel", "¥", 11505, "2026-09-29", None, None, None, None, next="2026-10-30", url="https://stockanalysis.com/quote/tyo/8035/", flag="Published target looks stale (not split-adjusted), so it is left out.")
QT("snps", "$", 415.09, "2026-09-29", "Strong Buy", 26, 545.93, 31.5, url=US("snps"))
QT("cdns", "$", 324.17, "2026-09-29", "Strong Buy", 26, 405.47, 25.1, url=US("cdns"))
QT("advantest", "¥", 33910, "2026-09-29", "Buy", 21, 42138, 24.3, next="2026-10-28", proj="About 55% of chip test equipment", url="https://stockanalysis.com/quote/tyo/6857/")
QT("disco", "¥", 54040, "2026-09-03", "Buy", 21, 83880, 55.2, proj="Revenue ¥556B next year (+27%)", url="https://stockanalysis.com/quote/tyo/6146/forecast/")
QT("lasertec", "¥", 40910, "2026-09-25", "Buy", 17, 48775, 19.2, next="2026-10-30", proj="Sole actinic EUV mask-inspection supplier", url="https://stockanalysis.com/quote/tyo/6920/")
QT("hanmi", "₩", 240500, "2026-09-07", "Hold", 7, 268571, 11.7, next="2026-11-13", proj="71.2% of HBM TC bonders; 2025 sales ₩576.7B", url="https://stockanalysis.com/quote/krx/042700/")
QT("besi", "€", 187.60, "2026-09-25", "Buy", 22, 293.09, 56.2, next="2026-10-22", url="https://stockanalysis.com/quote/ams/BESI/")
QT("shinetsu", "¥", 5889, "2026-09-25", "Buy", 17, 7775, 32.0, next="2026-10-27", proj="28% of 300mm wafers; EUV resist", url="https://stockanalysis.com/quote/tyo/4063/")
QT("gwafers", "NT$", 948, "2026-09-24", "Buy", 14, 1039.29, 9.6, next="2026-11-05", url="https://stockanalysis.com/quote/tpex/6488/")
QT("tok", "¥", 8609, "2026-09-30", "Buy", 12, 11070, 28.6, next="2026-11-10", url="https://stockanalysis.com/quote/tyo/4186/")
QT("ajinomoto", "¥", 4904, "2026-09-18", "Buy", 14, 6146, 25.3, next="2026-11-09", proj="95% of GPU-grade ABF; a new supplier needs 18-24 months", url="https://stockanalysis.com/quote/tyo/2802/")
QT("nittobo", "¥", 2899, "2026-09-16", "Buy", 10, 4846, 67.2, next="2026-11-05", proj="~90% of T-glass; relief not before mid-2027", url="https://stockanalysis.com/quote/tyo/3110/")
QT("ibiden", "¥", 23345, "2026-09-25", "Buy", 18, 24729, 5.9, next="2026-10-29", proj="¥500B through FY2028 for 2.5x substrate capacity", url="https://stockanalysis.com/quote/tyo/4062/")
QT("unimicron", "NT$", 1165, "2026-09-29", "Strong Buy", 19, 1264, 8.5, next="2026-10-29", url="https://stockanalysis.com/quote/tpe/3037/")
QT("ase", "$", 44.70, "2026-09-30", None, None, None, None, next="2026-10-29", url="https://stockanalysis.com/stocks/asx/")
QT("amkor", "$", 53.39, "2026-09-28", "Buy", 11, 76.40, 43.1, url=US("amkr"))
QT("entg", "$", 151.89, "2026-09-25", "Buy", 12, 173.36, 14.1, url=US("entg"))
QT("linde", "$", 477.69, "2026-09-30", "Buy", 28, 542.60, 13.6, proj="Helium: Qatar's third offline; spot prices doubled", url=US("lin"))
QT("axt", "$", 76.27, "2026-09-30", "Buy", 5, 91.60, 20.1, url=US("axti"))
QT("sumitomo", "¥", 2200, "2026-09-28", "Buy", 11, 3447, 56.7, next="2026-10-30", url="https://stockanalysis.com/quote/tyo/5802/")
QT("mp", "$", 45.43, "2026-09-29", "Strong Buy", 19, 74.29, 63.5, proj="China's No. 18 rare-earth controls still in force", url=US("mp"))
QT("fcx", "$", 70.79, "2026-09-29", "Buy", 23, 72.45, 2.3, url=US("fcx"))
QT("clf", "$", 12.76, "2026-09-17", "Hold", 13, 12.30, -3.6, proj="Only qualified US DR-GOES maker; $400M DLA deal (Jul 2026)", url=US("clf"))
QT("mtk", "NT$", 5285, "2026-09-24", "Strong Buy", 26, 5907, 11.8, url="https://stockanalysis.com/quote/tpe/2454/")
QT("alchip", "NT$", 3770, "2026-09-24", "Buy", 16, 5772, 53.1, next="2026-11-11", url="https://stockanalysis.com/quote/tpe/3661/")
QT("cambricon", "CN¥", 1121, "2026-09-22", "Strong Buy", 8, 1641.07, 46.4, next="2026-10-26", proj="First-half revenue +108%", url="https://stockanalysis.com/quote/sha/688256/")
QT("aspeed", "NT$", 17255, "2026-09-01", "Strong Buy", 16, 19763, 14.5, next="2026-11-11", proj="Moving boards to E-glass as substrates run short", url="https://stockanalysis.com/quote/tpex/5274/")
QT("innolight", "CN¥", 808.44, "2026-09-30", "Strong Buy", 17, 1392, 72.2, next="2026-10-19", proj="#1 transceiver maker: 2025 revenue $5.3B; Q1 2026 +207%", url="https://stockanalysis.com/quote/she/300308/")
QT("eoptolink", "CN¥", 455.00, "2026-09-22", "Strong Buy", 9, 652.48, 43.4, proj="#2 transceiver maker: 2025 revenue $3.5B (+189%)", url="https://stockanalysis.com/quote/she/300502/")
QT("cohr", "$", 292.21, "2026-09-29", "Buy", 23, 415.36, 42.1, proj="Nvidia invested $2B (Mar 2026); InP expansion to 2027", url=US("cohr"))
QT("lite", "$", 968.25, "2026-09-30", "Buy", 26, 1157.00, 19.5, proj="Nvidia invested $2B (Mar 2026); InP gap bigger than DRAM's", url=US("lite"))
QT("fn", "$", 412.48, "2026-09-29", "Buy", 9, 734.11, 78.0, url=US("fn"))
QT("glw", "$", 153.40, "2026-09-30", "Strong Buy", 17, 189.94, 23.8, url=US("glw"))
QT("fujikura", "¥", 4986, "2026-09-25", "Buy", 12, 7352, 47.5, next="2026-11-10", url="https://stockanalysis.com/quote/tyo/5803/")
QT("aph", "$", 84.34, "2026-09-29", "Strong Buy", 17, 99.39, 17.8, url=US("aph"))
QT("anet", "$", 202.86, "2026-09-29", "Strong Buy", 31, 241.93, 19.3, url=US("anet"))
QT("csco", "$", 106.94, "2026-09-29", "Buy", 28, 137.25, 28.3, url=US("csco"))
QT("honhai", "NT$", 250.50, "2026-09-24", "Buy", 21, 347.45, 38.7, next="2026-11-12", proj="~44% of GB200/GB300 racks (Apr 2026)", url="https://stockanalysis.com/quote/tpe/2317/")
QT("quanta", "NT$", 337.00, "2026-09-29", "Buy", 19, 427.84, 27.0, next="2026-11-11", proj="~2,100 of 8,300 GB racks (Apr 2026)", url="https://stockanalysis.com/quote/tpe/2382/")
QT("wiwynn", "NT$", 2490, "2026-09-07", "Strong Buy", 19, 2750, 10.4, next="2026-11-06", url="https://stockanalysis.com/quote/tpe/6669/")
QT("cls", "$", 366.47, "2026-09-29", "Strong Buy", 21, 471.20, 28.6, url=US("cls"))
QT("smci", "$", 40.55, "2026-09-30", "Hold", 19, 42.38, 4.5, url=US("smci"))
QT("dell", "$", 545.73, "2026-09-30", "Buy", 29, 579.36, 6.2, url=US("dell"))
QT("gev", "$", 955.01, "2026-09-30", "Buy", 37, 1237.00, 29.6, proj="116 GW turbine backlog; capacity 20 to 24 to 30 GW/yr; 2031 slots on sale", url=US("gev"))
QT("enr", "€", 142.60, "2026-09-25", "Buy", 25, 196.32, 37.7, next="2026-11-11", proj="69 GW gas-turbine backlog; 3+ year lead times", url="https://stockanalysis.com/quote/etr/ENR/")
QT("mhi", "¥", 3801, "2026-09-30", "Buy", 16, 5451, 43.4, next="2026-11-06", proj="35 GW large-turbine backlog; deliveries 2028-30", url="https://stockanalysis.com/quote/tyo/7011/")
QT("hitachi", "¥", 5536, "2026-09-25", "Buy", 14, 6600, 19.2, next="2026-10-27", proj="Hitachi Energy's Virginia transformer plant due 2028", url="https://stockanalysis.com/quote/tyo/6501/")
QT("hdhe", "₩", 708000, "2026-09-23", "Buy", 22, 1171760, 65.5, next="2026-11-13", proj="Transformer lead times up to 4 years; prices up ~80%", url="https://stockanalysis.com/quote/krx/267260/")
QT("etn", "$", 429.71, "2026-09-30", "Buy", 28, 481.55, 12.1, next="2026-11-03", url="https://stockanalysis.com/stocks/etn/")
QT("su", "€", 291.00, "2026-09-25", "Buy", 23, 329.93, 13.4, next="2026-10-28", url="https://stockanalysis.com/quote/epa/SU/")
QT("vrt", "$", 242.10, "2026-09-30", "Strong Buy", 29, 338.22, 39.7, proj="Revenue $14.0B in 2026 (+37%), $18.2B in 2027; EPS $9.16", url=US("vrt"))
QT("delta", "NT$", 1910, "2026-09-24", "Strong Buy", 22, 2470, 29.3, next="2026-10-29", url="https://stockanalysis.com/quote/tpe/2308/")
QT("cat", "$", 816.00, "2026-09-30", "Buy", 28, 975.61, 19.6, url=US("cat"))
QT("be", "$", 291.25, "2026-09-29", "Buy", 29, 280.24, -3.8, url=US("be"))
QT("pwr", "$", 643.51, "2026-09-30", "Strong Buy", 31, 769.63, 19.6, url=US("pwr"))
QT("ceg", "$", 254.02, "2026-09-30", "Buy", 22, 347.28, 36.6, next="2026-11-06", url=US("ceg"))
QT("vst", "$", 140.83, "2026-09-29", "Strong Buy", 20, 217.58, 54.5, url=US("vst"))
QT("oklo", "$", 37.00, "2026-09-30", "Buy", 25, 76.43, 106.6, url=US("oklo"))
QT("ccj", "$", 86.88, "2026-09-29", "Buy", 21, 127.77, 47.1, proj="US ban on Russian enriched uranium from 2028", url=US("ccj"))
QT("leu", "$", 138.18, "2026-09-29", "Buy", 19, 247.40, 79.0, proj="US ban on Russian enriched uranium from 2028 (waivers to 2027)", url=US("leu"))
QT("msft", "$", 512.90, "2026-09-30", "Strong Buy", 55, 577.26, 12.6, proj="2026 capex about $190B (Investment Atlas)", url=US("msft"))
QT("googl", "$", 344.08, "2026-09-30", "Strong Buy", 61, 429.46, 24.8, proj="2026 capex about $200B (Investment Atlas)", url=US("googl"))
QT("amzn", "$", 249.15, "2026-09-30", "Strong Buy", 59, 329.54, 32.3, proj="2026 capex about $220B (Investment Atlas)", url=US("amzn"))
QT("meta", "$", 725.44, "2026-09-30", "Strong Buy", 62, 793.91, 9.4, proj="2026 capex about $137.5B (Investment Atlas)", url=US("meta"))
QT("orcl", "$", 137.52, "2026-09-30", "Buy", 43, 237.97, 73.0, proj="S&P BBB- (9 Jul 2026); $117B of bonds; $300B OpenAI contract", url=US("orcl"))
QT("crwv", "$", 87.10, "2026-09-30", "Buy", 41, 141.58, 62.6, proj="Revenue $26.3B next year vs $12.9B; debt $35B, $640M quarterly interest", url=US("crwv"))
QT("nbis", "$", 237.36, "2026-09-29", "Buy", 19, 283.58, 19.5, url=US("nbis"))
QT("spcx", "$", 150.88, "2026-09-30", "Buy", 35, 222.42, 47.4, proj="Revenue $112.8B next year vs $44.5B", url=US("spcx"))
QT("eqix", "$", 1008.58, "2026-09-28", "Buy", 34, 1233.00, 22.3, proj="Revenue $11.4B in 2027 (+11%)", url=US("eqix"))
QT("softbank", "¥", 6315, "2026-09-18", "Buy", 19, 7749.71, 22.7, next="2026-11-11", url="https://stockanalysis.com/quote/tyo/9984/")

# watchlist groups (display order)
GROUPS = [
    ("design", "Chip designers", ["nvda", "amd", "avgo", "mrvl", "arm", "cbrs", "alab", "crdo", "mtk", "alchip", "cambricon", "aspeed"]),
    ("fabs", "Foundry & memory", ["tsmc", "samsung", "skhynix", "mu", "sndk", "stx", "intc", "smic"]),
    ("tools", "Equipment & EDA", ["asml", "amat", "lrcx", "klac", "tel", "advantest", "ter", "lasertec", "disco", "hanmi", "besi", "snps", "cdns"]),
    ("materials", "Materials & minerals", ["shinetsu", "gwafers", "tok", "ajinomoto", "nittobo", "entg", "linde", "axt", "sumitomo", "mp", "fcx", "clf"]),
    ("pkg", "Substrates & packaging", ["ibiden", "unimicron", "ase", "amkor"]),
    ("net", "Optics & networking", ["innolight", "eoptolink", "cohr", "lite", "fn", "glw", "fujikura", "aph", "anet", "csco"]),
    ("servers", "Servers", ["honhai", "quanta", "wiwynn", "cls", "dell", "smci"]),
    ("power", "Power & cooling gear", ["gev", "enr", "mhi", "hitachi", "hdhe", "etn", "su", "vrt", "delta", "cat", "be", "pwr"]),
    ("energy", "Power producers & fuel", ["ceg", "vst", "oklo", "ccj", "leu"]),
    ("clouds", "Clouds, capital & labs", ["msft", "googl", "amzn", "meta", "orcl", "crwv", "nbis", "spcx", "eqix", "softbank"]),
]
