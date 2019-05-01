# find the term text of this indenture
def find_text(Indenture_name, all_info):
    for ele in all_info:
        if Indenture_name in ele[0]:
            return ele[1]
    else:
        return None

# highlight the difference between text a and b
def inline_diff(a, b):
    import difflib
    from colr import color
    matcher = difflib.SequenceMatcher(None, a, b)
    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'insert':
            return color('......', fore='black', back='orange')
        elif tag!='equal':
            return color(matcher.a[i1:i2], fore='black', back='orange')
        else:
            return matcher.a[i1:i2]
    return ''.join(process_tag(*t) for t in matcher.get_opcodes())
