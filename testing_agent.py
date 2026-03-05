import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
BASE_URL = "http://127.0.0.1:5001"
SCREENSHOT_DIR = "testing_screenshots"
REPORT_FILE = "testing_report.md"
CREDENTIALS = {"username": "admin", "password": "AtmaSuddhi74"}

# Ensure screenshot directory exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class TestingAgent:
    def __init__(self):
        self.findings = {
            "errors": [],
            "improvements": [],
            "usability": [],
            "screenshots": []
        }
        self.visited_urls = set()

    async def log_finding(self, category, message, screenshot=None):
        print(f"[{category.upper()}] {message}")
        self.findings[category].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "screenshot": screenshot
        })

    async def take_screenshot(self, page, name):
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        await page.screenshot(path=path)
        self.findings["screenshots"].append(path)
        return path

    async def explore(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Handle console errors
            page.on("console", lambda msg: self.handle_console(msg))
            page.on("pageerror", lambda err: self.handle_page_error(err))

            try:
                # 1. Access Login Page
                await self.log_finding("usability", f"Accessing {BASE_URL}")
                await page.goto(BASE_URL)
                
                # Check if redirected to login
                if "/login" in page.url:
                    await self.log_finding("usability", "Redirected to login page.")
                    await self.take_screenshot(page, "login_page")
                    
                    # 2. Perform Login
                    await page.fill("#username", CREDENTIALS["username"])
                    await page.fill("#password", CREDENTIALS["password"])
                    await page.click("button[type='submit']")
                    await page.wait_for_load_state("networkidle")
                    
                    if "/login" in page.url:
                        await self.log_finding("errors", "Login failed with provided credentials.")
                        return
                    else:
                        await self.log_finding("usability", "Login successful. Accessing dashboard.")
                
                await self.take_screenshot(page, "dashboard")

                # 3. Extract Links from Navbar or Main Menu
                # Navigation links in this app are likely in a sidebar or header
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: e.innerText.trim(), href: e.href}))")
                
                # Filter for internal links and discard common non-nav links
                internal_links = [l for l in links if l['href'].startswith(BASE_URL) and "#" not in l['href']]
                
                to_visit = []
                seen_hrefs = {page.url}
                for l in internal_links:
                    if l['href'] not in seen_hrefs and l['text']:
                        to_visit.append(l)
                        seen_hrefs.add(l['href'])

                await self.log_finding("usability", f"Found {len(to_visit)} internal links to explore: {[l['text'] for l in to_visit]}")

                # 4. Visit Key Sections
                for link in to_visit:
                    await self.log_finding("usability", f"Visiting: {link['text']} ({link['href']})")
                    try:
                        resp = await page.goto(link['href'], wait_until="networkidle")
                        if resp.status >= 400:
                            await self.log_finding("errors", f"Link {link['href']} ({link['text']}) returned status {resp.status}")
                        
                        safe_text = "".join([c for c in link['text'] if c.isalnum() or c==' ']).replace(" ", "_").lower()
                        await self.take_screenshot(page, f"section_{safe_text}")
                        
                        # Check for empty states or obvious UI issues
                        content = await page.content()
                        if "Internal Server Error" in content:
                            await self.log_finding("errors", f"500 Error detected on {link['href']}")
                        
                        if "No hay datos" in content or "Lista vacía" in content:
                            await self.log_finding("improvements", f"Section '{link['text']}' appears empty. Verify if data seeding worked completely.")

                    except Exception as e:
                        await self.log_finding("errors", f"Failed to visit {link['href']}: {str(e)}")

            finally:
                await browser.close()
                self.generate_report()

    def handle_console(self, msg):
        if msg.type == "error":
            self.findings["errors"].append({"timestamp": datetime.now().isoformat(), "message": f"Console Error: {msg.text}"})

    def handle_page_error(self, err):
        self.findings["errors"].append({"timestamp": datetime.now().isoformat(), "message": f"Page Error: {err.message}"})

    def generate_report(self):
        with open(REPORT_FILE, "w") as f:
            f.write(f"# 🕵️ Testing Agent Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📝 Summary\n")
            f.write(f"- Errors Found: {len(self.findings['errors'])}\n")
            f.write(f"- Usability & Exploration Notes: {len(self.findings['usability'])}\n")
            f.write(f"- Potential Improvements: {len(self.findings['improvements'])}\n")
            f.write(f"- Screenshots Captured: {len(self.findings['screenshots'])}\n\n")

            f.write("## ❌ Errors & Bugs\n")
            if not self.findings["errors"]:
                f.write("No critical errors found during exploration.\n")
            for err in self.findings["errors"]:
                f.write(f"- [{err.get('timestamp', '')}] {err['message']}\n")

            f.write("\n## 💡 Suggested Improvements & Usability\n")
            for item in self.findings["usability"]:
                f.write(f"- {item['message']}\n")
            for item in self.findings["improvements"]:
                f.write(f"- IMPROVEMENT: {item['message']}\n")

            f.write("\n## 📸 Visual Audit (Screenshots)\n")
            f.write("| Section | Screenshot |\n")
            f.write("| --- | --- |\n")
            for ss in self.findings["screenshots"]:
                name = os.path.basename(ss).split('_')[0]
                f.write(f"| {name.capitalize()} | ![{os.path.basename(ss)}]({ss}) |\n")

            f.write("\n---\n")
            f.write("### 📜 Literary Inspiration\n")
            f.write("> \"Caminante, son tus huellas el camino y nada más; caminante, no hay camino, se hace camino al andar.\" — Antonio Machado, *Campos de Castilla*.\n\n")
            f.write("Al igual que en los versos de Machado, este agente de pruebas ha trazado su propia ruta a través de la arquitectura del sistema, no siguiendo senderos preestablecidos, sino descubriendo la solidez y los huecos de la aplicación con cada paso (o clic) automatizado. La calidad no es un destino hacia el que se viaja, sino el camino que se construye con cada revisión y mejora.\n")

if __name__ == "__main__":
    agent = TestingAgent()
    asyncio.run(agent.explore())
