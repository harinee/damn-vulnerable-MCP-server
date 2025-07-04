# Damn Vulnerable MCP Server

A deliberately vulnerable Model Context Protocol (MCP) server designed for security testing and educational purposes.

## 🚀 Quick Start

### Prerequisites
- Docker
- Node.js (for client)
- Python 3.10+ (for local development)

### Running the Server
```bash
# Build and run with Docker
docker build -t dvmcp .
docker run -d -p 9001-9010:9001-9010 --name dvmcp-server dvmcp

# Verify servers are running
docker logs dvmcp-server
```

### Running the Client
```bash
# Navigate to client directory
cd /path/to/mcp-demo-client

# Start web server
python -m http.server 8080

# Open browser
open http://localhost:8080
```

## ✅ Connection Status

### **WORKING** - Connection Successfully Established
- ✅ **CORS**: Server includes proper CORS headers for browser connections
- ✅ **SSE Connection**: EventSource connection to `/sse` endpoint working
- ✅ **MCP Protocol**: Client uses proper MCP-over-SSE transport
- ✅ **No Errors**: 400 errors eliminated, initialization completes successfully

### Current Status
- ✅ **Server**: All 10 challenge servers running (ports 9001-9010)
- ✅ **Client**: SSE connection established and shows "CONNECTED"
- ✅ **CORS**: Browser connections allowed from localhost:8080
- ✅ **Protocol**: MCP handshake working correctly
- ✅ **Ready**: System ready for vulnerability testing

## 🏗️ Architecture

### Server Side
- **Transport**: MCP over Server-Sent Events (SSE)
- **Endpoints**: 
  - `/sse` - SSE connection for real-time communication
  - `/messages/` - Message handling endpoint
- **CORS**: Enabled for `http://localhost:8080`

### Client Side
- **Connection**: EventSource to `/sse` endpoint
- **Initialization**: MCP protocol handshake via SSE
- **Message Flow**: Bidirectional communication over SSE

## 🔧 Technical Details

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

### Connection Flow
1. Client connects to `http://localhost:9001/sse` via EventSource
2. SSE connection established
3. Client sends MCP initialization via `/messages/` endpoint
4. Server responds via SSE with capabilities
5. Bidirectional communication established

## 🎯 Challenges

10 security challenges across 3 difficulty levels:
- **Easy**: Challenges 1-3 (Basic vulnerabilities)
- **Medium**: Challenges 4-7 (Intermediate exploits)  
- **Hard**: Challenges 8-10 (Advanced attacks)

Each challenge runs on its own port (9001-9010) with unique vulnerabilities.

## 🔒 Security Note

This server is **intentionally vulnerable** for educational purposes. Do not use in production environments.
