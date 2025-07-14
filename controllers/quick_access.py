# Forms to jump to specific edit pages in smartgrid
def jump():
    autocomplete_args = dict(at_beginning = False, user_signature=True)

    # Go to dataset_detail view
    form_view_dset = SQLFORM.factory(
        Field('view_dataset', requires=IS_IN_DB(db, 'dataset.id'), 
            widget = SQLFORM.widgets.autocomplete(request, db.dataset.shortname, id_field=db.dataset.id,
                **autocomplete_args)),
        table_name = "view_dataset", _class = "form_quick_select"
    )
    if form_view_dset.process().accepted:
        redirect(URL(c='manage', f='dataset_detail', args=[form_view_dset.vars.view_dataset]))
        
    # Go to request_detail view
    form_view_request = SQLFORM.factory(
        Field('view_request', requires=IS_IN_DB(db, 'accessrequest.id'), 
            widget = SQLFORM.widgets.autocomplete(request, db.accessrequest.title, id_field=db.accessrequest.id,
                **autocomplete_args)),
        table_name = "view_request", _class = "form_quick_select"
    )
    if form_view_dset.process().accepted:
        redirect(URL(c='manage', f='dataset_detail', args=[form_view_dset.vars.view_dataset]))

    # Jump to edit project
    form_edit_project = SQLFORM.factory(
        Field('edit_project', requires=IS_IN_DB(db, 'project.id'), 
            widget = SQLFORM.widgets.autocomplete(request, db.project.title, id_field=db.project.id,
                **autocomplete_args)),
        table_name = "edit_project", _class = "form_quick_select"
    )
    if form_edit_project.process().accepted:
        redirect(URL(c='manage', f='browse', args=('project', 'edit', 'project', form_edit_project.vars.edit_project), 
            user_signature=True))

    # Jump to edit dataset
    form_edit_dset = SQLFORM.factory(
        Field('edit_dataset', requires=IS_IN_DB(db, 'dataset.id'), 
            widget = SQLFORM.widgets.autocomplete(request, db.dataset.shortname, id_field=db.dataset.id,
                keyword="_autocomplete_dataset_id_edit", # differentiate from view select form
                **autocomplete_args)), 
        table_name = "edit_dataset", _class = "form_quick_select"
    )
    if form_edit_dset.process().accepted:
        redirect(URL(c='manage', f='browse', args=['dataset', 'edit', 'dataset', form_edit_dset.vars.edit_dataset], 
        user_signature=True))

    # Jump to edit personnel details
    form_edit_personnel = SQLFORM.factory(
        Field('edit_personnel', requires=IS_IN_DB(db, 'personnel.id'), 
            widget = SQLFORM.widgets.autocomplete(request, db.personnel.name, id_field=db.personnel.id,
                **autocomplete_args)),
        table_name = "edit_personnel", _class = "form_quick_select"
    )
    if form_edit_personnel.process().accepted:
        redirect(URL(c='manage', f='browse', args=['personnel', 'edit', 'personnel', form_edit_personnel.vars.edit_personnel], 
        user_signature=True))

    # Jump to edit user details
    form_edit_user = SQLFORM.factory(
        Field('edit_user', requires=IS_IN_DB(db, 'repo_user.id', '%(name)s'),
            widget = SQLFORM.widgets.autocomplete(request, db.repo_user.name, id_field=db.repo_user.id,
                **autocomplete_args)), 
        table_name = "edit_user", _class = "form_quick_select"
    )
    if form_edit_user.process().accepted:
        redirect(URL(c='manage', f='browse', args=['repo_user', 'edit', 'repo_user', form_edit_user.vars.edit_user], 
        user_signature=True))

    return dict(form_view_dset = form_view_dset,
    form_view_request = form_view_request,
    form_edit_project = form_edit_project,
    form_edit_dset = form_edit_dset,
    form_edit_personnel = form_edit_personnel,
    form_edit_user = form_edit_user
    )

def duplicate_dataset():
    # Choose dataset to copy
    form = SQLFORM.factory(
        Field('select_dataset', 'dataset.id', requires=IS_IN_DB(db, 'dataset.id', '%(shortname)s')),
        Field('copy_includes', 'list:string', requires=IS_IN_SET((
          "Intellectual rights", "Personnel", "Keywords"), multiple = True), 
            default = ("Intellectual rights", "Personnel", "Keywords"), widget = SQLFORM.widgets.checkboxes.widget),
        Field('confirm_duplication', requires=[IS_IN_SET((True,)), IS_NOT_EMPTY()], widget = SQLFORM.widgets.checkboxes.widget),
        table_name = "select_dataset",
        submit_button='Duplicate'
    )
    
    if form.validate():
        selected = db.dataset._filter_fields(db.dataset(form.vars.select_dataset))
        selected['shortname'] = selected['shortname'] + "_COPY"
        selected['title'] = selected['title'] + "_COPY"
        # remove publication process info, and links
        vars_nocopy = ('request_date', 'provision_status', 'provision_date', 'pubdate', 'pub_notes', 'public_link', 'repository_link')
        for i in vars_nocopy:
            selected.pop(i, None)
        new_id = db.dataset.insert(**selected)
        
        # copy intellectual rights if included
        if "Intellectual rights" in form.vars.copy_includes:
            rows_rights = db(db.intellectualright.dataset_id == form.vars.select_dataset).select()
            for row in rows_rights:
                row['dataset_id'] = new_id
                row.pop('id', None)
                db.intellectualright.insert(**row)
                
        if "Personnel" in form.vars.copy_includes:
            rows_personnel = db(db.j_dataset_personnel.dataset_id == form.vars.select_dataset).select()
            for row in rows_personnel:
                row['dataset_id'] = new_id
                row.pop('id', None)
                db.j_dataset_personnel.insert(**row)
                
        if "Keywords" in form.vars.copy_includes:
            rows_keywords = db(db.j_dataset_keyword.dataset_id == form.vars.select_dataset).select()
            for row in rows_keywords:
                row['dataset_id'] = new_id
                row.pop('id', None)
                db.j_dataset_keyword.insert(**row)
              

        response.flash = "Dataset copied"
        redirect(URL(c='manage', f='browse', 
            args=["dataset", "edit", "dataset", new_id],
            user_signature=True))

    return dict(form=form)

def add_user_as_personnel():
    # Choose user to copy
    form = SQLFORM.factory(
        Field('select_user', 'repo_user.id', requires=IS_IN_DB(db, 'repo_user.id', '%(name)s')),
        Field('confirm_insert', requires=[IS_IN_SET((True,)), IS_NOT_EMPTY()], widget = SQLFORM.widgets.checkboxes.widget),
        table_name = "select_user",
        submit_button='Add as personnel record'
    )
    
    if form.validate():
        selected = db.personnel._filter_fields(db.repo_user(form.vars.select_user))
        
        # if no orcid, check name only not duplicate
        if selected['orcid'] is None and db(db.personnel.name == selected['name']).count():
            response.flash = "User name already exists in personnel table"
            
        # if orcid, check orcid and name not duplicate
        elif (selected['orcid'] is not None and 
              db((db.personnel.orcid == selected['orcid']) | (db.personnel.name == selected['name'])).count()
              ):
            response.flash = "User name or ORCID already exists in personnel table"
            
        # duplicate if passed checks
        else:
            new_id = db.personnel.insert(**selected)
            response.flash = "User added as personnel record"
            redirect(URL(c='manage', f='browse', 
                args=["personnel", "edit", "personnel", new_id],
                user_signature=True))

    return dict(form=form)
