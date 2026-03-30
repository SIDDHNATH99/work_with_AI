# In-Built MCP Server Creation Methods

* [ ] 

## 1. Filesystem

- [ ] Connects to a local directory on your machine
- [ ] Can fetch, read, and navigate files from a given folder path
- [ ] Useful for giving Claude access to local project files or documents

## 2. GitHub

- Connects to the GitHub API
- Can fetch information about repositories from a given GitHub account
- Useful for reading repo contents, issues, pull requests, and metadata

## 3. Postgres

- Connects to a PostgreSQL database
- Can fetch and query data from a given table
- Useful for giving Claude read access to structured database data

---

## Prerequisites

```bash
# Check these are installed
node -v        # Should be 18+
npm -v         # Should be 9+
claude -v      # Should be latest
```

---

## Setup Guide

### Step 1 — Open Claude Config File

Open PowerShell and run:

```powershell
notepad "$HOME\.claude.json"
```

---

### Step 2 — Add MCP Servers to Config

Find the `projects` section and add the following (replace paths and credentials with your own):

```json
"your/project/path": {
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "cmd",
      "args": [
        "/c", "npx", "-y",
        "@modelcontextprotocol/server-filesystem",
        "D:/your/project/path",
        "C:/Users/YourUsername"
      ],
      "env": {}
    },
    "postgres": {
      "type": "stdio",
      "command": "cmd",
      "args": [
        "/c", "npx", "-y",
        "mcp-postgres-server"
      ],
      "env": {
        "PG_HOST": "localhost",
        "PG_PORT": "5432",
        "PG_USER": "your_db_user",
        "PG_PASSWORD": "your_db_password",
        "PG_DATABASE": "your_db_name"
      }
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer your_github_token_here"
      }
    }
  }
}
```

---

### Step 3 — Generate a GitHub Personal Access Token (PAT)

1. Go to https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Select scopes: `repo`, `read:org`, `read:user`, `workflow`
4. Copy the token and paste it into the config above in place of `your_github_token_here`

---

### Step 4 — Verify MCP Servers Are Loaded

Navigate to your project folder and open Claude:

```powershell
cd D:\your\project\path
claude
```

Then inside Claude, run:

```
/mcp
```

All configured servers (filesystem, postgres, github) should appear as connected.

---

### Step 5 — Test Each MCP Server

**Test 1 — Filesystem**

```
List all files and folders in D:\AI\work_with_AI
```

**Test 2 — PostgreSQL**

```
List all tables in my postgres database
```

**Test 3 — GitHub**

```
List all my GitHub repositories
```
