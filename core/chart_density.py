import logging
logger = logging.getLogger("chart_density")
logger.setLevel(logging.DEBUG)
def get_range_coverage_ratio(closes, lower, upper):
    if not closes or not isinstance(closes, list):
        return 0.0
    total = len(closes)
    in_range = [c for c in closes if lower <= c <= upper]
    return len(in_range) / total if total > 0 else 0.0