import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create MCP server
const server = new McpServer({
  name: "rest-api-fetcher",
  version: "1.0.0"
});

// Tool 1 — Fetch all posts
server.tool(
  "get-posts",
  "Fetch all posts from the API",
  {},
  async () => {
    const response = await fetch("https://jsonplaceholder.typicode.com/posts");
    const posts = await response.json() as unknown[];
    return {
      content: [{
        type: "text",
        text: JSON.stringify(posts.slice(0, 5), null, 2) // first 5 posts
      }]
    };
  }
);

// Tool 2 — Fetch post by ID
server.tool(
  "get-post-by-id",
  "Fetch a specific post by ID",
  { id: z.number().describe("Post ID to fetch") },
  async ({ id }) => {
    const response = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`);
    if (!response.ok) {
      return {
        content: [{
          type: "text",
          text: `Error: Post ${id} not found`
        }]
      };
    }
    const post = await response.json();
    return {
      content: [{
        type: "text",
        text: JSON.stringify(post, null, 2)
      }]
    };
  }
);

// Tool 3 — Fetch user by ID
server.tool(
  "get-user",
  "Fetch a user by ID",
  { id: z.number().describe("User ID to fetch") },
  async ({ id }) => {
    const response = await fetch(`https://jsonplaceholder.typicode.com/users/${id}`);
    const user = await response.json();
    return {
      content: [{
        type: "text",
        text: JSON.stringify(user, null, 2)
      }]
    };
  }
);

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("REST API MCP Server running!");
}

main().catch(console.error);