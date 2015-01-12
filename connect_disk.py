# This Python file uses the following encoding: utf-8
#
import httplib
import json
import urllib
import uritemplate

# headers = {'Authorization': 'd9489d7ec91544a1a8f3ded0c6de141a',
#            'Accept': 'application/hal+json'}

headers = {'Authorization': 'f7b5a57c24524cbd87a39c031e09a717',
           'Accept': 'application/hal+json'}


connection = httplib.HTTPSConnection('cloud-api.yandex.net')
resource_url = '/v1/disk/resources?path={p_a_t_h}&sort=name'

def get_connect(path, size = ''):
    url = uritemplate.expand(resource_url, {'p_a_t_h': path.encode('windows-1251')})
    if not size == '':
        url += '&preview_size=' + size

    connection.request('GET', url, headers=headers)
    resp = connection.getresponse()
    content = resp.read()
    obj = json.loads(content) if content else None
    r = {}
    r['obj'] = obj

    if not resp.status == 200:
        r ['status'] = resp.status
    elif content == None:
        r['status'] = 404#Непонятно по какой причине это может произойти
    else:
        r['status'] = 200

    return r

# def get_preview(param):
#     path_preview = param['path'] + '/preview/' + param['size'] + param['name']
#     resp = get_connect(path_preview)
#     if resp['status'] == 200:


def get_image_from_url(path, size = '', limit = 0):
    resp = get_connect(path, size)
    if not resp['status'] == 200:
         return {'status':resp['status']}

    count = 0
    list_files = []
    files = resp['obj']['_embedded']['items']
    for file in files:
        count += 1

        if 'media_type' in file and file['media_type'] == "image":
            if limit > 0 and count >= limit + 1:
                pass
            else:
                full_path = file['path']
                name = file['name']
                param_preview = {}
                param_preview['path'] = full_path[0:full_path.find(name)]
                param_preview['size'] = size
                param_preview['name'] = name
                param_preview['preview'] = file['preview']

                #preview = get_preview(param_preview)
                list_files.append(file['preview'])


    return {'files': list_files,
            'status': 200,
            'name': resp['obj']['name'],
            'count': count}

def get_list_directories():
    resp = get_connect('app:/')
    list_posts = []
    result = {}
    if resp['status'] == 200:
        files = resp['obj']['_embedded']['items']
        for file in files:
            if "type" in file and file['type'] == 'dir':
                if file['name'] == 'preview':
                    continue

                list_posts.append({'name': file['name'],
                                   'path': 'p/' + urllib.quote(file['path'].encode('windows-1251')),
                                   'orig': file['path']})
        result['status'] = 200
        result['list_directories'] = list_posts
    else:
        result['status'] = resp['status']

    return result
