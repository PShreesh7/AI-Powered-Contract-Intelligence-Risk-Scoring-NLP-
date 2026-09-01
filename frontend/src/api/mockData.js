/**
 * Mock analysis data — matches the normalized frontend schema produced by client.js.
 * Used when USE_MOCK = true in client.js for offline development.
 */
export const mockAnalysis = {
  documentId:    'mock-doc-001',
  filename:      'Sample_Master_Service_Agreement.pdf',
  rawTextLength: 4821,
  overallRisk:   67,

  fullText:
    'This Master Services Agreement ("Agreement") is entered into as of January 1, 2024, between Acme Corporation ("Client"), ' +
    'a Delaware corporation, and TechPro Solutions Inc. ("Provider"), a California corporation.\n\n' +
    'The Provider shall indemnify and hold harmless the Client from any and all claims, damages, losses, and liabilities arising ' +
    'from the Provider\'s negligence or willful misconduct, without limitation as to amount or duration, including any third-party claims.\n\n' +
    'Either party may terminate this Agreement for convenience upon thirty (30) days written notice to the other party. ' +
    'Provider may terminate immediately upon material breach.\n\n' +
    'In no event shall either party be liable for indirect, incidental, punitive, or consequential damages, including but not limited ' +
    'to loss of profits, data, or business opportunities, even if advised of the possibility of such damages.\n\n' +
    'This Agreement shall automatically renew for successive one (1) year terms unless either party provides written notice of ' +
    'non-renewal at least sixty (60) days prior to the end of the then-current term.\n\n' +
    'All disputes, controversies, or claims arising out of or in connection with this Agreement shall be resolved through binding ' +
    'arbitration administered by JAMS in a venue chosen solely by the Provider, in San Francisco, California.',

  clauses: [
    {
      id: 'c1',
      label: 'Indemnification',
      clauseType: 'indemnification',
      text: "The Provider shall indemnify and hold harmless the Client from any and all claims, damages, losses, and liabilities arising from the Provider's negligence or willful misconduct, without limitation as to amount or duration, including any third-party claims.",
      startOffset: 188,
      endOffset: 440,
      risk: 'high',
      riskScore: 91,
      confidence: 0.94,
      rationale: 'Uncapped, unlimited-duration indemnity is unusually broad. The phrase "without limitation as to amount or duration" creates unbounded exposure.',
      suggestion: 'Negotiate a cap tied to fees paid in the prior 12 months and add a sunset clause on indemnification obligations.',
    },
    {
      id: 'c2',
      label: 'Termination for Convenience',
      clauseType: 'termination',
      text: 'Either party may terminate this Agreement for convenience upon thirty (30) days written notice to the other party. Provider may terminate immediately upon material breach.',
      startOffset: 442,
      endOffset: 614,
      risk: 'medium',
      riskScore: 52,
      confidence: 0.88,
      rationale: 'Mutual termination is balanced, but Provider\'s unilateral immediate termination right on "material breach" creates asymmetric risk without a cure period.',
      suggestion: 'Add a 30-day cure period before Provider can invoke immediate termination for breach.',
    },
    {
      id: 'c3',
      label: 'Limitation of Liability',
      clauseType: 'limitation_of_liability',
      text: 'In no event shall either party be liable for indirect, incidental, punitive, or consequential damages, including but not limited to loss of profits, data, or business opportunities, even if advised of the possibility of such damages.',
      startOffset: 616,
      endOffset: 852,
      risk: 'low',
      riskScore: 22,
      confidence: 0.96,
      rationale: 'Mutual exclusion of consequential damages is industry-standard and balanced between both parties.',
      suggestion: null,
    },
    {
      id: 'c4',
      label: 'Auto-Renewal',
      clauseType: 'auto_renewal',
      text: 'This Agreement shall automatically renew for successive one (1) year terms unless either party provides written notice of non-renewal at least sixty (60) days prior to the end of the then-current term.',
      startOffset: 854,
      endOffset: 1058,
      risk: 'medium',
      riskScore: 58,
      confidence: 0.91,
      rationale: '60-day opt-out window on auto-renewal is longer than typical (30 days). Easy to miss in high-volume contract environments — flag for calendar tracking.',
      suggestion: 'Set a calendar reminder 90 days before each renewal date. Consider negotiating the opt-out window down to 30 days.',
    },
    {
      id: 'c5',
      label: 'Dispute Resolution / Venue',
      clauseType: 'dispute_resolution',
      text: 'All disputes, controversies, or claims arising out of or in connection with this Agreement shall be resolved through binding arbitration administered by JAMS in a venue chosen solely by the Provider, in San Francisco, California.',
      startOffset: 1060,
      endOffset: 1290,
      risk: 'high',
      riskScore: 84,
      confidence: 0.89,
      rationale: 'One-sided venue selection (Provider\'s city) and JAMS arbitration are heavily skewed in favor of Provider. Binding arbitration also waives jury trial rights.',
      suggestion: 'Negotiate for neutral venue (e.g., mutual agreement or Client\'s jurisdiction) and consider whether binding arbitration is acceptable.',
    },
  ],

  entities: [
    { label: 'ORG',    text: 'Acme Corporation',          start_char: 105, end_char: 122 },
    { label: 'ORG',    text: 'TechPro Solutions Inc.',     start_char: 143, end_char: 165 },
    { label: 'DATE',   text: 'January 1, 2024',            start_char:  70, end_char:  86 },
    { label: 'DATE',   text: 'thirty (30) days',           start_char: 495, end_char: 511 },
    { label: 'DATE',   text: 'sixty (60) days',            start_char: 948, end_char: 963 },
    { label: 'DATE',   text: 'one (1) year',               start_char: 885, end_char: 897 },
    { label: 'DATE',   text: '12 months',                  start_char: 300, end_char: 309 },
    { label: 'GPE',    text: 'Delaware',                   start_char: 130, end_char: 138 },
    { label: 'GPE',    text: 'California',                 start_char: 160, end_char: 170 },
    { label: 'GPE',    text: 'San Francisco, California',  start_char: 1258, end_char: 1283 },
    { label: 'ORG',    text: 'JAMS',                       start_char: 1210, end_char: 1214 },
    { label: 'PERSON', text: 'Client',                     start_char: 125, end_char: 131 },
    { label: 'PERSON', text: 'Provider',                   start_char: 147, end_char: 155 },
  ],
};
