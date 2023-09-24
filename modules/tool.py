import shutil
import os
import datetime
from . import settings


def save_file(from_path,to_path):
    """给文件存档"""
    if to_path==None:
        return
    nowtime=datetime.datetime.now()
    month=nowtime.strftime('%Y%m')
    if os.path.isdir(from_path):
        file_extension='folder'
        to_path=os.path.join(to_path,month,file_extension,os.path.basename(os.path.normpath(from_path)))
        i=1
        to_pathname=to_path
        while os.path.exists(to_pathname):
            to_pathname = f"{to_path}_{i}"
            i += 1

        append_file(settings.FILE_RECORD,f"[{nowtime.strftime('%Y-%m-%d %H:%M:%S')}] {from_path} -> {to_pathname}]")
        shutil.copytree(from_path, to_pathname)
    else:
        _, file_extension = os.path.splitext(from_path)
        file_extension=file_extension.lower()
        if file_extension in ('.bmp','.jpg','.jpeg','.png','.gif','.ico','.icns'):
            file_extension='picture'
        elif file_extension in ('.avi','.mp4','.mov','.wmv','.flv','.mkv'):
            file_extension='movie'
        elif file_extension in ('.xlsx','.xls'):
            file_extension='excel'
        elif file_extension in ('.doc','.docx'):
            file_extension='docx'
        else:
            file_extension='other'
        to_file=os.path.join(to_path,month,file_extension,os.path.basename(from_path))
        to_dir=os.path.dirname(to_file)
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)
        name, ext = os.path.splitext(to_file)
        i=1
        while os.path.exists(to_file):
            new_name = f"{name}_{i}{ext}"
            to_file = os.path.join(os.path.dirname(to_file), new_name)
            i += 1
        append_file(settings.FILE_RECORD, f"[{nowtime.strftime('%Y-%m-%d %H:%M:%S')}] {from_path} -> {to_file}]")
        shutil.copy2(from_path,to_file)



def append_file(filename,content):
    with open(filename,'a') as f:
        f.write(content+os.linesep)
