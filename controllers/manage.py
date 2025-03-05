# General table browse with CRUD
def browse():
    table = request.args(0)
    if not table in db.tables(): redirect(URL('error'))

    # prettify
    response.title="Browse {}".format(table)

    # add anchor links in sidebar for create, view and edit forms (in hierarchy) 
    if request.args(-3) in ('view', 'edit') or request.args(-2) == 'new':
        if request.args(-3) in ('view', 'edit'):
            table_name = request.args(-2)
        elif request.args(-2) == 'new':
            table_name = request.args(-1)
         # in view/edit/create
        fields = [f.name for f in db[table_name]]
        # remove audit fields from display
        [fields.remove(f) for f in ('id', 'is_active', 'created_on', 'created_by', 'modified_on', 'modified_by') if f in fields]

        field_html_ids = [(f, "_".join([table_name, f, "_row"])) for f in fields]
        sidebar =  MENU([(fieldname, False, "#"+link) for fieldname, link in field_html_ids])


    ## options for smartgrid 
    # show these fields in smartgrid
    fields_to_show = [
            db.project.title, 
            db.j_project_personnel.project_id, db.j_project_personnel.personnel_id, db.j_project_personnel.role,

            db.dataset.shortname, db.dataset.url_link,
            db.j_dataset_personnel.dataset_id, db.j_dataset_personnel.personnel_id, db.j_dataset_personnel.role,
            db.entity.entityname, db.entity.physical_distribution,
            db.intellectualright.licence_code,
            db.dataset_publication.title, db.dataset_publication.author, db.dataset_publication.link,
            
            db.keyword.thesaurus, db.keyword.keyword,
            db.j_dataset_keyword.dataset_id, db.j_dataset_keyword.keyword_id,
            db.dataset_linkage.parent_dataset, db.dataset_linkage.child_dataset, db.dataset_linkage.linkage,

            db.attr.variable_name, db.attr.units,
            
            db.accessrequest.title, db.accessrequest.date_of_request, db.accessrequest.category_access, db.accessrequest.primary_purpose,
            db.request_dataset.accessrequest_id, db.request_dataset.dataset_id, db.request_dataset.approved, db.request_dataset.approval_date,
            db.accessor.accessrequest_id, db.accessor.repo_user_id, db.accessor.begin_date, db.accessor.end_date, db.accessor.role, db.accessor.key_contact,
            db.request_output.accessrequest_id, db.request_output.output_category, db.request_output.link, db.request_output.title, db.request_output.publication_date, db.request_output.status,

            db.repo_user.name, db.repo_user.email, db.repo_user.orcid,

            db.personnel.name, db.personnel.email, db.personnel.orcid, db.personnel.rorid
        ]
    
    orderby = dict(
        project = db.project.title,
        dataset = db.dataset.shortname,
        entity = db.entity.entityname,
        request_output = ~db.request_output.publication_date,
        repo_user = db.repo_user.name
    )
    
    # custom fields for individual tables
    links = dict()

    grid = SQLFORM.smartgrid(
        db[table],
        linked_tables=[
            'j_project_personnel', 'dataset', # child tables of project
            'j_dataset_personnel', 'entity', 'intellectualright', 'dataset_publication', 'j_dataset_keyword', # child tables of dataset
            'attr', # child table of entity
            'accessor', 'request_output', 'request_dataset' # child tables of accessrequest
            ],
        fields = fields_to_show,
        orderby = orderby,
        links = links,
        user_signature=True,
        maxtextlength = 50, 
        showbuttontext = False,
        csv=False, 
        paginate=50)

    return dict(grid=grid, 
        left_sidebar_enabled='sidebar' in locals(),
        left_sidebar=sidebar if 'sidebar' in locals() else None
        )

def dataset_detail():
    dset_id = request.args[0]
    if not dset_id in db.dataset.id: redirect(URL('error'))

    form = SQLFORM(db.dataset, record=dset_id, readonly=True, comments = False)
    # form_licence = SQLFORM(db.intellectualright, record=dset_id, readonly=True, comments = False)

    rows_licence = db(db.intellectualright.dataset_id == dset_id).select(
        db.intellectualright.id, db.intellectualright.licence_code)

    rows_personnel = db(db.j_dataset_personnel.dataset_id == dset_id).select(
        db.j_dataset_personnel.personnel_id, db.j_dataset_personnel.role)
    
    rows_accessrequests = db(db.request_dataset.dataset_id == dset_id).select(
        db.request_dataset.accessrequest_id, db.request_dataset.approval_date, 
        orderby = ~db.request_dataset.approval_date, limitby = (0, 10))

    # row = db.dataset(db.dataset.id == dset_id).select()
    # print(row)
    
    sidebar =  MENU([('Dataset details', False, '#h-dataset'),
    ('Personnel', False, '#h-personnel'),
    ('Licencing', False, '#h-licencing'),
    ('Access requests', False, '#h-accessrequests')]
    )
    
    return dict(
        form=form,
        rows_licence = rows_licence,
        rows_personnel = rows_personnel,
        rows_accessrequests = rows_accessrequests,
        left_sidebar_enabled='sidebar' in locals(),
        left_sidebar=sidebar if 'sidebar' in locals() else None
    )
    