# General table browse with CRUD
def browse():
    table = request.args(0)
    allowed_tables = ('project', 'dataset', 'entity', 'attr',
                      'personnel', 'j_project_personnel', 'j_dataset_personnel',
                      'intellectualright', 'dataset_publication', 'keyword', 'j_dataset_keyword', 'dataset_linkage',
                      'repo_user', 'accessrequest', 'request_dataset', 'accessor', 'request_output')
    if not table in allowed_tables: redirect(URL('error'))

    # prettify
    response.title='Browse ({} descendants)'.format(table)

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

        field_html_ids = [(f, '_'.join([table_name, f, '_row'])) for f in fields]
        
        # Construct sidebar
        # add a data dictionary link if table exists in data dictionary
        if db(db.tbl_description.tbl_nm == table_name).count() != 0:
            sidebar = P(A(XML('<strong>Open data dictionary -></strong>'), 
                        _href = URL(c='index', f="data_dictionary", args = table_name, user_signature = True),
                        _target = "_blank")) + HR(_style = "margin:5px;")
        else:
            sidebar = P()
        sidebar += SPAN(XML("Jump to field:")) + MENU([(fieldname, False, '#'+link) for fieldname, link in field_html_ids])



    ## options for smartgrid 
    # show these fields in smartgrid
    fields_to_show = [
            db.project.title, 
            db.j_project_personnel.project_id, db.j_project_personnel.personnel_id, db.j_project_personnel.role,

            db.dataset.shortname, db.dataset.provision_status,
            db.j_dataset_personnel.dataset_id, db.j_dataset_personnel.personnel_id, db.j_dataset_personnel.role,
            db.entity.entityname, db.entity.entityformat, db.entity.physical_distribution,
            db.intellectualright.licence_code, db.intellectualright.accessibility,
            db.dataset_publication.title, db.dataset_publication.author, db.dataset_publication.link,
            
            db.keyword.thesaurus, db.keyword.keyword,
            db.j_dataset_keyword.dataset_id, db.j_dataset_keyword.keyword_id,
            db.dataset_linkage.parent_dataset, db.dataset_linkage.child_dataset, db.dataset_linkage.linkage,

            db.attr.variable_name, db.attr.units,
            
            db.accessrequest.title, db.accessrequest.date_of_request, db.accessrequest.category_access, db.accessrequest.primary_purpose,
            db.request_dataset.accessrequest_id, db.request_dataset.dataset_id, db.request_dataset.status, db.request_dataset.approval_date,
            db.accessor.accessrequest_id, db.accessor.repo_user_id, db.accessor.begin_date, db.accessor.end_date, db.accessor.role, db.accessor.key_contact,
            db.request_output.accessrequest_id, db.request_output.output_category, db.request_output.link, db.request_output.title, db.request_output.publication_date, db.request_output.status,

            db.repo_user.name, db.repo_user.affiliation, db.repo_user.email, db.repo_user.orcid,

            db.personnel.name, db.personnel.affiliation, db.personnel.email, db.personnel.orcid, db.personnel.rorid
        ]
    
    orderby = dict(
        project = db.project.title,
        dataset = db.dataset.shortname,
        entity = db.entity.entityname,
        accessrequest = ~db.accessrequest.date_of_request,
        request_output = ~db.request_output.publication_date,
        accessor = ~db.accessor.begin_date,
        repo_user = db.repo_user.name
    )
    
    # custom fields for individual tables, mostly to link upwards for child tables
    # (e.g. accessor table link upwards to repo_user and request)
    links = dict(
      dataset = [
        dict(header="Details page",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'dataset_detail',
                                  args = [row.id], user_signature = True),
                                  _target = "blank"))
        ],
      accessor = [
        dict(header="Request record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['accessrequest', 'view', 'accessrequest', row.accessrequest_id], user_signature = True))),
        dict(header="User record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['repo_user', 'view', 'repo_user', row.repo_user_id], user_signature = True)))
        ],
      request_dataset = [
        dict(header="Request record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['accessrequest', 'view', 'accessrequest', row.accessrequest_id], user_signature = True))),
        dict(header="Dataset record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['dataset', 'view', 'dataset', row.dataset_id], user_signature = True)))
        ],
      j_project_personnel = [
        dict(header="Project record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['project', 'view', 'project', row.project_id], user_signature = True))),
        dict(header="Personnel record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['personnel', 'view', 'personnel', row.personnel_id], user_signature = True)))
        ],
      j_dataset_personnel = [
        dict(header="Dataset record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                                  args = ['dataset', 'view', 'dataset', row.dataset_id], user_signature = True))),
        dict(header="Personnel record",
             body = lambda row: A(XML("&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                                  args = ['personnel', 'view', 'personnel', row.personnel_id], user_signature = True)))
        ]
    )
    
    # alter display of text and pagination
    maxtextlength = dict(
      project = 75, 
      dataset = 100, 
      personnel = 50, 
      accessrequest = 100,
      accessor = 100
    )
    paginate = dict(
      project = 25,
      dataset = 25,
      accessrequest = 10,
      accessor = 10
    )

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
        maxtextlength = maxtextlength, 
        user_signature=True,
        showbuttontext = False,
        csv=False)

    return dict(grid=grid, 
        left_sidebar_enabled='sidebar' in locals(),
        left_sidebar=sidebar if 'sidebar' in locals() else None
        )

def dataset_detail():
    dset_id = request.args[0]
    if not dset_id in db.dataset.id: redirect(URL('error'))

    # Main metadata for dataset
    rows=db(db.dataset.id == dset_id).select()
    if rows: # transpose this and manually build table (match subtable structure)
        rows_tbl = []
        count = 1
        for field in db.dataset.fields:
            val = rows[0][field]
            if field in ('abstract', 'methods_protocol', 'methods_steps', 'sampling_desc', 'additional_info', 'pub_notes') and val is not None:
                val = XML(val.replace('\n', '<br>'), sanitize=True, permitted_tags=['br/'])
            rows_tbl.append(TR(TD(field), TD(val), _class = 'w2p_even' if count % 2 == 0 else 'w2p_odd'))
            count += 1
        table=TABLE(THEAD(TR(TH('Field'), TH('Value'))), 
                *rows_tbl,
                _class = 'dset_detail_tbl')
    else:
        table='No metadata record found.'

    table_heading = H4('Dataset metadata (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'edit', 'dataset', dset_id], user_signature = True)), 
            ')', _id='h-dataset')

    # Further tables attached to this dataset record
    rows_licence = db(db.intellectualright.dataset_id == dset_id).select(
        db.intellectualright.licence_code, db.intellectualright.accessibility)

    rows_personnel = db(db.j_dataset_personnel.dataset_id == dset_id).select(
        db.j_dataset_personnel.personnel_id, db.j_dataset_personnel.role)
    
    rows_accessrequests = db(db.request_dataset.dataset_id == dset_id).select(
        db.request_dataset.accessrequest_id, db.request_dataset.approval_date, 
        orderby = ~db.request_dataset.approval_date, limitby = (0, 10))

    rows_entity = db(db.entity.dataset_id == dset_id).select(
        db.entity.entityname)
    
    rows_publications = db(db.dataset_publication.dataset_id == dset_id).select(
        db.dataset_publication.title, db.dataset_publication.link, db.dataset_publication.author)
        
    rows_keywords = db(db.j_dataset_keyword.dataset_id == dset_id).select(
        db.j_dataset_keyword.keyword_id)

    # row = db.dataset(db.dataset.id == dset_id).select()
    # print(row)
    
    sidebar =  MENU([('Dataset details', False, '#h-dataset'),
    ('Personnel', False, '#h-personnel'),
    ('Entities', False, '#h-entities'),
    ('Licencing', False, '#h-licencing'),
    ('Access requests', False, '#h-accessrequests'),
    ('Publications', False, "#h-publications"),
    ('Keywords', False, "#h-keywords")]
    )

    # list of lists (tables to be shown)
    # each sublist has the following 3 elements - Heading, rows (to be shown), Message if zero rows
    subtbls = [
        [H4('Personnel (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'j_dataset_personnel.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-personnel'), 
         rows_personnel, P(XML('<strong>No personnel attached.</strong>'))
         ],
        [H4('Entities (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'entity.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-entities'), 
         rows_entity, P(XML('<strong>No entities attached.</strong>'))],
         [H4('Licencing (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'intellectualright.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-licencing'), 
         rows_licence, P(XML('<strong>No licence attached.</strong>'))],
         [H4('Access requests (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'request_dataset.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-accessrequests'), 
         rows_accessrequests, P(XML('<strong>No access requests attached.</strong>'))],
         [H4('Publications (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'dataset_publication.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-publications'), 
         rows_publications, P(XML('<strong>No publications attached.</strong>'))],
         [H4('Keywords (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'j_dataset_keyword.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-keywords'), 
         rows_keywords, P(XML('<strong>No keywords attached.</strong>'))]
    ]
    
    return dict(
        table_heading=table_heading,
        table=table,
        subtbls = subtbls,
        left_sidebar_enabled='sidebar' in locals(),
        left_sidebar=sidebar if 'sidebar' in locals() else None
    )
    
