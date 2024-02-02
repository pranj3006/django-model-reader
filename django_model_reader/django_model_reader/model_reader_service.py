from django.apps import apps

class ModelReaderService:
    def __init__(self) -> None:
        self.apps_config = apps.get_app_configs()
        self.lst_app_label_model_name=[]
        self.set_all_lst_app_label_model_names()

    def get_model_by_name(self,app_name:str,model_name:str):
        for app_config in self.apps_config:            
            if self.get_app_label(app_config=app_config)==app_name:                
                models= app_config.get_models()
                for model in models:                    
                    if self.get_model_name(model)==model_name:
                        return model
        return None
    
    def get_app_name(self,app_config):
        """
        Get App name from app config
        """
        return app_config.name
    
    def get_app_label(self,app_config):
        """
        Get App label from app config
        """
        return app_config.label

    def get_model_app_name(self,model):
        """
        Get app name of the model
        """
        return model._meta.app_label
    
    def get_model_name(self,model):
        """
        Get model name
        """
        return model.__name__

    def get_model_db_table_name(self,model):
        """
        get db table name of the model
        """
        return model._meta.db_table
    
    def set_all_lst_app_label_model_names(self):

        for app_config in self.apps_config:
            app_label=self.get_app_label(app_config=app_config)
            models = app_config.get_models()                    
            for model in models:
                if not self.is_model_to_exclude(model):
                    model_name = self.get_model_name(model=model)
                    self.lst_app_label_model_name.append(app_label+"."+model_name)
        
    def get_model_column_names(self,model):
        return model._meta.get_fields()

    def is_model_to_exclude(self,model):
        """
        Check if a model is part of exclusion model list
        """
        
        if ("user" in str.lower(model.__name__)):
            return False
        else:
            # Check if the model's app is part of the Django core or a third-party package    
            return model._meta.app_config.name.startswith('django.') or model._meta.app_config.name.startswith('third_party_package.') 
        return False

    def get_primary_key_fields(self,model):
        """
        Get primary key fields of a Django model.
        """
        lst_primary_fields = []
        for field in model._meta.get_fields():
            if hasattr(field,"primary_key"):
                if field.primary_key:
                    lst_primary_fields.append(field.name)

        return {"lst_primary_fields": lst_primary_fields}

    def get_field_name(self,field):
        """
        Get name of the field
        """
        field_name = field.name    
        return {"field_name": field_name}

    def get_db_column(self,field):
        """
        get DB name of the field if available else use field name
        """
        db_column_name = self.get_field_name(field)["field_name"]
        if hasattr(field,"db_column"):
            if field.db_column:
                db_column_name = field.db_column
        return {"db_column_name": db_column_name}

    def get_datatype(self,field):
        """
        Get field Datatype
        """
        datatype = field.get_internal_type()
        return {"datatype": datatype}
        
    def get_related_field_details(self,field):
        """
        Get primary key fields of a Django model.
        """
        field_details = {}
        if field.is_relation and hasattr(field, 'remote_field') and field.remote_field is not None:
            # For ForeignKey fields
            
            related_app_name = field.related_model._meta.app_label
            related_model_name = field.related_model.__name__            
            related_db_table_name = field.related_model._meta.db_table
            
            related_name = getattr(field, 'related_name', None)
            if related_name:
                related_field_name=related_name
                related_db_column_name=related_name
            else:
                related_field_name = field.remote_field.name
                related_db_column_name = self.get_db_column(field.remote_field)["db_column_name"]
            
            field_details.update({"related_app_name":related_app_name})
            field_details.update({"related_model_name":related_model_name})
            field_details.update({"related_db_table_name":related_db_table_name})
            field_details.update({"related_field_name":related_field_name})
            field_details.update({"related_db_column_name":related_db_column_name})
        return field_details

    def get_column_details(self,model):
        """
        Get columns with their data types and related tables/columns of a Django model.
        """
        
        lst_column_details = []

        for field in model._meta.get_fields():
            field_details = {}
            field_details.update(self.get_field_name(field=field))
            field_details.update(self.get_db_column(field=field))
            field_details.update(self.get_datatype(field=field))
            field_details.update({"model_name":self.get_model_name(model=model)})
            field_details.update({"app_name":self.get_model_app_name(model=model)})

            field_details.update(self.get_related_field_details(field=field))
            
            lst_column_details.append(field_details)
            
        return {"lst_column_details":lst_column_details}
    
    def prepare_joins_data(self,lst_column_details):
        lst_joins = []
        for column_details in lst_column_details:
            join_details = {}
            if column_details.get("datatype")=="ForeignKey":
                source_model = column_details.get("model_name")                
                app_name = column_details.get("related_app_name")
                model_name = column_details.get("related_model_name")
                if app_name+"."+model_name in self.lst_app_label_model_name:
                    related_field_name = column_details.get("related_field_name")
                    inst_model = self.get_model_by_name(app_name=app_name,model_name=model_name)
                    if inst_model:
                        if related_field_name in self.get_model_column_names(model=inst_model):
                            join_details.update({"target_model":model_name})
                            join_details.update({"related_field":related_field_name})
                            join_details.update({'type': 'ForeignKey'})
                            join_details.update({"source_model":source_model})
                            
                            lst_joins.append(join_details)
                        else:
                            lst_primary_fields = self.get_primary_key_fields(model=inst_model)["lst_primary_fields"]
                            
                            if len(lst_primary_fields)>0:
                                lst_primary_fields=lst_primary_fields[0]
                                join_details.update({"target_model":model_name})
                                join_details.update({"related_field":lst_primary_fields})
                                join_details.update({'type': 'ForeignKey'})
                                join_details.update({"source_model":source_model})
                                lst_joins.append(join_details)
        return {"joins":lst_joins}
    
    def get_all_models(self):
        lst_apps = []        
        lst_models = []
        dct_data = {}

        # print("--------------------------------------------------------------------------------------")
        # Iterate through all installed apps
        for app_config in self.apps_config:
            lst_app_models = []
            app_name = self.get_app_name(app_config=app_config)
            dct_data.update({app_name:{}})
            # Get all models for the current app
            models = app_config.get_models()
            # Print the names of all models
            lst_apps.append(app_name)
            for model in models:
                if not self.is_model_to_exclude(model):
                    model_name = self.get_model_name(model=model)
                    db_table_name = self.get_model_db_table_name(model=model)
                    lst_primary_fields = self.get_primary_key_fields(model=model)
                    lst_column_details = self.get_column_details(model=model)
                    lst_joins_details = self.prepare_joins_data(lst_column_details["lst_column_details"])

                    dct_data[app_name].update({model_name:{}})
                    model_details = {}
                    model_details.update({"app_name":app_name,"model_name":model_name,"db_table_name":db_table_name})
                    model_details.update(lst_primary_fields)
                    model_details.update(lst_column_details)
                    model_details.update(lst_column_details)
                    model_details.update(lst_joins_details)                    
                    
                    dct_data[app_name][model_name].update(model_details)
                    lst_models.append(model_name)
                    lst_app_models.append(model_name)

                    # print("App : " + app_name + " Model : "+ model_name)
                    # print("Primary key fields : ",lst_primary_fields["lst_primary_fields"])
                    # print("Joins Details  : ",lst_joins_details["joins"])
                    
                    # for column_details in lst_column_details["lst_column_details"]:
                        # print(f"{column_details}")
                    # print("--------------------------------------------------------------------------------------")
            dct_data[app_name].update({"lst_app_models":lst_app_models})
            
            if len(lst_app_models)==0:
                del dct_data[app_name]
                lst_apps.remove(app_name)
        
        return {"lst_apps":lst_apps,"dct_data":dct_data}        

