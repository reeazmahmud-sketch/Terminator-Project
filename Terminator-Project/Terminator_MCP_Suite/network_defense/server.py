import subprocess
import socket
from typing import List, Dict

class NetworkDefenseMCP:
    """
    MCP Module for Home Network Security & Cyber Defense.
    """

    def scan_network(self, subnet: str = "192.168.1.0/24") -> str:
        """
        Scan local network for connected devices.
        Uses nmap if available, else ping sweep.
        """
        try:
            # Try nmap first
            result = subprocess.run(["nmap", "-sn", subnet], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return "Nmap not found. Please install nmap for detailed scanning."
        except FileNotFoundError:
            return "Nmap not installed. (Use 'brew install nmap')"

    def check_router_security(self, router_ip: str = "192.168.1.1") -> str:
        """
        Check for common router vulnerabilities.
        1. Default Creds (Warning only)
        2. Open Ports (80, 443, 8080, 22)
        """
        report = f"Security Report for Router {router_ip}:\n"
        
        # Check Ports
        common_ports = [22, 80, 443, 8080, 23]
        open_ports = []
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((router_ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        if 23 in open_ports:
            report += "🚨 CRITICAL: Telnet (23) is OPEN. Disable immediately.\n"
        if 80 in open_ports:
            report += "⚠️  WARNING: HTTP (80) is OPEN. Ensure Admin panel is password protected.\n"
            
        report += f"Open Ports: {open_ports}\n"
        report += "Recommendation: Change default admin/admin password if not done."
        
        return report

    def analyze_phishing_link(self, url: str) -> str:
        """
        Analyze a URL for phishing characteristics.
        """
        score = 0
        reasons = []
        
        if "@" in url:
            score += 5
            reasons.append("Contains '@' symbol (obfuscation attempt)")
        if "http://" in url:
            score += 3
            reasons.append("Insecure HTTP protocol")
        if url.count(".") > 3:
            score += 2
            reasons.append("Suspiciously long subdomain")
            
        if score > 4:
            return f"🚫 DANGEROUS: {url} (Risk Score: {score}/10). Reasons: {', '.join(reasons)}"
        elif score > 0:
            return f"⚠️  SUSPICIOUS: {url} (Risk Score: {score}/10). Reasons: {', '.join(reasons)}"
        return f"✅ LIKELY SAFE: {url}"

# Tool Registry
tools = [
    NetworkDefenseMCP().scan_network,
    NetworkDefenseMCP().check_router_security,
    NetworkDefenseMCP().analyze_phishing_link
]
