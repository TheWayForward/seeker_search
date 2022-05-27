import hashlib
import re


def array_verification(value):
    return not isinstance(value, (frozenset, list, set, tuple,))


def extract_num(text):
    # extract number from string
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_space(text):
    return text.replace(" ", "")


def extract_num_from_separator(text):
    text = remove_space(text)
    return int(text.replace(",", ""))


def zhihu_extract_num_from_comment(text):
    text = remove_space(text)
    if text == "添加评论":
        return 0
    else:
        return extract_num_from_separator(text.replace("条评论", ""))


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == "__main__":
    print(zhihu_extract_num_from_comment("1,222条评论"))
