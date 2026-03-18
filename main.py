import streamlit as st
from serpapi import GoogleSearch
import os
import dotenv
import re
import json
from datetime import datetime
import time

dotenv.load_dotenv()

# =========================
# 🔍 SAFE OSINT DORK GENERATOR
# =========================
class OSINTDorker:
    def __init__(self):
        self.categories = {
            "general": [
                'site:linkedin.com "{}"',
                'site:github.com "{}"',
                'site:twitter.com "{}"',
                '"{}" news',
                '"{}" interview',
            ],
            "documents": [
                '"{}" filetype:pdf',
                '"{}" filetype:ppt',
                '"{}" filetype:docx',
            ],
            "tech": [
                '"{}" "technology stack"',
                '"{}" "uses"',
                '"{}" software',
            ],
            "company": [
                '"{}" about',
                '"{}" team',
                '"{}" careers',
            ]
        }

    def generate_dorks(self, target, category="general"):
        words = list(set(re.findall(r'\w+', target.lower())))
        dorks = []

        if category == "all":
            for cat in self.categories.values():
                for pattern in cat:
                    dorks.append(pattern.format(target))
        elif category in self.categories:
            for pattern in self.categories[category]:
                dorks.append(pattern.format(target))

        # add word-based variations
        for w in words:
            dorks.append(f'"{w}" {target}')

        return list(set(dorks))[:30]


# =========================
# 🔎 SERP FETCH
# =========================
def fetch_results(dorks, api_key, max_results=5):
    results_data = []

    for i, dork in enumerate(dorks):
        if i >= 10:  # limit usage
            break

        try:
            params = {
                "api_key": api_key,
                "engine": "google",
                "q": dork,
                "num": max_results
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            if "organic_results" in results:
                for item in results["organic_results"]:
                    results_data.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "dork": dork
                    })

            time.sleep(1)

        except Exception as e:
            st.warning(f"Error: {str(e)}")
            time.sleep(1)

    return results_data


# =========================
# 📊 SIMPLE ANALYZER
# =========================
def analyze_results(results):
    analyzed = []

    for r in results:
        score = 0
        tags = []

        text = (r["title"] + " " + r["snippet"]).lower()

        if "github" in r["link"]:
            score += 2
            tags.append("code")

        if "pdf" in r["link"]:
            score += 1
            tags.append("document")

        if "news" in text:
            score += 1
            tags.append("news")

        r.update({
            "score": score,
            "tags": tags
        })

        analyzed.append(r)

    return sorted(analyzed, key=lambda x: x["score"], reverse=True)


# =========================
# 🚀 STREAMLIT UI
# =========================
def main():
    st.set_page_config(page_title="OSINT Dorker", layout="wide")

    st.title("🔍 OSINT Research Tool")
    st.markdown("Safe Google search automation for research & analysis")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        category = st.selectbox(
            "Category",
            ["all", "general", "documents", "tech", "company"]
        )
        max_dorks = st.slider("Max Dorks", 5, 30, 15)

    # Input
    target = st.text_input("🎯 Target", placeholder="company name, keyword...")

    execute = st.button("🚀 Search", use_container_width=True)

    if execute:
        if not target:
            st.error("Enter a target")
            return

        api_key = os.getenv("SERPAPI_KEY")

        if not api_key:
            try:
                api_key = st.secrets["SERPAPI_KEY"]
            except:
                api_key = None

        if not api_key:
            st.error("Missing SERPAPI_KEY")
            return

        # Generate dorks
        dorker = OSINTDorker()
        dorks = dorker.generate_dorks(target, category)[:max_dorks]

        st.subheader("🧠 Generated Queries")
        for d in dorks:
            st.code(d)

        # Fetch
        with st.spinner("Searching..."):
            results = fetch_results(dorks, api_key)

        if not results:
            st.warning("No results")
            return

        # Analyze
        analyzed = analyze_results(results)

        st.subheader("📊 Results")

        for r in analyzed:
            with st.expander(f"{r['title']} ⭐{r['score']}"):
                st.markdown(f"""
                **Query:** `{r['dork']}`  
                **Link:** {r['link']}  
                **Snippet:** {r['snippet']}  

                **Tags:** {', '.join(r['tags'])}
                """)

        # Export
        st.download_button(
            "💾 Download JSON",
            data=json.dumps(analyzed, indent=2),
            file_name=f"osint_{target}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
