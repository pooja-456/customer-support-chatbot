"""
Stage 4C: Historical Resolution Extraction
Extracts structural resolutions from the historically retrieved brand responses.
Calculates consistency across retrieved examples.
"""
import re

class HistoricalResolutionExtractor:
    def __init__(self):
        # Define basic heuristic patterns for extracting actions
        self.patterns = {
            'routes_to_dm': re.compile(r'(?i)\b(dm|direct message)\b'),
            'provides_link': re.compile(r'(?i)(http|apple\.co|support\.apple\.com)'),
            'requests_info': re.compile(r'(?i)(\?|let us know|what version|which device|which iphone)'),
            'troubleshooting': re.compile(r'(?i)\b(restart|update|reset|settings|plug in|turn off)\b')
        }

    def extract_action(self, brand_text):
        """Extracts resolution signals from a single brand response."""
        actions = {}
        for action_name, pattern in self.patterns.items():
            actions[action_name] = bool(pattern.search(brand_text))
        return actions

    def aggregate_resolutions(self, retrieved_evidence):
        """
        Takes the output of Stage 4B (list of retrieved evidence dictionaries).
        Returns aggregated resolution and consistency metrics.
        """
        if not retrieved_evidence:
            return {
                'actions_summary': {},
                'is_consistent': False,
                'consistency_score': 0.0,
                'extracted_links': []
            }

        counts = {key: 0 for key in self.patterns.keys()}
        total = len(retrieved_evidence)
        links = []

        for item in retrieved_evidence:
            text = item.get('brand_response', '')
            actions = self.extract_action(text)
            for k, v in actions.items():
                if v: counts[k] += 1
                
            # Extract actual links if any
            found_links = re.findall(r'(https?://[^\s]+)', text)
            links.extend(found_links)

        # Calculate consistency: what % of retrieved examples agree on the primary action?
        # Primary action is the most common action found.
        max_count = max(counts.values()) if counts else 0
        consistency_score = max_count / total if total > 0 else 0.0
        
        # We define consistency as >= 60% agreement on the dominant action
        is_consistent = consistency_score >= 0.60
        
        # Deduplicate links
        unique_links = list(set(links))

        return {
            'actions_summary': {k: (v / total) for k, v in counts.items()},
            'is_consistent': is_consistent,
            'consistency_score': consistency_score,
            'dominant_action': max(counts, key=counts.get) if max_count > 0 else None,
            'extracted_links': unique_links
        }

if __name__ == "__main__":
    extractor = HistoricalResolutionExtractor()
    evidence = [
        {'brand_response': 'Please DM us so we can help. https://t.co/abc'},
        {'brand_response': 'We want to look into this. Send us a DM.'},
        {'brand_response': 'Have you tried a restart? DM us the result.'}
    ]
    res = extractor.aggregate_resolutions(evidence)
    print("Aggregate Resolutions:")
    for k, v in res.items():
        print(f"  {k}: {v}")
