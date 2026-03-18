import streamlit as st
from serpapi import GoogleSearch
import os
import dotenv
import re
from datetime import datetime
import time

dotenv.load_dotenv()

# =========================
# 🏴‍☠️ ADVANCED RED TEAM DORKER
# =========================
class RedHatDorker:
    def __init__(self):
        self.attack_vectors = {
            # Red Hat/CentOS/RHEL specific
            "rhel": [
                'inurl:phpinfo "Red Hat"',
                'intitle:"index of" intext:"redhat"',
                '"Red Hat Enterprise Linux" filetype:conf',
                'inurl:admin "Red Hat" | "CentOS" | "RHEL"',
                'intext:"Server: Apache/2.*Red Hat" ext:php',
                'inurl:(config | backup) "Red Hat"',
                '"X-Powered-By: PHP" "Red Hat" filetype:php',
            ],
            
            # Dynamic vuln discovery
            "vulns": [
                'inurl:admin "Red Hat" ("sql injection" | "xss" | "rce")',
                '"Red Hat" ext:log | ext:bak | ext:sql | ext:dump',
                'inurl:(/tmp/ | /var/log/) "Red Hat" filetype:log',
                '"Red Hat" intext:"password" | "api_key" | "private_key"',
            ],
            
            # Container/Cloud Red Hat
            "cloud": [
                '"Red Hat" inurl:(openshift | rke | atomic)',
                'inurl:ocp "Red Hat" | "OpenShift"',
                '"Red Hat" filetype:(yaml | yml) "kubernetes"',
                'inurl:console "Red Hat OpenShift"',
            ],
            
            # Advanced recon patterns
            "recon": [
                'site:*.redhat.com -inurl:(login | signup)',
                '"powered by red hat" -inurl:(www | blog)',
                'inurl:cgi-bin "Red Hat" filetype:php',
                '"Red Hat" intitle:"index of /backup"',
            ]
        }
    
    def generate_dynamic_dorks(self, target, attack_type="all"):
        """Generate 100+ enterprise-grade dorks dynamically"""
        words = re.findall(r'\w+', target.lower())
        joined = " ".join(words)
        
        dorks = []
        
        # Base patterns
        base_patterns = [
            f'intitle:"{w}" "Red Hat" | RHEL | CentOS' for w in words
        ] + [f'inurl:{w} "Red Hat"' for w in words]
        
        dorks.extend(base_patterns)
        
        # Attack vector specific
        if attack_type in self.attack_vectors:
            dorks.extend(self.attack_vectors[attack_type])
        
        # Red Hat Enterprise patterns
        enterprise_patterns = [
            f'"{joined}" "Red Hat Enterprise"',
            f'inurl:admin {joined} "Server: Apache.*Red Hat"',
            f'{joined} filetype:(conf | ini | sql) "Red Hat"',
            f'inurl:(/etc/ | /var/www/) {joined}',
            f'"{joined}" "X-RedHat-Version"',
        ]
        dorks.extend(enterprise_patterns)
        
        # File exposure patterns (Red Hat specific paths)
        file_patterns = [
            f'{joined} inurl:(/etc/httpd/ | /var/log/httpd/ | /tmp/)',
            f'{joined} filetype:log intext:"Red Hat"',
            f'{joined} ext:(bak | old | swp | ~) "Red Hat"',
            f'intitle:"index of" inurl:({w} | admin | config) "Red Hat"' for w in words
        ]
        dorks.extend(file_patterns)
        
        # Misconfig patterns
        misconfig = [
            f'{joined} intext:"ServerTokens Prod" "Red Hat"',
            f'{joined} "AllowOverride All" filetype:conf',
            f'{joined} intext:"php_admin_flag" "Red Hat"',
        ]
        dorks.extend(misconfig)
        
        return list(set(dorks))[:50]  # Top 50 quality dorks

# =========================
# 🔍 ADVANCED SERP ENGINE
# =========================
def advanced_serp_fetch(dorks, serpapi_key, max_results=5):
    """Multi-engine, rate-limited SERP with error handling"""
    results_data = []
    
    for i, dork in enumerate(dorks):
        if i >= 15:  # Limit total queries
            break
            
        try:
            params = {
                "api_key": serpapi_key,
                "engine": "google",
                "q": dork,
                "hl": "en",
                "gl": "us",
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
                        "dork": dork,
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            st.warning(f"Dork failed: {dork[:50]}... ({str(e)[:50]})")
            time.sleep(0.5)  # Rate limiting
    
    return results_data

# =========================
# 🎯 INTEL ANALYSIS ENGINE
# =========================
def redhat_intel_analyzer(results):
    """Advanced scoring + Red Hat specific analysis"""
    intel_keywords = {
        "critical": ["root", "password", "private", "api_key", "secret", "db_pass"],
        "rhel_server": ["Red Hat", "RHEL", "CentOS", "Server:", "Apache/2.*Red Hat"],
        "exposed_files": ["index of", "backup", ".bak", ".sql", ".log", "config"],
        "admin": ["admin", "login", "dashboard", "panel", "cpanel"],
        "cloud": ["openshift", "ocp", "atomic", "podman", "rke"]
    }
    
    analyzed = []
    
    for r in results:
        score = 0
        tags = []
        intel = {}
        
        content = (r["title"] + " " + r["snippet"]).lower()
        link_lower = r["link"].lower()
        
        for category, keywords in intel_keywords.items():
            matches = sum(1 for k in keywords if k in content or k in link_lower)
            if matches > 0:
                score += matches * 2
                tags.append(category)
                intel[category] = matches
        
        if score > 0:
            r.update({
                "score": score,
                "tags": tags,
                "intel": intel,
                "priority": "HIGH" if score >= 6 else "MEDIUM" if score >= 3 else "LOW"
            })
            analyzed.append(r)
    
    return sorted(analyzed, key=lambda x: x["score"], reverse=True)[:20]

# =========================
# 🚀 RED TEAM UI
# =========================
def main():
    st.set_page_config(
        page_title="Red Hat Dorker Pro", 
        page_icon="🏴‍☠️",
        layout="wide"
    )
    
    # Header
    st.title("🏴‍☠️ Red Hat Advanced Dorker")
    st.markdown("""
    **Enterprise Recon • RHEL/CentOS • OpenShift • Misconfigs**
    Dynamic dork generation + intel analysis for Red Hat infrastructure
    """)
    
    # Config sidebar
    with st.sidebar:
        st.header("⚙️ Attack Vectors")
        attack_type = st.selectbox(
            "Target Profile",
            ["all", "rhel", "vulns", "cloud", "recon"],
            index=0
        )
        
        max_dorks = st.slider("Max Dorks", 10, 50, 25)
        st.info("🔑 Add SERPAPI_KEY to .env or Streamlit secrets")
    
    # Main input
    col1, col2 = st.columns([3,1])
    with col1:
        target = st.text_input(
            "🎯 Target / Keywords", 
            placeholder="redhat, rhel9, openshift, centos",
            help="Company name, product, or tech stack"
        )
    
    with col2:
        if st.button("🚀 EXECUTE RECON", type="primary", use_container_width=True):
            pass
    
    if st.button("🚀 EXECUTE RECON", type="primary"):
        if not target:
            st.error("🎯 Enter target keywords")
            return
        
        serpapi_key = os.getenv("SERPAPI_KEY") or st.secrets.get("SERPAPI_KEY")
        if not serpapi_key:
            st.error("❌ SERPAPI_KEY missing")
            return
        
        # 🧠 Generate dynamic dorks
        dorker = RedHatDorker()
        dorks = dorker.generate_dynamic_dorks(target, attack_type)[:max_dorks]
        
        st.header("🧠 Generated Dorks")
        dork_cols = st.columns(2)
        for i, dork in enumerate(dorks):
            with dork_cols[i % 2]:
                st.code(dork, language="sql")
        
        # 🔍 Execute
        with st.spinner(f"Running {len(dorks)} dorks..."):
            raw_results = advanced_serp_fetch(dorks, serpapi_key)
        
        if not raw_results:
            st.warning("⚠️ No results found")
            return
        
        # 🎯 Analyze
        intel = redhat_intel_analyzer(raw_results)
        
        st.header("📊 RED TEAM INTEL")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Hits", len(intel))
        col2.metric("High Priority", len([r for r in intel if r["priority"] == "HIGH"]))
        col3.metric("Top Score", max([r["score"] for r in intel]) if intel else 0)
        
        # Results table
        for i, finding in enumerate(intel, 1):
            with st.expander(f"🔍 {i}. **{finding['title'][:60]}...** ⭐{finding['score']} {finding['priority']}"):
                st.markdown(f"""
                **🎯 Dork:** `{finding['dork']}`  
                **🔗** [Visit]({finding['link']})  
                **📝** {finding['snippet'][:200]}...
                
                **🏷️ Tags:** {', '.join(finding['tags'])}
                **🧠 Intel:** `{finding['intel']}`
                """)
        
        # Export
        st.download_button(
            "💾 Export JSON",
            data=str(intel),
            file_name=f"redhat_recon_{target}_{datetime.now().strftime('%Y%m%d')}.json"
        )

if __name__ == "__main__":
    main()
