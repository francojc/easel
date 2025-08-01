# Easel CLI Development Workflows

**Claude Code Integration for Autonomous Milestone Development**

This directory contains a comprehensive set of slash commands and sub-agents designed specifically for developing the Easel CLI - a Python-based Canvas LMS automation tool for educational institutions.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     EASEL CLI DEVELOPMENT                       │
│                      (6 Milestone Project)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MILESTONE WORKFLOW                           │
│                                                                 │
│  setup → analyze → implement → validate → integrate → submit   │
│    │        │         │          │           │         │       │
│    ▼        ▼         ▼          ▼           ▼         ▼       │
│   /cmd    /cmd      @agent     @agent      /cmd      /cmd     │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌───────────────┐ ┌───────────────┐ ┌─────────────────┐
        │   UTILITIES   │ │  SPECIALISTS  │ │   TROUBLESHOOT  │
        │               │ │               │ │                 │  
        │ /easel:test   │ │ @analytics-   │ │ @doctor         │
        │ /easel:docs   │ │  specialist   │ │ @troubleshooting│
        │ /easel:release│ │ @security-    │ │  -specialist    │
        │               │ │  specialist   │ │                 │
        └───────────────┘ └───────────────┘ └─────────────────┘
```

## 🚀 Core Milestone Workflow

The development process follows a strict 6-phase approach with quality gates:

```
Phase 1: SETUP                     Phase 2: ANALYZE
┌─────────────────┐                ┌─────────────────┐
│ /milestone:setup│───────────────▶│/milestone:analyze│
│                 │                │      <N>        │
│ • Verify tools  │                │                 │
│ • Install deps  │                │ • Read specs    │
│ • Pre-commit    │                │ • Create issue  │
│ • Validate env  │                │ • Create branch │
└─────────────────┘                └─────────────────┘
         │                                   │
         ▼                                   ▼
    ✅ All tools                       ✅ Branch ready
       available                          Issue created
                                         Context set

Phase 3: IMPLEMENT                 Phase 4: VALIDATE  
┌─────────────────┐                ┌─────────────────┐
│@implementation- │───────────────▶│  @qa-specialist │
│   specialist    │                │                 │
│                 │                │ • Test coverage │
│ • Architecture  │                │ • Code quality  │
│ • Code patterns │                │ • Security scan │
│ • TDD approach  │                │ • Acceptance    │
│ • Security      │                │   criteria      │
└─────────────────┘                └─────────────────┘
         │                                   │
         ▼                                   ▼
    ✅ Code complete                   ✅ Quality gates
       Tests written                      passed (≥80%)
       Patterns followed                  Security clean

Phase 5: INTEGRATE                 Phase 6: SUBMIT
┌─────────────────┐                ┌─────────────────┐
│/milestone:      │───────────────▶│ /milestone:     │
│  integrate      │                │   submit        │
│                 │                │                 │
│ • Documentation │                │ • Create PR     │
│ • CLI help      │                │ • Comprehensive │
│ • End-to-end    │                │   documentation │
│ • Integration   │                │ • Link issues   │
└─────────────────┘                └─────────────────┘
         │                                   │
         ▼                                   ▼
    ✅ Docs current                    ✅ PR created
       E2E tests pass                     Ready for review
       Integration OK                     Complete docs
```

## 🤖 Sub-Agent Specialists

### Milestone Development Agents

```
@doctor                           @implementation-specialist
┌─────────────────────────┐      ┌─────────────────────────┐
│ 🏥 HEALTH DIAGNOSTICS   │      │ 👩‍💻 CODE IMPLEMENTATION   │
│                         │      │                         │
│ • Environment checks    │      │ • Architectural comply  │
│ • Tool validation       │      │ • Pattern recognition   │
│ • Dependency status     │      │ • Test-driven dev       │
│ • Configuration review │      │ • Security practices    │
│ • Milestone readiness   │      │ • Iterative refinement │
└─────────────────────────┘      └─────────────────────────┘

@qa-specialist                   @troubleshooting-specialist  
┌─────────────────────────┐      ┌─────────────────────────┐
│ 🧪 QUALITY ASSURANCE    │      │ 🔧 ERROR RECOVERY       │
│                         │      │                         │
│ • Test coverage (≥80%)  │      │ • Failure diagnosis     │
│ • Code quality checks  │      │ • Recovery procedures   │
│ • Security scanning    │      │ • Root cause analysis  │
│ • Performance testing  │      │ • Prevention strategies │
│ • Acceptance criteria  │      │ • Systematic recovery   │
└─────────────────────────┘      └─────────────────────────┘
```

### Domain Specialists

```
@analytics-specialist             @security-specialist
┌─────────────────────────┐      ┌─────────────────────────┐
│ 📊 CANVAS DATA EXPERT    │      │ 🔒 SECURITY & COMPLIANCE│
│                         │      │                         │
│ • Canvas API patterns   │      │ • FERPA compliance      │
│ • Large dataset handling│      │ • Educational security  │
│ • Educational analytics │      │ • Vulnerability analysis│
│ • Export optimization   │      │ • Secure coding         │
│ • Performance scaling   │      │ • Privacy controls      │
│ • FERPA data handling   │      │ • Institutional standards│
└─────────────────────────┘      └─────────────────────────┘
```

## ⚡ Utility Commands

```
Development Utilities Workflow
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Code Changes  ──┐                                          │
│                  │    ┌─────────────────┐                  │
│                  └───▶│  /easel:test    │                  │
│                       │                 │                  │
│                       │ • pytest + cov │                  │
│                       │ • black/flake8  │                  │
│                       │ • mypy typing   │                  │
│                       │ • security scan │                  │
│                       │ • pre-commit    │                  │
│                       └─────────────────┘                  │
│                                │                            │
│                                ▼                            │
│  Documentation ──┐    ┌─────────────────┐                  │
│    Updates       └───▶│  /easel:docs    │                  │
│                       │                 │                  │
│                       │ • API doc gen   │                  │
│                       │ • CLI help      │                  │
│                       │ • Link checking │                  │
│                       │ • Spell check   │                  │
│                       │ • Coverage badge │                  │
│                       └─────────────────┘                  │
│                                │                            │
│                                ▼                            │
│  Release Prep   ──┐    ┌─────────────────┐                  │
│                   └───▶│ /easel:release  │                  │
│                        │                 │                  │
│                        │ • Quality gates │                  │
│                        │ • Build artifacts│                 │
│                        │ • Test install  │                  │
│                        │ • Changelog gen │                  │
│                        │ • Version checks │                 │
│                        └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Usage Patterns by Development Phase

### Starting Development
```bash
# One-time setup
/milestone:setup

# Health check anytime  
@doctor

# Begin milestone work
/milestone:analyze 1    # (or 2, 3, 4, 5, 6)
```

### During Implementation
```bash
# Get implementation guidance
@implementation-specialist

# For Canvas data features (Milestone 3)
@analytics-specialist

# For security features or reviews
@security-specialist

# Run tests frequently
/easel:test
```

### Quality Assurance
```bash
# Comprehensive validation
@qa-specialist

# Update documentation
/easel:docs

# If issues arise
@troubleshooting-specialist
```

### Completion
```bash
# Final integration
/milestone:integrate

# Create pull request
/milestone:submit

# Prepare releases
/easel:release
```

## 📋 Quality Gates & Standards

### Milestone Quality Requirements
```
┌─────────────────────────────────────────────────────────────┐
│                    QUALITY STANDARDS                        │
├─────────────────────────────────────────────────────────────┤
│ Test Coverage:     ≥80% (≥95% for production milestone)    │
│ Code Quality:      All linting and type checks pass        │
│ Security:          No high/critical vulnerabilities        │
│ Documentation:     Complete docstrings and help text       │
│ Performance:       <2s uncached, <100ms cached operations  │
│ Compliance:        FERPA, institutional requirements       │
└─────────────────────────────────────────────────────────────┘
```

### Automated Validation Pipeline
```
Code Commit ──▶ Pre-commit Hooks ──▶ CI Pipeline
     │               │                    │
     ▼               ▼                    ▼
┌─────────┐   ┌─────────────┐    ┌──────────────┐
│ Format  │   │ • black     │    │ • pytest    │
│ & Lint  │   │ • flake8    │    │ • coverage   │
│ & Type  │   │ • mypy      │    │ • security   │
│ & Test  │   │ • pytest    │    │ • integration│
└─────────┘   └─────────────┘    └──────────────┘
```

## 🔄 Error Recovery Workflow

```
Phase Failure Detected
         │
         ▼
┌─────────────────┐
│ @troubleshooting│
│   -specialist   │
│                 │
│ 1. Diagnose     │
│ 2. Analyze root │
│ 3. Recovery plan│
│ 4. Execute fix  │
│ 5. Validate     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Re-run Failed   │
│ Phase           │
│                 │
│ • setup         │
│ • analyze       │
│ • implement     │
│ • validate      │
│ • integrate     │
│ • submit        │
└─────────────────┘
         │
         ▼
    Success? ──No──┐
         │         │
         Yes       │
         │         ▼
         ▼    Escalate to
    Continue     Human Review
```

## 🏫 Educational Technology Focus

### Canvas LMS Integration
- **API Security**: Secure token management and rate limiting
- **Data Privacy**: FERPA-compliant data handling and anonymization
- **Institutional Scale**: Performance optimization for 1000+ courses, 10k+ students
- **Educational Workflows**: Academic term awareness, grade posting patterns

### Compliance & Security
- **FERPA**: Educational record protection and access controls
- **COPPA**: Age-appropriate data collection where applicable  
- **GDPR**: Data subject rights and privacy by design
- **Institutional**: Custom security and governance requirements

## 🚀 Getting Started

1. **Initialize Environment**
   ```bash
   /milestone:setup
   ```

2. **Start First Milestone**
   ```bash
   /milestone:analyze 1
   ```

3. **Get Implementation Help**
   ```bash
   @implementation-specialist
   ```

4. **Run Quality Checks**
   ```bash
   /easel:test
   ```

This comprehensive workflow system ensures production-quality development for educational institutions while maintaining the highest standards of security, privacy, and reliability.

---

**Remember**: Easel CLI handles sensitive educational data. Every decision prioritizes **student privacy**, **institutional security**, and **regulatory compliance** over development speed.