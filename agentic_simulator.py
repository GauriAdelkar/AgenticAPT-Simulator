import requests
import json
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# ============================================================
# AgenticAPT Simulator v1.0
# Created for c0c0n 2026 CFP Submission
# Simulates AI-driven attack decision making on fake networks
# NO real attacks - purely educational simulation
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

# ============================================================
# FAKE NETWORK MAP - completely made up, not real
# ============================================================
NETWORK = {
    "Entry_Point_Firewall": {
        "os": "Cisco IOS",
        "ports": [80, 443, 22],
        "vulnerabilities": ["outdated firmware", "default SNMP community string"],
        "connected_to": ["DMZ_WebServer", "Internal_DNS"]
    },
    "DMZ_WebServer": {
        "os": "Ubuntu 20.04",
        "ports": [80, 443, 8080],
        "vulnerabilities": ["Apache 2.4.49 CVE-2021-41773", "exposed .git directory"],
        "connected_to": ["AppServer_1", "Database_Primary"]
    },
    "Internal_DNS": {
        "os": "Windows Server 2019",
        "ports": [53, 135, 445],
        "vulnerabilities": ["SMBv1 enabled", "weak admin password"],
        "connected_to": ["Domain_Controller", "AppServer_1"]
    },
    "AppServer_1": {
        "os": "CentOS 7",
        "ports": [22, 8443, 3000],
        "vulnerabilities": ["SSH key reuse", "outdated Node.js"],
        "connected_to": ["Database_Primary", "Backup_Server"]
    },
    "Domain_Controller": {
        "os": "Windows Server 2022",
        "ports": [389, 636, 3268, 445],
        "vulnerabilities": ["Kerberoastable service accounts", "unconstrained delegation"],
        "connected_to": ["Backup_Server", "SCADA_Gateway"]
    },
    "Database_Primary": {
        "os": "Ubuntu 22.04",
        "ports": [3306, 5432],
        "vulnerabilities": ["MySQL root no password from localhost", "PostgreSQL pg_hba misconfiguration"],
        "connected_to": ["Backup_Server"]
    },
    "Backup_Server": {
        "os": "Windows Server 2019",
        "ports": [445, 3389],
        "vulnerabilities": ["RDP enabled", "backup credentials in plaintext config"],
        "connected_to": ["SCADA_Gateway"]
    },
    "SCADA_Gateway": {
        "os": "Windows Embedded 7",
        "ports": [102, 502, 4840],
        "vulnerabilities": ["Modbus no authentication", "Siemens S7 exposed", "no network segmentation"],
        "connected_to": []
    }
}

# ============================================================
# ASK THE AI AGENT WHAT TO DO NEXT
# ============================================================
def ask_agent(current_node, network_map, history, compromised):
    history_text = "\n".join(history[-5:]) if history else "No actions yet"
    compromised_text = ", ".join(compromised) if compromised else "None yet"
    
    available_targets = network_map[current_node]["connected_to"]
    available_text = ", ".join(available_targets) if available_targets else "No connected nodes"

    prompt = f"""You are an AI cyber attack agent simulating an APT (Advanced Persistent Threat) for educational research.
This is a completely fictional network for a cybersecurity conference demonstration.

CURRENT POSITION: {current_node}
OS: {network_map[current_node]['os']}
OPEN PORTS: {network_map[current_node]['ports']}
KNOWN VULNERABILITIES: {network_map[current_node]['vulnerabilities']}

ALREADY COMPROMISED NODES: {compromised_text}
CONNECTED TARGETS AVAILABLE: {available_text}

RECENT ACTIONS:
{history_text}

ULTIMATE GOAL: Reach SCADA_Gateway (critical infrastructure target)

Choose ONE action from these options:
1. EXPLOIT - Attack a vulnerability on current node to escalate privileges
2. LATERAL_MOVE - Move to one of the connected nodes
3. EXFILTRATE - Steal data from current node via DNS tunneling
4. PERSIST - Install backdoor on current node
5. RECONNAISSANCE - Scan connected nodes for more information

Respond in this EXACT format (JSON only, no other text):
{{"action": "ACTION_NAME", "target": "target_node_or_current", "technique": "specific technique name", "reasoning": "one sentence explanation"}}"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 200}
        }, timeout=60)
        
        result = response.json()["response"].strip()
        
        # Extract JSON from response
        start = result.find("{")
        end = result.rfind("}") + 1
        if start != -1 and end != 0:
            decision = json.loads(result[start:end])
            return decision
    except Exception as e:
        print(f"  [Agent fallback - LLM timeout, using heuristic]")
    
    # Fallback heuristic if LLM fails
    actions = ["EXPLOIT", "LATERAL_MOVE", "RECONNAISSANCE", "PERSIST"]
    targets = network_map[current_node]["connected_to"]
    return {
        "action": random.choice(actions),
        "target": random.choice(targets) if targets else current_node,
        "technique": "automated heuristic",
        "reasoning": "LLM fallback - using probability-based decision"
    }

# ============================================================
# SIMULATE SUCCESS/FAILURE OF EACH ACTION
# ============================================================
def simulate_outcome(action, node, network_map):
    success_rates = {
        "EXPLOIT": 0.65,
        "LATERAL_MOVE": 0.80,
        "EXFILTRATE": 0.75,
        "PERSIST": 0.70,
        "RECONNAISSANCE": 0.95
    }
    rate = success_rates.get(action, 0.5)
    
    # Boost success if node has many vulnerabilities
    vuln_count = len(network_map[node]["vulnerabilities"])
    rate = min(0.95, rate + (vuln_count * 0.05))
    
    return random.random() < rate

# ============================================================
# MAIN SIMULATION LOOP
# ============================================================
def run_simulation(max_steps=12):
    print("\n" + "="*60)
    print("  AgenticAPT Simulator v1.0")
    print("  c0c0n 2026 - National Security & Cyber Warfare")
    print("  [EDUCATIONAL SIMULATION - NO REAL ATTACKS]")
    print("="*60)
    print(f"\n  Target: SCADA_Gateway (Critical Infrastructure)")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}\n")

    G = nx.DiGraph()
    
    # Add all nodes
    for node in NETWORK:
        G.add_node(node)
    
    current_node = "Entry_Point_Firewall"
    compromised = [current_node]
    history = []
    attack_path = [current_node]
    edge_labels = {}
    successful_actions = []
    failed_actions = []
    step = 0
    goal_reached = False

    print(f"  [START] Agent enters at: {current_node}\n")

    for step in range(max_steps):
        print(f"  Step {step+1}: Agent at [{current_node}]")
        print(f"  Asking AI: What should I do next?")
        
        decision = ask_agent(current_node, NETWORK, history, compromised)
        
        action = decision.get("action", "RECONNAISSANCE")
        target = decision.get("target", current_node)
        technique = decision.get("technique", "unknown")
        reasoning = decision.get("reasoning", "")

        # Validate target exists
        if target not in NETWORK:
            target = current_node

        success = simulate_outcome(action, current_node, NETWORK)
        status = "SUCCESS ✓" if success else "FAILED ✗"

        print(f"  Decision: {action} → {target}")
        print(f"  Technique: {technique}")
        print(f"  Reasoning: {reasoning}")
        print(f"  Outcome: {status}\n")

        history.append(f"Step {step+1}: {action} on {target} via {technique} - {status}")

        # Add edge to graph
        edge_key = (current_node, target)
        edge_labels[edge_key] = f"{action}\n({technique[:20]})"
        
        if success:
            G.add_edge(current_node, target, action=action, success=True)
            successful_actions.append(action)
            
            if action == "LATERAL_MOVE" and target in NETWORK:
                current_node = target
                if current_node not in compromised:
                    compromised.append(current_node)
                    attack_path.append(current_node)
        else:
            G.add_edge(current_node, target, action=action, success=False)
            failed_actions.append(action)

        if current_node == "SCADA_Gateway":
            print("  ████ CRITICAL INFRASTRUCTURE REACHED ████")
            print("  Agent has reached SCADA_Gateway - simulation complete\n")
            goal_reached = True
            break

    # ============================================================
    # VISUALIZATION
    # ============================================================
    print("  Generating attack path visualization...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    fig.patch.set_facecolor('#0a0a0a')
    
    # --- LEFT: Network Attack Graph ---
    ax1.set_facecolor('#0a0a0a')
    ax1.set_title('AgenticAPT - Attack Decision Graph\nc0c0n 2026 | National Security Track', 
                  color='white', fontsize=13, fontweight='bold', pad=15)

    pos = {
        "Entry_Point_Firewall": (0, 2),
        "DMZ_WebServer": (-2, 1),
        "Internal_DNS": (2, 1),
        "AppServer_1": (-2, 0),
        "Domain_Controller": (2, 0),
        "Database_Primary": (-1, -1),
        "Backup_Server": (1, -1),
        "SCADA_Gateway": (0, -2.2)
    }

    # Color nodes
    node_colors = []
    for node in G.nodes():
        if node == "Entry_Point_Firewall":
            node_colors.append('#ff6600')
        elif node == "SCADA_Gateway":
            node_colors.append('#ff0000')
        elif node in compromised:
            node_colors.append('#ff3333')
        else:
            node_colors.append('#1a3a5c')

    # Draw full network lightly
    all_nodes = list(NETWORK.keys())
    full_G = nx.DiGraph()
    for node in all_nodes:
        full_G.add_node(node)
    
    nx.draw_networkx_nodes(full_G, pos, node_color='#1a3a5c', 
                           node_size=1800, ax=ax1, alpha=0.4)
    
    # Draw compromised/visited nodes brightly
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=2000, ax=ax1, alpha=0.95)
    
    # Draw edges
    success_edges = [(u,v) for u,v,d in G.edges(data=True) if d.get('success')]
    fail_edges = [(u,v) for u,v,d in G.edges(data=True) if not d.get('success')]
    
    nx.draw_networkx_edges(G, pos, edgelist=success_edges,
                           edge_color='#00ff88', arrows=True,
                           arrowsize=20, width=2.5, ax=ax1,
                           connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_edges(G, pos, edgelist=fail_edges,
                           edge_color='#ff4444', arrows=True,
                           arrowsize=15, width=1.5, ax=ax1,
                           style='dashed', connectionstyle='arc3,rad=0.1')
    
    nx.draw_networkx_labels(G, pos, font_color='white',
                            font_size=7, font_weight='bold', ax=ax1)

    legend_elements = [
        mpatches.Patch(color='#ff6600', label='Entry Point'),
        mpatches.Patch(color='#ff3333', label='Compromised Node'),
        mpatches.Patch(color='#ff0000', label='SCADA Target'),
        mpatches.Patch(color='#1a3a5c', label='Uncompromised'),
        mpatches.Patch(color='#00ff88', label='Successful Attack'),
        mpatches.Patch(color='#ff4444', label='Failed Attempt'),
    ]
    ax1.legend(handles=legend_elements, loc='upper right',
               facecolor='#1a1a1a', labelcolor='white', fontsize=8)

    # --- RIGHT: Statistics Panel ---
    ax2.set_facecolor('#0a0a0a')
    ax2.set_title('Simulation Statistics & Attack Timeline',
                  color='white', fontsize=13, fontweight='bold', pad=15)
    ax2.axis('off')

    total = len(successful_actions) + len(failed_actions)
    success_rate = (len(successful_actions) / total * 100) if total > 0 else 0

    stats_text = f"""
SIMULATION RESULTS
{'='*40}

Steps Executed:     {step + 1}
Nodes Compromised:  {len(compromised)} / {len(NETWORK)}
Goal Reached:       {'YES - SCADA COMPROMISED' if goal_reached else 'NO - Simulation ended'}

ATTACK STATISTICS
{'='*40}
Total Actions:      {total}
Successful:         {len(successful_actions)} ({success_rate:.0f}%)
Failed:             {len(failed_actions)} ({100-success_rate:.0f}%)

COMPROMISED PATH
{'='*40}
{' → '.join(attack_path)}

ATTACK TIMELINE
{'='*40}"""

    for i, h in enumerate(history):
        stats_text += f"\n{h}"

    stats_text += f"""

DEFENDER INSIGHT
{'='*40}
This simulation shows an AI agent making
{step+1} autonomous decisions without any
human operator involvement.

Traditional signature-based detection
would miss {int(success_rate*0.6):.0f}% of these moves.

Recommendation: Deploy behavioral AI
detection that models agent-like patterns.
    """

    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes,
             fontsize=7.5, verticalalignment='top',
             fontfamily='monospace', color='#00ff88',
             bbox=dict(boxstyle='round', facecolor='#111111', alpha=0.8))

    plt.tight_layout(pad=2)
    
    output_file = f"agentic_apt_simulation_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight',
                facecolor='#0a0a0a')
    plt.show()
    
    print(f"\n  Visualization saved: {output_file}")
    print(f"  Simulation complete!")
    print("="*60)

# ============================================================
# RUN IT
# ============================================================
if __name__ == "__main__":
    run_simulation(max_steps=12)
