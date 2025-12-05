# Contributing to Reformatters Knowledge Base

Thank you for contributing! This guide will help you add documentation, playbooks, and examples.

## Quick Contribution Guide

### For Engineers: Adding Guides

1. Create a new markdown file in `knowledge/guides/`:
```bash
touch knowledge/guides/my-new-guide.md
```

2. Write your guide using markdown

3. Commit and push:
```bash
git add knowledge/guides/my-new-guide.md
git commit -m "Add guide for [topic]"
git push
```

4. Your guide is now accessible via the MCP server!

### For Support: Adding Playbooks

1. Choose the right category:
   - `knowledge/playbooks/troubleshooting/` - For fixing issues
   - `knowledge/playbooks/operations/` - For routine operations

2. Use the template:
```bash
cp knowledge/playbooks/templates/playbook-template.md \\
   knowledge/playbooks/troubleshooting/my-issue.md
```

3. Fill in the template with your steps

4. Commit and push

### Adding Code Examples

1. Create a directory in `knowledge/examples/`:
```bash
mkdir -p knowledge/examples/my-integration/
```

2. Add your code files and a README.md explaining the example

3. Commit and push

## Writing Guidelines

### Markdown Style

- Use clear, descriptive headers
- Include code blocks with language tags
- Add links to related content
- Use bullet points for lists
- Keep paragraphs short and focused

### Code Examples

- Include comments explaining what the code does
- Show both the code and expected output
- Test your examples before committing
- Use realistic examples that users can adapt

### Playbook Structure

Follow the template in `knowledge/playbooks/templates/playbook-template.md`:

1. **Overview**: What this playbook solves
2. **Symptoms**: How to recognize the issue
3. **Steps**: Clear, numbered resolution steps
4. **Verification**: How to confirm it's fixed
5. **Prevention**: How to avoid it in future

## File Naming

- Use lowercase with hyphens: `my-guide-name.md`
- Be descriptive: `troubleshooting-s3-access.md` not `fix-s3.md`
- Group related files in subdirectories

## Testing Your Changes

Before committing, ensure:

1. Markdown renders correctly
2. Code examples run without errors
3. Links work
4. No typos or grammatical errors

### Testing with Claude Desktop Locally

To test your documentation changes with Claude Desktop:

1. Configure Claude Desktop to use your local server:
   - Edit config file (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`)
   - Add:
     ```json
     {
       "mcpServers": {
         "reformatters-kb-local": {
           "command": "uv",
           "args": [
             "--directory",
             "/path/to/reformatters-knowledge-base",
             "run",
             "reformatters-kb-stdio"
           ]
         }
       }
     }
     ```
   - Replace `/path/to/reformatters-knowledge-base` with your actual project path
   - Restart Claude Desktop

2. Test your changes by asking Claude to search for your new content

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Test locally if possible
4. Submit PR with clear description
5. Address review feedback

## Questions?

- Check existing guides and playbooks for examples
- Ask in GitHub Discussions
- Contact the team

Thank you for helping make reformatters better documented!
