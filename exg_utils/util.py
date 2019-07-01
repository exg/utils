def pairwise_iter(obj):
    it = iter(obj)
    return zip(it, it)


def xml_dict_get(tree, key):
    dict_elem = tree.find(".//dict[key='%s']" % key)
    if dict_elem:
        for k, v in pairwise_iter(dict_elem):
            if k.text == key:
                return v.text
    return None
