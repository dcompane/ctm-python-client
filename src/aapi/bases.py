import attrs
import enum
import typing
import json
import random
from ctm_python_client.core.workflow import WorkflowDefaults, Workflow
from ctm_python_client.core.comm import Environment
from ctm_python_client.core.monitoring import RunMonitor
from aapi import *

class AAPIJob:
    pass

class AAPIObject:
    def as_aapi_dict(self):
        res = {}

        if '_type' in attrs.fields_dict(self.__class__):
            if not self._type.startswith('Condition') and not self._type.startswith('Event'):
                res['Type'] = self._type
            
        if attrs.has(self):
            for field in attrs.fields(self.__class__):
                value = self.__getattribute__(field.name)
                aapi_repr = field.metadata.get('_aapi_repr_')

                if value in [None, [], {}]:
                    continue

                if aapi_repr:
                    if '_type_aapi_' in field.metadata:
                        if '_hide_type_' in field.metadata:
                            if 'Type' in res:
                                res.__delitem__('Type')
                        continue
                    if 'as_aapi_dict' in dir(value):
                        res[aapi_repr] = value.as_aapi_dict()
                    elif isinstance(value, list):
                        res[aapi_repr] = [
                            (o.as_aapi_dict() if 'as_aapi_dict' in dir(o) else o) for o in value
                        ]
                    elif isinstance(value, enum.Enum):
                        res[aapi_repr] = value.value
                    else:
                        res[aapi_repr] = value

                elif field.metadata.get('_abstract_aapi_container_'):
                    for obj in value:
                        res[obj.object_name] = obj.as_aapi_dict()

        else:
            res['attrsibutes_valid'] = False

        return res


    def dumps_aapi(self, indent=None):
        return json.dumps(self.as_aapi_dict(), indent=indent)

    def dump_aapi(self, f,  indent=None):
        return json.dump(self.as_aapi_dict(), f, indent=indent)

    def as_dict(self):        
        return attrs.asdict(self)
    
    def run_on_demand(self, environment: Environment, workflow_defaults: WorkflowDefaults = None, inpath: str = f'run_on_demand{random.randint(100,999)}', skip_login: bool = False, file_path: str = None, delete_afterwards: bool = True) -> RunMonitor:        
        if isinstance(self, Job) or (hasattr(self, 'job_list') and self.job_list is not None and 
                  len(self.job_list) > 0) or isinstance(self, FolderJobBaseSmart):
            try:
                on_demand_workflow = Workflow(
                    environment,
                    workflow_defaults
                )
                if isinstance(self, Folder):
                    on_demand_workflow.add(self)
                else:
                    on_demand_workflow.add(self, inpath=inpath)
                
                on_demand_workflow.run_on_demand(
                    skip_login=skip_login, 
                    file_path=file_path, 
                    delete_afterwards=delete_afterwards
                    )
            except Exception as e:
                errors = [err.get('message', '') + ' ' + err.get('item', '')
                    for err in json.loads(e.body)['errors']]
                raise RuntimeError(f"AAPI request failed: {', '.join(errors)}")
            finally:
                on_demand_workflow.clear_all()
        else:
            raise Exception('Run is not allowed for json without jobs')
