@auth.requires_login()
def dataset_check():
  # prettify
    response.title='Dataset audit tracker'
    
    if db.dataset.id.count() != db.dataset_audit.dataset_id.count():
        db.executesql('INSERT INTO dataset_audit (dataset_id) (SELECT id FROM dataset WHERE id NOT IN (SELECT dataset_id from dataset_audit));')
    
    grid = SQLFORM.grid(
        query = db(db.dataset_audit),
        field_id = db.dataset_audit.id,
        fields = [db.project.title, db.dataset.shortname, 
                  db.dataset.provision_status,
                  db.dataset_audit.description_check,
                  db.dataset_audit.personnel_check, 
                  db.dataset_audit.entity_check, 
                  db.dataset_audit.licence_check,
                  db.dataset_audit.publication_check, 
                  db.dataset_audit.keywords_check,
                  db.dataset_audit.audit_completed],
        left = [db.dataset.on(db.dataset.id==db.dataset_audit.dataset_id), db.project.on(db.dataset.project_id==db.project.id)],
        deletable = False, 
        showbuttontext = False,
        maxtextlength=100,
        orderby = [db.dataset_audit.audit_completed, db.project.title, db.dataset.shortname]
      )
    
    return dict(grid=grid)
