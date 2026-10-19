# AI Mastery Hub
A light-themed personal AI study site with course links, interview library, notes, a model lab, projects and a daily briefing pipeline.

## GitHub Pages
In Settings > Pages, select Deploy from branch, main, /(root). The public URL will be shown there. Published Pages sites are publicly accessible; private learning notes should never be committed. GitHub Actions runs daily at approximately 07:30 Asia/Shanghai, with no guarantee of exact delivery. To enable AI-generated summaries, add OPENAI_API_KEY as a repository Actions secret and allow Actions read/write repository permissions. Without a key, the workflow publishes headline-based leads, not deep researched summaries. It is important that the summarizer does not read full articles.

## Cross-device sync
To enable personal sync, create a Supabase project and execute supabase.sql in SQL Editor. In Supabase Auth URL Configuration add the actual GitHub Pages URL as Site URL and allowed redirect. Place only the public Supabase URL and publishable/anon key in config.js. Never commit the service_role key. Email magic-link sign-in then supports loading and pushing data. Cloud sync uses whole-document last-write-wins; export JSON backups and avoid simultaneous editing on two devices.

## Content caveats
News is collected from public Hacker News metadata, so the resulting briefing is not a verified complete article review. Courses are curated, and the link checker only tests selected URLs; it does not discover newly released courses. Interviews are curated and currently do not auto-update. The historical example shown before the first successful workflow run must not be interpreted as fresh news.

## First run
Actions > Daily AI Briefing and Course Checks > Run workflow. Check Actions logs and the visible report date. Set an API budget limit if using OpenAI API.
