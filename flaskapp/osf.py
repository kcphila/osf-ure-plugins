import flask
import requests
import re
import sys

from requests.models import stream_decode_response_unicode 

bp = flask.Blueprint('osf', __name__, url_prefix='/osf')


abspath = re.compile(r'https?://', re.I)
osf_server = "https://api.osf.io/v2"




def osfapicall(url, reqparams, method):

    if not url:
        raise Exception('must provide a url')    
    
    if not reqparams:
        reqparams = None
    
    if not abspath.match(url):
        url = osf_server + url

    access_token = flask.session.get('access_token')
    if not access_token:
        return({
            'errors': [{'detail': "You must be logged in to OSF to perform this action."}],
            'action': 'login',
            'status_code': -1,
        })
    
    #print(f"about to make {method} req:\n\t{url}\n\t{reqparams}\n\tToken: {access_token}", file=sys.stderr)
    if method == 'get':
        # 'params' is the payload, not 'data'
        # Returns contentful json  
        req = requests.get(
            url,
            headers={"Authorization" : "Bearer " + access_token},
            params=reqparams,
        )
    elif method in ('post', 'delete'):
        # 'data' is the payload. 'params' is available for explicit url params, but this doesn't exist in the OSF API
        req = getattr(requests, method)(
            url,
            headers={"Authorization" : "Bearer " + access_token},
            data=reqparams,
        )    
    else:
        raise Exception(f"Unknown method {method}")


    if req.status_code == 401 or req.status_code == 403:
        #
        # 401 - this happens when our access token is incorrect or expired
        #
        js = req.json()
        js['errors'].append({'detail': f'status_code: {req.status_code}'})
        js['action'] = 'reauthorize'
        js['status_code'] = req.status_code
        return(js)

    if not req.ok:
        raise Exception(f"Attempt to {method} {url} returned unexpected status code {req.status_code}.\n<h3>Debug Info</h3>\nResponse Status Code: {req.status_code}\nResponse Reason: {req.reason}\nResponse Headers: {req.headers}\nResponse Text: {req.text}")
    if method in ('delete',):
        return({
            'url': url,
            'params': reqparams,
            'status_code': req.status_code,
            'reason': method + " api call successful.",
        })

    js = req.json()
    return(js)     

def osfpost(url, url_params=None):
    return(osfapicall(url, url_params, method='post'))

def osfget(url, url_params=None):
    return(osfapicall(url, url_params, method='get'))

def osfdelete(url, url_params=None):
    return(osfapicall(url, url_params, method='delete'))


def osfgetdata(url, url_params=None, fetch_all=False):
    
    resp = osfget(url, url_params)
    if 'data' not in resp:
        if 'errors' not in resp:
            resp['errors'] = f"Call to osfgetdata for {url}, but this returned neither data nor an error message"
        return(resp)
    
    data = resp['data']
    if type(data) not in (tuple, list):
        return(data)

    if fetch_all:
        if 'links' in resp and 'next' in resp['links'] and resp['links']['next']:
            nextdata = osfgetdata(resp['links']['next'], fetch_all=True)
            if type(nextdata) is list:
                return(data + nextdata)
            if not 'errors' in nextdata and nextdata['errors']:
                raise Exception(f"Unexpected result. Data returned was an array for the first page but not an array for the follow pages")
            return(nextdata)
    
    return(data)


@bp.route('/admin', methods=['GET', 'POST'])
def ap_admin():
    if flask.request.url_root != 'http://localhost:3000/':
        raise Exception("Path not allowed")
    params = flask.request.values.to_dict()
    url = params['url']
    del params['url']  
    if 'method' in params:
        method = params['method']
        del params['method']
    else:
        method = 'get'      
    return(osfapicall(url, params, method=method))

@bp.route('/api', methods=['GET', 'POST'])
def osfget_url():
    params = flask.request.values.to_dict()
    url = params['url']
    del params['url']    
    return(osfget(url, params))

@bp.route('/data', methods=['GET', 'POST'])
def osfget_data():
    params = flask.request.values.to_dict()
    url = params['url']
    del params['url']    
    if 'fetch_all' in params:
        fetch_all = params['fetch_all']
        del params['fetch_all']
    else:
        fetch_all = False
    return(osfgetdata(url, params, fetch_all=fetch_all))


@bp.route('/me', methods=['GET', 'POST'])
def getme(refresh=False):
    data = flask.session.get('me')
    if refresh or not data:        
        js = osfget('/users/me/')
        if not 'data' in js:
            # error
            return(js)
        js = js['data']            
        data = {
            'name': js['attributes']['full_name'],
            'id': js['id'],
            'nodes': js['relationships']['nodes']['links']['related']['href'],
        }
        flask.session['me'] = data
    return(data)

@bp.route('/nodes', methods=['GET', 'POST'])
def getnodes():
    data = flask.session.get('nodes')
    if data:
        return(data)

    me = getme()
    if not data:
        bibliographic_only = flask.request.form.get('bibliographic')
        include_components = flask.request.form.get('include_components')
        if include_components == 'false':
            include_components = False
        
        params = {}
        if bibliographic_only:
            params = {                
                'embed': 'contributors',
                'fields': {
                    'nodes': ['category','current_user_is_contributor','current_user_permissions','date_created','date_modified','public','title','wiki_enabled','description','id','links','contributors'],                
                    'contributors': ['bibliographic','id','permission','users'],
                    'users': ['id', 'full_name'],
                },
                #'fields[users]': 'id,full_name',

                #'filter[parent]':'null', 
                #'embed': 'contributors',
                #'fields[nodes]': 'category,current_user_is_contributor,current_user_permissions,date_created,date_modified,public,title,wiki_enabled,description,id,links,contributors',
                #'fields[contributors]': 'bibliographic,id,permission,users',
                #'fields[users]': 'id,full_name',
            }
        else:
            params = {
                #'filter[parent]': 'null',
                #'filter[contributors]': me['id'],
                #'filter': {
                #    'parent':None,
                #    'contributors': me['id'],
                #},
            }
        if not include_components:
            params['filter[parent]'] = 'null'
        #else:
        #    print(f"WTF? Include components is {include_components}", file=sys.stderr)

        data = osfgetdata(f"/users/{me['id']}/nodes/", params, fetch_all=True)
        if type(data) is not list:
            return(data)

        
        if bibliographic_only:
            bibliographic = [] 
            for node in data:
                # find the contributor record 
                for contrib in node['embeds']['contributors']['data']:
                    # if this is the user AND it's a bibliographic contribution, add it and break
                    if contrib['embeds']['users']['data']['id'] != me['id']:                        
                        continue
                    if contrib['attributes']['bibliographic']:                        
                        bibliographic.append(node)
                        break   
            return({'data': bibliographic})
        else:
            return({'data': data})

