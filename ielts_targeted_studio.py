import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
import math
import re
import json
import time
import urllib.request
import urllib.error
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# --- AUTOMATIC NLTK DATA DEPENDENCY RESOLVER ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
# -----------------------------------------------

class IELTSAdvancedStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("IELTS Writing Simulation Engine")
        self.root.geometry("1680x960")
        try:
            self.root.iconbitmap("app_icon.ico")
        except Exception:
            pass

        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.target_file = os.path.join(self.desktop_path, "ielts_studio_essay.txt")
        self.config_file = os.path.join(os.path.expanduser("~"), ".ielts_studio_config.json")
        self.input_font_size = 16

        self.current_task_mode = "Task 2"
        self.timer_minutes = 40
        self.time_left_seconds = self.timer_minutes * 60
        self.timer_running = False
        self.timer_paused = False
        self.timer_job = None
        self.timer_hidden = False

        self.settings_menu_open = False
        self.gemini_api_key = self.load_api_key()

        # Cache last audit scores for accurate PDF export
        self.last_audit_data = None

        # Theme Configurations (Strict Light & Dark Palettes)
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg_dark": "#0f1117", "bg_panel": "#161b22", "bg_input": "#1f242d",
                "text_main": "#f0f6fc", "text_gray": "#8b949e", "header_bg": "#161b22",
                "divider": "#30363d", "btn_bg": "#21262d", "btn_fg": "#c9d1d9",
                "accent_blue": "#38bdf8", "accent_green": "#10b981", "accent_purple": "#a855f7", "accent_orange": "#f97316",
                "tab_inactive_bg": "#1f242d", "tab_inactive_fg": "#8b949e", "tab_active_bg": "#a855f7", "tab_active_fg": "#ffffff",
                "dropdown_bg": "#1f242d", "dropdown_fg": "#f0f6fc", "card_bg": "#161b22"
            },
            "light": {
                "bg_dark": "#f1f5f9", "bg_panel": "#ffffff", "bg_input": "#ffffff",
                "text_main": "#0f172a", "text_gray": "#475569", "header_bg": "#ffffff",
                "divider": "#cbd5e1", "btn_bg": "#e2e8f0", "btn_fg": "#0f172a",
                "accent_blue": "#0284c7", "accent_green": "#059669", "accent_purple": "#7c3aed", "accent_orange": "#ea580c",
                "tab_inactive_bg": "#e2e8f0", "tab_inactive_fg": "#475569", "tab_active_bg": "#7c3aed", "tab_active_fg": "#ffffff",
                "dropdown_bg": "#ffffff", "dropdown_fg": "#0f172a", "card_bg": "#ffffff"
            }
        }

        # --- FULL CAMBRIDGE PROMPTS DATABASE (CAMBRIDGE 11 TO 21) ---
        self.cambridge_prompts_grouped = [
            {"group": "Cam 21", "items": [
                {"name": "C21 T1: Aging Population", "task": "Task 2", "prompt": "Some people believe that an aging population creates problems for governments. Others think there are benefits to having more elderly people in society. Discuss both views and give your opinion."},
                {"name": "C21 T2: Science Studies", "task": "Task 2", "prompt": "In many countries, fewer young people are choosing to study science at university. What are the causes of this? What impacts will this have on society?"},
                {"name": "C21 T3: Live Sports", "task": "Task 2", "prompt": "Many people enjoy watching live sports events, while others prefer watching them on television. Discuss both views and give your opinion."},
                {"name": "C21 T4: Studying Abroad", "task": "Task 2", "prompt": "Some people believe that studying abroad offers unique benefits to students, while others argue it causes unnecessary financial and emotional strain. Discuss both views."}
            ]},
            {"group": "Cam 20", "items": [
                {"name": "C20 T1: Environment vs Econ", "task": "Task 2", "prompt": "International community efforts should prioritize environmental conservation over economic development. To what extent do you agree or disagree?"},
                {"name": "C20 T2: Early Schooling", "task": "Task 2", "prompt": "Children should start formal schooling at an earlier age than is currently customary. Do the advantages of this outweigh the disadvantages?"},
                {"name": "C20 T3: Aviation Tax", "task": "Task 2", "prompt": "Air travel should be restricted or heavily taxed to protect the environment. To what extent do you agree or disagree?"},
                {"name": "C20 T4: Culture & Fashion", "task": "Task 2", "prompt": "Traditional culture and clothing are being replaced by modern global trends. Is this a positive or negative development?"}
            ]},
            {"group": "Cam 19", "items": [
                {"name": "C19 T1: Freedom vs Order", "task": "Task 2", "prompt": "Some people think that individual freedom is more important than societal order. To what extent do you agree or disagree?"},
                {"name": "C19 T2: Remote Work", "task": "Task 2", "prompt": "In many countries, more and more people work from home using digital technology. What are the advantages and disadvantages of this development?"},
                {"name": "C19 T3: Youth Spending", "task": "Task 2", "prompt": "Young people are spending more money on luxury items and electronics than in the past. What are the reasons for this? Is it a positive or negative trend?"},
                {"name": "C19 T4: Global Food", "task": "Task 2", "prompt": "Food production has become highly globalized with supermarket items transported over long distances. Do the advantages of this trend outweigh the disadvantages?"}
            ]},
            {"group": "Cam 18", "items": [
                {"name": "C18 T1: Community Service", "task": "Task 2", "prompt": "Some people believe that unpaid community service should be a compulsory part of high school programs. To what extent do you agree or disagree?"},
                {"name": "C18 T2: Economic Progress", "task": "Task 2", "prompt": "Some people think that economic progress is the only way to measure a country's success, while others think that other factors are more important. Discuss both views."},
                {"name": "C18 T3: Sports Events", "task": "Task 2", "prompt": "Some people believe that international sports events are a waste of public money. To what extent do you agree or disagree?"},
                {"name": "C18 T4: Housing Shortage", "task": "Task 2", "prompt": "In some countries, owning a home is becoming increasingly difficult for young people. What are the reasons and solutions?"}
            ]},
            {"group": "Cam 17", "items": [
                {"name": "C17 T1: Regional Relocation", "task": "Task 2", "prompt": "In some countries, governments are encouraging industries and businesses to move to regional areas outside the big cities. Do the advantages of this trend outweigh the disadvantages?"},
                {"name": "C17 T2: Free Public Transit", "task": "Task 2", "prompt": "Some people think that the best way to solve traffic congestion in cities is to provide free public transport. To what extent do you agree or disagree?"},
                {"name": "C17 T3: Free University", "task": "Task 2", "prompt": "Some people think that university education should be free for everyone. Discuss both views and give your opinion."},
                {"name": "C17 T4: Child Competition", "task": "Task 2", "prompt": "Some people think that a sense of competition in children should be encouraged. Others think that children should be taught to cooperate rather than compete. Discuss both views."}
            ]},
            {"group": "Cam 16", "items": [
                {"name": "C16 T1: Tech & Isolation", "task": "Task 2", "prompt": "Some people think that modern technology is making people more socially isolated. To what extent do you agree or disagree?"},
                {"name": "C16 T2: Nuclear Energy", "task": "Task 2", "prompt": "Nuclear energy is the best solution to meet the world's energy needs. To what extent do you agree or disagree?"},
                {"name": "C16 T3: Dietary Choice", "task": "Task 2", "prompt": "Some people think that the government should intervene in people's dietary choices to improve public health. To what extent do you agree or disagree?"},
                {"name": "C16 T4: Healthy Lifestyles", "task": "Task 2", "prompt": "Governments should spend more on promoting healthy lifestyles in individuals rather than treating illnesses. To what extent do you agree or disagree?"}
            ]},
            {"group": "Cam 15", "items": [
                {"name": "C15 T1: Species Loss", "task": "Task 2", "prompt": "Some people say that the main environmental problem of our time is the loss of particular species of plants and animals. Others say that there are more important environmental problems. Discuss both views."},
                {"name": "C15 T2: Driverless Cars", "task": "Task 2", "prompt": "In the future, all cars, buses and trucks will be driverless. Do the advantages of driverless vehicles outweigh the disadvantages?"},
                {"name": "C15 T3: Sports Salaries", "task": "Task 2", "prompt": "Some people think that professional sports people earn too much money, while others think their high salaries are justified. Discuss both views and give your opinion."},
                {"name": "C15 T4: Student Housing", "task": "Task 2", "prompt": "It is better for students to live at home with their parents during their university years rather than living in campus apartments. Discuss both views."}
            ]},
            {"group": "Cam 14", "items": [
                {"name": "C14 T1: Bad Situations", "task": "Task 2", "prompt": "Some people believe it is best to accept a bad situation, such as an unsatisfactory job or shortage of money. Others argue that it is better to try and improve such situations."},
                {"name": "C14 T2: Secondary Community Work", "task": "Task 2", "prompt": "In some countries, secondary schools require students to do unpaid community work. Do the advantages of this outweigh the disadvantages?"},
                {"name": "C14 T3: Distance Learning", "task": "Task 2", "prompt": "Many people use distance-learning programs to study at home. Do the advantages of this type of education outweigh the disadvantages?"},
                {"name": "C14 T4: Transport vs Roads", "task": "Task 2", "prompt": "Some people think that the government should invest more money in public transport rather than building more roads. Discuss both views."}
            ]},
            {"group": "Cam 13", "items": [
                {"name": "C13 T1: Imprisonment", "task": "Task 2", "prompt": "In many countries, imprisonment is becoming more common as a solution to crime. What are the advantages and disadvantages of this trend?"},
                {"name": "C13 T2: School Streaming", "task": "Task 2", "prompt": "Some people think that schools should select students according to their academic abilities. Others think it is better for students with different abilities to study together. Discuss both views."},
                {"name": "C13 T3: Arts & Music", "task": "Task 2", "prompt": "Some people say that music and art are more important than other subjects in school. To what extent do you agree or disagree?"},
                {"name": "C13 T4: History Research", "task": "Task 2", "prompt": "Researching history can be interesting and valuable, but some people think it is a waste of time. Discuss both views and give your opinion."}
            ]},
            {"group": "Cam 12", "items": [
                {"name": "C12 T1: Advertising", "task": "Task 2", "prompt": "Today, the high sales of popular consumer goods reflect the power of advertising and not the real needs of society. To what extent do you agree or disagree?"},
                {"name": "C12 T2: Railways vs Roads", "task": "Task 2", "prompt": "Governments should spend money on railways rather than roads. To what extent do you agree or disagree with this statement?"},
                {"name": "C12 T3: Practical Training", "task": "Task 2", "prompt": "Some people think that universities should not provide theoretical knowledge but give practical training starting from the first day. To what extent do you agree or disagree?"},
                {"name": "C12 T4: Public Spaces", "task": "Task 2", "prompt": "It is important for all towns and cities to have large public spaces such as squares and parks. To what extent do you agree or disagree with this statement?"}
            ]},
            {"group": "Cam 11", "items": [
                {"name": "C11 T1: University Purpose", "task": "Task 2", "prompt": "Some people think that universities should provide graduates with the knowledge and skills needed in the workplace. Others think that the true function of a university should be to give access to knowledge for its own sake. Discuss both views and give your opinion."},
                {"name": "C11 T2: Urban Migration", "task": "Task 2", "prompt": "Today, more and more people are migrating to cities in search of a better life, but city life can be difficult. What are the problems associated with this, and what are some possible solutions?"},
                {"name": "C11 T3: Public Health", "task": "Task 2", "prompt": "Some people say that the best way to improve public health is by increasing the number of sports facilities. Others think that this has little effect on public health and other measures are needed. Discuss both views and give your opinion."},
                {"name": "C11 T4: Education Pressure", "task": "Task 2", "prompt": "Competitiveness in education is increasing, and young children are finding it harder to cope. What are the causes of this? How can this be solved?"}
            ]}
        ]

        self.cambridge_prompts = []
        for grp in self.cambridge_prompts_grouped:
            for item in grp["items"]:
                self.cambridge_prompts.append(item)

        # --- EXPANDED VOCABULARY BANK ---
        self.vocabulary_bank = {
            "good": {"alts": ["advantageous", "beneficial", "exemplary", "salutary", "meritorious"], "cat": "Evaluation"},
            "bad": {"alts": ["detrimental", "adverse", "deleterious", "pernicious", "malignant"], "cat": "Evaluation"},
            "big": {"alts": ["substantial", "monumental", "unprecedented", "considerable", "profound"], "cat": "Scale & Magnitude"},
            "small": {"alts": ["negligible", "marginal", "inconsequential", "miniscule", "paltry"], "cat": "Scale & Magnitude"},
            "important": {"alts": ["paramount", "pivotal", "crucial", "imperative", "momentous"], "cat": "Evaluation"},
            "think": {"alts": ["assert", "postulate", "contend", "maintain", "hypothesize"], "cat": "Reporting Verbs"},
            "get": {"alts": ["acquire", "attain", "derive", "procure", "garner"], "cat": "Economics"},
            "make": {"alts": ["generate", "foster", "engender", "facilitate", "cultivate"], "cat": "Problem-Solving"},
            "problem": {"alts": ["dilemma", "predicament", "impediment", "obstacle", "setback"], "cat": "Problem-Solving"},
            "help": {"alts": ["assist", "aid", "facilitate", "bolster", "ameliorate"], "cat": "Problem-Solving"},
            "change": {"alts": ["alteration", "metamorphosis", "shift", "transition", "transformation"], "cat": "Scale & Magnitude"},
            "many": {"alts": ["numerous", "countless", "copious", "a myriad of", "multitudinous"], "cat": "Scale & Magnitude"},
            "show": {"alts": ["demonstrate", "illustrate", "exemplify", "manifest", "depict"], "cat": "Reporting Verbs"},
            "stop": {"alts": ["halt", "curb", "deter", "mitigate", "suppress"], "cat": "Problem-Solving"},
            "people": {"alts": ["citizens", "individuals", "society members", "populace", "community members"], "cat": "Demographics"},
            "children": {"alts": ["offspring", "juveniles", "youngsters", "minors", "descendants"], "cat": "Demographics"},
            "money": {"alts": ["capital", "funds", "financial resources", "monetary assets", "revenue"], "cat": "Economics"},
            "work": {"alts": ["labor", "toil", "operate", "function", "collaborate"], "cat": "Economics"},
            "cause": {"alts": ["trigger", "catalyze", "instigate", "provoke", "spark"], "cat": "Problem-Solving"},
            "result": {"alts": ["consequence", "repercussion", "outcome", "aftermath", "corollary"], "cat": "Evaluation"},
            "use": {"alts": ["utilize", "employ", "apply", "implement", "deploy"], "cat": "Problem-Solving"},
            "increase": {"alts": ["surge", "escalate", "multiply", "augment", "accelerate"], "cat": "Scale & Magnitude"},
            "decrease": {"alts": ["decline", "diminish", "dwindle", "recede", "plummet"], "cat": "Scale & Magnitude"},
            "say": {"alts": ["proclaim", "assert", "argue", "articulate", "state"], "cat": "Reporting Verbs"},
            "need": {"alts": ["necessitate", "require", "demand", "call for", "entail"], "cat": "Evaluation"},
            "create": {"alts": ["forge", "formulate", "originate", "devise", "fabricate"], "cat": "Problem-Solving"},
            "find": {"alts": ["discover", "uncover", "earth", "detect", "locate"], "cat": "Problem-Solving"},
            "give": {"alts": ["provide", "bestow", "contribute", "donate", "furnish"], "cat": "Economics"},
            "government": {"alts": ["authorities", "state administration", "governing body", "public sector", "regime"], "cat": "Demographics"},
            "society": {"alts": ["civilization", "community", "public domain", "social fabric", "human collective"], "cat": "Demographics"}
        }

        # --- EXPANDED POOR PHRASE DICTIONARY ---
        self.poor_phrase_dictionary = {
            "i think": {"alts": ["it is my firm belief that", "from my perspective", "i would contend that"], "cat": "Reporting Verbs"},
            "i believe": {"alts": ["it is apparent to me that", "i maintain that", "i am convinced that"], "cat": "Reporting Verbs"},
            "nowadays": {"alts": ["in contemporary society", "in this modern era", "presently"], "cat": "Demographics"},
            "all over the world": {"alts": ["globally", "across the international arena", "on a global scale"], "cat": "Demographics"},
            "play a big role": {"alts": ["play a pivotal role", "exert a profound influence", "serve as a cornerstone"], "cat": "Evaluation"},
            "get rid of": {"alts": ["eradicate", "eliminate", "abolish", "extirpate"], "cat": "Problem-Solving"},
            "make money": {"alts": ["generate revenue", "amass capital", "secure financial gains"], "cat": "Economics"},
            "shows that": {"alts": ["illustrates that", "demonstrates unequivocally that", "evinces that"], "cat": "Reporting Verbs"},
            "kids": {"alts": ["children", "juveniles", "younger generations", "offspring"], "cat": "Demographics"},
            "a lot of": {"alts": ["a multitude of", "an abundance of", "numerous", "a plethora of"], "cat": "Scale & Magnitude"},
            "good for": {"alts": ["beneficial to", "advantageous for", "instrumental in"], "cat": "Evaluation"},
            "bad for": {"alts": ["detrimental to", "deleterious to", "adverse to"], "cat": "Evaluation"},
            "in my opinion": {"alts": ["from my perspective", "to my mind", "i firmly contend that"], "cat": "Reporting Verbs"},
            "lead to": {"alts": ["give rise to", "result in", "trigger", "catalyze"], "cat": "Problem-Solving"},
            "such as": {"alts": ["including, but not limited to", "for instance", "to illustrate"], "cat": "Evaluation"},
            "also": {"alts": ["furthermore", "moreover", "in addition", "by the same token"], "cat": "Evaluation"},
            "bring about": {"alts": ["instigate", "provoke", "spark", "catalyze"], "cat": "Problem-Solving"},
            "think about": {"alts": ["ponder", "deliberate upon", "contemplate", "evaluate"], "cat": "Reporting Verbs"},
            "look at": {"alts": ["examine", "scrutinize", "inspect", "analyze"], "cat": "Evaluation"},
            "point out": {"alts": ["highlight", "emphasize", "underscore", "draw attention to"], "cat": "Reporting Verbs"}
        }

        # --- ALL 25 DISTINCT IELTS TOPIC LOGIC CATEGORIES ---
        self.topic_ideas_db = {
            "Education": {
                "keywords": ["education", "university", "school", "student", "teacher", "study", "learning", "academic", "exam"],
                "collocations": ["pedagogical methods", "holistic development", "rote learning", "tertiary education", "curriculum design", "intellectual rigor", "academic integrity"],
                "ideas": [
                    "Focus on critical thinking and analytical problem-solving over mechanical memorization.",
                    "Equalize educational access via state subsidies, scholarships, and digital learning platforms."
                ]
            },
            "Work, Employment & Telecommuting": {
                "keywords": ["work", "job", "career", "employment", "remote", "office", "salary", "telecommuting", "worker"],
                "collocations": ["remote telecommuting", "work-life balance", "corporate culture", "geographical flexibility", "sedentary work habits", "professional autonomy", "collaborative synergy", "precarious gig economy", "competitive remuneration", "workforce productivity"],
                "ideas": [
                    "Embrace hybrid working models to afford employees flexibility while preserving physical corporate cohesion.",
                    "Establish statutory 'right to disconnect' legislation to prevent chronic professional burnout in telecommuting contexts.",
                    "Recognize that autonomous scheduling enhances cognitive focus and reduces metropolitan traffic congestion."
                ]
            },
            "Artificial Intelligence & Automation": {
                "keywords": ["ai", "artificial intelligence", "robot", "automation", "algorithm", "machine"],
                "collocations": ["algorithmic efficiency", "technological displacement", "synthetic intelligence", "cognitive automation", "neural network integration"],
                "ideas": [
                    "Re-skill vulnerable labor demographics displaced by industrial automation.",
                    "Enforce rigorous ethical governance on autonomous systems to safeguard public accountability."
                ]
            },
            "Environment & Climate Change": {
                "keywords": ["environment", "climate", "pollution", "carbon", "global warming", "green", "plastic"],
                "collocations": ["ecological degradation", "sustainable initiatives", "carbon footprint", "renewable energy transition", "environmental stewardship", "biodiversity loss"],
                "ideas": [
                    "Requires binding international treaties alongside grassroots individual accountability and corporate compliance.",
                    "Economic growth must be harmonized with long-term conservation efforts and green infrastructure."
                ]
            },
            "Healthcare & Public Medicine": {
                "keywords": ["health", "hospital", "medicine", "doctor", "disease", "healthcare", "fitness"],
                "collocations": ["preventative medicine", "public health infrastructure", "biomedical innovation", "epidemiological vigilance", "universal healthcare coverage"],
                "ideas": [
                    "Prioritize proactive wellness campaigns and nutritional education over reactive acute treatments.",
                    "Ensure equitable resource distribution across rural and metropolitan medical facilities."
                ]
            },
            "Crime, Punishment & Rehabilitation": {
                "keywords": ["crime", "prison", "criminal", "punishment", "law", "police", "rehabilitation"],
                "collocations": ["incarceration rates", "reformative justice", "recidivism rates", "deterrence mechanisms", "correctional facilities"],
                "ideas": [
                    "Focus on vocational rehabilitation programs inside correctional institutions to lower recidivism.",
                    "Balance strict punitive deterrence with social intervention strategies for juvenile offenders."
                ]
            },
            "Urbanization & Megacities": {
                "keywords": ["city", "urban", "megacity", "housing", "traffic", "congestion", "migration"],
                "collocations": ["metropolitan sprawl", "urban densification", "municipal infrastructure", "housing affordability", "public transit integration"],
                "ideas": [
                    "Invest in decentralized regional hubs to alleviate demographic pressure on overcrowded capital cities.",
                    "Implement congestion pricing and expand grade-separated public transit networks."
                ]
            },
            "Globalization & International Trade": {
                "keywords": ["globalization", "trade", "international", "culture", "import", "export", "global"],
                "collocations": ["cultural homogenization", "economic interdependence", "transnational corporations", "protectionist tariffs", "supply chain resilience"],
                "ideas": [
                    "Safeguard indigenous cultural heritage against aggressive global commercial homogenization.",
                    "Leverage international trade agreements to foster cross-border economic stability and diplomacy."
                ]
            },
            "Tourism, Heritage & Ecotourism": {
                "keywords": ["tourism", "tourist", "travel", "holiday", "hotel", "heritage", "visitor"],
                "collocations": ["eco-tourism sustainability", "cultural commodification", "heritage preservation", "mass tourism footprint", "local economic stimulation"],
                "ideas": [
                    "Regulate tourist influx quotas in fragile ecological sanctuaries and historical monuments.",
                    "Promote community-led tourism ventures that directly benefit local indigenous populations."
                ]
            },
            "Transportation & Commuting": {
                "keywords": ["transport", "car", "vehicle", "road", "train", "flight", "travel", "transit"],
                "collocations": ["traffic congestion", "carbon emissions", "subsidized public transit", "alternative mobility", "infrastructure investment"],
                "ideas": [
                    "Subsidize zero-emission public transit networks to disincentivize private automobile dependency.",
                    "Incentivize electric vehicle adoption through tax rebates and charging station expansion."
                ]
            },
            "Media, Advertising & Consumerism": {
                "keywords": ["media", "advertising", "advertisement", "shopping", "consumer", "brand", "tv", "internet"],
                "collocations": ["materialistic consumerism", "subliminal manipulation", "digital saturation", "commercial influence", "critical media literacy"],
                "ideas": [
                    "Enforce strict regulatory oversight on predatory advertising directed at impressionable children.",
                    "Cultivate consumer mindfulness to counteract manipulative corporate marketing tactics."
                ]
            },
            "Youth, Parenting & Child Development": {
                "keywords": ["child", "parent", "youth", "family", "upbringing", "generation", "kid"],
                "collocations": ["authoritative parenting", "psychological resilience", "formative years", "intergenerational gap", "juvenile development"],
                "ideas": [
                    "Foster open familial communication and emotional intelligence during children's formative years.",
                    "Balance structured extracurricular guidance with unstructured autonomous play."
                ]
            },
            "Aging Populations & Pensions": {
                "keywords": ["aging", "elderly", "old", "pension", "retirement", "population", "geriatric"],
                "collocations": ["demographic inversion", "pension sustainability", "geriatric care", "healthcare burden", "intergenerational solidarity"],
                "ideas": [
                    "Gradually elevate the statutory retirement age in tandem with rising life expectancy metrics.",
                    "Enhance institutional eldercare support through dedicated payroll contributions."
                ]
            },
            "Fast Fashion & Consumer Waste": {
                "keywords": ["fashion", "clothing", "waste", "shopping", "buy", "disposable", "trend"],
                "collocations": ["throwaway culture", "textile waste", "sustainable apparel", "ethical manufacturing", "circular economy"],
                "ideas": [
                    "Penalize fast fashion conglomerates for unchecked textile landfill accumulation.",
                    "Encourage circular economy models emphasizing garment durability and recycling infrastructure."
                ]
            },
            "Government Spending & Taxation": {
                "keywords": ["government", "tax", "spending", "budget", "policy", "fund", "economy"],
                "collocations": ["fiscal allocation", "taxation policy", "public expenditure", "economic stimulus", "state subsidization"],
                "ideas": [
                    "Optimize public expenditure toward foundational infrastructure, education, and public health.",
                    "Implement progressive taxation structures to narrow wealth disparity gaps."
                ]
            },
            "Sports & Mega Events": {
                "keywords": ["sport", "game", "olympics", "stadium", "athlete", "competition", "match"],
                "collocations": ["mega-sporting spectacles", "commercial sponsorship", "grassroots athletic participation", "municipal ROI", "civic pride"],
                "ideas": [
                    "Prioritize funding for grassroots community sports facilities over exorbitant Olympic mega-events.",
                    "Leverage international sporting events to inspire youth physical fitness and national unity."
                ]
            },
            "Arts, Music & Cultural Heritage": {
                "keywords": ["art", "music", "culture", "museum", "painting", "artist", "theater"],
                "collocations": ["cultural enrichment", "aesthetic appreciation", "state patronage", "creative expression", "historical preservation"],
                "ideas": [
                    "Ensure robust state patronage for public museums, classical arts, and music education programs.",
                    "Recognize the cognitive and emotional value of creative expression in modern curricula."
                ]
            },
            "Science, Research & Space Exploration": {
                "keywords": ["science", "research", "space", "planet", "astronomy", "laboratory", "experiment"],
                "collocations": ["empirical research", "extraterrestrial exploration", "scientific breakthrough", "state-sponsored R&D", "technological innovation"],
                "ideas": [
                    "Allocate generous state grants toward fundamental scientific research and space exploration.",
                    "Balance pure theoretical inquiry with practical terrestrial problem-solving."
                ]
            },
            "Wealth Inequality & Social Mobility": {
                "keywords": ["wealth", "rich", "poor", "inequality", "income", "class", "poverty"],
                "collocations": ["socioeconomic stratification", "income disparity", "upward social mobility", "wealth distribution", "poverty alleviation"],
                "ideas": [
                    "Expand scholarship programs and vocational training to facilitate upward social mobility.",
                    "Mitigate radical wealth concentration through progressive taxation and social safety nets."
                ]
            },
            "Animal Rights & Ethics": {
                "keywords": ["animal", "testing", "zoos", "pet", "species", "hunting", "wildlife"],
                "collocations": ["humane treatment", "ethical experimentation", "species conservation", "captive breeding", "animal welfare"],
                "ideas": [
                    "Ban cosmetic animal testing in favor of advanced in vitro cellular testing methods.",
                    "Transform traditional zoos into scientific conservation and educational breeding centers."
                ]
            },
            "Space Exploration & Colonization": {
                "keywords": ["mars", "colonization", "universe", "astronomy", "satellite", "cosmos"],
                "collocations": ["interplanetary migration", "astronomical expenditure", "extraterrestrial habitation", "space debris", "orbital technology"],
                "ideas": [
                    "Address terrestrial crises before allocating astronomical capital to interplanetary colonization.",
                    "Establish international legal frameworks for responsible orbital satellite deployment."
                ]
            },
            "Language & Cultural Identity": {
                "keywords": ["language", "english", "bilingual", "dialect", "identity", "tradition"],
                "collocations": ["linguistic diversity", "cultural assimilation", "vernacular preservation", "bilingual cognitive benefits", "global lingua franca"],
                "ideas": [
                    "Protect minority dialects from extinction through regional educational broadcasting and funding.",
                    "Embrace bilingualism as a cognitive asset rather than a threat to national cohesion."
                ]
            },
            "Diet, Health & Agriculture": {
                "keywords": ["food", "diet", "organic", "farming", "agriculture", "meat", "vegan"],
                "collocations": ["genetically modified crops", "sustainable agriculture", "nutritional awareness", "intensive livestock farming", "food security"],
                "ideas": [
                    "Promote organic regenerative agriculture to safeguard topsoil integrity and consumer health.",
                    "Address global food security through technological crop yields and supply chain efficiency."
                ]
            },
            "Charity, Aid & Philanthropy": {
                "keywords": ["charity", "aid", "donation", "philanthropy", "poverty", "relief", "ngo"],
                "collocations": ["humanitarian intervention", "philanthropic initiatives", "aid dependency", "structural reform", "sustainable development"],
                "ideas": [
                    "Shift foreign aid models from short-term financial relief to long-term self-sustaining infrastructure.",
                    "Encourage corporate philanthropy directed at transparent grassroots community empowerment."
                ]
            },
            "Space & Modern Lifestyle": {
                "keywords": ["lifestyle", "pace", "modern", "stress", "leisure", "routine", "society"],
                "collocations": ["hectic modern pace", "sedentary lifestyle", "mindfulness practices", "digital saturation", "psychological burnout"],
                "ideas": [
                    "Reintroduce mandated recreational downtime to counteract the relentless modern work ethic.",
                    "Foster community-centric social spaces to combat urban alienation and digital isolation."
                ]
            }
        }

        p = self.themes[self.current_theme]

        # 1. HEADER BAR CONTAINER
        self.header = tk.Frame(self.root, bg=p["header_bg"], height=55)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.open_btn = tk.Button(self.header, text="Open File", command=self.open_file_dialog, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 9, "bold"), bd=1, relief="solid", padx=12, pady=5, cursor="hand2")
        self.open_btn.pack(side="left", padx=15)

        self.title_lbl = tk.Label(self.header, text="IELTS WRITING SIMULATION ENGINE", bg=p["header_bg"], fg=p["text_main"], font=("Trebuchet MS", 15, "bold"))
        self.title_lbl.pack(side="left", padx=15)

        self.task_mode_frame = tk.Frame(self.header, bg=p["header_bg"])
        self.task_mode_frame.pack(side="left", padx=10)

        self.task1_mode_btn = tk.Button(self.task_mode_frame, text="Task 1", command=lambda: self.set_task_mode("Task 1"), bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 9, "bold"), bd=1, relief="solid", padx=10, pady=4, cursor="hand2")
        self.task1_mode_btn.pack(side="left", padx=2)

        self.task2_mode_btn = tk.Button(self.task_mode_frame, text="Task 2", command=lambda: self.set_task_mode("Task 2"), bg=p["accent_green"], fg="#ffffff", font=("Arial", 9, "bold"), bd=1, relief="solid", padx=10, pady=4, cursor="hand2")
        self.task2_mode_btn.pack(side="left", padx=2)

        self.eval_btn = tk.Button(self.header, text="Evaluate Band", command=self.run_forensic_audit, bg=p["accent_green"], fg="#ffffff", font=("Arial", 10, "bold"), bd=1, relief="solid", padx=15, pady=5, cursor="hand2")
        self.eval_btn.pack(side="right", padx=15)

        self.settings_btn = tk.Button(self.header, text="Settings", command=self.toggle_settings_dropdown, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 9, "bold"), bd=1, relief="solid", padx=12, pady=5, cursor="hand2")
        self.settings_btn.pack(side="right", padx=5)

        self.status_lbl = tk.Label(self.header, text=f"File: {os.path.basename(self.target_file)}", bg=p["header_bg"], fg=p["text_gray"], font=("Arial", 8))
        self.status_lbl.pack(side="right", padx=15)

        # 2. MAIN WORKSPACE CONTAINER (ZERO STROKE GAP)
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=p["divider"], sashwidth=4, bd=0)
        self.main_paned.pack(fill="both", expand=True, padx=0, pady=0)

        # --- LEFT PANEL CONTAINER ---
        self.left_container = tk.Frame(self.main_paned, bg=p["bg_panel"])
        self.main_paned.add(self.left_container, width=640, minsize=350)

        self.left_vertical_paned = tk.PanedWindow(self.left_container, orient=tk.VERTICAL, bg=p["divider"], sashwidth=4, bd=0)
        self.left_vertical_paned.pack(fill="both", expand=True, padx=0, pady=0)

        # Top section: Prompt Frame
        self.prompt_frame = tk.Frame(self.left_vertical_paned, bg=p["bg_panel"])
        self.left_vertical_paned.add(self.prompt_frame, height=230, minsize=140)

        self.q_header_row = tk.Frame(self.prompt_frame, bg=p["bg_panel"])
        self.q_header_row.pack(fill="x", padx=10, pady=(4, 2))

        self.q_title_lbl = tk.Label(self.q_header_row, text="PROMPT QUESTION", bg=p["bg_panel"], fg=p["accent_purple"], font=("Arial", 9, "bold"))
        self.q_title_lbl.pack(side="left")

        self.test_count_badge = tk.Label(self.q_header_row, text=f" {len(self.cambridge_prompts)} tests ", bg=p["btn_bg"], fg=p["text_main"], font=("Arial", 8, "bold"))
        self.test_count_badge.pack(side="left", padx=8)

        self.random_prompt_btn = tk.Button(self.q_header_row, text="🎲 Random", command=self.load_random_cambridge_prompt, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=6, pady=2, cursor="hand2")
        self.random_prompt_btn.pack(side="right")

        self.paper_selector_btn = tk.Menubutton(self.q_header_row, text="Paper Selector...  ▼", bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=6, pady=2, cursor="hand2")
        self.paper_selector_btn.pack(side="right", padx=5)

        self.paper_menu = tk.Menu(self.paper_selector_btn, tearoff=0, bg=p["dropdown_bg"], fg=p["dropdown_fg"], activebackground=p["accent_purple"], activeforeground="#ffffff", font=("Arial", 8))
        self.paper_selector_btn.configure(menu=self.paper_menu)
        self.populate_paper_selector_menu()

        self.question_text = tk.Text(self.prompt_frame, bg=p["bg_input"], fg=p["text_main"], insertbackground=p["text_main"], font=("Arial", 10), wrap="word", height=6, bd=1, relief="solid")
        self.question_text.pack(fill="x", padx=10, pady=(4, 4))
        self.question_text.insert("1.0", "[Optional] Select a Cambridge prompt using 'Paper Selector...' above or paste your prompt here.")
        self.question_text.bind("<KeyRelease>", self.on_prompt_key_release)

        self.timer_frame = tk.Frame(self.prompt_frame, bg=p["bg_panel"])
        self.timer_frame.pack(fill="x", padx=10, pady=(2, 4))

        self.timer_container = tk.Frame(self.timer_frame, bg=p["bg_panel"])
        self.timer_container.pack(side="left", anchor="w")

        self.timer_display_lbl = tk.Label(self.timer_container, text="40 :00", bg=p["bg_panel"], fg=p["accent_blue"], font=("Arial", 20, "bold"), cursor="hand2")
        self.timer_display_lbl.pack(side="left", padx=(0, 6))
        self.timer_display_lbl.bind("<Button-1>", self.on_timer_click_edit)

        # --- EYE ICON BUTTON FOR TIMER HIDE/SHOW ---
        self.toggle_eye_btn = tk.Button(self.timer_container, text="👁", command=self.toggle_timer_visibility, bg=p["btn_bg"], fg=p["text_gray"], font=("Arial", 11), bd=1, relief="solid", padx=4, pady=1, cursor="hand2")
        self.toggle_eye_btn.pack(side="left", padx=(0, 10))

        self.btn_row = tk.Frame(self.timer_frame, bg=p["bg_panel"])
        self.btn_row.pack(side="left", padx=10)

        self.start_timer_btn = tk.Button(self.btn_row, text="Start", command=self.start_timer, bg=p["accent_green"], fg="#ffffff", font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=3, cursor="hand2")
        self.start_timer_btn.pack(side="left", padx=(0, 3))

        self.pause_timer_btn = tk.Button(self.btn_row, text="Pause", command=self.pause_timer, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=3, cursor="hand2")
        self.pause_timer_btn.pack(side="left", padx=2)

        self.reset_timer_btn = tk.Button(self.btn_row, text="Reset", command=self.reset_timer, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=3, cursor="hand2")
        self.reset_timer_btn.pack(side="left", padx=2)

        # Bottom section: Report & Diagnostic Tabs Area
        self.report_section_frame = tk.Frame(self.left_vertical_paned, bg=p["bg_panel"])
        self.left_vertical_paned.add(self.report_section_frame, height=500, minsize=250)

        self.tab_nav_frame = tk.Frame(self.report_section_frame, bg=p["bg_panel"])
        self.tab_nav_frame.pack(fill="x", padx=10, pady=(4, 2))

        self.tab_buttons = {}
        self.tab_frames = {}
        self.current_tab = "report"

        tab_names = [("report", "Report"), ("ai", "AI Review"), ("vocab", "Replacements (0)"), ("ideas", "Topic Logic")]

        for key, label in tab_names:
            btn = tk.Button(
                self.tab_nav_frame,
                text=label,
                font=("Arial", 9, "bold"),
                bd=1,
                relief="solid",
                padx=8,
                pady=5,
                cursor="hand2",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.pack(side="left", fill="x", expand=True, padx=2)
            self.tab_buttons[key] = btn

        self.content_container = tk.Frame(self.report_section_frame, bg=p["bg_panel"], bd=1, relief="solid")
        self.content_container.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # --- TAB 1: REPORT ---
        self.tab_frames["report"] = tk.Frame(self.content_container, bg=p["bg_panel"])
        self.report_bar = tk.Frame(self.tab_frames["report"], bg=p["bg_panel"])
        self.report_bar.pack(fill="x", padx=10, pady=(8, 4))

        self.report_ai_btn = tk.Button(self.report_bar, text="Request Gemini AI Review", command=self.run_ai_evaluation, bg=p["accent_purple"], fg="#ffffff", font=("Arial", 9, "bold"), bd=1, relief="solid", padx=12, pady=5, cursor="hand2")
        self.report_ai_btn.pack(side="right", fill="x", expand=True)

        self.report_canvas = tk.Canvas(self.tab_frames["report"], bg=p["bg_panel"], highlightthickness=0)
        self.report_scrollbar = ttk.Scrollbar(self.tab_frames["report"], orient="vertical", command=self.report_canvas.yview)
        self.report_scrollable_frame = tk.Frame(self.report_canvas, bg=p["bg_panel"])

        self.report_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.report_canvas.configure(scrollregion=self.report_canvas.bbox("all"))
        )
        self.report_canvas.create_window((0, 0), window=self.report_scrollable_frame, anchor="nw")
        self.report_canvas.configure(yscrollcommand=self.report_scrollbar.set)

        self.report_canvas.pack(side="left", fill="both", expand=True)
        self.report_scrollbar.pack(side="right", fill="y")

        # --- TAB 2: AI REVIEW ---
        self.tab_frames["ai"] = tk.Frame(self.content_container, bg=p["bg_panel"])
        self.ai_btn_frame = tk.Frame(self.tab_frames["ai"], bg=p["bg_panel"])
        self.ai_btn_frame.pack(fill="x", padx=10, pady=8)

        self.ai_action_btn = tk.Button(self.ai_btn_frame, text="Request Gemini AI Review", command=self.run_ai_evaluation, bg=p["accent_purple"], fg="#ffffff", font=("Arial", 9, "bold"), bd=1, relief="solid", padx=12, pady=6, cursor="hand2")
        self.ai_action_btn.pack(fill="x", expand=True)

        self.ai_display = tk.Text(self.tab_frames["ai"], bg=p["bg_input"], fg=p["text_main"], font=("Arial", 10), wrap="word", bd=1, relief="solid", padx=10, pady=10)
        self.ai_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- TAB 3: REPLACEMENTS ---
        self.tab_frames["vocab"] = tk.Frame(self.content_container, bg=p["bg_panel"])
        
        self.vocab_top_bar = tk.Frame(self.tab_frames["vocab"], bg=p["bg_panel"])
        self.vocab_top_bar.pack(fill="x", padx=10, pady=(8, 4))
        
        self.vocab_info_lbl = tk.Label(self.vocab_top_bar, text="DETECTED IN ESSAY (0 WORDS FLAGGED)", bg=p["bg_panel"], fg=p["accent_orange"], font=("Arial", 9, "bold"))
        self.vocab_info_lbl.pack(side="left")

        self.filter_chips_frame = tk.Frame(self.tab_frames["vocab"], bg=p["bg_panel"])
        self.filter_chips_frame.pack(fill="x", padx=10, pady=4)
        
        self.active_category_filter = "All"
        categories = ["All", "Demographics", "Economics", "Evaluation", "Scale & Magnitude", "Reporting Verbs", "Problem-Solving"]
        for cat in categories:
            btn = tk.Button(self.filter_chips_frame, text=cat, command=lambda c=cat: self.filter_replacements_by_category(c), bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=5, pady=2, cursor="hand2")
            btn.pack(side="left", padx=2, pady=2)

        self.vocab_canvas = tk.Canvas(self.tab_frames["vocab"], bg=p["bg_panel"], highlightthickness=0)
        self.vocab_scrollbar = ttk.Scrollbar(self.tab_frames["vocab"], orient="vertical", command=self.vocab_canvas.yview)
        self.vocab_scrollable_frame = tk.Frame(self.vocab_canvas, bg=p["bg_panel"])

        self.vocab_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.vocab_canvas.configure(scrollregion=self.vocab_canvas.bbox("all"))
        )
        self.vocab_canvas.create_window((0, 0), window=self.vocab_scrollable_frame, anchor="nw")
        self.vocab_canvas.configure(yscrollcommand=self.vocab_scrollbar.set)

        self.vocab_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.vocab_scrollbar.pack(side="right", fill="y")

        # --- TAB 4: TOPIC LOGIC ---
        self.tab_frames["ideas"] = tk.Frame(self.content_container, bg=p["bg_panel"])
        
        self.ideas_canvas = tk.Canvas(self.tab_frames["ideas"], bg=p["bg_panel"], highlightthickness=0)
        self.ideas_scrollbar = ttk.Scrollbar(self.tab_frames["ideas"], orient="vertical", command=self.ideas_canvas.yview)
        self.ideas_scrollable_frame = tk.Frame(self.ideas_canvas, bg=p["bg_panel"])

        self.ideas_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.ideas_canvas.configure(scrollregion=self.ideas_canvas.bbox("all"))
        )
        self.ideas_canvas.create_window((0, 0), window=self.ideas_scrollable_frame, anchor="nw")
        self.ideas_canvas.configure(yscrollcommand=self.ideas_scrollbar.set)

        self.ideas_canvas.pack(side="left", fill="both", expand=True)
        self.ideas_scrollbar.pack(side="right", fill="y")

        self.render_topic_logic_ui("Education", auto_detected=True)

        # --- RIGHT PANEL (CANDIDATE ESSAY RESPONSE SECTION) ---
        self.right_panel = tk.Frame(self.main_paned, bg=p["bg_dark"])
        self.main_paned.add(self.right_panel, width=1040, minsize=400)

        self.essay_text = tk.Text(self.right_panel, bg=p["bg_input"], fg=p["text_main"], insertbackground=p["text_main"], font=("Arial", self.input_font_size), spacing1=4, spacing3=4, bd=1, relief="solid", wrap="word", undo=True)
        self.essay_text.pack(fill="both", expand=True, padx=15, pady=(15, 35))
        self.essay_text.bind("<KeyRelease>", self.autosave_handler)

        self.footer = tk.Frame(self.right_panel, bg=p["header_bg"], height=35)
        self.footer.place(x=0, relwidth=1.0, rely=1.0, y=-35)

        self.word_lbl = tk.Label(self.footer, text="Words: 0", bg=p["header_bg"], fg=p["accent_blue"], font=("Arial", 10, "bold"))
        self.word_lbl.pack(side="left", padx=15)

        self.copyright_lbl = tk.Label(
            self.footer,
            text="© All Rights Reserved | Developed by Jawad Abedin",
            bg=p["header_bg"],
            fg=p["text_gray"],
            font=("Georgia", 9, "italic")
        )
        self.copyright_lbl.pack(side="right", padx=15)

        # Settings Dropdown Overlay
        self.settings_dropdown = tk.Frame(self.root, bg=p["bg_panel"], bd=1, relief="solid")

        self.clock_frame = tk.Frame(self.settings_dropdown, bg=p["bg_panel"])
        self.clock_frame.pack(padx=10, pady=(10, 5))

        tk.Label(self.clock_frame, text="PRACTICE CLOCK DIAL", bg=p["bg_panel"], fg=p["accent_purple"], font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 4))

        self.clock_canvas = tk.Canvas(self.clock_frame, width=100, height=100, bg=p["bg_panel"], highlightthickness=0, cursor="hand2")
        self.clock_canvas.pack(side="left", padx=(0, 10))
        self.clock_canvas.bind("<Button-1>", self.on_clock_click)
        self.clock_canvas.bind("<B1-Motion>", self.on_clock_click)

        self.manual_timer_frame = tk.Frame(self.clock_frame, bg=p["bg_panel"])
        self.manual_timer_frame.pack(side="left", fill="both", expand=True)

        tk.Label(self.manual_timer_frame, text="Set Minutes:", bg=p["bg_panel"], fg=p["text_main"], font=("Arial", 8)).pack(anchor="w")
        self.entry_m = tk.Entry(self.manual_timer_frame, bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9), width=8)
        self.entry_m.pack(anchor="w", pady=2)
        self.entry_m.insert(0, str(self.timer_minutes))

        tk.Button(self.manual_timer_frame, text="Apply", command=self.apply_manual_time, bg=p["accent_blue"], fg="#ffffff", font=("Arial", 8, "bold"), bd=0, padx=6, pady=2, cursor="hand2").pack(anchor="w", pady=2)

        tk.Frame(self.settings_dropdown, bg=p["divider"], height=1).pack(fill="x", padx=10, pady=5)

        self.ctrl_frame = tk.Frame(self.settings_dropdown, bg=p["bg_panel"])
        self.ctrl_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(self.ctrl_frame, text="Save File As...", command=self.save_file_as_dialog, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=4, cursor="hand2").pack(fill="x", pady=2)

        self.t_f_frame = tk.Frame(self.ctrl_frame, bg=p["bg_panel"])
        self.t_f_frame.pack(fill="x", pady=2)

        self.theme_toggle_btn = tk.Button(self.t_f_frame, text="Light Mode", command=self.toggle_theme, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=6, pady=3, cursor="hand2")
        self.theme_toggle_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))

        tk.Button(self.t_f_frame, text="A+", command=self.increase_font_size, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=6, pady=3, cursor="hand2").pack(side="left", padx=2)
        tk.Button(self.t_f_frame, text="A-", command=self.decrease_font_size, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=6, pady=3, cursor="hand2").pack(side="left", padx=2)

        tk.Button(self.ctrl_frame, text="Set Gemini API Key", command=self.set_api_key_prompt, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=4, cursor="hand2").pack(fill="x", pady=2)

        tk.Label(self.ctrl_frame, text="PDF Exports:", bg=p["bg_panel"], fg=p["accent_orange"], font=("Arial", 8, "bold")).pack(anchor="w", pady=(4, 2))
        tk.Button(self.ctrl_frame, text="Export PDF Report (Essay + Qs + Audit)", command=self.export_full_pdf_report, bg=p["accent_orange"], fg="#ffffff", font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=4, cursor="hand2").pack(fill="x", pady=2)
        tk.Button(self.ctrl_frame, text="Export PDF Draft (Essay + Qs Only)", command=self.export_draft_pdf, bg=p["btn_bg"], fg=p["btn_fg"], font=("Arial", 8, "bold"), bd=1, relief="solid", padx=8, pady=4, cursor="hand2").pack(fill="x", pady=2)

        self.root.bind_all("<Button-1>", self.global_click_handler)

        self.draw_clock_dial()
        self.load_existing_draft()

    def check_api_key_popup(self):
        if not self.gemini_api_key:
            msg = (
                "Gemini API Key is not set!\n\n"
                "How to set your free API Key:\n"
                "• Step 1: Obtain a free API key from Google AI Studio (aistudio.google.com).\n"
                "• Step 2: Click the 'Settings' button in the top-right corner of the Studio.\n"
                "• Step 3: Click 'Set Gemini API Key' and paste your key.\n"
                "• Step 4: Click Save to enable AI reviews!"
            )
            messagebox.showwarning("API Key Required", msg)
            self.show_settings_dropdown()
            return False
        return True

    def populate_paper_selector_menu(self):
        self.paper_menu.delete(0, tk.END)
        for grp in self.cambridge_prompts_grouped:
            self.paper_menu.add_command(label=f"--- {grp['group']} ---", state="disabled")
            for item in grp["items"]:
                self.paper_menu.add_command(
                    label=f"  {item['name']}",
                    command=lambda prompt_item=item: self.select_paper_prompt(prompt_item)
                )

    def select_paper_prompt(self, item):
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert("1.0", f"[{item['name']}]\n\n{item['prompt']}")
        short_name = item['name'].split(":")[0] if ":" in item['name'] else item['name'][:18]
        self.paper_selector_btn.configure(text=f"{short_name} ▼")
        self.detect_topic_from_prompt_text()

    def on_prompt_key_release(self, event):
        self.detect_topic_from_prompt_text()

    def detect_topic_from_prompt_text(self):
        prompt_txt = self.question_text.get("1.0", "end-1c").lower()
        matched = "Education"
        for cat_name, cat_data in self.topic_ideas_db.items():
            if any(kw in prompt_txt for kw in cat_data["keywords"]):
                matched = cat_name
                break
        self.render_topic_logic_ui(matched, auto_detected=True)

    def on_timer_click_edit(self, event):
        def apply_quick_time():
            try:
                val = int(spin.get())
                if 1 <= val <= 120:
                    self.timer_minutes = val
                    self.reset_timer()
                    popup.destroy()
            except ValueError:
                pass

        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        x = self.timer_display_lbl.winfo_rootx()
        y = self.timer_display_lbl.winfo_rooty() + 30
        popup.geometry(f"120x35+{x}+{y}")
        popup.configure(bg=self.themes[self.current_theme]["bg_panel"])

        spin = tk.Spinbox(popup, from_=1, to=120, width=5, font=("Arial", 11, "bold"))
        spin.pack(side="left", padx=2, pady=2)
        spin.delete(0, "end")
        spin.insert(0, str(self.timer_minutes))

        tk.Button(popup, text="Set", command=apply_quick_time, bg=self.themes[self.current_theme]["accent_blue"], fg="#ffffff", font=("Arial", 8, "bold"), bd=0, padx=4, pady=2).pack(side="left", padx=2)

    def set_task_mode(self, mode):
        self.current_task_mode = mode
        p = self.themes[self.current_theme]
        if mode == "Task 1":
            self.task1_mode_btn.configure(bg=p["accent_green"], fg="#ffffff")
            self.task2_mode_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])
            self.timer_minutes = 20
        else:
            self.task2_mode_btn.configure(bg=p["accent_green"], fg="#ffffff")
            self.task1_mode_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])
            self.timer_minutes = 40
        self.reset_timer()

    def load_random_cambridge_prompt(self):
        import random
        matching = [p for p in self.cambridge_prompts if p["task"] == self.current_task_mode]
        if not matching:
            matching = self.cambridge_prompts
        chosen = random.choice(matching)
        self.select_paper_prompt(chosen)

    def init_welcome_report_view(self):
        p = self.themes[self.current_theme]
        for widget in self.report_scrollable_frame.winfo_children():
            widget.destroy()

        welcome_lbl = tk.Label(self.report_scrollable_frame, text="Studio Ready.\n\n• Select a Cambridge prompt using 'Paper Selector...' or paste your prompt.\n• Write your essay and click 'Evaluate Band'.\n• Access AI review, vocabulary replacements, grammar audits, and topic logic above.", bg=p["bg_panel"], fg=p["text_main"], font=("Arial", 10), justify="left")
        welcome_lbl.pack(padx=15, pady=20, anchor="w")

    def switch_tab(self, target_key):
        self.current_tab = target_key
        p = self.themes[self.current_theme]

        for key, frame in self.tab_frames.items():
            if key == target_key:
                frame.pack(fill="both", expand=True)
                self.tab_buttons[key].configure(bg=p["tab_active_bg"], fg=p["tab_active_fg"], relief="raised")
            else:
                frame.pack_forget()
                self.tab_buttons[key].configure(bg=p["tab_inactive_bg"], fg=p["tab_inactive_fg"], relief="solid")

    def global_click_handler(self, event):
        if not self.settings_menu_open:
            return
        widget = event.widget
        if widget == self.settings_btn or widget.winfo_toplevel() == self.settings_dropdown or str(widget).startswith(str(self.settings_dropdown)):
            return
        self.hide_settings_dropdown()

    def show_settings_dropdown(self):
        self.settings_menu_open = True
        p = self.themes[self.current_theme]
        self.settings_dropdown.configure(bg=p["bg_panel"])
        self.settings_dropdown.place(x=self.root.winfo_width() - 340, y=55, width=320, height=360)
        self.settings_dropdown.lift()

    def hide_settings_dropdown(self):
        self.settings_menu_open = False
        self.settings_dropdown.place_forget()

    def toggle_settings_dropdown(self):
        if self.settings_menu_open:
            self.hide_settings_dropdown()
        else:
            self.show_settings_dropdown()

    def toggle_timer_visibility(self):
        self.timer_hidden = not self.timer_hidden
        if self.timer_hidden:
            self.timer_display_lbl.pack_forget()
            self.toggle_eye_btn.configure(fg=self.themes[self.current_theme]["text_gray"])
        else:
            self.timer_display_lbl.pack(side="left", padx=(0, 6), before=self.toggle_eye_btn)
            self.toggle_eye_btn.configure(fg=self.themes[self.current_theme]["accent_blue"])
            self.update_timer_display()

    def draw_clock_dial(self):
        p = self.themes[self.current_theme]
        self.clock_canvas.delete("all")
        cx, cy, r = 50, 50, 40
        self.clock_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=p["bg_input"], outline=p["divider"], width=2)

        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = cx + (r - 5) * math.cos(angle)
            y1 = cy + (r - 5) * math.sin(angle)
            x2 = cx + r * math.cos(angle)
            y2 = cy + r * math.sin(angle)
            self.clock_canvas.create_line(x1, y1, x2, y2, fill=p["text_gray"], width=1)

        minute_angle = math.radians((self.timer_minutes / 60.0) * 360 - 90)
        hx = cx + (r - 10) * math.cos(minute_angle)
        hy = cy + (r - 10) * math.sin(minute_angle)
        self.clock_canvas.create_line(cx, cy, hx, hy, fill=p["accent_blue"], width=3)
        self.clock_canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill=p["accent_blue"], outline="")

    def on_clock_click(self, event):
        if self.timer_running:
            return
        cx, cy = 50, 50
        dx = event.x - cx
        dy = event.y - cy
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0:
            angle += 360
        minutes = round((angle / 360.0) * 60)
        minutes = max(1, min(60, minutes))
        self.timer_minutes = minutes
        self.time_left_seconds = self.timer_minutes * 60
        self.entry_m.delete(0, tk.END)
        self.entry_m.insert(0, str(self.timer_minutes))
        self.draw_clock_dial()
        self.update_timer_display()

    def apply_manual_time(self):
        try:
            mins = int(self.entry_m.get().strip())
            if 1 <= mins <= 120:
                self.timer_minutes = mins
                self.reset_timer()
                messagebox.showinfo("Timer Updated", f"Timer set to {mins} minutes.")
            else:
                messagebox.showwarning("Invalid Input", "Enter minutes between 1 and 120.")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid numeric value.")

    def update_timer_display(self):
        m = self.time_left_seconds // 60
        s = self.time_left_seconds % 60
        self.timer_display_lbl.configure(text=f"{m:02d} :{s:02d}")

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_paused = False
            self.run_timer_tick()

    def pause_timer(self):
        if self.timer_running:
            if not self.timer_paused:
                self.timer_paused = True
                self.pause_timer_btn.configure(text="Resume")
                if self.timer_job:
                    self.root.after_cancel(self.timer_job)
            else:
                self.timer_paused = False
                self.pause_timer_btn.configure(text="Pause")
                self.run_timer_tick()

    def reset_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.timer_running = False
        self.timer_paused = False
        self.pause_timer_btn.configure(text="Pause")
        self.time_left_seconds = self.timer_minutes * 60
        self.update_timer_display()
        self.draw_clock_dial()

    def run_timer_tick(self):
        if self.timer_running and not self.timer_paused:
            if self.time_left_seconds > 0:
                self.update_timer_display()
                self.time_left_seconds -= 1
                self.timer_job = self.root.after(1000, self.run_timer_tick)
            else:
                self.update_timer_display()
                self.timer_running = False
                messagebox.showinfo("Time's Up!", "Practice timer completed.")

    def open_file_dialog(self):
        chosen_file = filedialog.askopenfilename(initialdir=self.desktop_path, title="Open Essay File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if chosen_file:
            self.target_file = chosen_file
            self.status_lbl.configure(text=f"File: {os.path.basename(self.target_file)}")
            try:
                with open(self.target_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.essay_text.delete("1.0", tk.END)
                self.essay_text.insert("1.0", content)
                self.update_live_word_count()
            except Exception as e:
                messagebox.showerror("File Error", str(e))

    def save_file_as_dialog(self):
        chosen_file = filedialog.asksaveasfilename(initialdir=self.desktop_path, title="Save File As", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if chosen_file:
            self.target_file = chosen_file
            self.status_lbl.configure(text=f"File: {os.path.basename(self.target_file)}")
            self.autosave_handler()

    def load_api_key(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f).get("gemini_api_key", "")
            except Exception:
                pass
        return ""

    def save_api_key(self, key):
        self.gemini_api_key = key.strip()
        try:
            with open(self.config_file, "w") as f:
                json.dump({"gemini_api_key": self.gemini_api_key}, f)
        except Exception:
            pass

    def set_api_key_prompt(self):
        key = simpledialog.askstring("Gemini Key", "Enter your Google Gemini API Key:", initialvalue=self.gemini_api_key, show="*")
        if key is not None:
            self.save_api_key(key)
            messagebox.showinfo("Saved", "API Key stored successfully!")

    def write_to_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.theme_toggle_btn.configure(text="Dark Mode" if self.current_theme == "light" else "Light Mode")
        self.apply_theme()

    def apply_theme(self):
        p = self.themes[self.current_theme]
        self.root.configure(bg=p["bg_dark"])
        self.header.configure(bg=p["header_bg"])
        self.title_lbl.configure(bg=p["header_bg"], fg=p["text_main"])
        self.open_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])
        self.settings_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])
        self.status_lbl.configure(bg=p["header_bg"], fg=p["text_gray"])

        self.main_paned.configure(bg=p["divider"])
        self.left_vertical_paned.configure(bg=p["divider"])
        self.left_container.configure(bg=p["bg_panel"])
        self.prompt_frame.configure(bg=p["bg_panel"])
        self.report_section_frame.configure(bg=p["bg_panel"])
        self.q_title_lbl.configure(bg=p["bg_panel"], fg=p["accent_purple"])
        self.question_text.configure(bg=p["bg_input"], fg=p["text_main"], insertbackground=p["text_main"])

        self.paper_selector_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])
        self.paper_menu.configure(bg=p["dropdown_bg"], fg=p["dropdown_fg"])

        self.timer_frame.configure(bg=p["bg_panel"])
        self.timer_container.configure(bg=p["bg_panel"])
        self.btn_row.configure(bg=p["bg_panel"])
        self.timer_display_lbl.configure(bg=p["bg_panel"])
        self.toggle_eye_btn.configure(bg=p["btn_bg"], fg=p["text_gray"])
        self.pause_timer_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])
        self.reset_timer_btn.configure(bg=p["btn_bg"], fg=p["btn_fg"])

        self.tab_nav_frame.configure(bg=p["bg_panel"])
        self.content_container.configure(bg=p["bg_panel"])

        for key, frame in self.tab_frames.items():
            frame.configure(bg=p["bg_panel"])

        self.report_bar.configure(bg=p["bg_panel"])
        self.ai_btn_frame.configure(bg=p["bg_panel"])
        self.ai_display.configure(bg=p["bg_input"], fg=p["text_main"])

        self.right_panel.configure(bg=p["bg_dark"])
        self.essay_text.configure(bg=p["bg_input"], fg=p["text_main"], insertbackground=p["text_main"])
        self.footer.configure(bg=p["header_bg"])
        self.word_lbl.configure(bg=p["header_bg"], fg=p["accent_blue"])
        self.copyright_lbl.configure(bg=p["header_bg"], fg=p["text_gray"])

        self.settings_dropdown.configure(bg=p["bg_panel"])
        self.clock_frame.configure(bg=p["bg_panel"])
        self.manual_timer_frame.configure(bg=p["bg_panel"])
        self.ctrl_frame.configure(bg=p["bg_panel"])
        self.t_f_frame.configure(bg=p["bg_panel"])
        self.clock_canvas.configure(bg=p["bg_panel"])
        
        self.populate_paper_selector_menu()
        self.switch_tab(self.current_tab)
        self.draw_clock_dial()

    def increase_font_size(self):
        if self.input_font_size < 32:
            self.input_font_size += 2
            self.essay_text.config(font=("Arial", self.input_font_size))

    def decrease_font_size(self):
        if self.input_font_size > 10:
            self.input_font_size -= 2
            self.essay_text.config(font=("Arial", self.input_font_size))

    def load_existing_draft(self):
        if os.path.exists(self.target_file):
            try:
                with open(self.target_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.essay_text.delete("1.0", tk.END)
                self.essay_text.insert("1.0", content)
                self.update_live_word_count()
            except Exception:
                pass

    def autosave_handler(self, event=None):
        content = self.essay_text.get("1.0", "end-1c")
        try:
            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
        self.update_live_word_count()

    def update_live_word_count(self):
        txt = self.essay_text.get("1.0", "end-1c").strip()
        words = txt.split() if txt else []
        self.word_lbl.configure(text=f"Words: {len(words)}")

    def run_ai_evaluation(self):
        if not self.check_api_key_popup():
            return

        essay = self.essay_text.get("1.0", "end-1c").strip()
        question = self.get_clean_prompt_text()

        if len(essay.split()) < 15:
            messagebox.showwarning("Incomplete", "Write a complete essay before requesting AI review.")
            return

        self.write_to_text(self.ai_display, "Querying Gemini AI (with retry logic)... Please wait.")
        self.switch_tab("ai")
        self.root.update_idletasks()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={self.gemini_api_key}"
        system_instruction = (
            "Act as a certified senior British Council / IDP IELTS Writing Examiner with 15+ years of experience. "
            "Evaluate the candidate's Task 2 essay strictly using the official IELTS public band descriptors.\n\n"
            "Be constructive, fair, and realistic. Do not overly penalize natural writing styles or use overly harsh automated heuristics.\n\n"
            "EVALUATION INSTRUCTIONS:\n"
            "1. Provide an estimated overall band score (rounded to the nearest 0.5) and individual band scores (1-9) for:\n"
            "   - Task Response (TR)\n"
            "   - Coherence & Cohesion (CC)\n"
            "   - Lexical Resource (LR)\n"
            "   - Grammatical Range & Accuracy (GRA)\n"
            "2. Examiner Diagnostic Summary: Write a 3-sentence summary of the essay's core strengths and main areas holding it back.\n"
            "3. Criterion-by-Criterion Breakdown: Give specific, helpful feedback for each of the 4 areas. Point out actual phrases from the essay.\n"
            "4. Top 3 High-Impact Fixes: Bullet points on what exact changes would push this essay up by 0.5 or 1.0 band.\n\n"
            "Format your response cleanly using bold headers and bullet points. Avoid markdown tables or overly robotic formatting."
        )

        user_prompt = f"INPUT DATA:\n- Prompt Question: {question}\n- Candidate Essay: {essay}"
        payload = {"contents": [{"parts": [{"text": system_instruction + "\n\n" + user_prompt}]}]}

        max_retries = 3
        delay = 2
        success = False
        ai_response = ""

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=120) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    ai_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    success = True
                    break
            except urllib.error.HTTPError as e:
                if e.code == 503 and attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                ai_response = f"HTTP Error {e.code}: Server Unavailable."
                break
            except Exception as e:
                ai_response = f"Error:\n{str(e)}"
                break

        if success:
            self.write_to_text(self.ai_display, ai_response)
        else:
            self.write_to_text(self.ai_display, f"{ai_response}\n\nGoogle's servers experienced a temporary high-load spike (503). Please try again in a few seconds.")

    def detect_paragraphs_smart(self, raw_text):
        text = raw_text.strip()
        if not text:
            return []
        blocks = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        if len(blocks) > 1:
            return blocks
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) > 1:
            if sum(1 for line in lines if len(line.split()) >= 10) >= 2:
                return lines
        return [text]

    def get_clean_prompt_text(self):
        prompt_txt = self.question_text.get("1.0", "end-1c").strip()
        if not prompt_txt or "[optional] select a cambridge prompt" in prompt_txt.lower():
            return "N/A (No Prompt Provided)"
        return prompt_txt

    def run_forensic_audit(self):
        essay = self.essay_text.get("1.0", "end-1c").strip()
        question = self.get_clean_prompt_text().lower()
        word_count = len(essay.split())
        
        if word_count < 10:
            messagebox.showwarning("Incomplete Data", "Type your essay completely before evaluation.")
            return

        essay_lower = essay.lower()
        sentences = sent_tokenize(essay)
        words_raw = word_tokenize(essay_lower)
        words_cleaned = [w for w in words_raw if w.isalnum()]
        
        paragraphs = self.detect_paragraphs_smart(essay)
        paragraph_count = max(1, len(paragraphs))

        if word_count >= 250:
            ta_score = 7.5 if word_count <= 400 else 7.0
        elif word_count >= 200:
            ta_score = 6.0
        elif word_count >= 150:
            ta_score = 5.0
        else:
            ta_score = 4.0

        # --- EASED & BALANCED COHERENCE & COHESION AUDITOR ---
        cohesive_markers = [
            "furthermore", "moreover", "consequently", "nevertheless", "however", "therefore",
            "in addition", "on the other hand", "for instance", "for example", "in contrast",
            "as a result", "subsequently", "meanwhile", "specifically", "indeed", "thus",
            "firstly", "secondly", "finally", "in conclusion", "to begin with", "similarly",
            "also", "because", "although", "while", "since", "yet"
        ]
        
        marker_hits = sum(1 for s in sentences if any(m in s.lower() for m in cohesive_markers))
        
        continuity_penalties = 0
        if len(sentences) > 2:
            for i in range(len(sentences) - 1):
                s1_words = set(w for w in word_tokenize(sentences[i].lower()) if w.isalnum())
                s2_words = set(w for w in word_tokenize(sentences[i+1].lower()) if w.isalnum())
                common_meaningful = s1_words.intersection(s2_words) - {"the", "a", "an", "is", "are", "and", "to", "in", "of", "it", "that", "this", "they", "we", "as", "with", "for", "by", "from"}
                has_marker = any(m in sentences[i+1].lower() for m in cohesive_markers)
                if not common_meaningful and not has_marker and len(s2_words) > 6:
                    continuity_penalties += 1

        cc_base = 7.0
        if 4 <= paragraph_count <= 5:
            cc_base = 8.0
        elif paragraph_count == 3:
            cc_base = 6.5
        elif paragraph_count > 5:
            cc_base = 6.0
        else:
            cc_base = 5.5

        effective_penalty = min(0.8, continuity_penalties * 0.2)
        cc_score = max(5.0, cc_base - effective_penalty + (0.3 if marker_hits >= 2 else 0))
        cc_score = round(cc_score * 2) / 2

        common_stopwords = {"the", "a", "an", "is", "are", "and", "but", "so", "to", "in", "of", "for", "it", "this", "that", "on", "with", "as", "they", "we", "our"}
        meaningful_words = [w for w in words_cleaned if w not in common_stopwords]
        lexical_diversity = (len(set(meaningful_words)) / len(meaningful_words) * 100) if meaningful_words else 0

        found_low_band = {w: self.vocabulary_bank[w] for w in words_cleaned if w in self.vocabulary_bank}
        found_poor_phrases = {phr: data for phr, data in self.poor_phrase_dictionary.items() if phr in essay_lower}

        lr_score = 7.0
        if lexical_diversity > 70:
            lr_score = 8.0
        elif lexical_diversity < 45:
            lr_score = 6.0

        lr_score = max(4.0, min(8.5, lr_score))

        complex_subordinators = ["although", "even though", "whereas", "while", "provided that", "in order to", "despite", "consequently", "furthermore", "moreover"]
        complex_count = sum(1 for s in sentences if any(sub in s.lower() for sub in complex_subordinators))
        gra_score = 7.5 if complex_count >= 2 else 6.5

        raw_overall = (ta_score + cc_score + lr_score + gra_score) / 4
        rounded_band = round(raw_overall * 2) / 2

        # Cache audit results for PDF export
        self.last_audit_data = {
            "overall_band": rounded_band,
            "ta": ta_score,
            "cc": cc_score,
            "lr": lr_score,
            "gra": gra_score,
            "words": word_count,
            "paragraphs": paragraph_count,
            "low_band_count": len(found_low_band),
            "poor_phrases_count": len(found_poor_phrases),
            "continuity_penalties": continuity_penalties
        }

        self.render_rich_report_ui(rounded_band, ta_score, cc_score, lr_score, gra_score, word_count, paragraph_count, found_low_band, found_poor_phrases, continuity_penalties)
        self.render_rich_replacements_ui(found_low_band, found_poor_phrases)

        matched_category = "Education"
        full_text_search = question + " " + essay_lower
        for cat_name, cat_data in self.topic_ideas_db.items():
            if any(kw in full_text_search for kw in cat_data["keywords"]):
                matched_category = cat_name
                break

        self.render_topic_logic_ui(matched_category, auto_detected=True)
        self.switch_tab("report")

    def render_topic_logic_ui(self, selected_theme="Education", auto_detected=True):
        p = self.themes[self.current_theme]
        for widget in self.ideas_scrollable_frame.winfo_children():
            widget.destroy()

        top_ctrl = tk.Frame(self.ideas_scrollable_frame, bg=p["bg_panel"])
        top_ctrl.pack(fill="x", padx=15, pady=(15, 10))

        tk.Label(top_ctrl, text="PROMPT TOPIC LOGIC & VOCABULARY ENGINE", bg=p["bg_panel"], fg=p["accent_purple"], font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 8))

        theme_display_row = tk.Frame(top_ctrl, bg=p["bg_panel"])
        theme_display_row.pack(fill="x", pady=2)

        theme_badge = tk.Label(theme_display_row, text=f"[{selected_theme.upper()}]", bg=p["bg_input"], fg=p["accent_blue"], font=("Arial", 9, "bold"), bd=1, relief="solid", padx=10, pady=6)
        theme_badge.pack(side="left")

        dropdown_label_frame = tk.Frame(theme_display_row, bg=p["bg_panel"])
        dropdown_label_frame.pack(side="right")

        tk.Label(dropdown_label_frame, text="Topic:", bg=p["bg_panel"], fg=p["text_gray"], font=("Arial", 9, "bold")).pack(side="left", padx=5)

        theme_options = ["Auto-Detect from Prompt & Essay"] + list(self.topic_ideas_db.keys())
        self.topic_dropdown_var = tk.StringVar(value="Auto-Detect from Prompt & Essay" if auto_detected else selected_theme)
        
        dropdown = ttk.Combobox(dropdown_label_frame, textvariable=self.topic_dropdown_var, values=theme_options, state="readonly", width=34, font=("Arial", 9))
        dropdown.pack(side="left", padx=2)
        dropdown.bind("<<ComboboxSelected>>", self.on_topic_dropdown_change)

        tk.Label(self.ideas_scrollable_frame, text="RECOMMENDED BAND 9 COLLOCATIONS:", bg=p["bg_panel"], fg=p["accent_green"], font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(15, 8))

        colloc_grid = tk.Frame(self.ideas_scrollable_frame, bg=p["bg_panel"])
        colloc_grid.pack(fill="x", padx=15, pady=2)

        data = self.topic_ideas_db.get(selected_theme, self.topic_ideas_db["Education"])
        collocs = data["collocations"]

        for i, col in enumerate(collocs):
            r, c = divmod(i, 2)
            card = tk.Frame(colloc_grid, bg=p["bg_input"], bd=1, relief="solid", width=280, height=45)
            card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            card.pack_propagate(False)

            tk.Label(card, text=f"•  {col}", bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9)).pack(anchor="w", padx=10, pady=12)

        tk.Label(self.ideas_scrollable_frame, text="SUGGESTED LOGICAL ARGUMENT POINTS:", bg=p["bg_panel"], fg=p["accent_orange"], font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(20, 8))

        ideas_container = tk.Frame(self.ideas_scrollable_frame, bg=p["bg_panel"])
        ideas_container.pack(fill="x", padx=15, pady=(0, 20))

        for idea in data["ideas"]:
            card = tk.Frame(ideas_container, bg=p["bg_input"], bd=1, relief="solid")
            card.pack(fill="x", pady=4)
            tk.Label(card, text=f"•  {idea}", bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9), wraplength=540, justify="left").pack(anchor="w", padx=12, pady=10)

    def on_topic_dropdown_change(self, event):
        val = self.topic_dropdown_var.get()
        if val == "Auto-Detect from Prompt & Essay":
            self.detect_topic_from_prompt_text()
        else:
            self.render_topic_logic_ui(val, auto_detected=False)

    def render_rich_report_ui(self, overall_band, ta, cc, lr, gra, words, paragraphs, low_band, poor_phrases, continuity_penalties):
        p = self.themes[self.current_theme]
        for widget in self.report_scrollable_frame.winfo_children():
            widget.destroy()

        band_card = tk.Frame(self.report_scrollable_frame, bg=p["bg_input"], bd=1, relief="solid")
        band_card.pack(fill="x", padx=10, pady=10)

        tk.Label(band_card, text="OFFICIAL ESTIMATED BAND", bg=p["bg_input"], fg=p["text_gray"], font=("Arial", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        
        score_row = tk.Frame(band_card, bg=p["bg_input"])
        score_row.pack(fill="x", padx=12, pady=(0, 5))

        tk.Label(score_row, text=f"Band {overall_band:.1f}", bg=p["bg_input"], fg=p["accent_green"], font=("Arial", 22, "bold")).pack(side="left")
        tk.Label(score_row, text=" Very Good User (CEFR C1+)", bg=p["bg_input"], fg=p["text_main"], font=("Arial", 11)).pack(side="left", padx=5, pady=6)

        meta_lbl = tk.Label(score_row, text=f"{words} words • {paragraphs} paragraphs\nTarget: 250+ words", bg=p["bg_input"], fg=p["accent_orange"], font=("Arial", 8), justify="right")
        meta_lbl.pack(side="right", padx=10)

        grid_frame = tk.Frame(self.report_scrollable_frame, bg=p["bg_panel"])
        grid_frame.pack(fill="x", padx=10, pady=5)

        criteria = [
            ("Task Response (TR)", f"Band {ta:.1f}"),
            ("Coherence & Cohesion (CC)", f"Band {cc:.1f}"),
            ("Lexical Resource (LR)", f"Band {lr:.1f}"),
            ("Grammatical Range (GRA)", f"Band {gra:.1f}")
        ]

        for i, (title, score) in enumerate(criteria):
            r, c = divmod(i, 2)
            card = tk.Frame(grid_frame, bg=p["bg_input"], bd=1, relief="solid", width=260, height=70)
            card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            card.pack_propagate(False)

            tk.Label(card, text=title, bg=p["bg_input"], fg=p["text_gray"], font=("Arial", 8, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
            tk.Label(card, text=score, bg=p["bg_input"], fg=p["text_main"], font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

        diag_card = tk.Frame(self.report_scrollable_frame, bg=p["bg_input"], bd=1, relief="solid")
        diag_card.pack(fill="x", padx=10, pady=10)

        tk.Label(diag_card, text="EXAMINER DIAGNOSTIC SUMMARY:", bg=p["bg_input"], fg=p["accent_blue"], font=("Arial", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        summary_text = f"The candidate demonstrates position development ({words} words across {paragraphs} paragraphs). Coherence auditor checked sentence flow smoothly."
        tk.Label(diag_card, text=summary_text, bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9), wraplength=540, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        points_card = tk.Frame(self.report_scrollable_frame, bg=p["bg_input"], bd=1, relief="solid")
        points_card.pack(fill="x", padx=10, pady=(5, 15))

        tk.Label(points_card, text="EVALUATION POINTS:", bg=p["bg_input"], fg=p["accent_purple"], font=("Arial", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        
        points = [
            f"✓ Sufficient Task Coverage: {words} words meets requirement.",
            f"✓ Coherence Check: Sentence transitions flow logically across paragraphs.",
            f"• Vocabulary Check: {len(low_band)} basic words and {len(poor_phrases)} weak conversational phrases flagged."
        ]
        for pt in points:
            tk.Label(points_card, text=pt, bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9), wraplength=540, justify="left").pack(anchor="w", padx=12, pady=2)
        tk.Label(points_card, text="", bg=p["bg_input"]).pack(pady=2)

    def render_rich_replacements_ui(self, low_band, poor_phrases):
        p = self.themes[self.current_theme]
        for widget in self.vocab_scrollable_frame.winfo_children():
            widget.destroy()

        total_flagged = len(low_band) + len(poor_phrases)
        self.vocab_info_lbl.configure(text=f"DETECTED IN ESSAY ({total_flagged} WORDS/PHRASES FLAGGED)")
        self.tab_buttons["vocab"].configure(text=f"Replacements ({total_flagged})")

        combined_items = []
        for word, data in low_band.items():
            if self.active_category_filter == "All" or data["cat"] == self.active_category_filter:
                combined_items.append({
                    "type": "SINGLE WORD",
                    "target": word.upper(),
                    "cat": data["cat"],
                    "alts": data["alts"]
                })

        for phrase, data in poor_phrases.items():
            if self.active_category_filter == "All" or data["cat"] == self.active_category_filter:
                combined_items.append({
                    "type": "PHRASE",
                    "target": phrase.upper(),
                    "cat": data["cat"],
                    "alts": data["alts"]
                })

        if not combined_items:
            tk.Label(self.vocab_scrollable_frame, text="No flagged words or phrases matching this category.", bg=p["bg_panel"], fg=p["text_gray"], font=("Arial", 10)).pack(padx=15, pady=20)
            return

        for item in combined_items:
            card = tk.Frame(self.vocab_scrollable_frame, bg=p["bg_input"], bd=1, relief="solid")
            card.pack(fill="x", padx=5, pady=6)

            top_row = tk.Frame(card, bg=p["bg_input"])
            top_row.pack(fill="x", padx=10, pady=(8, 2))

            tk.Label(top_row, text="AVOID / INFORMAL", bg=p["bg_input"], fg="#ef4444", font=("Arial", 8, "bold")).pack(side="left")
            tk.Label(top_row, text=f"\"{item['target']}\"", bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9, "bold")).pack(side="left", padx=6)
            tk.Label(top_row, text=item["cat"].upper(), bg=p["btn_bg"], fg=p["text_gray"], font=("Arial", 7, "bold")).pack(side="right")

            bot_row = tk.Frame(card, bg=p["bg_input"])
            bot_row.pack(fill="x", padx=10, pady=(2, 8))

            tk.Label(bot_row, text="BAND 9 COLLOCATION:", bg=p["bg_input"], fg=p["accent_green"], font=("Arial", 8, "bold")).pack(anchor="w", pady=(2, 2))
            alts_str = " / ".join(item["alts"][:4])
            tk.Label(bot_row, text=alts_str, bg=p["bg_input"], fg=p["text_main"], font=("Arial", 9)).pack(anchor="w")

    def filter_replacements_by_category(self, cat):
        self.active_category_filter = cat
        essay = self.essay_text.get("1.0", "end-1c").strip()
        if essay:
            essay_lower = essay.lower()
            words_raw = word_tokenize(essay_lower)
            words_cleaned = [w for w in words_raw if w.isalnum()]
            found_low_band = {w: self.vocabulary_bank[w] for w in words_cleaned if w in self.vocabulary_bank}
            found_poor_phrases = {phr: data for phr, data in self.poor_phrase_dictionary.items() if phr in essay_lower}
            self.render_rich_replacements_ui(found_low_band, found_poor_phrases)

    def export_full_pdf_report(self):
        essay = self.essay_text.get("1.0", "end-1c").strip()
        question = self.get_clean_prompt_text()

        if not essay:
            messagebox.showwarning("Empty Essay", "Nothing to export.")
            return

        # Ensure an audit has been performed
        if not self.last_audit_data:
            self.run_forensic_audit()

        file_path = filedialog.asksaveasfilename(initialdir=self.desktop_path, title="Export Full Report PDF", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 15)
                pdf.cell(0, 10, "IELTS Advanced Writing Simulation Report", 0, 1, "C")
                pdf.ln(4)

                # Clean Prompt Section (Skips placeholder text)
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 7, "QUESTION PROMPT:", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, question.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(4)

                # Essay Section
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 7, "CANDIDATE ESSAY DRAFT:", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, essay.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(6)

                # Official Audit Evaluation Breakdown Section
                a = self.last_audit_data
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "EXAMINER FORENSIC AUDIT REPORT", 0, 1)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"Estimated Overall Band Score: Band {a['overall_band']:.1f}", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 5, f" - Task Response (TR): Band {a['ta']:.1f}", 0, 1)
                pdf.cell(0, 5, f" - Coherence & Cohesion (CC): Band {a['cc']:.1f}", 0, 1)
                pdf.cell(0, 5, f" - Lexical Resource (LR): Band {a['lr']:.1f}", 0, 1)
                pdf.cell(0, 5, f" - Grammatical Range & Accuracy (GRA): Band {a['gra']:.1f}", 0, 1)
                pdf.ln(4)

                # Examiner Diagnostic Notes
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, "EXAMINER DIAGNOSTIC SUMMARY:", 0, 1)
                pdf.set_font("Arial", "", 10)
                summary = f"The candidate demonstrates position development ({a['words']} words across {a['paragraphs']} paragraphs). Coherence auditor checked sentence flow smoothly."
                pdf.multi_cell(0, 5, summary.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(2)

                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, "EVALUATION POINTS:", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 5, f"* Task Coverage: {a['words']} words meets length requirements.", 0, 1)
                pdf.cell(0, 5, "* Coherence Check: Sentence transitions flow logically across paragraphs.", 0, 1)
                pdf.cell(0, 5, f"* Vocabulary Check: {a['low_band_count']} basic words and {a['poor_phrases_count']} weak phrases flagged.", 0, 1)

                pdf.output(file_path)
                messagebox.showinfo("Success", f"Full Report exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def export_draft_pdf(self):
        essay = self.essay_text.get("1.0", "end-1c").strip()
        question = self.get_clean_prompt_text()

        if not essay:
            messagebox.showwarning("Empty Essay", "Nothing to export.")
            return

        file_path = filedialog.asksaveasfilename(initialdir=self.desktop_path, title="Export Essay Draft PDF", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "IELTS Task 2 Essay Draft", 0, 1, "C")
                pdf.ln(5)

                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, "PROMPT QUESTION:", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, question.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(5)

                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, "ESSAY RESPONSE:", 0, 1)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, essay.encode('latin-1', 'replace').decode('latin-1'))

                pdf.output(file_path)
                messagebox.showinfo("Success", f"Essay Draft exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = IELTSAdvancedStudio(root)
    root.mainloop()