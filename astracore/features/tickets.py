"""AstraCore Tickets feature toolkit. Each operation is deterministic and production-safe."""

def normalize_name_tickets(value):
    return str(value).strip().lower().replace(" ", "-")[:100]

def clean_text_tickets(value):
    return " ".join(str(value).split())

def truncate_text_tickets(value, limit=2000):
    return str(value)[:limit]

def clamp_value_tickets(value, low, high):
    return max(low, min(high, value))

def paginate_items_tickets(items, page=1, size=20):
    return list(items)[max(0,page-1)*size:page*size]

def page_count_tickets(total, size=20):
    return (max(0,total)+size-1)//size if size>0 else 0

def contains_token_tickets(value, token):
    return token.casefold() in str(value).casefold()

def safe_int_tickets(value, default=0):
    return int(value) if str(value).lstrip("-").isdigit() else default

def safe_bool_tickets(value):
    return str(value).strip().lower() in {"1","true","yes","on"}

def positive_or_zero_tickets(value):
    return max(0, int(value))

def format_id_tickets(value):
    return f"{int(value):d}"

def unique_ints_tickets(values):
    return list(dict.fromkeys(int(x) for x in values))

def merge_sets_tickets(left, right):
    return sorted(set(left).union(right))

def difference_sets_tickets(left, right):
    return sorted(set(left).difference(right))

def overlap_sets_tickets(left, right):
    return sorted(set(left).intersection(right))

def ratio_tickets(numerator, denominator):
    return 0.0 if denominator==0 else numerator/denominator

def percent_tickets(part, total):
    return 0.0 if total==0 else round(part/total*100, 2)

def is_within_tickets(value, minimum, maximum):
    return minimum <= value <= maximum

def sort_records_tickets(records, key, reverse=False):
    return sorted(records, key=lambda item: item.get(key, 0), reverse=reverse)

def first_or_none_tickets(value):
    return next(iter(items), None)

def count_matches_tickets(items, predicate):
    return sum(1 for item in items if predicate(item))

def filter_matches_tickets(items, predicate):
    return [item for item in items if predicate(item)]

def map_values_tickets(items, transform):
    return [transform(item) for item in items]

def chunk_items_tickets(items, size=20):
    return [list(items)[i:i+size] for i in range(0,len(list(items)),size)] if size>0 else []

def key_exists_tickets(mapping, key):
    return key in mapping

def with_default_tickets(mapping, key, default=None):
    return mapping.get(key, default)
