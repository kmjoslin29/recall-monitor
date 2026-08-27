"""
reference_data.py
-----------------
Shared lookups and classifiers used by the fetcher, the workbook builder,
and the dashboard builder. Keeping them in one place means the spreadsheet
and the dashboard always agree.

Everything here is curated reference data with a stated confidence level,
following the four-tier convention:
    well-established | supported-but-contested | low-confidence | speculative

Sources for the hazard->illness table are CDC and FDA/USDA consumer pages
(general, textbook-level facts about foodborne pathogens). They are
"well-established" but are educational summaries, not medical advice.
"""

# ---------------------------------------------------------------------------
# US state -> Census region  (region is DERIVED from where a recall was
# distributed, per the chosen design. "Nationwide" is handled separately.)
# ---------------------------------------------------------------------------

STATE_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC", "washington dc": "DC", "washington d.c.": "DC",
    "puerto rico": "PR", "guam": "GU", "virgin islands": "VI",
}

ABBR_SET = set(STATE_ABBR.values())

REGION_OF = {}
for _st in ["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"]:
    REGION_OF[_st] = "Northeast"
for _st in ["IL", "IN", "MI", "OH", "WI", "IA", "KS", "MN", "MO", "NE", "ND", "SD"]:
    REGION_OF[_st] = "Midwest"
for _st in ["DE", "FL", "GA", "MD", "NC", "SC", "VA", "DC", "WV", "AL",
            "KY", "MS", "TN", "AR", "LA", "OK", "TX"]:
    REGION_OF[_st] = "South"
for _st in ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY", "AK", "CA",
            "HI", "OR", "WA"]:
    REGION_OF[_st] = "West"
for _st in ["PR", "GU", "VI"]:
    REGION_OF[_st] = "Territories"

REGIONS_ORDER = ["Northeast", "Midwest", "South", "West", "Territories",
                 "Nationwide", "Unknown"]


def parse_states(text):
    """Best-effort extraction of state abbreviations from free text.

    FDA `distribution_pattern` is unstructured prose ("Nationwide",
    "the states of CA, NV and AZ", "TX and OK"). USDA `field_states` is a
    clean comma-separated list of full state names. This handles both.

    Returns (set_of_abbr, is_nationwide).
    """
    if not text:
        return set(), False
    low = text.lower()
    nationwide = any(k in low for k in
                     ("nationwide", "nation wide", "national distribution",
                      "throughout the united states", "all 50 states",
                      "throughout the u.s", "throughout the us"))
    found = set()
    # Full state names first (handles USDA and prose).
    for name, abbr in STATE_ABBR.items():
        if name in low:
            found.add(abbr)
    # Then bare two-letter codes as whole words (handles terse FDA prose).
    import re
    for tok in re.findall(r"\b[A-Z]{2}\b", text):
        if tok in ABBR_SET:
            found.add(tok)
    return found, nationwide


def regions_for(states, nationwide):
    """Map a set of state abbreviations to the set of Census regions."""
    if nationwide:
        return ["Nationwide"]
    regions = sorted({REGION_OF.get(s, "Unknown") for s in states})
    return regions or ["Unknown"]


# ---------------------------------------------------------------------------
# Food-type categorization (derived from product description keywords).
# FDA/USDA do not provide a granular food-type field, so this is best-effort.
# Order matters: earlier rules win.
# ---------------------------------------------------------------------------

FOOD_TYPE_RULES = [
    ("Infant & Baby Food", ["infant formula", "baby food", "infant", "toddler formula"]),
    ("Pet & Animal Food", ["pet food", "dog food", "cat food", "dog treat",
                            "cat treat", "animal feed", "pet treat", "kibble",
                            "canine", "feline"]),
    ("Dietary Supplements", ["supplement", "vitamin", "capsule", "softgel",
                             "gummies", "probiotic", "herbal"]),
    ("Seafood", ["fish", "salmon", "tuna", "shrimp", "crab", "lobster",
                 "oyster", "clam", "mussel", "scallop", "seafood", "tilapia",
                 "catfish", "cod", "anchovy", "sardine", "smoked fish"]),
    ("Poultry", ["chicken", "turkey", "poultry", "duck", "hen"]),
    ("Meat", ["beef", "pork", "bacon", "sausage", "ham", "steak", "ground beef",
              "veal", "lamb", "goat", "meat", "jerky", "hot dog", "frankfurter",
              "salami", "pepperoni", "brisket", "ribs", "bison"]),
    ("Dairy & Eggs", ["milk", "cheese", "yogurt", "butter", "cream", "dairy",
                      "egg", "ice cream", "kefir", "custard"]),
    ("Produce", ["lettuce", "spinach", "onion", "tomato", "cucumber", "melon",
                 "cantaloupe", "pepper", "carrot", "apple", "berry", "berries",
                 "peach", "mango", "sprout", "leafy green", "salad mix",
                 "vegetable", "fruit", "produce", "avocado", "potato",
                 "mushroom", "cilantro", "herb", "grape"]),
    ("Nuts, Seeds & Butters", ["peanut", "almond", "cashew", "walnut", "pecan",
                               "pistachio", "nut butter", "tahini", "seed",
                               "sunflower", "trail mix", "granola bar"]),
    ("Bakery & Grains", ["bread", "flour", "cereal", "cracker", "cookie",
                         "cake", "muffin", "pasta", "rice", "oat", "grain",
                         "tortilla", "bagel", "pastry", "dough", "pizza"]),
    ("Snacks & Confectionery", ["chip", "snack", "candy", "chocolate", "popcorn",
                                "pretzel", "confection", "caramel"]),
    ("Beverages", ["juice", "beverage", "drink", "soda", "water", "coffee",
                   "tea", "smoothie", "kombucha", "cider"]),
    ("Condiments, Sauces & Spices", ["sauce", "dressing", "condiment", "spice",
                                     "seasoning", "salsa", "dip", "hummus",
                                     "gravy", "marinade", "ketchup", "mustard",
                                     "mayonnaise", "pickle"]),
    ("Prepared & Ready-to-Eat", ["ready-to-eat", "ready to eat", "rte",
                                 "prepared", "frozen meal", "entree", "soup",
                                 "wrap", "sandwich", "burrito", "sushi",
                                 "deli", "meal kit"]),
]


def categorize_food(description):
    if not description:
        return "Uncategorized"
    low = description.lower()
    for label, keywords in FOOD_TYPE_RULES:
        if any(k in low for k in keywords):
            return label
    return "Other / Multiple"


# ---------------------------------------------------------------------------
# Hazard categorization + pathogen/allergen extraction (derived from the
# recall reason text). A single recall can be biological AND allergen; we
# pick the primary category by priority, and also record the specific agent.
# ---------------------------------------------------------------------------

PATHOGENS = {
    "Listeria monocytogenes": ["listeria"],
    "Salmonella": ["salmonella"],
    "E. coli (STEC/O157:H7)": ["e. coli", "e.coli", "escherichia", "stec",
                               "o157", "shiga toxin"],
    "Clostridium botulinum": ["botulinum", "botulism"],
    "Hepatitis A virus": ["hepatitis a", "hepatitis"],
    "Norovirus": ["norovirus"],
    "Cronobacter sakazakii": ["cronobacter"],
    "Staphylococcus aureus": ["staphylococcus", "staph "],
    "Cyclospora": ["cyclospora"],
    "Bacillus cereus": ["bacillus cereus"],
    "Vibrio": ["vibrio"],
    "Clostridium perfringens": ["perfringens"],
}

ALLERGENS = ["milk", "egg", "soy", "wheat", "gluten", "peanut", "tree nut",
             "almond", "cashew", "walnut", "pecan", "hazelnut", "fish",
             "shellfish", "crustacean", "sesame", "sulfite", "mustard",
             "coconut", "pistachio"]


def classify_hazard(reason):
    """Return (hazard_category, specific_agent) from the recall reason text."""
    if not reason:
        return "Unspecified", ""
    low = reason.lower()

    # 1) Biological / pathogen (highest severity priority)
    for agent, keys in PATHOGENS.items():
        if any(k in low for k in keys):
            return "Biological (pathogen)", agent

    # 2) Undeclared allergen
    if "allerg" in low or "undeclared" in low or "unreported" in low or "misbrand" in low:
        for a in ALLERGENS:
            if a in low:
                return "Undeclared allergen", a.title()
        if "allerg" in low:
            return "Undeclared allergen", "Unspecified allergen"

    # 3) Foreign material
    if any(k in low for k in ["foreign material", "foreign matter", "metal",
                              "plastic", "glass", "wood", "rubber", "bone",
                              "extraneous"]):
        return "Foreign material", ""

    # 4) Chemical / contaminant
    if any(k in low for k in ["chemical", "benzene", "lead", "arsenic",
                              "cadmium", "heavy metal", "pesticide", "toxin",
                              "aflatoxin", "cleaning", "sanitizer", "melamine",
                              "per- and polyfluoro", "pfas"]):
        return "Chemical / contaminant", ""

    # 5) Processing / production
    if any(k in low for k in ["without benefit of inspection",
                              "without the benefit of inspection",
                              "not presented for import", "import violation",
                              "underprocess", "undercook", "temperature abuse",
                              "insanitary", "unsanitary", "adulterat"]):
        return "Processing / production", ""

    # 6) Labeling / quality (non-allergen)
    if any(k in low for k in ["mislabel", "label", "spoil", "mold", "off-odor",
                              "quality", "expired", "date", "packaging"]):
        return "Labeling / quality", ""

    return "Other / Unspecified", ""


# ---------------------------------------------------------------------------
# Hazard -> potential illness reference (educational; CDC/FDA/USDA level).
# confidence: all "well-established" textbook facts. NOT medical advice.
# Fields: agent, category, illness, typical symptoms, usual onset,
#         higher-risk groups, source.
# ---------------------------------------------------------------------------

HAZARD_ILLNESS = [
    {
        "agent": "Listeria monocytogenes",
        "category": "Biological (pathogen)",
        "illness": "Listeriosis",
        "symptoms": "Fever, muscle aches, sometimes diarrhea; can spread to the "
                    "nervous system (headache, stiff neck, confusion).",
        "onset": "Same day up to ~10 weeks (median ~1-4 weeks)",
        "higher_risk": "Pregnant people, newborns, adults 65+, immunocompromised. "
                       "Can cause miscarriage/stillbirth.",
        "confidence": "well-established",
        "source": "CDC Listeria; FDA",
    },
    {
        "agent": "Salmonella",
        "category": "Biological (pathogen)",
        "illness": "Salmonellosis",
        "symptoms": "Diarrhea (sometimes bloody), fever, stomach cramps, vomiting.",
        "onset": "6 hours - 6 days",
        "higher_risk": "Children under 5, adults 65+, immunocompromised.",
        "confidence": "well-established",
        "source": "CDC Salmonella; USDA FSIS",
    },
    {
        "agent": "E. coli (STEC/O157:H7)",
        "category": "Biological (pathogen)",
        "illness": "Shiga toxin-producing E. coli infection",
        "symptoms": "Severe stomach cramps, diarrhea (often bloody), vomiting.",
        "onset": "3-4 days (range 1-10)",
        "higher_risk": "Young children and older adults at risk of hemolytic "
                       "uremic syndrome (HUS), a type of kidney failure.",
        "confidence": "well-established",
        "source": "CDC E. coli",
    },
    {
        "agent": "Clostridium botulinum",
        "category": "Biological (pathogen)",
        "illness": "Botulism",
        "symptoms": "Double/blurred vision, drooping eyelids, slurred speech, "
                    "difficulty swallowing, muscle weakness. A medical emergency.",
        "onset": "18-36 hours (range 6 hours - 10 days)",
        "higher_risk": "Anyone; infants at special risk from certain foods. "
                       "Can cause paralysis and be fatal.",
        "confidence": "well-established",
        "source": "CDC Botulism",
    },
    {
        "agent": "Hepatitis A virus",
        "category": "Biological (pathogen)",
        "illness": "Hepatitis A",
        "symptoms": "Fatigue, nausea, stomach pain, jaundice (yellow skin/eyes), "
                    "dark urine.",
        "onset": "15-50 days (average ~28)",
        "higher_risk": "Unvaccinated people; more severe in older adults and "
                       "those with liver disease.",
        "confidence": "well-established",
        "source": "CDC Hepatitis A",
    },
    {
        "agent": "Norovirus",
        "category": "Biological (pathogen)",
        "illness": "Norovirus gastroenteritis",
        "symptoms": "Sudden vomiting, diarrhea, nausea, stomach pain.",
        "onset": "12-48 hours",
        "higher_risk": "Very contagious; dehydration risk in young children and "
                       "older adults.",
        "confidence": "well-established",
        "source": "CDC Norovirus",
    },
    {
        "agent": "Cronobacter sakazakii",
        "category": "Biological (pathogen)",
        "illness": "Cronobacter infection",
        "symptoms": "In infants: fever, poor feeding, crying, low energy; can "
                    "cause sepsis or meningitis.",
        "onset": "Days",
        "higher_risk": "Infants (especially <2 months), premature babies, "
                       "immunocompromised. Linked to powdered infant formula.",
        "confidence": "well-established",
        "source": "CDC Cronobacter; FDA",
    },
    {
        "agent": "Staphylococcus aureus",
        "category": "Biological (pathogen)",
        "illness": "Staphylococcal food poisoning",
        "symptoms": "Sudden nausea, vomiting, stomach cramps; usually short-lived.",
        "onset": "30 minutes - 8 hours",
        "higher_risk": "Anyone; caused by a toxin, so cooking does not always "
                       "make food safe.",
        "confidence": "well-established",
        "source": "CDC Staph",
    },
    {
        "agent": "Cyclospora",
        "category": "Biological (pathogen)",
        "illness": "Cyclosporiasis",
        "symptoms": "Watery diarrhea, loss of appetite, cramping, fatigue; can "
                    "relapse.",
        "onset": "~1 week",
        "higher_risk": "Often linked to fresh produce; anyone exposed.",
        "confidence": "well-established",
        "source": "CDC Cyclospora",
    },
    {
        "agent": "Undeclared allergen",
        "category": "Undeclared allergen",
        "illness": "Allergic reaction (up to anaphylaxis)",
        "symptoms": "Hives, swelling, vomiting, trouble breathing; severe "
                    "reactions (anaphylaxis) can be life-threatening.",
        "onset": "Seconds to ~2 hours after eating",
        "higher_risk": "People allergic to the undeclared ingredient (e.g., milk, "
                       "egg, peanut, tree nut, soy, wheat, fish, shellfish, sesame).",
        "confidence": "well-established",
        "source": "FDA Food Allergies; FASTER Act (sesame, 2023)",
    },
    {
        "agent": "Foreign material",
        "category": "Foreign material",
        "illness": "Physical injury / choking",
        "symptoms": "Choking, dental damage, cuts, or internal injury from metal, "
                    "plastic, glass, etc.",
        "onset": "On consumption",
        "higher_risk": "Anyone; higher concern for children.",
        "confidence": "well-established",
        "source": "FDA / USDA FSIS recall classifications",
    },
]


# ---------------------------------------------------------------------------
# FDA/USDA recall class definitions (verbatim-style paraphrase).
# ---------------------------------------------------------------------------

CLASS_DEFINITIONS = [
    ("Class I", "Reasonable probability that use will cause serious adverse "
                "health consequences or death. (Highest severity.)"),
    ("Class II", "Use may cause temporary or medically reversible adverse "
                 "health consequences; serious harm is unlikely."),
    ("Class III", "Use is not likely to cause adverse health consequences "
                  "(e.g., minor labeling issues)."),
    ("Public Health Alert (USDA)", "Issued when there is a health concern but a "
                                   "recall cannot yet be recommended (e.g., "
                                   "source not confirmed)."),
]


# ---------------------------------------------------------------------------
# Policy / regulatory timeline. This is the "watch the rules while you watch
# the trends" layer. Two of these items double as TREND CONFOUNDERS: they can
# change how many recalls get *reported* independent of actual food safety.
# Each entry: date, title, summary, effect_on_recalls, confidence, source.
# confidence reflects how directly the item bears on recall COUNTS.
# ---------------------------------------------------------------------------

POLICY_TIMELINE = [
    {
        "date": "2022-11-21",
        "title": "FSMA 204 Food Traceability Final Rule published",
        "summary": "Enhanced farm-to-fork recordkeeping (Key Data Elements at "
                   "Critical Tracking Events) for high-risk 'Food Traceability "
                   "List' foods; designed to speed traceback from weeks to days.",
        "effect_on_recalls": "When in force, expected to make recalls faster and "
                             "more precise, not necessarily more or fewer.",
        "confidence": "well-established",
        "source": "FDA; 87 FR 70910",
    },
    {
        "date": "2025-03-20",
        "title": "FDA announces intent to delay FSMA 204 compliance by 30 months",
        "summary": "Compliance date proposed to move from Jan 20, 2026 to "
                   "July 20, 2028, citing industry-wide readiness/coordination.",
        "effect_on_recalls": "Delays the traceability improvements that would "
                             "sharpen recall response.",
        "confidence": "well-established",
        "source": "FDA Constituent Update, Mar 2025",
    },
    {
        "date": "2025-08-07",
        "title": "Proposed rule to extend FSMA 204 to July 20, 2028 published",
        "summary": "Formal Notice of Proposed Rulemaking in the Federal Register; "
                   "comment period closed Sep 8, 2025.",
        "effect_on_recalls": "Procedural step toward the delay.",
        "confidence": "well-established",
        "source": "90 FR / Federal Register, Aug 7, 2025",
    },
    {
        "date": "2025-11-12",
        "title": "Longest US government shutdown ends; FY2026 appropriations",
        "summary": "Appropriations act codifies the FSMA 204 delay (no enforcement "
                   "funds before July 20, 2028) and restricts enforcement funds "
                   "for the Produce Safety Rule and pre-harvest agricultural water "
                   "rule for certain commodities. FDA Human Foods Program funded "
                   "at ~$1.17B for FY2026.",
        "effect_on_recalls": "CONFOUNDER: a prolonged shutdown can suppress recall "
                             "*reporting/classification* for weeks, independent of "
                             "actual food safety.",
        "confidence": "supported-but-contested",
        "source": "P.L. 119-37, Div. B; CRS R48925",
    },
    {
        "date": "2026-01-20",
        "title": "Original FSMA 204 compliance date (now not enforced)",
        "summary": "The date the rule would have taken effect absent the delay. "
                   "Congress directed FDA not to enforce before July 20, 2028.",
        "effect_on_recalls": "No traceability step-change occurs on this date.",
        "confidence": "well-established",
        "source": "FDA; P.L. 119-37",
    },
    {
        "date": "2025-2026",
        "title": "Proposed FDA budget cut and FDA/USDA staffing reductions",
        "summary": "Draft FY2026 budget documents proposed a ~17% FDA cut; "
                   "workforce reductions at FDA and USDA reported. Some routine "
                   "food-facility inspection potentially shifting to states.",
        "effect_on_recalls": "CONFOUNDER: reduced inspection/lab capacity can lower "
                             "the number of recalls that get detected and issued, "
                             "which is NOT the same as safer food.",
        "confidence": "supported-but-contested",
        "source": "Reporting on FY2026 budget drafts; CRS",
    },
    {
        "date": "2028-07-20",
        "title": "Extended FSMA 204 compliance date",
        "summary": "New enforcement date for the Food Traceability Rule.",
        "effect_on_recalls": "From here, faster/more-precise recalls expected once "
                             "traceability records are in force.",
        "confidence": "well-established",
        "source": "P.L. 119-37; FDA",
    },
]


# Convenience: agent -> illness row, for quick joins in the builders.
ILLNESS_BY_AGENT = {row["agent"]: row for row in HAZARD_ILLNESS}
