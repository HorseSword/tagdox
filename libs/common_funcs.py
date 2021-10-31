
def get_split_path(full_path) -> list:
    '''
    通用函数：    
    将完整路径按照斜杠拆分，得到每个文件夹到文件名的列表。
    '''
    test_str = full_path.replace('\\', '/', -1)
    test_str_res = test_str.split('/')
    return (test_str_res)
