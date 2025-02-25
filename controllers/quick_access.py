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
        redirect(URL(c='manage', f='browse', args=('project', 'edit ', 'project', form_edit_project.vars.edit_project), 
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

    return dict(form=[form_view_dset,
    form_edit_project,
    form_edit_dset,
    form_edit_personnel,
    form_edit_user
    ])

    