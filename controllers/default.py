# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    return dict(form=auth.login())

def principal():
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def user_info():
    message = T("User doesn't exist.")
    user = db.auth_user(username=request.args(0)) or message
    last_project = db(db.projects.project_owner == user.id).select(orderby=db.projects.created_on).last() or None
    my_projects = db(db.projects.project_owner == user.id).select(orderby=db.projects.created_on, limitby=(0,5)) or None
    user_id = user.id
    team = db(db.projects).select(orderby=db.projects.created_on, limitby=(0,5)) or None
    colaborate_projects = {}
    if team != None:
        for n,i in enumerate(team):
            if str(user_id) in i.team:
                colaborate_projects[n] = i
    else:
        colaborate_projects = None
    return dict(user=user, message=message, last_project=last_project, my_projects=my_projects, colaborate_projects=colaborate_projects)

def projects():
    message = T("Project not found.")
    project = db.projects(id=request.args(0)) or message
    return dict(project=project, message=message)

@auth.requires_login()
def create_project():
    form = SQLFORM(db.projects)
    if form.process().accepted:
        response.flash = T('Project created!')
    elif form.errors:
        response.flash = T('Form has errors!')
    return dict(form=form)


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
