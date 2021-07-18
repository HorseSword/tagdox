import os
'''
批量修改文件名的工具。
将文件名里面的标签符号批量转换。

'''
#%%

vPath=r'D:\MaJian\Desktop\青创赛'
V_SEP_OLD='#' # 这是旧标签符号
V_SEP_NEW='^' # 这是新标签符号
V_SEP=V_SEP_NEW

def safe_get_name(new_name):
    '''

    输入目标全路径，返回安全的新路径（可用于重命名、新建等）
    输入和输出都是字符串。

    '''
    n=1
    [tmp_path,tmp_new_name]=os.path.split(new_name)

    p=tmp_new_name.find(V_SEP)
    if p>=0:
        name_1=tmp_new_name[:p]
        name_2=tmp_new_name[p:]
    else:
        p=tmp_new_name.rfind('.')
        if p>=0:
            name_1=tmp_new_name[:p]
            name_2=tmp_new_name[p:]
        else: # 连'.'都没有的话
            name_1=tmp_new_name
            name_2=''
    
    tmp_new_full_name=new_name   
    while os.path.isfile(tmp_new_full_name):
        tmp_new_name=name_1+'('+ str(n)+')'+name_2
        tmp_new_full_name=tmp_path+'/'+tmp_new_name
        n+=1
    # print(tmp_new_full_name)
    return(tmp_new_full_name)

def safe_rename(old_name,new_name):
    '''
    在基础的重命名之外，增加了对文件是否重名的判断；
    返回值str, 如果重命名成功，返回添加数字之后的最终文件名；
    如果重命名失败，返回原始文件名。
    '''
    old_name=old_name.replace('\\','/')
    new_name=new_name.replace('\\','/')

    tmp_new_full_name=safe_get_name(new_name)
    try:
        os.rename(old_name,tmp_new_full_name)
        return(tmp_new_full_name)
    except:
        print('安全重命名失败！')
        return(old_name)
        pass

if __name__=='__main__':
    for root, dirs, files in os.walk(vPath):
        for name in files:
            
            name2=name.replace(V_SEP_OLD,V_SEP_NEW)
            name2=name2.replace('\xa0',' ')
            tmp=os.path.join(root, name)
            tmp2=os.path.join(root, name2)
            file_old=tmp.replace('\\','/')
            file_new=tmp2.replace('\\','/')
            # print(file_old)
            # file_new=file_old.replace(V_SEP_OLD,V_SEP_NEW)
            # print(file_new)
            try:
                if file_old !=file_new:
                    if os.path.isfile(file_new): 
                        print('异常：新文件名已存在')
                        print(file_new)
                    else:
                        safe_rename(file_old,file_new)
                        # os.rename(file_old,file_new)
            except Exception as e:
                print(e)
                print('重命名失败')
                print(file_old)
                print(file_new)
            # break
        # break
    print('执行完毕')
