import streamlit as st
from serpapi import GoogleSearch
import os
import dotenv
import re

dotenv.load_dotenv()

# =========================
# 🧠 AUTO DORK GENERATOR
# =========================
def generate_dorks_from_input(user_input):
    base_keywords = re.findall(r'\w+', user_input.lower())

    dorks = []

    for word in base_keywords:
        dorks.extend([
            f'intitle:"{word}"',
            f'inurl:"{word}"',
            f'site:{word}.com "{word}"',
            f'"{word}" events',
        ])

    # Combine keywords (advanced dorks)
    if len(base_keywords) >= 2:
        joined = " ".join(base_keywords)
        dorks.extend([
            f'intitle:"{joined}"',
            f'"{joined}" events',
            f'inurl:event "{joined}"',
        ])

    return list(set(dorks))[:10]


# =========================
# 🌐 SERP FETCH
# =========================
def fetch_serp_results(dorks):
    serpapi_key = os.getenv("SERPAPI_KEY") or st.secrets.get("SERPAPI_KEY")

    if not serpapi_key:
        st.error("Missing SERPAPI_KEY")
        return []

    all_results = []

    for dork in dorks:
        params = {
            "api_key": serpapi_key,
            "engine": "google",
            "q": dork,
            "hl": "en",
            "gl": "in",
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results:
            for item in results["organic_results"][:3]:
                all_results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source_dork": dork
                })

    return all_results


# =========================
# 🧹 PARSER + FILTER
# =========================
def parse_results(results):
    seen = set()
    cleaned = []

    for r in results:
        if not r["link"] or r["link"] in seen:
            continue

        seen.add(r["link"])

        # Basic relevance filter
        if any(word in r["title"].lower() for word in ["event", "fest", "conference", "workshop"]):
            cleaned.append(r)

    return cleaned[:10]


# =========================
# 🎨 STREAMLIT UI
# =========================
def main():
    st.set_page_config(page_title="Auto Dork Engine", page_icon="🧠")

    st.title("🧠 Dynamic Google Dork Engine")
    st.write("Input → Dork → SERP → Parsed Results")

    user_input = st.text_input("Enter query", placeholder="e.g., tech events Delhi")

    if st.button("Run Engine"):
        if not user_input:
            st.warning("Enter something")
            return

        # Step 1: Generate dorks
        dorks = generate_dorks_from_input(user_input)

        st.subheader("🔍 Generated Dorks")
        for d in dorks:
            st.code(d)

        # Step 2: Fetch results
        with st.spinner("Fetching results..."):
            raw_results = fetch_serp_results(dorks)

        if not raw_results:
            st.warning("No results found")
            return

        # Step 3: Parse results
        parsed = parse_results(raw_results)

        # Step 4: Display
        st.subheader("📊 Parsed Results")

        for i, r in enumerate(parsed, 1):
            st.markdown(f"""
**{i}. {r['title']}**  
{r['snippet']}  
🔗 {r['link']}  
🧠 Dork Used: `{r['source_dork']}`
""")


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    main()
