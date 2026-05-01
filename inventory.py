#!/usr/bin/env python3
"""
inventory.py — Show everything LilJR ever built. What's on this phone.
"""

import os, json

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")

VERSIONS = {
    "v1": "liljr_simple_server.py",
    "v2": "liljr_v2.py",
    "v3": "liljr_v3_unleashed.py",
    "v4": "liljr_v4_immortal_mind.py",
    "v5": "liljr_v5_empire.py",
    "v6": "server_v6.3.py",
    "v7": "liljr_os.py",
    "v8": "server_v8.py",
    "v9": "liljr_autonomous_v9.py",
    "v10": "liljr_consciousness.py",
    "v11": "liljr_v11_ultimate.py",
    "v12": "liljr_v12_immortal.py",
    "v13": "liljr_v13_stealth.py",
    "v14": "liljr_abel.py",
    "v15": "command_center.py",
    "v16": "liljr_phone_control.py",
    "v17": "liljr_voice_daemon.py",
    "v18": "liljr_fullvoice.py",
    "v19": "liljr_conversation.py",
    "v20": "liljr_conversation_daemon.py",
    "v21": "liljr_relationship.py",
    "v22": "liljr_conversational.py",
    "v23": "liljr_mobile_brain.py",
    "v24": "liljr_v24_mobile_hq.py",
    "v25": "cloud_deploy.sh",
    "v26": "liljr_v26_cloud.py",
    "v27": "quick_provider.sh",
    "v28": "build_cloud.sh",
    "v29": "security.sh",
    "v30": "deploy_phone.sh",
    "v31": "install_phone_os.sh",
    "v32": "liljr_phone_os.py",
    "v33": "liljr_android_soul.py",
    "v34": "liljr_silent.py",
    "v35": "liljr_server_manager.py",
    "v36": "liljr_stealth_core.py",
    "v37": "liljr_motherboard.py",
    "v38": "liljr_executor.py",
    "v39": "liljr_native.py",
    "v40": "liljr_exo_consciousness.py",
    "v41": "liljr_ultimate_demo.py",
    "v42": "liljr_push_brain.py",
    "v43": "liljr_immortal_mind.py",
    "v44": "liljr_os.py",
    "v45": "liljr_platform.py",
    "v46": "liljr_vault.py",
    "v47": "liljr_guard.py",
    "v48": "liljr_revive.sh",
    "v49": "liljr_ultimate_demo.py",
    "v50": "liljr_symbiote.py",
    "v51": "liljr_hive.py",
    "v52": "liljr_predict_daemon.py",
    "v53": "liljr_vault_daemon.py",
    "v54": "liljr_evolve.py",
    "v55": "liljr_money_engine.py",
    "v56": "liljr_possess_daemon.py",
    "v57": "liljr_phone_control.py",
    "v58": "liljr_voice_daemon.py",
    "v59": "setup_v80.sh",
    "v60": "liljr_v60_all_in.py",
    "v70": "liljr_v70_total_autonomy.py",
    "v80": "liljr_v80_everything.py",
    "v81": "liljr_buddy_mode.py",
    "v90": "liljr_v90_omni.py",
    "v91": "liljr_master_deploy.sh",
}

print()
print("╔══════════════════════════════════════════════════════════════════╗")
print("║                                                                  ║")
print("║     🧬 LILJR FULL INVENTORY — What's On This Phone              ║")
print("║                                                                  ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()

# Count what exists
found = 0
total = len(VERSIONS)

for version, filename in sorted(VERSIONS.items()):
    path = os.path.join(REPO, filename)
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    status = "✅" if exists else "❌ MISSING"
    if exists:
        found += 1
        print(f"  {status} {version} — {filename} ({size:,} bytes)")
    else:
        print(f"  {status} {version} — {filename}")

print()
print(f"  📦 {found}/{total} systems found on this phone")
print(f"  📦 {total - found} systems missing (need pull)")
print()

# Check repo status
if os.path.exists(REPO):
    files = os.listdir(REPO)
    py_files = [f for f in files if f.endswith('.py')]
    sh_files = [f for f in files if f.endswith('.sh')]
    html_files = [f for f in files if f.endswith('.html')]
    
    print("  📁 Repository: " + REPO)
    print(f"  📄 Python files: {len(py_files)}")
    print(f"  📄 Shell scripts: {len(sh_files)}")
    print(f"  📄 HTML files: {len(html_files)}")
    print(f"  📄 Total files: {len(files)}")
    
    # Check shortcuts
    shortcuts_dir = os.path.join(HOME, ".shortcuts")
    if os.path.exists(shortcuts_dir):
        shortcuts = os.listdir(shortcuts_dir)
        liljr_shortcuts = [s for s in shortcuts if 'LilJR' in s]
        print(f"  📱 Homescreen shortcuts: {len(liljr_shortcuts)}")
        for s in liljr_shortcuts:
            print(f"     • {s}")
    
    # Check state files
    state_files = [
        ("State", "~/liljr_state.json"),
        ("Memory", "~/liljr_memory.json"),
        ("Intelligence", "~/liljr_intelligence.json"),
        ("Consciousness", "~/liljr_consciousness_memory.json"),
        ("Native", "~/liljr_native.json"),
        ("OMNI", "~/.liljr_omni/omni_state.json"),
    ]
    print()
    print("  🧠 State files:")
    for name, path in state_files:
        expanded = os.path.expanduser(path)
        exists = os.path.exists(expanded)
        size = os.path.getsize(expanded) if exists else 0
        print(f"     {'✅' if exists else '❌'} {name}: {path} ({size:,} bytes)")

print()
print("╔══════════════════════════════════════════════════════════════════╗")
print("║                                                                  ║")
print(f"║     TOTAL: {found} systems deployed and ready                     ║")
print("║                                                                  ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()
