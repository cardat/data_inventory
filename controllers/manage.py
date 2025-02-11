import form_helper
from gluon.custom_import import track_changes
track_changes(True)

# General table browse with CRUD
def browse():
    table = request.args(0)
    if not table in db.tables(): redirect(URL('error'))

    # show these fields in smartgrid
    fields_to_show = [
            db.project.title, 
            db.j_project_personnel.project_id, db.j_project_personnel.personnel_id, db.j_project_personnel.role,

            db.dataset.shortname, db.dataset.url_link,
            db.j_dataset_personnel.dataset_id, db.j_dataset_personnel.personnel_id, db.j_dataset_personnel.role,
            db.entity.entityname, db.entity.physical_distribution,
            db.intellectualright.licence_code,
            db.dataset_publication.title, db.dataset_publication.author, db.dataset_publication.link,
            db.j_dataset_keyword.dataset_id, db.j_dataset_keyword.keyword_id,

            db.attr.variable_name, db.attr.units,
            
            db.accessrequest.title, db.accessrequest.date_of_request, db.accessrequest.category_access, db.accessrequest.primary_purpose,
            db.request_dataset.accessrequest_id, db.request_dataset.dataset_id, db.request_dataset.approval_date,
            db.accessor.accessrequest_id, db.accessor.cardat_user_id, db.accessor.begin_date, db.accessor.end_date, db.accessor.role,
            db.request_output.accessrequest_id, db.request_output.output_category, db.request_output.link, db.request_output.title, db.request_output.publication_date, db.request_output.status,

            db.cardat_user.name, db.cardat_user.email, db.cardat_user.orcid,

            db.personnel.name, db.personnel.email, db.personnel.orcid, db.personnel.rorid
        ]
    
    orderby = dict(
        project = db.project.title,
        dataset = db.dataset.shortname,
        entity = db.entity.entityname,
        request_output = ~db.request_output.publication_date,
        cardat_user = db.cardat_user.name
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
    return dict(grid=grid)
