---
applyTo: '**'
---

# Global Project Instructions

## Architecture Standards
- Follow TOGAF-aligned architecture principles
- Document all architecture decisions and rationale
- Maintain clear separation of concerns between layers

## Documentation Standards
- Use AsciiDoc format (.adoc extension)
- Main docs use .asciidoc extension
- Extreme Hemingway style: short sentences, simple words, active voice
- No adjectives unless essential
- No adverbs
- One idea per sentence
- No emojis
- VT100 terminal text style
- PlantUML diagrams only

## Code Standards
- Follow DRY principle throughout codebase
- Keep functions and modules simple and focused (KISS)
- Use clear, descriptive variable and function names
- Minimize dependencies and complexity (KISS)
- Write code that is easily testable and maintainable (Modular and KISS)

## Container Standards
- Support both Docker and Podman environments
- Structure container projects under docker/ directory
- Use descriptive container and image names
- Include health checks and graceful shutdown handling
- Base on debian:stable-slim where possible

## File Organization
- Keep related files grouped logically
- Use consistent naming conventions
- Maintain clean directory structures
- Document file purposes and relationships
- images in /images
- ADRs in /adr
- /docs directory reserved for GitHub Pages deployment ONLY

## Running Commands
- System runs on Steam Deck in desktop mode
- VSCode runs as flatpak
- Use podman for containers

## VSCode Terminal Limits
- Copilot agent has 5-second timeout on terminal output
- Commands under 5 seconds return output
- Commands over 5 seconds do not return output
- Commands still execute but output is lost
- Background processes work without limit
- Use `command &` for long operations
- Chain with checks: `long-cmd > /tmp/out.txt & sleep 2 && cat /tmp/out.txt`
- Break operations into steps under 5 seconds each
- Use tmux or screen on remote hosts for long tasks
- The timeout is in agent tool layer not VSCode
- The timeout is in agent tool layer not flatpak-spawn
- Terminal itself works correctly 