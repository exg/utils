import math

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


def format_size(n):
    if n == 0:
        return "0"
    units = ("", "K", "M", "G", "T", "P", "E", "Z", "Y")
    exp = int(math.log(n, 1024))
    n /= 1 << (10 * exp)
    return "{:.2f}{}".format(n, units[exp])
