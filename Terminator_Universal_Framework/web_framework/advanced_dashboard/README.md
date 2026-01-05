# Sider Clone - MVP

A production-ready single-page web application that replicates core Sider functionality with AI chat capabilities, multi-provider support, and admin monitoring.

## Features

### Core Functionality
- **Floating Sidebar Chat UI** - Collapsible sidebar with context options (URL, text, file upload)
- **Multi-Provider AI Support** - OpenAI and Anthropic (Claude) with easy extensibility
- **Streaming Responses** - Real-time AI responses with token tracking
- **Message History** - Persistent conversation storage per user
- **Conversation Export** - Download chat history as JSON
- **File Upload** - Support for PDF and TXT files with text extraction

### Security & Authentication
- **Email/Password Authentication** - Supabase-powered secure auth
- **Encrypted API Key Storage** - Client-side encryption for user API keys
- **Row Level Security (RLS)** - Database-level access control
- **Profile Management** - User profiles with API key management

### Admin Features
- **Usage Monitoring Dashboard** - Real-time stats and metrics
- **Activity Logs** - Track all API calls, uploads, and errors
- **Error Tracking** - Monitor system health and error rates
- **Token Usage Analytics** - Track API consumption across users

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Vite** for fast development and builds

### Backend
- **Supabase** - PostgreSQL database with built-in auth and RLS
- **Client-side API calls** - Direct integration with OpenAI and Anthropic APIs
- **Web Crypto API** - Client-side encryption for API keys

### Database
- **PostgreSQL** via Supabase
- Tables: profiles, api_keys, conversations, messages, uploaded_files, usage_logs

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Supabase account (free tier works)
- API keys for OpenAI and/or Anthropic

### Environment Variables

The project uses Supabase, and the connection details are already configured in `.env`:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

These values are already set up in your project.

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Database is already set up:**
   - The Supabase database has been configured with all necessary tables
   - Migrations have been applied automatically
   - Row Level Security (RLS) policies are active

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

### First Time Setup

1. **Create an account:**
   - Open the app and click "Sign Up"
   - Enter your email, password, and optional full name
   - You'll be automatically logged in

2. **Add API Keys:**
   - Navigate to the "Profile" page
   - Click "Add Key"
   - Select your provider (OpenAI or Anthropic)
   - Give it a name and paste your API key
   - Your keys are encrypted before storage

3. **Start chatting:**
   - Return to the "Chat" view
   - Click the floating button to open the sidebar
   - Choose your context source (Text, URL, or File)
   - Select your model from the settings panel
   - Start a conversation

## Project Structure

```
src/
├── components/
│   ├── Auth/              # Authentication components
│   │   ├── AuthPage.tsx
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   ├── Chat/              # Chat interface components
│   │   ├── ChatSidebar.tsx
│   │   ├── ChatWindow.tsx
│   │   └── ModelSelector.tsx
│   ├── Profile/           # User profile and API key management
│   │   └── ProfilePage.tsx
│   ├── Admin/             # Admin dashboard
│   │   └── AdminPanel.tsx
│   └── MainApp.tsx        # Main application layout
├── contexts/
│   └── AuthContext.tsx    # Authentication state management
├── lib/
│   ├── supabase.ts        # Supabase client and types
│   ├── crypto.ts          # API key encryption/decryption
│   └── api.ts             # AI provider integrations
├── App.tsx                # Root component
└── main.tsx               # Application entry point
```

## API Integration

### OpenAI Integration

The app supports OpenAI models through direct API calls:

```typescript
// In src/lib/api.ts - streamOpenAI function
// Endpoint: https://api.openai.com/v1/chat/completions
// Supported models: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo
```

### Anthropic (Claude) Integration

Claude models are integrated via the Messages API:

```typescript
// In src/lib/api.ts - streamAnthropic function
// Endpoint: https://api.anthropic.com/v1/messages
// Supported models: claude-3-opus, claude-3-sonnet, claude-3-haiku
```

### Adding New Providers

To add a new AI provider:

1. Add provider to `PROVIDERS` object in `src/components/Chat/ModelSelector.tsx`
2. Implement streaming function in `src/lib/api.ts` (follow pattern of `streamOpenAI`)
3. Add case to `streamChat` function to handle the new provider
4. Update profile page to allow adding keys for the new provider

## Extending with Vector Embeddings / Private Knowledge Base

The database schema is ready for vector embeddings. To add private KB functionality:

1. **Enable pgvector extension:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Add embedding column to uploaded_files:**
   ```sql
   ALTER TABLE uploaded_files
   ADD COLUMN embedding vector(1536);
   ```

3. **Create vector similarity function:**
   ```sql
   CREATE OR REPLACE FUNCTION match_documents(
     query_embedding vector(1536),
     match_threshold float,
     match_count int
   )
   RETURNS TABLE (
     id uuid,
     filename text,
     extracted_text text,
     similarity float
   )
   LANGUAGE plpgsql
   AS $$
   BEGIN
     RETURN QUERY
     SELECT
       uploaded_files.id,
       uploaded_files.filename,
       uploaded_files.extracted_text,
       1 - (uploaded_files.embedding <=> query_embedding) as similarity
     FROM uploaded_files
     WHERE 1 - (uploaded_files.embedding <=> query_embedding) > match_threshold
     ORDER BY uploaded_files.embedding <=> query_embedding
     LIMIT match_count;
   END;
   $$;
   ```

4. **Generate embeddings when uploading files:**
   - Use OpenAI's `text-embedding-ada-002` or similar
   - Store embeddings in the database
   - Query relevant context before sending to chat

5. **Integration points:**
   - `src/lib/api.ts` - `uploadFile` function (add embedding generation)
   - `src/lib/api.ts` - `streamChat` function (retrieve context via similarity search)

## Database Schema

### Tables

- **profiles** - User profiles extending auth.users
- **api_keys** - Encrypted API keys per user/provider
- **conversations** - Chat conversation metadata
- **messages** - Individual messages with token tracking
- **uploaded_files** - File uploads with extracted text
- **usage_logs** - Admin monitoring and analytics

### Security

All tables have Row Level Security (RLS) enabled:
- Users can only access their own data
- Admins have read-only access to all data
- API keys are encrypted at application level before storage

## Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run typecheck    # Run TypeScript type checking
```

## Deployment

### Build the project
```bash
npm run build
```

The built files will be in the `dist/` directory.

### Deploy to Vercel, Netlify, or similar
1. Connect your Git repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables (Supabase credentials)

### Supabase Configuration

Your Supabase instance is already configured and ready to use. No additional setup needed.

## Admin Access

To grant admin privileges to a user:

1. Log into Supabase dashboard
2. Navigate to Table Editor → profiles
3. Find the user's profile
4. Set `is_admin` to `true`

## Security Notes

⚠️ **Important Security Considerations:**

1. **API Key Encryption** - Keys are encrypted client-side, but the encryption key (`ENCRYPTION_KEY` in `src/lib/crypto.ts`) should be environment-specific in production
2. **HTTPS Required** - Always use HTTPS in production to protect API keys in transit
3. **Rate Limiting** - Consider adding rate limiting for API calls
4. **Cost Monitoring** - Monitor token usage to prevent unexpected costs
5. **Supabase RLS** - All database access is restricted via Row Level Security policies

## License

This is an MVP project for demonstration purposes.

## Support

For issues or questions, please refer to the documentation for:
- [Supabase](https://supabase.com/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com)
