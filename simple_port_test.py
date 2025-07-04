#!/usr/bin/env python3
"""
Simple port connectivity test for MCP servers on ports 9001-9010
Uses only built-in Python modules
"""

import socket
import sys
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import time

def check_port_listening(port):
    """Check if a port is listening"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except Exception:
        return False

def test_http_endpoint(port, endpoint=""):
    """Test HTTP endpoint"""
    try:
        url = f"http://localhost:{port}{endpoint}"
        with urlopen(url, timeout=3) as response:
            return True, f"HTTP {response.getcode()}"
    except HTTPError as e:
        return True, f"HTTP {e.code} (server responding)"
    except URLError as e:
        if "Connection refused" in str(e):
            return False, "Connection refused"
        return False, f"URL Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def test_single_port(port):
    """Test a single port"""
    print(f"Testing port {port}...")
    
    # Check if port is listening
    listening = check_port_listening(port)
    if not listening:
        print(f"  ❌ Port {port}: Not listening")
        return False
    
    print(f"  ✅ Port {port}: Listening")
    
    # Test root endpoint
    root_success, root_msg = test_http_endpoint(port, "/")
    print(f"     Root (/): {root_msg}")
    
    # Test SSE endpoint
    sse_success, sse_msg = test_http_endpoint(port, "/sse")
    print(f"     SSE (/sse): {sse_msg}")
    
    # Test messages endpoint
    msg_success, msg_msg = test_http_endpoint(port, "/messages")
    print(f"     Messages (/messages): {msg_msg}")
    
    # Overall assessment
    if sse_success or msg_success:
        print(f"  🎉 Port {port}: MCP server appears to be working!")
        return True
    elif root_success:
        print(f"  ⚠️  Port {port}: Server running but MCP endpoints may have issues")
        return True
    else:
        print(f"  ❌ Port {port}: Server not responding properly")
        return False

def main():
    print("Simple MCP Server Port Test")
    print("Testing ports 9001-9010...")
    print("=" * 50)
    
    working_ports = []
    listening_ports = []
    
    for port in range(9001, 9011):
        success = test_single_port(port)
        if success:
            working_ports.append(port)
        if check_port_listening(port):
            listening_ports.append(port)
        print()
    
    print("=" * 50)
    print("SUMMARY:")
    print(f"Ports listening: {listening_ports}")
    print(f"Working MCP servers: {working_ports}")
    print(f"Not running: {[p for p in range(9001, 9011) if p not in listening_ports]}")
    
    if working_ports:
        print(f"\n🎉 {len(working_ports)} servers are working!")
        print("Connect using SSE endpoints:")
        for port in working_ports[:3]:  # Show first 3
            print(f"  http://localhost:{port}/sse")
    else:
        print("\n❌ No servers are working properly.")
        if not listening_ports:
            print("💡 Try running: ./start_sse_servers.sh")

if __name__ == "__main__":
    main()
