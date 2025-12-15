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

## running commands that are not on the system (we're testing from a steamdeck in desktop mode from in a flatpack)
- we have podman use it 