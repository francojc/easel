# Easel CLI Sub-Agents

This directory contains specialized Claude Code sub-agents for complex milestone development tasks. These sub-agents replace the corresponding slash commands with more sophisticated, conversational AI specialists.

## Sub-Agent Overview

### Milestone Development Sub-Agents

| Sub-Agent | Expertise | Converted From |
|-----------|-----------|----------------|
| `doctor` | Environment diagnostics and health assessment | `/milestone:doctor` |
| `implementation-specialist` | Architectural compliance and code implementation | `/milestone:implement` |
| `qa-specialist` | Quality assurance, testing, and security validation | `/milestone:validate` |
| `troubleshooting-specialist` | Error recovery and systematic troubleshooting | `/milestone:recover` |

### Specialized Domain Sub-Agents

| Sub-Agent | Expertise | Purpose |
|-----------|-----------|---------|
| `analytics-specialist` | Canvas data analysis and export strategies | Milestone 3 (Data Export & Analytics) specialist |
| `security-specialist` | Educational security and compliance | Comprehensive security analysis and FERPA compliance |


### Remaining Slash Commands

These commands remain as slash commands due to their procedural nature:

- `/milestone:setup` - Environment initialization (procedural)
- `/milestone:submit` - PR creation workflow (structured)
- `/milestone:analyze` - Specification reading and issue creation
- `/milestone:integrate` - Documentation and integration procedures

## Sub-Agent Capabilities

### Milestone Development Sub-Agents

#### 1. doctor
**Comprehensive Environment Health Assessment**
- Systematic diagnostic evaluation of development prerequisites
- Intelligent health scoring with actionable recommendations
- Pattern recognition for common environment issues
- Context-aware milestone readiness validation

#### 2. implementation-specialist
**Expert Code Implementation with Architectural Compliance**
- Deep understanding of Easel CLI architectural patterns
- Conversational implementation with iterative refinement
- Test-driven development with quality-first approach
- Security-conscious coding practices throughout

#### 3. qa-specialist
**Multi-Layered Quality Assurance Validation**
- Comprehensive testing strategy execution and analysis
- Security analysis with vulnerability detection
- Code quality assessment using multiple validation tools
- Systematic acceptance criteria verification

#### 4. troubleshooting-specialist
**Systematic Recovery and Problem Resolution**
- Pattern-based failure diagnosis across all milestone phases
- Phase-specific recovery procedures with escalation protocols
- Root cause analysis with preventive recommendations
- Intelligent recovery strategy selection based on failure severity

### Specialized Domain Sub-Agents

#### 5. analytics-specialist
**Canvas Data Analysis and Export Expertise**
- Canvas data model and API optimization expertise
- Large-scale institutional data processing (1000+ courses, 10k+ students)
- Educational analytics patterns and statistical reporting
- Performance-optimized export strategies with streaming and caching
- FERPA-compliant data handling and anonymization capabilities

#### 6. security-specialist
**Educational Security and Compliance**
- Educational technology security standards (FERPA, COPPA, GDPR)
- Canvas API security assessment and secure authentication patterns
- Institutional compliance and data governance requirements
- Comprehensive vulnerability analysis and secure coding practices
- Educational data protection and privacy controls

## Benefits of Sub-Agent Architecture

### Conversational Context
- **Iterative Problem Solving**: "That approach had issues, let's try this instead"
- **Real-time Guidance**: "I noticed a potential issue, here's how to address it"
- **Adaptive Strategy**: Adjust approach based on discoveries during execution

### Specialized Expertise
- **Domain Knowledge**: Each agent is an expert in their specific area
- **Pattern Recognition**: Learning from previous interactions and outcomes
- **Quality Focus**: Specialized validation and best practices for each domain

### Architectural Benefits
- **Modularity**: Clean separation of concerns and responsibilities
- **Maintainability**: Easier to update and enhance individual capabilities
- **Extensibility**: Simple to add new specialized agents as needs evolve

## Usage Patterns

### Direct Invocation
Sub-agents can be invoked directly by name:

**Milestone Development:**
```
@doctor - for environment health checks
@implementation-specialist - for complex implementation tasks
@qa-specialist - for comprehensive quality validation  
@troubleshooting-specialist - for error recovery and troubleshooting
```

**Specialized Domain Experts:**
```
@analytics-specialist - for Canvas data analysis and export optimization
@security-specialist - for security analysis and educational compliance
```

### Integration with Workflow
Sub-agents maintain the same workflow integration as the original slash commands:
1. `setup` → `analyze` → **`@implementation-specialist`** → **`@qa-specialist`** → `integrate` → `submit`
2. **`@doctor`** - available any time for health checks
3. **`@troubleshooting-specialist`** - available when any phase fails

### Context Management
Each sub-agent maintains focused context for their domain while integrating seamlessly with the overall milestone development workflow.

## Technical Implementation

### Sub-Agent Definition
Each sub-agent is defined in a Markdown file with YAML frontmatter specifying:
- `name`: Unique identifier
- `description`: Capabilities and purpose
- `tools`: Specific tool permissions

### Tool Access
- **doctor**: Bash, Read, Glob (diagnostic tools)
- **implementation-specialist**: Bash, Read, Write, Edit, Glob, Grep (full development)
- **qa-specialist**: Bash, Read (validation and testing)
- **troubleshooting-specialist**: Bash, Read, Write, Edit (recovery operations)

### Quality Standards
All sub-agents maintain the same high-quality standards as the original commands:
- Production-quality code for educational institutions
- Comprehensive security practices
- Thorough testing and validation
- Complete documentation and help text

## Migration Notes

### From Slash Commands
The conversion maintains full functionality while adding conversational capabilities:
- All original features and validation remain intact
- Enhanced with iterative problem-solving and real-time guidance
- Improved error handling and recovery strategies
- Better integration with project patterns and architectural decisions

### Workflow Compatibility
The overall milestone development workflow remains unchanged:
- Same phase sequence and dependencies
- Same quality gates and validation requirements
- Same security and compliance standards
- Enhanced with intelligent, contextual assistance

## Future Enhancements

The sub-agent architecture enables future enhancements:
- Additional specialized agents (e.g., performance optimizer, security auditor)
- Cross-agent collaboration for complex scenarios
- Machine learning integration for pattern recognition
- Enhanced context sharing and workflow orchestration

---

This sub-agent architecture transforms the Easel CLI from a command executor into an intelligent development partner, providing expert assistance while maintaining the highest standards of quality, security, and architectural integrity.
