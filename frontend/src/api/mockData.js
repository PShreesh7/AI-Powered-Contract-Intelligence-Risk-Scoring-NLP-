export const mockAnalysis = {
  overallRisk: 64,
  fullText:
    "This Master Services Agreement (\"Agreement\") is entered into between the Client and the Provider. " +
    "The Provider shall indemnify and hold harmless the Client from any and all claims arising from " +
    "the Provider's negligence, without limitation as to amount or duration. " +
    "Either party may terminate this Agreement for convenience upon thirty (30) days written notice. " +
    "In no event shall either party be liable for indirect, incidental, or consequential damages. " +
    "This Agreement shall automatically renew for successive one (1) year terms unless either party " +
    "provides notice of non-renewal at least sixty (60) days prior to the end of the then-current term. " +
    "All disputes arising under this Agreement shall be resolved through binding arbitration in a venue " +
    "chosen solely by the Provider.",
  clauses: [
    {
      id: 'c1',
      label: 'Indemnification',
      text: "indemnify and hold harmless the Client from any and all claims arising from the Provider's negligence, without limitation as to amount or duration",
      startOffset: 108,
      endOffset: 253,
      risk: 'high',
      riskScore: 88,
      rationale: 'Uncapped, unlimited-duration indemnity is unusually broad and should be scoped or capped.'
    },
    {
      id: 'c2',
      label: 'Termination for Convenience',
      text: 'Either party may terminate this Agreement for convenience upon thirty (30) days written notice.',
      startOffset: 255,
      endOffset: 353,
      risk: 'low',
      riskScore: 20,
      rationale: 'Mutual, reasonable notice period. Standard and balanced.'
    },
    {
      id: 'c3',
      label: 'Limitation of Liability',
      text: 'In no event shall either party be liable for indirect, incidental, or consequential damages.',
      startOffset: 355,
      endOffset: 449,
      risk: 'low',
      riskScore: 25,
      rationale: 'Mutual carve-out for consequential damages is standard practice.'
    },
    {
      id: 'c4',
      label: 'Auto-Renewal',
      text: 'This Agreement shall automatically renew for successive one (1) year terms unless either party provides notice of non-renewal at least sixty (60) days prior to the end of the then-current term.',
      startOffset: 451,
      endOffset: 646,
      risk: 'medium',
      riskScore: 55,
      rationale: 'Auto-renewal with a 60-day opt-out window is common but easy to miss — flag for calendar tracking.'
    },
    {
      id: 'c5',
      label: 'Dispute Resolution / Venue',
      text: 'All disputes arising under this Agreement shall be resolved through binding arbitration in a venue chosen solely by the Provider.',
      startOffset: 648,
      endOffset: 780,
      risk: 'high',
      riskScore: 82,
      rationale: "One-sided venue selection favors the Provider and should be negotiated to a neutral or mutually agreed forum."
    }
  ]
};
