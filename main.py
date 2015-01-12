# This Python file uses the following encoding: utf-8
#
#гугло-библиотеки
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
import webapp2
# from google.appengine.api import memcache

import urllib
import random

import jinja2
import os

import connect_disk as yd


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
def get_db_key():
    return ndb.Key(table_name, 'default_token')

#Классы для работы с БД
class TempImage(ndb.Model):
    url = ndb.StringProperty()

class Users(ndb.Model):
    user = ndb.UserProperty()

def get_random_number(l = 15, st = 2):
    random.seed()
    cont = True
    s = "1234567890abcdefghijklmnopqrstuvwxyz" if st == 1 else "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ran_str = ""

    for i in range(l):
        ran_str += "".join(random.sample(s, 1))

    return ran_str


class PostHandler(webapp2.RequestHandler):
    def get(self, param1 = None):
        if param1 == None:
            self.abort(404)


        self.response.write(urllib.quote(param1.decode('utf-8')))
        #r = yd.get_image_from_url(urllib.quote(param1.decode('windows-1251')), 'XL')
        #urllib.quote(dir['orig'].encode('utf-8'))
        if not r['status'] == 200:
            self.abort(r['status'])

        directories = yd.get_list_directories()['list_directories']
        for post in directories:
            if post['orig'] == param1:
                post['active'] = True
            else:
                post['active'] = False

            #self.response.write(post['path'] + '=' + param1 + '=' +post['orig'] + '<br>')
        template_values = {'list_prev': r['files'],
                           'name': r['name'],
                           'list_links': directories}

        template = jinja_environment.get_template('static/tmpl/post.html')
        self.response.write(template.render(template_values))

class CreatePreview(webapp2.RequestHandler):
    def post(self):

        name = self.request.get('name')
        temp_image = TempImage()
        temp_image.url = name
        temp_image.put()

class CreateRecord(webapp2.RequestHandler):
    def get(self):
        # Add the task to the default queue.
        #taskqueue.add(url='/tasks', params={'name': 'roman'})
        self.redirect('https://oauth.yandex.ru/authorize?response_type=code&client_id=ae4c2e272bc64cd99f68ea0325883a83')
        #self.response.write('ok')

class CreateRecord2(webapp2.RequestHandler):
    def get(self):

        code_client = '4675537'
        #Формирование параметров (тела) POST-запроса с указанием кода подтверждения
        query = {
            'grant_type': 'authorization_code',
            'code': code_client,
            'client_id': 'ae4c2e272bc64cd99f68ea0325883a83',
            'client_secret': '9fe5fe5f5857452fa7eb405f644b0e85',
        }
        query = urllib.urlencode(query)

        #Формирование заголовков POST-запроса
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        #Выполнение POST-запроса и вывод результата
        connection = httplib.HTTPSConnection('oauth.yandex.ru')
        connection.request('POST', '/token', query, header)
        response = connection.getresponse()
        result = response.read()
        connection.close()

        self.response.write(str(result))

class CreateRecord3(webapp2.RequestHandler):
    def get(self):
        r = yd.get_list_directories()
        for dir in r['list_directories']:
            pass


class MainHandler(webapp2.RequestHandler):
    def get(self):

        resp = yd.get_list_directories()
        if resp['status'] == 200:
            for dir in resp['list_directories']:
                r = yd.get_image_from_url(urllib.quote(dir['orig'].encode('utf-8')), 'S', 3)

                dir['list_prev'] = r['files']
                dir['count'] = r['count']
        else:
            self.abort(resp['status'])

        template_values = {'list_posts': resp['list_directories']}
        template = jinja_environment.get_template('static/tmpl/index.html')
        self.response.write(template.render(template_values))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/p/(.+)', PostHandler),
    ('/tasks', CreatePreview),
    ('/test', CreateRecord),
    ('/test2', CreateRecord2),
    ('/test3', CreateRecord3)
], debug=True)
