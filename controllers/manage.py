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
            sidebar = P(A(XML('Open data dictionary ->'), 
                        _href = URL(c='index', f="data_dictionary", args = table_name, user_signature = True),
                        _target = "_blank")) + HR(_style = "margin:5px;")
        else:
            sidebar = P()
        sidebar += SPAN(XML("Jump to field:")) + MENU([(fieldname, False, '#'+link) for fieldname, link in field_html_ids])

    # bug fix of view forms - date fields not compatible with argument represent_none
    if request.args(-3) == "view":
        # no idea why omitting this causing problems with displaying view SQLFORM
        function_none_date = lambda v: v if v is not None else None
        db.project.project_established.represent = function_none_date
        db.dataset.request_date.represent = function_none_date
        db.dataset.pubdate.represent = function_none_date
        db.dataset.provision_date.represent = function_none_date
        db.dataset.temporalcoverage_begindate.represent = function_none_date
        db.dataset.temporalcoverage_enddate.represent = function_none_date
        db.accessrequest.date_of_request.represent = function_none_date
        db.accessor.begin_date.represent = function_none_date
        db.accessor.end_date.represent = function_none_date
        db.request_dataset.process_date.represent = function_none_date
        db.request_dataset.revoke_date.represent = function_none_date

    ## options for smartgrid 
    # show these fields in smartgrid
    fields_to_show = [
            db.personnel.name, db.personnel.affiliation, db.personnel.email, db.personnel.orcid, db.personnel.rorid,
            
            db.project.title, 
            db.j_project_personnel.project_id, db.j_project_personnel.personnel_id, db.j_project_personnel.role,

            db.dataset.shortname, db.dataset.dataset_type, db.dataset.provision_status, db.dataset.pubdate,
            db.j_dataset_personnel.dataset_id, db.j_dataset_personnel.personnel_id, db.j_dataset_personnel.role,
            db.entity.entityname, db.entity.entityformat, db.entity.physical_distribution,
            db.intellectualright.licence_code, db.intellectualright.accessibility, db.intellectualright.path_to_licence,
            db.dataset_publication.title, db.dataset_publication.author, db.dataset_publication.link,
            
            db.keyword.thesaurus, db.keyword.keyword,
            db.j_dataset_keyword.dataset_id, db.j_dataset_keyword.keyword_id,
            db.dataset_linkage.parent_dataset, db.dataset_linkage.child_dataset, db.dataset_linkage.linkage,

            db.attr.variable_name, db.attr.units,
            
            db.accessrequest.title, db.accessrequest.date_of_request, db.accessrequest.category_access, db.accessrequest.primary_purpose,
            db.request_dataset.accessrequest_id, db.request_dataset.dataset_id, db.request_dataset.status, db.request_dataset.process_date,
            db.accessor.accessrequest_id, db.accessor.repo_user_id, db.accessor.begin_date, db.accessor.end_date, db.accessor.role, db.accessor.key_contact,
            db.request_output.accessrequest_id, db.request_output.output_category, db.request_output.link, db.request_output.title, db.request_output.publication_date, db.request_output.status,

            db.repo_user.name, db.repo_user.affiliation, db.repo_user.email, db.repo_user.orcid
        ]
    
    orderby = dict(
        project = db.project.title,
        dataset = db.dataset.shortname,
        entity = db.entity.entityname,
        accessrequest = ~db.accessrequest.date_of_request,
        request_dataset = ~db.request_dataset.process_date,
        request_output = ~db.request_output.publication_date,
        accessor = ~db.accessor.begin_date,
        repo_user = db.repo_user.name
    )
    
    # custom fields for individual tables, mostly to link upwards for child tables
    # (e.g. accessor table link upwards to repo_user and request)
    links = dict(
      project = [
        dict(header="Datasets",
             body = lambda row: A(XML("Datasets"), _href=URL(c = 'manage', f = 'browse',
                                  args = ["project", "dataset.project_id", row.id], user_signature = True)))
        ],
      dataset = [
        dict(header="Full details",
             body = lambda row: A(XML("Details&#10143;"), _href=URL(c = 'manage', f = 'dataset_detail',
                                  args = [row.id], user_signature = True),
                                  _target = "_blank"))
        ],
      accessrequest = [
        dict(header="Full details",
             body = lambda row: A(XML("Details&#10143;"), _href=URL(c = 'manage', f = 'request_detail',
                                  args = [row.id], user_signature = True),
                                  _target = "_blank"))
        ],
      accessor = [
        dict(header="Request record",
             body = lambda row: A(XML("Request&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['accessrequest', 'view', 'accessrequest', row.accessrequest_id], user_signature = True))),
        dict(header="User record",
             body = lambda row: A(XML("User&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['repo_user', 'view', 'repo_user', row.repo_user_id], user_signature = True)))
        ],
      request_dataset = [
        dict(header="Request record",
             body = lambda row: A(XML("Request&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['accessrequest', 'view', 'accessrequest', row.accessrequest_id], user_signature = True))),
        dict(header="Dataset record",
             body = lambda row: A(XML("Dataset&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['dataset', 'view', 'dataset', row.dataset_id], user_signature = True)))
        ],
      j_project_personnel = [
        dict(header="Project record",
             body = lambda row: A(XML("Project&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['project', 'view', 'project', row.project_id], user_signature = True))),
        dict(header="Personnel record",
             body = lambda row: A(XML("Personnel&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                  args = ['personnel', 'view', 'personnel', row.personnel_id], user_signature = True)))
        ],
      j_dataset_personnel = [
        dict(header="Dataset record",
             body = lambda row: A(XML("Dataset&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                                  args = ['dataset', 'view', 'dataset', row.dataset_id], user_signature = True))),
        dict(header="Personnel record",
             body = lambda row: A(XML("Personnel&#10143;"), _href=URL(c = 'manage', f = 'browse',
                                                  args = ['personnel', 'view', 'personnel', row.personnel_id], user_signature = True)))
        ]
    )
    
    # alter display of text and pagination
    maxtextlength = dict(
      project = 75, 
      dataset = 100, 
      personnel = 50, 
      j_project_personnel = 50, 
      j_dataset_personnel = 50, 
      intellectualright = 100,
      accessrequest = 100,
      request_dataset = 100,
      request_output = 100,
      accessor = 100,
      repo_user = 100
    )
    paginate = dict(
      project = 25,
      dataset = 25,
      accessrequest = 10,
      accessor = 10
    )
    
    # allow correctly linked tables
    # do not include dataset as browsing via dataset to joining tables produces URL on dataset (from joining table) which errors
    linked_tables = [
      'j_project_personnel', # child tables of project
      'j_dataset_personnel', 'entity', 'intellectualright', 'dataset_publication', 'j_dataset_keyword', # child tables of dataset
      'attr', # child table of entity
      'accessor', 'request_output', 'request_dataset' # child tables of accessrequest
    ]

    grid = SQLFORM.smartgrid(
        db[table],
        linked_tables=linked_tables,
        fields = fields_to_show,
        orderby = orderby,
        links = links,
        maxtextlength = maxtextlength, 
        user_signature=True,
        showbuttontext = False,
        csv=False,
        represent_none="-")

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
        db.request_dataset.accessrequest_id, db.request_dataset.process_date, 
        orderby = ~db.request_dataset.process_date, limitby = (0, 10))

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
         rows_personnel, P(EM('No personnel attached.'))
         ],
        [H4('Entities (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'entity.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-entities'), 
         rows_entity, P(EM('No entities attached.'))],
         [H4('Licencing (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'intellectualright.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-licencing'), 
         rows_licence, P(EM('No licence attached.'))],
         [H4('Access requests (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'request_dataset.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-accessrequests'), 
         rows_accessrequests, P(EM('No access requests attached.'))],
         [H4('Publications (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'dataset_publication.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-publications'), 
         rows_publications, P(EM('No publications attached.'))],
         [H4('Keywords (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['dataset', 'j_dataset_keyword.dataset_id', dset_id]), user_signature = True), 
            ')', _id='h-keywords'), 
         rows_keywords, P(EM('No keywords attached.'))]
    ]
    
    return dict(
        table_heading=table_heading,
        table=table,
        subtbls = subtbls,
        left_sidebar_enabled='sidebar' in locals(),
        left_sidebar=sidebar if 'sidebar' in locals() else None
    )
    
    
def request_detail():
    accessrequest_id = request.args[0]
    if not accessrequest_id in db.accessrequest.id: redirect(URL('error'))

    # Main metadata for dataset
    rows=db(db.accessrequest.id == accessrequest_id).select()
    if rows: # transpose this and manually build table (match subtable structure)
        rows_tbl = []
        count = 1
        for field in db.accessrequest.fields:
            val = rows[0][field]
            if field in ('description', 'other_info') and val is not None:
                val = XML(val.replace('\n', '<br>'), sanitize=True, permitted_tags=['br/'])
            rows_tbl.append(TR(TD(field), TD(val), _class = 'w2p_even' if count % 2 == 0 else 'w2p_odd'))
            count += 1
        table=TABLE(THEAD(TR(TH('Field'), TH('Value'))), 
                *rows_tbl,
                _class = 'request_detail_tbl')
    else:
        table='No metadata record found.'

    table_heading = H4('Access request description (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['accessrequest', 'edit', 'accessrequest', accessrequest_id], user_signature = True)), 
            ')', _id='h-request')

    # Further tables attached to this dataset record
    rows_request_dataset = db(db.request_dataset.accessrequest_id == accessrequest_id).select(
        db.request_dataset.dataset_id, db.request_dataset.status, db.request_dataset.process_date, db.request_dataset.revoke_date)

    rows_accessors = db(db.accessor.accessrequest_id == accessrequest_id).select(
        db.accessor.repo_user_id, db.accessor.role, db.accessor.key_contact, db.accessor.begin_date, db.accessor.end_date)
    
    rows_request_output = db(db.request_output.accessrequest_id == accessrequest_id).select(
        db.request_output.title, db.request_output.author, db.request_output.output_category, db.request_output.publication_date, db.request_output.link, db.request_output.status)

    # row = db.dataset(db.dataset.id == dset_id).select()
    # print(row)
    
    sidebar =  MENU([('Request description', False, '#h-request'),
    ('Request datasets', False, '#h-request_datasets'),
    ('Accessors', False, '#h-accessors'),
    ('Request outputs', False, '#h-request_outputs')])

    # list of lists (tables to be shown)
    # each sublist has the following 3 elements - Heading, rows (to be shown), Message if zero rows
    subtbls = [
        [H4('Request datasets (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['accessrequest', 'request_dataset.accessrequest_id', accessrequest_id]), user_signature = True), 
            ')', _id='h-request_datasets'), 
         rows_request_dataset, P(EM('No datasets attached.'))
         ],
        [H4('Accessors (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['accessrequest', 'accessor.accessrequest_id', accessrequest_id]), user_signature = True), 
            ')', _id='h-accessors'), 
         rows_accessors, P(EM('No accessors attached.'))],
        [H4('Outputs (', 
            A('edit', _href=URL(c = 'manage', f = 'browse', args = ['accessrequest', 'request_output.accessrequest_id', accessrequest_id]), user_signature = True), 
            ')', _id='h-request_outputs'), 
         rows_request_output, P(EM('No outputs attached.'))]
    ]
    
    return dict(
        table_heading=table_heading,
        table=table,
        subtbls = subtbls,
        left_sidebar_enabled='sidebar' in locals(),
        left_sidebar=sidebar if 'sidebar' in locals() else None
    )
    
