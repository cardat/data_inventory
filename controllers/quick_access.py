# Forms to jump to specific edit pages in smartgrid
def jump():
    autocomplete_args = dict(limitby=(0, 10), min_length=4, at_beginning = False)

    # Go to dataset_detail view
    form_view_dset = SQLFORM.factory(
        Field('view_dataset', requires=IS_IN_DB(db, 'dataset.id', '%(shortname)s')), 
        # widget = SQLFORM.widgets.autocomplete(request, db.dataset.shortname, **autocomplete_args)),
        table_name = "view_dataset"
    )
    if form_view_dset.process().accepted:
        redirect(URL(c='manage', f='dataset_detail', args=[form_view_dset.vars.view_dataset]))

    # Jump to edit project
    form_edit_project = SQLFORM.factory(
        Field('edit_project', requires=IS_IN_DB(db, 'project.id', '%(title)s')), 
        table_name = "edit_project"
    )
    if form_edit_project.process().accepted:
        redirect(URL(c='manage', f='browse', args=('project', 'edit', 'project', form_edit_project.vars.edit_project), 
            user_signature=True))

    # Jump to edit dataset
    form_edit_dset = SQLFORM.factory(
        Field('edit_dataset', requires=IS_IN_DB(db, 'dataset.id', '%(shortname)s')), 
        table_name = "edit_dataset"
    )
    if form_edit_dset.process().accepted:
        redirect(URL(c='manage', f='browse', args=['dataset', 'edit', 'dataset', form_edit_dset.vars.edit_dataset], 
        user_signature=True))

    # Jump to edit personnel details
    form_edit_personnel = SQLFORM.factory(
        Field('edit_personnel', requires=IS_IN_DB(db, 'personnel.id', '%(name)s')), 
        table_name = "edit_personnel"
    )
    if form_edit_personnel.process().accepted:
        redirect(URL(c='manage', f='browse', args=['personnel', 'edit', 'personnel', form_edit_personnel.vars.edit_personnel], 
        user_signature=True))

    # Jump to edit user details
    form_edit_user = SQLFORM.factory(
        Field('edit_user', requires=IS_IN_DB(db, 'cardat_user.id', '%(name)s')), 
        table_name = "edit_user"
    )
    if form_edit_user.process().accepted:
        redirect(URL(c='manage', f='browse', args=['cardat_user', 'edit', 'cardat_user', form_edit_user.vars.edit_user], 
        user_signature=True))

    return dict(form_view_dset = form_view_dset,
    form_edit_project = form_edit_project,
    form_edit_dset = form_edit_dset,
    form_edit_personnel = form_edit_personnel,
    form_edit_user = form_edit_user
    )

def duplicate_dataset():
    # Choose dataset to copy
    form = SQLFORM.factory(
        Field('select_dataset', 'dataset.id', requires=IS_IN_DB(db, 'dataset.id', '%(shortname)s')),
        Field('copy_level', requires=IS_IN_SET(("Basic metadata",)), 
            default = "Basic metadata", widget = SQLFORM.widgets.radio.widget),
        Field('confirm_duplication', requires=[IS_IN_SET((True,)), IS_NOT_EMPTY()], widget = SQLFORM.widgets.checkboxes.widget),
        table_name = "select_dataset",
        submit_button='Duplicate'
    )
    
    if form.validate():
        selected = db.dataset._filter_fields(db.dataset(form.vars.select_dataset))
        selected['shortname'] = selected['shortname'] + "_COPY"
        selected['title'] = selected['title'] + "_COPY"
        # remove publication process info, and links
        vars_nocopy = ('request_date', 'provision_status', 'provision_date', 'pubdate', 'pub_notes', 'url_link', 'repository_link')
        for i in vars_nocopy:
            selected.pop(i, None)
        new_id = db.dataset.insert(**selected)
        
        response.flash = "Dataset copied"
        redirect(URL(c='manage', f='browse', 
            args=["dataset", "edit", "dataset", new_id],
            user_signature=True))

    return dict(form=form)

def add_user_as_personnel():
    # Choose user to copy
    form = SQLFORM.factory(
        Field('select_user', 'cardat_user.id', requires=IS_IN_DB(db, 'cardat_user.id', '%(name)s')),
        Field('confirm_insert', requires=[IS_IN_SET((True,)), IS_NOT_EMPTY()], widget = SQLFORM.widgets.checkboxes.widget),
        table_name = "select_user",
        submit_button='Add as personnel record'
    )
    
    if form.validate():
        selected = db.personnel._filter_fields(db.cardat_user(form.vars.select_user))
        
        if db((db.personnel.orcid == selected['orcid']) | (db.personnel.name == selected['name'])).count():
            response.flash = "User name or ORCID already exists in personnel table"
        else:
            new_id = db.personnel.insert(**selected)
            response.flash = "User added as personnel record"
            redirect(URL(c='manage', f='browse', 
                args=["personnel", "edit", "personnel", new_id],
                user_signature=True))

    return dict(form=form)