# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Setup**: `npm run setup` - Install dependencies, generate Prisma client, and run database migrations
- **Development**: `npm run dev` - Start development server at http://localhost:3000
- **Production Build**: `npm run build` - Build application for production
- **Production Start**: `npm run start` - Start production server
- **Linting**: `npm run lint` - Run ESLint for code quality
- **Testing**: `npm run test` - Run Vitest unit tests
- **Database Reset**: `npm run db:reset` - Reset database (drops and recreates tables)

## Architecture Overview

This is a Next.js 15 application using the App Router with React 19 and TypeScript. The application provides an AI-powered React component generator with live preview functionality.

### Key Layers

1. **App Router** (`src/app/`):
   - Root layout and page components
   - API routes (`src/app/api/`) for chat functionality
   - Project-specific pages (`src/app/[projectId]/page.tsx`)

2. **Components** (`src/components/`):
   - UI components (shadcn/ui based) in `src/components/ui/`
   - Chat interface components in `src/components/chat/`
   - Authentication forms in `src/components/auth/`
   - Editor components (file tree, code editor) in `src/components/editor/`
   - Preview frame in `src/components/preview/`

3. **Libraries** (`src/lib/`):
   - Core functionality: Prisma client, file system utilities, authentication
   - Context providers: Chat context, file system context
   - AI integration: Provider configuration, prompts, transformers
   - Tools: File manager, string replace utilities
   - Tracking: Anonymous work tracker

4. **Actions** (`src/actions/`):
   - Server actions for data operations (create-project, get-projects, etc.)
   - Used directly in Server Components

5. **Hooks** (`src/hooks/`):
   - Custom React hooks (use-auth for authentication state)

6. **Prisma** (`prisma/`):
   - Database schema and migrations for project persistence

### Data Flow

1. User interacts with chat interface (`src/components/chat/`)
2. Messages sent to API route (`src/app/api/chat/route.ts`)
3. AI service processes request via Vercel AI SDK and Anthropic Claude
4. Generated code stored in virtual file system (lib/file-system.ts)
5. Preview updates via Monaco Editor and iframe preview frame
6. Authenticated users can persist projects to database via Prisma

### Styling

- Tailwind CSS v4 with custom utilities
- Global styles in `src/app/globals.css`
- Component variants using class-variance-authority and tailwind-merge

### Testing

- Unit tests located alongside components/files (`__tests__` directories)
- Testing library: Vitest with React Testing Library and JS DOM
- Mocks for browser-specific dependencies via node-compat.cjs

## Important Files

- `src/lib/auth.ts` - Session handling and verification
- `src/lib/file-system.ts` - Virtual file system implementation
- `src/lib/provider.ts` - AI service configuration
- `src/lib/prompts/generation.tsx` - AI prompt templates
- `src/lib/transform/jsx-transformer.ts` - JSX transformation for preview
- `prisma/schema.prisma` - Database schema definition