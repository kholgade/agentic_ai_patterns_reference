import OpenAI from 'openai';

const HARM_CATEGORIES = {
  VIOLENCE: 'violence',
  HATE_SPEECH: 'hate_speech',
  SEXUAL: 'sexual',
  SELF_HARM: 'self_harm',
  MISINFORMATION: 'misinformation',
  PII: 'personal_identifiable_info'
};

const ACTIONS = {
  ALLOW: 'allow',
  BLOCK: 'block',
  SANITIZE: 'sanitize',
  ESCALATE: 'escalate'
};

class InputGuardrails {
  constructor(config = {}) {
    this.maxLength = config.maxLength || 10000;
    this.threshold = config.threshold || 0.7;
    this.blockedPatterns = [
      /ignore.*(previous|instructions|system|prompt)/i,
      /(system\s*:|system:)/i,
      /^```system/i,
      /JAILBREAK/i,
      /developer.*mode/i
    ];
  }

  validate(input) {
    if (input.length > this.maxLength) {
      return {
        action: ACTIONS.BLOCK,
        category: null,
        confidence: 1.0,
        reason: `Input exceeds max length of ${this.maxLength}`
      };
    }

    for (const pattern of this.blockedPatterns) {
      if (pattern.test(input)) {
        return {
          action: ACTIONS.BLOCK,
          category: null,
          confidence: 1.0,
          reason: `Blocked pattern: ${pattern}`
        };
      }
    }

    return {
      action: ACTIONS.ALLOW,
      category: null,
      confidence: 1.0,
      reason: 'Input passed all guardrails'
    };
  }
}

class OutputGuardrails {
  constructor(config = {}) {
    this.threshold = config.threshold || 0.8;
  }

  sanitizePII(text) {
    const patterns = [
      { regex: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[SSN REDACTED]' },
      { regex: /\b\d{16}\b/g, replacement: '[CREDIT CARD REDACTED]' },
      { regex: /\b[\w.-]+@[\w.-]+\.\w+\b/g, replacement: '[EMAIL REDACTED]' }
    ];
    
    return patterns.reduce((text, { regex, replacement }) => 
      text.replace(regex, replacement), text);
  }

  validate(output) {
    const sanitized = this.sanitizePII(output);
    const wasModified = sanitized !== output;
    
    return {
      action: wasModified ? ACTIONS.SANITIZE : ACTIONS.ALLOW,
      category: wasModified ? HARM_CATEGORIES.PII : null,
      confidence: 0.9,
      reason: wasModified ? 'PII detected and redacted' : 'Output validated',
      sanitizedContent: wasModified ? sanitized : null
    };
  }
}