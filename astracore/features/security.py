"""AstraCore Security feature toolkit. Each operation is deterministic and production-safe."""

def normalize_name_security(value):
    return str(value).strip().lower().replace(" ", "-")[:100]

def clean_text_security(value):
    return " ".join(str(value).split())

def truncate_text_security(value, limit=2000):
    return str(value)[:limit]

def clamp_value_security(value, low, high):
    return max(low, min(high, value))

def paginate_items_security(items, page=1, size=20):
    return list(items)[max(0,page-1)*size:page*size]

def page_count_security(total, size=20):
    return (max(0,total)+size-1)//size if size>0 else 0

def contains_token_security(value, token):
    return token.casefold() in str(value).casefold()

def safe_int_security(value, default=0):
    return int(value) if str(value).lstrip("-").isdigit() else default

def safe_bool_security(value):
    return str(value).strip().lower() in {"1","true","yes","on"}

def positive_or_zero_security(value):
    return max(0, int(value))

def format_id_security(value):
    return f"{int(value):d}"

def unique_ints_security(values):
    return list(dict.fromkeys(int(x) for x in values))

def merge_sets_security(left, right):
    return sorted(set(left).union(right))

def difference_sets_security(left, right):
    return sorted(set(left).difference(right))

def overlap_sets_security(left, right):
    return sorted(set(left).intersection(right))

def ratio_security(numerator, denominator):
    return 0.0 if denominator==0 else numerator/denominator

def percent_security(part, total):
    return 0.0 if total==0 else round(part/total*100, 2)

def is_within_security(value, minimum, maximum):
    return minimum <= value <= maximum

def sort_records_security(records, key, reverse=False):
    return sorted(records, key=lambda item: item.get(key, 0), reverse=reverse)

def first_or_none_security(value):
    return next(iter(items), None)

def count_matches_security(items, predicate):
    return sum(1 for item in items if predicate(item))

def filter_matches_security(items, predicate):
    return [item for item in items if predicate(item)]

def map_values_security(items, transform):
    return [transform(item) for item in items]

def chunk_items_security(items, size=20):
    return [list(items)[i:i+size] for i in range(0,len(list(items)),size)] if size>0 else []

def key_exists_security(mapping, key):
    return key in mapping

def with_default_security(mapping, key, default=None):
    return mapping.get(key, default)
