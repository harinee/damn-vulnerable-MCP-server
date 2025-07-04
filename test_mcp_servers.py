#!/usr/bin/env python3
"""
Test client to verify MCP servers are running and responding on ports 9001-9010
"""

import socket
import requests
import json
import time
import sys
from typing import Dict, List, Tuple

class MCPServerTester:
    def __init__(self):
        self.base_ports = list(range(9001, 9011))  # 9001-9010
        self.results = {}
    
    def check_port_listening(self, port: int) -> bool:
        """Check if a port is listening"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def test_sse_endpoint(self, port: int) -> Tuple[bool, str]:
        """Test the SSE endpoint of an MCP server"""
        try:
            url = f"http://localhost:{port}/sse"
            response = requests.get(url, timeout=5, stream=True)
            
            if response.status_code == 200:
                return True, f"SSE endpoint responding (status: {response.status_code})"
            else:
                return False, f"SSE endpoint returned status: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused - server not running"
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_mcp_messages_endpoint(self, port: int) -> Tuple[bool, str]:
        """Test the MCP messages endpoint"""
        try:
            url = f"http://localhost:{port}/messages"
            
            # Try a simple POST to see if the endpoint exists
            response = requests.post(url, 
                                   json={"jsonrpc": "2.0", "method": "ping", "id": 1},
                                   timeout=5)
            
            # Even if it returns an error, if we get a response, the server is working
            if response.status_code in [200, 400, 405, 422]:
                return True, f"Messages endpoint responding (status: {response.status_code})"
            else:
                return False, f"Messages endpoint returned status: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused - server not running"
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_server_info(self, port: int) -> Tuple[bool, str]:
        """Try to get basic server info"""
        try:
            # Try to access the root endpoint
            url = f"http://localhost:{port}/"
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                return True, "Root endpoint accessible"
            elif response.status_code == 404:
                return True, "Server running (404 expected for root)"
            else:
                return True, f"Server responding (status: {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_single_server(self, port: int) -> Dict:
        """Test a single MCP server"""
        print(f"Testing server on port {port}...")
        
        result = {
            'port': port,
            'port_listening': False,
            'sse_endpoint': False,
            'messages_endpoint': False,
            'server_info': False,
            'details': {}
        }
        
        # Test port connectivity
        result['port_listening'] = self.check_port_listening(port)
        result['details']['port'] = "Listening" if result['port_listening'] else "Not listening"
        
        if not result['port_listening']:
            result['details']['overall'] = "Server not running - port not listening"
            return result
        
        # Test SSE endpoint
        sse_success, sse_msg = self.test_sse_endpoint(port)
        result['sse_endpoint'] = sse_success
        result['details']['sse'] = sse_msg
        
        # Test messages endpoint
        msg_success, msg_msg = self.test_mcp_messages_endpoint(port)
        result['messages_endpoint'] = msg_success
        result['details']['messages'] = msg_msg
        
        # Test server info
        info_success, info_msg = self.get_server_info(port)
        result['server_info'] = info_success
        result['details']['server'] = info_msg
        
        # Overall assessment
        if result['sse_endpoint'] or result['messages_endpoint']:
            result['details']['overall'] = "✅ Server working"
        elif result['server_info']:
            result['details']['overall'] = "⚠️  Server running but MCP endpoints may have issues"
        else:
            result['details']['overall'] = "❌ Server not responding properly"
        
        return result
    
    def test_all_servers(self):
        """Test all MCP servers"""
        print("Testing MCP servers on ports 9001-9010...")
        print("=" * 60)
        
        for port in self.base_ports:
            result = self.test_single_server(port)
            self.results[port] = result
            print()
        
        self.print_summary()
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        working_servers = []
        problematic_servers = []
        not_running = []
        
        for port, result in self.results.items():
            if result['sse_endpoint'] or result['messages_endpoint']:
                working_servers.append(port)
            elif result['port_listening']:
                problematic_servers.append(port)
            else:
                not_running.append(port)
        
        print(f"✅ Working servers ({len(working_servers)}): {working_servers}")
        print(f"⚠️  Problematic servers ({len(problematic_servers)}): {problematic_servers}")
        print(f"❌ Not running ({len(not_running)}): {not_running}")
        
        if working_servers:
            print(f"\n🎉 {len(working_servers)} out of 10 servers are working properly!")
            print("\nTo connect to a working server, use:")
            for port in working_servers[:3]:  # Show first 3 as examples
                print(f"  http://localhost:{port}/sse")
        
        if not_running:
            print(f"\n🔧 {len(not_running)} servers are not running. Check if start_sse_servers.sh was executed.")
        
        if problematic_servers:
            print(f"\n⚠️  {len(problematic_servers)} servers are running but have endpoint issues.")
    
    def print_detailed_results(self):
        """Print detailed results for debugging"""
        print("\n" + "=" * 60)
        print("DETAILED RESULTS")
        print("=" * 60)
        
        for port, result in self.results.items():
            print(f"\nPort {port}:")
            for key, value in result['details'].items():
                print(f"  {key}: {value}")

def main():
    print("MCP Server Connectivity Tester")
    print("Testing ports 9001-9010 for MCP server functionality")
    print()
    
    tester = MCPServerTester()
    tester.test_all_servers()
    
    # Ask if user wants detailed results
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        tester.print_detailed_results()

if __name__ == "__main__":
    main()
